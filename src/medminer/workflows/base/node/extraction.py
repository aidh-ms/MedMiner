"""Extraction and processing nodes for workflows.

This module provides node implementations for extracting structured information
from medical documents and processing the extracted data. Includes the main
InformationExtractor node that uses LLMs with structured output.
"""

from typing import Any, Literal

from langchain.chat_models import BaseChatModel
from langchain.messages import HumanMessage, SystemMessage

from medminer.workflows.base.node.base import BaseNode
from medminer.workflows.base.schema import ExtractionState, ResponseFormat


class NoProcessing(BaseNode):
    """Passthrough node that copies extracted data to processed data.

    This node is used when no additional processing is needed after extraction.
    """

    def __call__(self, state: ExtractionState) -> dict[Literal["processed_data"], list]:
        """Copy extracted data to processed data without modification.

        Args:
            state: The extraction state.

        Returns:
            Dictionary with 'processed_data' key containing the unmodified extracted data.
        """
        return {
            "processed_data": state.extracted_data
        }



class InformationExtractor(BaseNode):
    """Node for extracting structured information from text using an LLM.

    This node uses a language model with structured output to extract
    specific information from the doctor's letter based on a given prompt.

    Attributes:
        _model: Language model configured for structured output.
        _prompt: The extraction prompt for the LLM.
        _response_format: The expected response format schema.
    """

    def __init__(self, model: BaseChatModel, prompt: str, response_format: type[ResponseFormat], **kwargs: Any) -> None:
        """Initialize the information extractor.

        Args:
            model: The language model to use for extraction.
            prompt: The system prompt guiding the extraction.
            response_format: The Pydantic model defining the expected response structure.
        """
        super().__init__(model)

        self._model = model.with_structured_output(response_format)
        self._prompt = prompt
        self._response_format = response_format

    def __call__(self, state: ExtractionState) -> dict:
        """Extract information from the doctor's letter.

        Args:
            state: The extraction state containing the letter text.

        Returns:
            Dictionary with 'extracted_data' key containing the extracted items.
        """
        response = self._model.invoke([
            SystemMessage(content=self._prompt),
            HumanMessage(content=state.letter),
        ], response_format=self._response_format)

        assert isinstance(response, self._response_format)
        assert hasattr(response, "data")
        return {
            "extracted_data": response.data
        }
