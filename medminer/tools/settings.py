"""
This mmodule contains the base settings for the tools in the MedMiner project.
"""

from dataclasses import dataclass, field
from typing import Any, Type


@dataclass
class ToolUISetting:
    dependent: list[str] = field(default_factory=list)
    params: dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolSetting:
    id: str
    label: str
    type: Type
    ui: ToolUISetting = field(default_factory=ToolUISetting)


class ToolSettingMixin:
    """Mixin class for tools with settings."""

    settings: list[ToolSetting] = []

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        for setting in self.settings:
            if (value := kwargs.get(setting.id)) is None:
                raise ValueError(f"Missing required setting: {setting.id}")

            if not isinstance(value, setting.type):
                raise TypeError(f"Expected {setting.type} for setting {setting.id}, got {type(value)}")

            setattr(self, setting.id, value)
