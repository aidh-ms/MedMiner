"""Base schema definitions for workflow state management.

This module defines the fundamental state types used across all MedMiner workflows,
including doctor's letter state and extraction state templates.
"""

from types import get_original_bases

from pydantic import BaseModel, Field
from pydantic._internal._generics import get_args
from pydantic.generics import GenericModel


class DoctorsLetterState(BaseModel):
    """Base state for workflows processing doctor's letters.

    Attributes:
        patient_id: Unique identifier for the patient.
        letter: The full text content of the doctor's letter.
    """

    patient_id: str
    letter: str


class ResponseFormat[T](GenericModel):
    """Generic response format for structured LLM outputs.

    This is used to wrap extracted data from LLM responses.

    Attributes:
        data: List of extracted items of type T.
    """

    data: list[T]


class ExtractionState[ET, PT](DoctorsLetterState):
    """Generic state for extraction workflows.

    Extends DoctorsLetterState with fields for tracking extracted and processed data.

    Type Parameters:
        ET: The type of extracted (raw) data items.
        PT: The type of processed (enriched) data items.

    Attributes:
        extracted_data: List of raw data items extracted by the LLM.
        processed_data: List of processed/enriched data items.
        path: File path where the processed data is saved.
    """

    extracted_data: list[ET] = Field(default_factory=list)
    processed_data: list[PT] = Field(default_factory=list)
    path: str = ""

    @classmethod
    def response_format_type(cls) -> type[ResponseFormat[ET]]:
        """Get the response format type for LLM structured output.

        Returns:
            A ResponseFormat class parameterized with the extracted data type.
        """
        base = get_original_bases(cls)[0]
        if not (types := get_args(base)):
           raise TypeError(f"Could not resolve generic type for '{cls.__name__}'.")
        _type = types[0]

        class _ResponseFormat(ResponseFormat[_type]):
            data: list[_type]

        return _ResponseFormat
