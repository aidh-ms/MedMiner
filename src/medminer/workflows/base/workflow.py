"""Base workflow implementations for MedMiner.

This module defines the abstract base classes for all workflows in MedMiner,
including the base workflow and extraction workflow templates.
"""

from abc import ABCMeta, abstractmethod
from types import get_original_bases
from typing import get_args

from langchain.chat_models import BaseChatModel
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from pydantic import BaseModel

from medminer.utils.name import NameMixin
from medminer.workflows.base.node import BaseNode, DataStorage, InformationExtractor, NoProcessing
from medminer.workflows.base.schema import DoctorsLetterState, ExtractionState


class BaseWorkflow[T: BaseModel](NameMixin, metaclass=ABCMeta):
    """Abstract base class for all MedMiner workflows.

    This class provides the foundation for implementing LangGraph-based workflows.
    Subclasses must implement the _build_workflow_graph method to define their
    specific workflow structure.

    Attributes:
        _model: The language model used for processing.
        _workflow: The compiled LangGraph state graph.
    """

    def __init__(self, model: BaseChatModel) -> None:
        """Initialize the workflow with a language model.

        Args:
            model: The language model to use for processing.
        """
        self._model = model
        self._workflow = self._build_workflow_graph()

    def __call__(self, state: DoctorsLetterState) -> T:
        """Execute the workflow on a given state.

        Args:
            state: The input state containing patient data and letter.

        Returns:
            The updated state after workflow execution.
        """
        return self._state_type.model_validate(self._workflow.invoke(state))

    @property
    def _state_type(self) -> type[T]:
        """Get the state type from the generic type parameter.

        Returns:
            The ExtractionState type for this workflow.

        Raises:
            TypeError: If the generic type cannot be resolved.
        """
        base = get_original_bases(self.__class__)[0]
        if not (types := get_args(base)):
           raise TypeError(f"Could not resolve generic type for '{self.__class__.__name__}'.")

        return types[0]

    @abstractmethod
    def _build_workflow_graph(self) -> CompiledStateGraph:
        """Build and compile the workflow graph.

        Returns:
            A compiled LangGraph state graph.
        """
        pass

    def run(self, state: DoctorsLetterState) -> T:
        """Execute the workflow on a given state.

        Args:
            state: The input state containing patient data and letter.

        Returns:
            The updated state after workflow execution.
        """
        return self(state)

    def run_many(self, states: list[DoctorsLetterState]) -> list[T]:
        """Execute the workflow on multiple states.

        Args:
            states: List of input states to process.

        Returns:
            List of updated states after workflow execution.
        """
        return [
            self(state)
            for state in states
        ]


class BaseExtractionWorkflow[T: ExtractionState](BaseWorkflow[T], metaclass=ABCMeta):
    """Abstract base class for extraction workflows.

    This class provides a template for workflows that extract and process
    medical information from doctor's letters. The workflow follows a pattern of:
    Extraction → Processing Node(s) → Storage.

    Type Parameters:
        T: The ExtractionState type for this workflow.

    Attributes:
        prompt: The LLM prompt for extraction (must be defined in subclasses).
        process_nodes: Optional processing nodes to run after extraction.
    """

    prompt: str
    process_nodes: tuple[type[BaseNode], ...] = ()

    def __init__(
            self,
            model: BaseChatModel,
            prompt: str | None = None,
            process_nodes: tuple[type[BaseNode], ...] = (),
        ) -> None:
        """Initialize the extraction workflow.

        Args:
            model: The language model to use for processing.
            prompt: Optional custom extraction prompt (defaults to class attribute).
            process_nodes: Optional custom processing nodes (defaults to class attribute).
        """
        self._prompt = prompt or self.prompt
        self._nodes = self._build_nodes(process_nodes or self.process_nodes, model)

        super().__init__(model)

    def __init_subclass__ (cls, *args, **kwargs) -> None:
        """Validate that subclasses define required attributes.

        Raises:
            NotImplementedError: If the 'prompt' attribute is not defined.
        """
        super().__init_subclass__(*args, **kwargs)

        attrs = ('prompt', )
        for attr in attrs:
            if not hasattr(cls, attr):
                raise NotImplementedError(f"Subclasses '{cls.__name__}' of BaseExtractionWorkflow must define a '{attr}' attribute.")

    def _build_nodes(self, nodes: tuple[type[BaseNode], ...], model: BaseChatModel) -> list[BaseNode]:
        """Build the workflow nodes.

        Creates the extraction, processing, and storage nodes for the workflow.

        Args:
            nodes: Processing node classes to instantiate.
            model: The language model to pass to nodes.

        Returns:
            List of instantiated workflow nodes in execution order.
        """
        _nodes: list[BaseNode] = [
            node(model)
            for node in nodes
        ]
        if not nodes:
            _nodes = [NoProcessing(model)]

        extractor = InformationExtractor(
            model=model,
            prompt=self._prompt,
            response_format=self._state_type.response_format_type(),
        )
        _nodes.insert(0, extractor)

        storage = DataStorage(
            model=model,
            task_name=self.name,
        )
        _nodes.append(storage)
        return _nodes

    def _build_workflow_graph(self) -> CompiledStateGraph:
        """Build the workflow graph by connecting nodes sequentially.

        Returns:
            A compiled LangGraph state graph.
        """
        graph = StateGraph(self._state_type)
        nodes = self._nodes

        for node in nodes:
            graph.add_node(node.name, node)

        graph.add_edge(START, nodes[0].name)
        graph.add_edge(nodes[-1].name, END)

        for i, node in enumerate(nodes[:-1]):
            graph.add_edge(node.name, nodes[i + 1].name)

        return graph.compile()
