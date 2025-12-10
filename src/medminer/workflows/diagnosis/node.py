"""WHO ICD API integration for diagnosis code enrichment.

This module provides functionality to enrich extracted diagnosis data with ICD-11
codes using the World Health Organization's ICD-11 API. It includes LLM-assisted
selection of the best matching codes when multiple candidates are found.
"""

from textwrap import dedent
from typing import Any, Literal

from pydantic import BaseModel

from medminer.conf import settings
from medminer.workflows.base.node.base import HTTPBaseNode
from medminer.workflows.diagnosis.schema import Diagnosis, DiagnosisState, ExtractedDiagnosis


class ICDSelectionResponseFormat(BaseModel):
    """LLM selection of the best ICD-11 match."""
    code: str


class ICDDiagnosisLookup(HTTPBaseNode):
    """Lookup ICD-11 codes for extracted diagnoses using the WHO ICD API."""
    prompt = dedent("""\
        You are a medical coding expert. Given a diagnosis description and a list of ICD-11 matches, select the most appropriate ICD-11 code.

        Diagnosis Information:
        - Original reference: {ref}
        - Diagnosis name: {name}
        - Translated name: {translated}

        Available ICD-11 Matches (sorted by relevance score):
        {candidates}

        Select the most appropriate ICD-11 code that best matches the diagnosis. Consider:
        1. Specificity: Prefer more specific codes over general ones
        2. Accuracy: The code should accurately represent the diagnosis
        3. Clinical relevance: The code should be clinically meaningful
        4. Search score: Higher scores indicate better matches, but use your medical expertise

        Return the ICD-11 code (e.g., "1A00" or "BA00.0") of the best match.
    """)

    def __init__(self, model, **kwargs: Any) -> None:
        """Initialize the ICD diagnosis lookup node.

        Args:
            model: The language model to use for selection.
            **kwargs: Arbitrary keyword arguments passed to HTTPBaseNode.
        """
        super().__init__(
            model,
            base_url="https://id.who.int/",
            headers={
                "Accept-Language": "en",
                "API-Version": "v2",
            },
            auth={
                "client_id": settings.ICD_CLIENT_ID,
                "client_secret": settings.ICD_CLIENT_SECRET,
                "scope": ["icdapi_access"],
                "token_url": "https://icdaccessmanagement.who.int/connect/token",
            },
            **kwargs
        )


    def __call__(self, state: DiagnosisState) -> dict[Literal["processed_data"], list[Diagnosis]]:
        """Process extracted diagnoses and enrich with ICD-11 codes.

        Args:
            state: The current diagnosis extraction state containing extracted_data.

        Returns:
            Dictionary with "processed_data" key containing list of enriched Diagnosis objects.
        """
        diagnoses: list[Diagnosis] = []
        for diag in state.extracted_data:
            icd11_code, icd11_title = "", ""
            if settings.ICD_CLIENT_ID and settings.ICD_CLIENT_SECRET:
                icd11_code, icd11_title = self._get_icd11_data(diag)

            diagnoses.append(
                Diagnosis.model_validate({
                    **diag.model_dump(),
                    "icd11_code": icd11_code,
                    "icd11_title": icd11_title,
                })
            )

        return {"processed_data": diagnoses}

    def _get_icd11_data(self, diag: ExtractedDiagnosis) -> tuple[str, str]:
        """
        Get the ICD-11 code for a diagnosis.

        Args:
            diag: The extracted diagnosis data

        Returns:
            Tuple of (icd11_code, icd11_title)
        """
        response = self._make_request(
            "icd/release/11/2022-02/mms/search",
            params={"q": diag.name_translated, "useFlexisearch": "true"}
        )
        assert isinstance(response, dict)

        candidates = [
            {
                "code": candidate.get("theCode", ""),
                "score": candidate.get("score", 0.0),
                "title": candidate.get("title", ""),
            }
            for candidate in response.get("destinationEntities", [])
            if candidate.get("score", 0.0) > 0.3
        ]

        if not candidates:
            return "", ""

        for candidate in candidates:
            if candidate.get("score", 0.0) == 1:
                return candidate.get("code", ""), candidate.get("title", "")


        candidates_text = "\n".join([
            f"- Code: {c.get('code', '')}, Title: {c.get('title', '')}, Score: {c.get('score', 0):.2f}"
            for c in candidates
        ])
        selected = self._invoke_model(
            system_prompt="You are a medical coding assistant.",
            user_prompt=self.prompt.format(
                ref=diag.reference,
                name=diag.name,
                translated=diag.name_translated,
                candidates=candidates_text
            ),
            response_format=ICDSelectionResponseFormat,
        )
        if selected:
            for candidate in candidates:
                if candidate.get("code") != selected.code:
                    continue
                return candidate.get("code", ""), candidate.get("title", "")

        return candidates[0].get("code", ""), candidates[0].get("title", "")
