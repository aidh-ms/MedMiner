"""SNOMED CT Snowstorm API integration for procedure code enrichment.

This module provides functionality to enrich extracted procedure data with SNOMED CT
codes using the Snowstorm API. It includes LLM-assisted selection of the best matching
codes when multiple candidates are found.
"""

from itertools import combinations
from textwrap import dedent
from typing import Any, Iterator, Literal

from pydantic import BaseModel

from medminer.conf import settings
from medminer.workflows.base.node.base import HTTPBaseNode
from medminer.workflows.procedure.schema import ExtractedProcedure, Procedure, ProcedureState


class SnomedSelectionResponseFormat(BaseModel):
    """LLM selection of the best SNOMED CT match."""
    selected_concept_id: str


class SnomedProcedureLookup(HTTPBaseNode):
    """Lookup SNOMED CT codes for extracted procedures using the Snowstorm API."""
    prompt = dedent("""\
        You are a medical coding expert. Given a procedure description and a list of SNOMED CT matches, select the most appropriate SNOMED CT code.

        Procedure Information:
        - Original reference: {ref}
        - Procedure name: {name}
        - Translated name: {translated}
        - Search term: {search_term}

        Available SNOMED CT Matches:
        {candidates}

        Select the most appropriate SNOMED CT code that best matches the procedure. Consider:
        1. Specificity: Prefer more specific codes over general ones
        2. Accuracy: The code should accurately represent the procedure
        3. Clinical relevance: The code should be clinically meaningful

        If none of the matches are appropriate, select the first concept ID and explain why in your reasoning.
    """)

    def __init__(self, model, **kwargs: Any) -> None:
        """Initialize the SNOMED procedure lookup node.

        Args:
            model: The language model to use for selection.
            **kwargs: Arbitrary keyword arguments passed to HTTPBaseNode.
        """
        super().__init__(
            model,
            base_url=settings.SNOWSTORM_BASE_URL,
            params = {
                "activeFilter": "true",
                "termActive": "true",
            },
            **kwargs
        )

    def __call__(self, state: ProcedureState) -> dict[Literal["processed_data"], list[Procedure]]:
        """Process extracted procedures and enrich with SNOMED CT codes.

        Args:
            state: The current procedure extraction state containing extracted_data.

        Returns:
            Dictionary with "processed_data" key containing list of enriched Procedure objects.
        """
        procedures: list[Procedure] = []
        for proc in state.extracted_data:
            snomed_id, snomed_fsn = "", ""
            if settings.SNOWSTORM_BASE_URL:
                snomed_id, snomed_fsn = self._get_snomed_info(proc)

            procedures.append(
                Procedure.model_validate({
                    **proc.model_dump(),
                    "snomed_id": snomed_id,
                    "snomed_fsn": snomed_fsn,
                })
            )

        return {"processed_data": procedures}

    def _get_snomed_info(self, proc: ExtractedProcedure) -> tuple[str, str]:
        """
        Get the SNOMED CT code for a procedure.

        Args:
            proc: The extracted procedure data

        Returns:
            Tuple of (snomed_id, snomed_fsn)
        """
        for query in self._build_ecl_queries(proc.search_term):
            response = self._make_request("concepts", params={"ecl": query})
            assert isinstance(response, dict)

            candidates = sorted([
                {"concept_id": candidate.get("conceptId", ""), "fsn": candidate.get("fsn", {}).get("term")}
                for candidate in response.get("items", [])
                if candidate.get("definitionStatus") in ["FULLY_DEFINED", "PRIMITIVE"]
            ], key=lambda x: len(x["fsn"]))

            if not response:
                continue

            candidates_text = "\n".join(
                [f"- Concept ID: {candidate['concept_id']}, FSN: {candidate['fsn']}" for candidate in candidates]
            )
            selected = self._invoke_model(
                system_prompt="You are a medical coding assistant.",
                user_prompt=self.prompt.format(
                    ref=proc.reference,
                    name=proc.name,
                    translated=proc.name_translated,
                    search_term=proc.search_term,
                    candidates=candidates_text
                ),
                response_format=SnomedSelectionResponseFormat
            )
            if selected:
                for candidate in candidates:
                    if candidate["concept_id"] == selected.selected_concept_id:
                        return candidate["concept_id"], candidate["fsn"]

        return "", ""

    def _build_ecl_queries(self, term: str) -> Iterator[str]:
        """
        Build ECL queries with progressively relaxed constraints.

        Args:
            term: The search term

        Yields:
            ECL query strings
        """
        procedure_definition = "< 71388002|Procedure|"

        yield f'{procedure_definition} {{{{ term = "{term}"}}}}'

        words = term.split(" ")
        if len(words) > 1:
            if len(words) > 2:
                for i in reversed(range(1, len(words) - 1)):
                    word_comps = [f'term = ("{" ".join(word_comp)}")' for word_comp in combinations(words, i + 1)]
                    yield f'{procedure_definition} {{{{ {", ".join(word_comps)} }}}}'

            yield f'{procedure_definition} {{{{ term = ("{'" "'.join(words)}")}}}}'
