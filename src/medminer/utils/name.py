"""Name conversion utilities for MedMiner.

This module provides utilities for converting class names to snake_case format.
"""

import re


def camel_to_snake(name: str) -> str:
    """Convert a CamelCase string to snake_case.

    Args:
        name: The CamelCase string to convert.

    Returns:
        The converted snake_case string.

    Examples:
        >>> camel_to_snake("MyClassName")
        'my_class_name'
        >>> camel_to_snake("HTTPServer")
        'http_server'
    """
    # Insert underscore before uppercase letters that follow lowercase letters
    # or before uppercase letters that are followed by lowercase letters
    _s = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', _s).lower()


class NameMixin:
    """Mixin class that provides a snake_case name property based on the class name.

    This mixin automatically converts the class name from CamelCase to snake_case
    and exposes it as a read-only `name` property.
    """

    @property
    def name(self) -> str:
        """Get the snake_case name of the class.

        Returns:
            The class name converted to snake_case.

        Examples:
            >>> class MyWorkflow(NameMixin):
            ...     pass
            >>> MyWorkflow().name
            'my_workflow'
        """
        return camel_to_snake(self.__class__.__name__)
