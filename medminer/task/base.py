import tempfile
from abc import ABC
from functools import cache
from pathlib import Path
from textwrap import dedent, indent
from typing import Any, Type, TypeVar
from uuid import uuid4

from smolagents import Model, MultiStepAgent, Tool, ToolCallingAgent

from medminer.tools.settings import ToolSetting, ToolSettingMixin


class Task(ABC):
    """Abstract base class for a task."""

    name: str
    verbose_name: str
    prompt: str
    agent_type: Type[MultiStepAgent] = ToolCallingAgent
    tools: list[Tool | Type[Tool]] = []
    agent_params: dict[str, Any] = {}
    skip_settings: list[str] = ["task_name", "session_id", "base_dir"]

    def __init__(
        self,
        model: Model,
        **kwargs: Any,
    ) -> None:
        """
        Initialize the task.

        Args:
            model: The model to use for the task.
            kwargs: Additional arguments for the task.
        """
        kwargs["task_name"] = self.name
        if "session_id" not in kwargs:
            kwargs["session_id"] = uuid4().hex
        if "base_dir" not in kwargs:
            kwargs["base_dir"] = Path(tempfile.mkdtemp())

        self._settings = kwargs

        tools = []
        for tool in self.tools:
            if not isinstance(tool, type):
                tools.append(tool)
                continue

            if not issubclass(tool, ToolSettingMixin):
                continue

            tools.append(tool(**kwargs))

        self._agent = self.agent_type(
            tools,
            model,
            name=self.name,
            description=f"Extracts and save the {self.verbose_name} for the given data",
            **self.agent_params,
        )

    @property
    def agent(self) -> MultiStepAgent:
        """
        Get the agent for the task.

        Returns:
            The agent for the task.
        """
        return self._agent

    @classmethod
    def settings(cls) -> list[ToolSetting]:
        """
        Get the settings for the task.

        Returns:
            A list of settings for the task.
        """
        settings: dict[str, ToolSetting] = {}
        for tool in cls.tools:
            if not isinstance(tool, type):
                continue

            if not issubclass(tool, ToolSettingMixin):
                continue

            for setting in tool.settings:
                if setting.id in settings:
                    continue

                if setting.id in cls.skip_settings:
                    continue

                settings[setting.id] = setting

        return list(settings.values())

    def _buidl_prompt(self, data: str) -> str:
        return dedent(
            f"""\
            Task name: {self.name}
            Prompt: \n{indent(self.prompt, " " * 4 * 5)}

            {"-" * 80}
            Data: \n{indent(data, " " * 4 * 5)}
            """
        )

    def run(self, data: str) -> Any:
        """
        Run the task.

        Args:
            data: The data to process.

        Returns:
            The result of the task.
        """
        return self.agent.run(self._buidl_prompt(data))


T = TypeVar("T", bound=Task)


def register_task(task: Type[T]) -> Type[T]:
    """
    Register a task.

    Args:
        task: The task to register.

    Returns:
        The registered task.
    """
    TaskRegistry().register(task)
    return task


@cache
class TaskRegistry:
    """
    A registry for tasks.
    """

    def __init__(self) -> None:
        """Initialize the task registry."""
        self.tasks: dict[str, Type[Task]] = {}

    def register(self, task: Type[Task]) -> Type[Task]:
        """
        Register a task.

        Args:
            task: The task to register.

        Returns:
            The registered task.
        """
        self.tasks[task.name] = task
        return task

    def get(self, name: str) -> Type[Task] | None:
        """
        Get a task by name.

        Args:
            name: The name of the task to get.

        Returns:
            The task with the given name, or None if not found.
        """
        return self.tasks.get(name)

    def all(self) -> list[Type[Task]]:
        """
        Get all tasks.

        Returns:
            A list of all tasks.
        """
        return list(self.tasks.values())

    def filter(self, names: list[str]) -> list[Type[Task]]:
        """
        Get all tasks that match the name.

        Args:
            names: A list of task names to filter by.

        Returns:
            A list of tasks that match the given names.
        """
        return [task for task in self.tasks.values() if task.name in names]

    def all_settings(self) -> list[ToolSetting]:
        """
        Get all task settings.

        Returns:
            A list of all task settings.
        """
        settings: dict[str, ToolSetting] = {}
        for task in self.tasks.values():
            for setting in task.settings():
                if setting.id in settings:
                    settings[setting.id].ui.dependent.append(task.name)  # type: ignore[union-attr]
                    continue

                setting.ui.dependent = [task.name]  # type: ignore[assignment]
                settings[setting.id] = setting

        return list(settings.values())
