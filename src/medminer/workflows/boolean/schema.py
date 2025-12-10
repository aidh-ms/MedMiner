"""Boolean statement extraction workflow schema definitions.

This module defines the data models for boolean statement extraction, which allows
filtering and labeling of patient data based on custom criteria from medical documents.
"""

from pydantic import BaseModel

from medminer.workflows.base.schema import ExtractionState


class ExtractedStatement(BaseModel):
    """Raw boolean statement data extracted from medical documents.

    Attributes:
        filter: Boolean value indicating whether the statement is true or false.
        information: The extracted information supporting the filter decision.
        reference: The exact text snippet used to make the decision.
    """
    filter: bool
    information: str
    reference: str


class StatementState(ExtractionState[ExtractedStatement, ExtractedStatement]):
    """State container for the boolean statement extraction workflow.

    Inherits from ExtractionState and specifies ExtractedStatement as both the raw data type
    and the processed data type (no transformation needed).
    """

    pass
