"""Main extraction workflow orchestration.

This module defines the ExtractionWorkflow which orchestrates all registered
extraction workflows (medications, diagnoses, procedures, etc.) in parallel.
Each registered BaseExtractionWorkflow is added as a node in the graph.
"""

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from medminer.workflows.base.schema import DoctorsLetterState
from medminer.workflows.base.workflow import BaseExtractionWorkflow, BaseWorkflow
from medminer.workflows.registry import register_workflow, registry


@register_workflow
class ExtractionWorkflow(BaseWorkflow[DoctorsLetterState]):
    def _build_workflow_graph(self) -> CompiledStateGraph:
        """Build the workflow graph by connecting nodes sequentially.

        Returns:
            A compiled LangGraph state graph.
        """
        graph = StateGraph(self._state_type)

        for name, workflow in registry.items():
            if not issubclass(workflow, BaseExtractionWorkflow):
                continue

            graph.add_node(name, workflow(self._model))
            graph.add_edge(START, name)
            graph.add_edge(name, END)

        return graph.compile()
