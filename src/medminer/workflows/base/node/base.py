"""Base node classes for workflow processing.

This module provides the abstract base class for all workflow nodes in MedMiner.
Nodes are the fundamental processing units within LangGraph workflows, each taking
a state as input and returning state updates.
"""

from abc import ABCMeta, abstractmethod
from typing import Any

from httpx import Auth, Client, HTTPError
from httpx_auth import OAuth2ClientCredentials
from langchain.chat_models import BaseChatModel
from langchain.messages import HumanMessage, SystemMessage
from pydantic import BaseModel
from typing_extensions import Literal

from medminer.utils.name import NameMixin


class BaseNode(NameMixin, metaclass=ABCMeta):
    """Abstract base class for workflow nodes.

    Nodes are the processing units within a workflow. Each node takes a state
    as input and returns a dictionary of state updates.

    Attributes:
        _model: The language model used by this node.
    """

    def __init__(self, model: BaseChatModel, **kwargs: Any) -> None:
        """Initialize the node with a language model.

        Args:
            model: The language model to use for processing.
        """
        self._model = model

    @abstractmethod
    def __call__(self, state) -> dict:
        """Process the state and return updates.

        Args:
            state: The current workflow state.

        Returns:
            Dictionary of state updates to apply.
        """
        pass

    def _invoke_model[T: BaseModel](self, system_prompt: str, user_prompt: str, response_format: type[T]) -> T | None:
        """Invoke the language model with structured output.

        Args:
            system_prompt: The system prompt guiding the model.
            user_prompt: The user prompt containing the input data.
            response_format: The Pydantic model defining the expected response structure.

        Returns:
            The model's response validated against the response_format.
        """
        structured_model = self._model.with_structured_output(response_format)

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]

        response = structured_model.invoke(
            messages,
            response_format=response_format
        )
        if isinstance(response, response_format):
            return response


class HTTPBaseNode(BaseNode, metaclass=ABCMeta):
    """Abstract base class for HTTP-based workflow nodes.

    This class extends BaseNode to provide common functionality for nodes
    that interact with HTTP APIs.
    """

    def __init__(
        self,
        model: BaseChatModel,
        base_url: str = "",
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        data: dict[str, Any] | None = None,
        auth: dict[str, Any] | None = None,
        **kwargs: Any
    ) -> None:
        """Initialize the HTTP base node.

        Args:
            model: The language model to use for processing.
            base_url: Base URL for HTTP requests.
            params: Default query parameters for all requests.
            headers: Default headers for all requests.
            data: Default data payload for all requests.
            auth: OAuth2 client credentials configuration.
            **kwargs: Additional arguments passed to BaseNode
        """
        super().__init__(model)
        self._base_url = base_url
        self._params = params or {}
        self._headers = headers or {}
        self._data = data or {}
        self._auth = auth or {}

    def _authenticate(self, auth: dict[str, Any] | None) -> None | Auth:
        """Authenticate the node if necessary.

        This method can be overridden by subclasses to implement
        specific authentication logic.
        """
        _auth = {**self._auth, **(auth or {})}
        if _auth:
            return OAuth2ClientCredentials(**_auth)

    def _make_request(
        self,
        url: str,
        base_url: str = "",
        method: Literal["get", "post", "put", "delete", "patch"] = "get",
        response_type: Literal["json", "text"] = "json",
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        data: dict[str, Any] | None = None,
        auth: dict[str, Any] | None = None,
    ) -> str | dict[str, Any]:
        """Make an HTTP request with merged configuration.

        Args:
            url: The endpoint URL path.
            base_url: Base URL to use (overrides instance default if provided).
            method: HTTP method to use.
            response_type: Expected response format (json or text).
            params: Query parameters to merge with instance defaults.
            headers: Headers to merge with instance defaults.
            data: Request body data to merge with instance defaults.
            auth: OAuth2 credentials to merge with instance defaults.

        Returns:
            Parsed JSON dict if response_type is 'json', otherwise response text.
            Returns empty dict or empty string on HTTP errors.
        """
        _base_url = base_url or self._base_url

        _params = {**self._params, **(params or {})}
        _headers = {**self._headers, **(headers or {})}
        _data = {**self._data, **(data or {})}

        with Client(base_url=_base_url, auth=self._authenticate(auth)) as client:
            try:
                response = client.request(
                    method=method,
                    url=url,
                    params=_params,
                    headers=_headers,
                    data=_data,
                    timeout=60,
                )
                response.raise_for_status()

                if response_type == "json":
                    return response.json()
                return response.text
            except HTTPError:
                if response_type == "json":
                    return {}
                return ""
