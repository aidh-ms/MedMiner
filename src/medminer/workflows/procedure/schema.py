"""Procedure extraction workflow schema definitions.

This module defines the data models for procedure extraction, including the raw
extracted procedure data and the enriched procedure data with SNOMED CT codes.
"""

from pydantic import BaseModel

from medminer.workflows.base.schema import ExtractionState


class ExtractedProcedure(BaseModel):
    """Raw procedure data extracted from medical documents.

    Attributes:
        reference: The procedure as it appears in the original text.
        name: The name of the procedure.
        name_translated: The procedure name translated to English.
        search_term: A search term optimized for finding the procedure in SNOMED CT.
        year: The year the procedure was performed (-1 if not specified).
        month: The month the procedure was performed (-1 if not specified).
        day: The day the procedure was performed (-1 if not specified).
    """
    reference: str
    name: str
    name_translated: str
    search_term: str
    year: int
    month: int
    day: int


class Procedure(ExtractedProcedure):
    """Enriched procedure data with SNOMED CT codes.

    Extends ExtractedProcedure with standardized SNOMED CT medical coding information.

    Attributes:
        snomed_id: The SNOMED CT concept ID.
        snomed_fsn: The SNOMED CT Fully Specified Name (FSN).
    """

    snomed_id: str
    snomed_fsn: str


class ProcedureState(ExtractionState[ExtractedProcedure, Procedure]):
    """State container for the procedure extraction workflow.

    Inherits from ExtractionState and specifies ExtractedProcedure as the raw data type
    and Procedure as the processed data type.
    """

    pass
