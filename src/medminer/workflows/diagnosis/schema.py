"""Diagnosis extraction workflow schema definitions.

This module defines the data models for diagnosis extraction, including the raw
extracted diagnosis data and the enriched diagnosis data with ICD-11 codes.
"""

from pydantic import BaseModel

from medminer.workflows.base.schema import ExtractionState


class ExtractedDiagnosis(BaseModel):
    """Raw diagnosis data extracted from medical documents.

    Attributes:
        reference: The diagnosis as it appears in the original text.
        name: The name of the diagnosis.
        name_translated: The diagnosis name translated to English.
        year: The year the diagnosis was made (-1 if not specified).
        month: The month the diagnosis was made (-1 if not specified).
        day: The day the diagnosis was made (-1 if not specified).
    """
    reference: str
    name: str
    name_translated: str
    year: int
    month: int
    day: int


class Diagnosis(ExtractedDiagnosis):
    """Enriched diagnosis data with ICD-11 codes.

    Extends ExtractedDiagnosis with standardized ICD-11 medical coding information.

    Attributes:
        icd11_code: The ICD-11 classification code from the WHO ICD API.
        icd11_title: The official ICD-11 title for the diagnosis.
    """

    icd11_code: str
    icd11_title: str

class DiagnosisState(ExtractionState[ExtractedDiagnosis, Diagnosis]):
    """State container for the diagnosis extraction workflow.

    Inherits from ExtractionState and specifies ExtractedDiagnosis as the raw data type
    and Diagnosis as the processed data type.
    """

    pass
