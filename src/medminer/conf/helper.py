"""Configuration test utilities for MedMiner.

This module provides decorators and utilities for managing settings,
particularly useful for testing and development scenarios.
"""

from collections.abc import Callable
from functools import wraps
from typing import Any, ParamSpec, TypeVar

from medminer.conf import settings

P = ParamSpec("P")
R = TypeVar("R")

def override_settings(**overrides: Any) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Decorator to override settings for a test function.

    This is the recommended way to override settings in pytest tests.
    The settings are automatically restored after the test completes.

    Usage:
        from medminer.conf import override_settings

        @override_settings(BASE_DIR="/tmp/test", SPLIT_PATIENT=True)
        def test_my_feature():
            assert settings.BASE_DIR == Path("/tmp/test")
            assert settings.SPLIT_PATIENT is True

        # Also works with pytest fixtures
        @override_settings(BASE_DIR="/tmp/test")
        def test_with_fixtures(some_fixture):
            # Test code here
            pass

        # Can be combined with other decorators
        @pytest.mark.parametrize("value", [1, 2, 3])
        @override_settings(BASE_DIR="/tmp/test")
        def test_parametrized(value):
            # Test with different values
            pass

    Args:
        **overrides: Settings to override (use UPPER_CASE field names)

    Returns:
        Decorated function with settings overrides applied
    """
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            global settings
            original_settings = settings.model_copy()

            try:
                for key, value in overrides.items():
                    if not hasattr(original_settings, key):
                        continue

                    setattr(settings, key, value)
                return func(*args, **kwargs)
            finally:
                for key in overrides.keys():
                    if not hasattr(original_settings, key):
                        continue
                    setattr(settings, key, getattr(original_settings, key))
        return wrapper
    return decorator
