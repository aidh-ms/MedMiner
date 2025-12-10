"""Workflow registration and management system for MedMiner.

This module provides a registry for managing workflow classes,
allowing workflows to be registered, retrieved, and managed dynamically.
"""

from medminer.utils.name import camel_to_snake
from medminer.workflows.base.workflow import BaseWorkflow


class WorkflowRegistry:
    """Registry for managing workflow classes.

    The registry stores workflow classes by name and provides methods
    for registration, retrieval, and management of workflows.

    Attributes:
        _workflows: Internal dictionary mapping workflow names to classes.
    """

    def __init__(self) -> None:
        """Initialize an empty workflow registry."""
        self._workflows: dict[str, type[BaseWorkflow]] = {}

    def __contains__(self, name: str) -> bool:
        """Check if a workflow is registered."""
        return name in self._workflows

    def __len__(self) -> int:
        """Return the number of registered items."""
        return len(self._workflows)

    def __repr__(self) -> str:
        """Return string representation of the registry."""
        return f"{self.__class__.__name__}(entries={len(self._workflows)})"

    def register(self, name: str, workflow_class: type[BaseWorkflow]) -> type[BaseWorkflow]:
        """
        Register a workflow class.

        Args:
            name: The name to register the workflow under
            workflow_class: The workflow class to register

        Returns:
            The workflow class (for use as decorator)
        """
        self._workflows[name] = workflow_class
        return workflow_class

    def unregister(self, name: str) -> None:
        """
        Unregister a workflow class.

        Args:
            name: The name of the workflow to unregister
        """
        if name in self._workflows:

            del self._workflows[name]

    def get(self, name: str, default: type[BaseWorkflow] | None = None) -> type[BaseWorkflow] | None:
        """
        Get a workflow class by name.

        Args:
            name: The name of the workflow

        Returns:
            The workflow class or default if not found

        Raises:
            KeyError: If workflow not found
        """
        if name not in self._workflows:
            return default
        return self._workflows[name]

    def clear(self) -> None:
        """Clear all registered workflows."""
        self._workflows.clear()

    def items(self) -> list[tuple[str, type[BaseWorkflow]]]:
        """
        Get all registered workflows.

        Returns:
            Items view of registered workflows
        """
        return list(self._workflows.items())

    def keys(self) -> list[str]:
        """
        Get all registered workflow names.

        Returns:
            List of workflow names
        """
        return list(self._workflows.keys())

    def values(self) -> list[type[BaseWorkflow]]:
        """
        Get all registered workflow classes.

        Returns:
            List of workflow classes
        """
        return list(self._workflows.values())


# Global registry instance
registry = WorkflowRegistry()


def register_workflow[T: BaseWorkflow](workflow: type[T]) -> type[T]:
    """Register a workflow class with the global registry.

    This function is typically used as a decorator to automatically register
    workflow classes. The workflow name is derived from the class name
    converted to snake_case.

    Args:
        workflow: The workflow class to register.

    Returns:
        The registered workflow class (for use as decorator).

    Examples:
        >>> @register_workflow
        ... class MyCustomWorkflow(BaseWorkflow):
        ...     pass
        >>> registry.get('my_custom_workflow')
        <class 'MyCustomWorkflow'>
    """
    name = camel_to_snake(workflow.__name__)
    registry.register(name, workflow)
    return workflow
