from __future__ import annotations

from enum import StrEnum, auto
from itertools import combinations

import httpx
from smolagents import Tool, tool

from medminer.tools.settings import ToolSetting, ToolSettingMixin


@tool
def extract_procedure_data(
    data: list[dict],
) -> list[dict]:
    """
    Adds extracted data to the task memory.

    Args:
        data: A list of dictionaries containing the data to save.
            All dictionaries must have the following keys.
            - patient_id: The patient ID.
            - date: The date of the procedure. If not applicable, write an empty string.
            - procedure_reference: The original text containing the procedure. Use only the procedure text.
            - procedure_corrected: Translate the procedures to English if necessary and infer the column. Change abbreviations to full words. For example, "CT" should be changed to "Computed Tomography".
            - procedure_search: The relevant procedure as a string. Remove everything that is not relevant. Separate the words with a space.
            - procedure: The relevant procedure as a string. Remove everything that is not relevant.
    Returns:
        A message indicating where the data was saved.

    Example:
        >>> data = [
        ...     {"patient_id": 1, ...},
        ...     {"patient_id": 2, ...},
        ... ]
        >>> extract_medication_data("medication", data)
    """
    return data


class SNOMEDQueryMethod(StrEnum):
    """Enum for SNOMED CT query types."""

    STRICT = auto()
    SUBSET = auto()
    ANY = auto()


class SNOMEDTool(ToolSettingMixin, Tool):
    """A tool for searching SNOMED CT concepts."""

    name = "search_snomed_procedures"
    description = "Search SNOMED CT for procedures matching the given term."
    inputs = {
        "term": {"type": "string", "description": "The search term (written out text) to query."},
    }
    output_type = "array"
    settings = [
        ToolSetting(id="base_url", label="Base URL", type=str),
        ToolSetting(id="edition", label="Edition", type=str),
    ]
    base_url: str
    edition: str

    def _build_ecl_query(self, term: str, method: SNOMEDQueryMethod) -> str:
        """
        Build the ECL query for SNOMED CT.

        Args:
            term (str): The search term to query.

        Returns:
            str: The ECL query string.
        """
        procedure_definition = "< 71388002|Procedure|"

        if method == SNOMEDQueryMethod.STRICT:
            return f'{procedure_definition} {{{{ term = "{term}"}}}}'

        terms = term.split(" ")
        if method == SNOMEDQueryMethod.SUBSET and len(terms) > 2:
            sub_terms = [" ".join(comb) for i in reversed(range(1, len(terms))) for comb in combinations(terms, i + 1)]
            return f'{procedure_definition} {{{{ term = ("{'" "'.join(sub_terms)}")}}}} '

        return f'< 71388002|Procedure| {{{{ term = ("{'" "'.join(terms)}")}}}}'

    def forward(
        self,
        term: str,
    ) -> list[dict]:
        """
        Search SNOMED CT for procedures matching the given term.

        Args:
            term (str): The search term to query.
            limit (int): The maximum number of results to return.
            semantic_tag (str): The semantic tag to filter results by.

        Returns:
            list[dict]: A list of dictionaries containing procedure details.
        """
        limit = 100
        params = {
            "activeFilter": "true",  # Recommended filter by SNOMED CT
            "termActive": "true",  # Recommended filter by SNOMED CT
            "ecl": f'< 71388002|Procedure| {{{{ term = "{term}"}}}}',
        }
        with httpx.Client(base_url=self.base_url) as client:
            for method in SNOMEDQueryMethod:
                params["ecl"] = self._build_ecl_query(term, method)
                response = client.get(f"{self.edition}/concepts", params=params)
                response.raise_for_status()
                items = response.json().get("items", [])

                if items:
                    break

            filtered_matches = [
                {
                    "id": match["conceptId"],
                    "term": match["pt"]["term"],
                    "fsn": match["fsn"]["term"],
                }
                for match in items
                if match["definitionStatus"] in ["FULLY_DEFINED", "PRIMITIVE"]
            ]
            filtered_matches = sorted(
                filtered_matches,
                key=lambda x: len(x["fsn"]),
            )

            return filtered_matches[:limit]
