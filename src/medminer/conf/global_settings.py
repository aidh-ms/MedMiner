"""Global settings configuration for MedMiner.

This module defines the application-wide settings using Pydantic BaseSettings,
supporting configuration via environment variables and .env files.
"""

from abc import ABCMeta
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseModelSettings(BaseModel, metaclass=ABCMeta):
    """Abstract base class for model provider settings.

    Attributes:
        model_provider: The name of the model provider (e.g., 'openai').
    """

    model_provider: str


class OpenAIModelSettings(BaseModelSettings):
    """Settings for OpenAI model configuration.

    Attributes:
        model_provider: The model provider name, defaults to 'openai'.
        model: The OpenAI model name (e.g., 'gpt-oss-120b').
        api_key: The OpenAI API key for authentication.
        base_url: The base URL for the OpenAI API endpoint.
    """

    model_provider: Literal["openai"] = Field(default="openai", description="Model provider")
    model: str = Field(..., description="OpenAI model name")
    api_key: str = Field(..., description="OpenAI API key")
    base_url: str = Field(..., description="OpenAI API base URL")


class Settings(BaseSettings):
    """Application-wide settings for MedMiner.

    Settings can be configured via environment variables with the MEDMINER_ prefix,
    or through a .env file. Nested settings use double underscore (__) as delimiter.

    Attributes:
        MODEL: Language model configuration settings.
        BASE_DIR: Base directory for storing extracted data (CSV files).
        SPLIT_PATIENT: Whether to split output files by patient ID.
        SNOWSTORM_BASE_URL: Base URL for the SNOMED Snowstorm server.
        ICD_CLIENT_ID: Client ID for ICD-11 API authentication.
        ICD_CLIENT_SECRET: Client Secret for ICD-11 API authentication.

    Examples:
        >>> # Via environment variables
        >>> # MEDMINER_MODEL__MODEL_PROVIDER=openai
        >>> # MEDMINER_MODEL__MODEL=gpt-oss-120b
        >>> settings = Settings()
    """
    model_config = SettingsConfigDict(
        env_prefix="MEDMINER_",
        env_file=".env",
        env_nested_delimiter="__",
        env_nested_max_split=1,
    )

    MODEL: OpenAIModelSettings | None = Field(default=None, description="Settings for the language model to use")

    # Storage settings
    BASE_DIR: Path = Field(
        default_factory=Path.cwd,
        description="Base directory for storing extracted data (CSV files)",
    )
    SPLIT_PATIENT: bool = Field(
        default=False,
        description="Whether to split output files by patient ID",
    )

    # SNOWSTORM (SNOMED CT) settings
    SNOWSTORM_BASE_URL: str = Field(
        default="",
        description="Base URL for the SNOMED Snowstorm server",
    )

    # ICD-11 settings
    ICD_CLIENT_ID: str = Field(
        default="",
        description="Client ID for ICD-11 API",
    )
    ICD_CLIENT_SECRET: str = Field(
        default="",
        description="Client Secret for ICD-11 API",
    )
