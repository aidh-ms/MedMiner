"""RxNav API integration for medication code enrichment.

This module provides functionality to enrich extracted medication data with RxNorm
Concept Unique Identifiers (RxCUI) and Anatomical Therapeutic Chemical (ATC) codes
using the RxNav API from the National Library of Medicine.
"""

from typing import Literal

from langchain.chat_models import BaseChatModel

from medminer.workflows.base.node.base import HTTPBaseNode
from medminer.workflows.medications.schema import ExtractedMedication, Medication, MedicationState


class RxNavLookup(HTTPBaseNode):
    """Processing node that enriches medications with RxNorm and ATC codes.

    This node queries the RxNav API to find RxCUI codes for medications and
    retrieves associated ATC classification codes.
    """
    def __init__(self, model: BaseChatModel, **kwargs: dict) -> None:
        super().__init__(model, base_url="https://rxnav.nlm.nih.gov/REST/", **kwargs)

    def __call__(self, state: MedicationState) -> dict[Literal["processed_data"], list[Medication]]:
        """Process extracted medications and enrich with RxNorm/ATC codes.

        Args:
            state: The current medication extraction state containing extracted_data.

        Returns:
            Dictionary with "processed_data" key containing list of enriched Medication objects.
        """
        medications: list[Medication] = []

        for med in state.extracted_data:
            rxcui = self._get_rxcui(med)

            if not rxcui:
                medications.append(Medication.model_validate({**med.model_dump(), "rxcui": "", "atc_codes": []}))
                continue

            atc_codes = self._get_atc_codes(rxcui)
            medications.append(Medication.model_validate({**med.model_dump(), "rxcui": rxcui, "atc_codes": atc_codes}))
        return {"processed_data": medications}

    def _get_rxcui(self, med: ExtractedMedication) -> str:
        """Retrieve RxNorm Concept Unique Identifier for a medication.

        Queries the RxNav API first with exact name match, then falls back to
        approximate term matching if no exact match is found.

        Args:
            med: The extracted medication data.

        Returns:
            RxCUI string if found, empty string otherwise.
        """
        response = self._make_request("rxcui.json", params={"name": med.name_translated})
        assert isinstance(response, dict)

        data = response.get("idGroup", {}).get("rxnormId", [])
        if data:
            return data[0]

        response = self._make_request("approximateTerm.json", params={"term": f"{med.name_translated} {med.active_ingredient}"})
        assert isinstance(response, dict)

        candidates = response.get("approximateGroup", {}).get("candidate", [])
        if candidates:
            return candidates[0].get("rxcui", "")

        return ""


    def _get_atc_codes(self, rxcui: str) -> list[str]:
        """Retrieve ATC codes for a given RxCUI.

        Queries the RxNav API to get all properties for a medication and extracts
        the Anatomical Therapeutic Chemical (ATC) classification codes.

        Args:
            rxcui: The RxNorm Concept Unique Identifier.

        Returns:
            List of ATC code strings, empty list if none found.
        """
        response = self._make_request(f"rxcui/{rxcui}/allProperties.json", params={"prop": "Codes"})
        assert isinstance(response, dict)

        codes = response.get("propConceptGroup", {}).get("propConcept", [])
        return [
            code["propValue"]
            for code in codes
            if code["propName"].lower() == "atc"
        ]
