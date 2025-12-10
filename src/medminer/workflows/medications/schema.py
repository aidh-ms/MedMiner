"""Medication extraction workflow schema definitions.

This module defines the data models for medication extraction, including the raw
extracted medication data and the enriched medication data with RxNorm and ATC codes.
"""

from pydantic import BaseModel

from medminer.workflows.base.schema import ExtractionState


class ExtractedMedication(BaseModel):
    """Raw medication data extracted from medical documents.

    Attributes:
        reference: The medication as it appears in the original text with all details.
        name: The name of the medication (brand name or generic name).
        name_translated: The medication name translated to English without additional details.
        active_ingredient: The active ingredient of the medication.
        dose: The numeric value of the dose (-1 if not specified).
        unit: The unit of the dose (e.g., mg, ml).
        route: The route of administration (e.g., oral, intravenous).
        frequency: The frequency of the medication (e.g., 1-0-1-0, as needed).
        frequency_code: The standardized frequency code (e.g., BID, Q8H).
    """
    reference: str
    name: str
    name_translated: str
    active_ingredient: str
    dose: float
    unit: str
    route: str
    frequency: str
    frequency_code: str


class Medication(ExtractedMedication):
    """Enriched medication data with RxNorm and ATC codes.

    Extends ExtractedMedication with standardized medical coding information.

    Attributes:
        rxcui: RxNorm Concept Unique Identifier from the RxNav API.
        atc_codes: List of Anatomical Therapeutic Chemical (ATC) classification codes.
    """
    rxcui: str
    atc_codes: list[str]


class MedicationState(ExtractionState[ExtractedMedication, Medication]):
    """State container for the medication extraction workflow.

    Inherits from ExtractionState and specifies ExtractedMedication as the raw data type
    and Medication as the processed data type.
    """

    pass
