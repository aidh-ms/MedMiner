"""Model initialization utilities for MedMiner.

This module provides utilities for initializing and configuring language models
used throughout the MedMiner application.
"""

from langchain.chat_models import init_chat_model

from medminer.conf import settings


def load_model():
    """Initialize and return a chat model based on the current settings.

    Retrieves the model configuration from the global settings and initializes
    a LangChain chat model with the configured provider and parameters.

    Returns:
        An initialized LangChain chat model instance.

    Raises:
        ValueError: If MODEL is not configured in settings.

    Examples:
        >>> from medminer.conf import settings
        >>> # Assuming settings.MODEL is properly configured
        >>> model = get_model()
        >>> # Use the model for chat completions
    """
    if settings.MODEL is None:
        raise ValueError("Model configuration is not set in settings.")

    return init_chat_model(
        **settings.MODEL.model_dump()  # type: ignore[possibly-missing-attribute]
    )
