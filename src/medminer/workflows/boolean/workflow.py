"""Boolean statement extraction workflow implementation.

This module defines the workflow for extracting and evaluating boolean statements
from medical documents, useful for filtering and categorizing patient data based
on specific criteria.
"""

from textwrap import dedent

from langchain.chat_models import BaseChatModel
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from medminer.workflows.base.node import DataStorage, InformationExtractor, NoProcessing
from medminer.workflows.base.workflow import BaseWorkflow
from medminer.workflows.boolean.schema import StatementState
from medminer.workflows.registry import register_workflow


@register_workflow
class BooleanStatementWorkflow(BaseWorkflow[StatementState]):
    """Workflow for extracting and evaluating boolean statements from medical documents.

    This workflow extracts information and evaluates whether specific statements or
    criteria are true or false for a given patient based on their medical document.

    Attributes:
        prompt: The LLM prompt instructing how to evaluate and extract boolean statements.
    """
    prompt = dedent("""\
        Given a medical information of a patient in form of a doctor's letter, extract all patients and label them according to the following statement.

        Values to extract:
        - filter: A boolean value indicating whether the statement is true (filter=true) or false (filter=false).
        - information: The extracted information from the document that supports the filter decision.
        - reference: The exact text snippet from the document that was used to make the decision.
    """)

    def __init__(
            self,
            model: BaseChatModel,
            statement: str,
            prompt: str | None = None,
        ) -> None:
        """Initialize the extraction workflow.

        Args:
            model: The language model to use for processing.
            prompt: Optional custom extraction prompt (defaults to class attribute).
            process_nodes: Optional custom processing nodes (defaults to class attribute).
        """

        self._prompt = (prompt or self.prompt) + f"\n\nStatement: {statement}\n"
        super().__init__(model)

    def _build_workflow_graph(self) -> CompiledStateGraph:
        """Build the workflow graph by connecting nodes sequentially.

        Returns:
            A compiled LangGraph state graph.
        """
        graph = StateGraph(self._state_type)
        nodes =[
            InformationExtractor(
                model=self._model,
                prompt=self._prompt,
                response_format=self._state_type.response_format_type(),
            ),
            NoProcessing(self._model),
            DataStorage(
                model=self._model,
                task_name=self.name,
            )
        ]

        for node in nodes:
            graph.add_node(node.name, node)

        graph.add_edge(START, nodes[0].name)
        graph.add_edge(nodes[-1].name, END)

        for i, node in enumerate(nodes[:-1]):
            graph.add_edge(node.name, nodes[i + 1].name)

        return graph.compile()
