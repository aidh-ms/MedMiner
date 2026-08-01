"""Procedure extraction workflow schema definitions.

This module defines the data models for procedure extraction, including the raw
extracted procedure data and the enriched procedure data with ICD-11 codes.
"""

from pydantic import BaseModel

from medminer.workflows.base.schema import ExtractionState


class ExtractedProcedure(BaseModel):
    """Raw procedure data extracted from medical documents.

    Attributes:
        reference: The procedure as it appears in the original text.
        name: The name of the procedure.
        name_translated: The procedure name translated to English.
        year: The year the procedure was performed (-1 if not specified).
        month: The month the procedure was performed (-1 if not specified).
        day: The day the procedure was performed (-1 if not specified).
    """
    reference: str
    name: str
    name_translated: str
    year: int
    month: int
    day: int


class Procedure(ExtractedProcedure):
    """Enriched procedure data with ICD-11 codes.

    Extends ExtractedProcedure with standardized ICD-11 medical coding information.

    Attributes:
        icd11_code: The ICD-11 code.
        icd11_title: The title of the ICD-11 code.
    """

    icd11_code: str
    icd11_title: str


class ProcedureState(ExtractionState[ExtractedProcedure, Procedure]):
    """State container for the procedure extraction workflow.

    Inherits from ExtractionState and specifies ExtractedProcedure as the raw data type
    and Procedure as the processed data type.
    """

    pass
