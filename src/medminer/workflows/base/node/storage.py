"""Data storage node for persisting extracted information.

This module provides the DataStorage node which writes processed extraction
results to CSV files. Supports optional patient-based file splitting for
organizing output by patient ID.
"""

from base64 import urlsafe_b64encode
from typing import Any, Literal

import pandas as pd
from langchain.chat_models import BaseChatModel

from medminer.conf import settings
from medminer.workflows.base.node.base import BaseNode
from medminer.workflows.base.schema import ExtractionState


class DataStorage(BaseNode):
    """Node for storing processed data to CSV files.

    This node writes the processed data to a CSV file, optionally splitting
    files by patient ID.

    Attributes:
        _task_name: Name of the task (used for the CSV filename).
        _base_dir: Base directory for storing CSV files.
        _split: Whether to split files by patient ID.
    """

    def __init__(self, model: BaseChatModel, task_name: str, **kwargs: Any) -> None:
        """Initialize the data storage node.

        Args:
            model: The language model (unused but required by BaseNode).
            task_name: Name of the task, used for the CSV filename.
        """
        super().__init__(model)
        self._task_name = task_name
        self._base_dir = settings.BASE_DIR
        self._split = settings.SPLIT_PATIENT

    def __call__(self, state: ExtractionState) -> dict[Literal["path"], str]:
        """Store processed data to a CSV file.

        If SPLIT_PATIENT is enabled, creates a subdirectory for each patient.
        Data is appended to existing files if they exist.

        Args:
            state: The extraction state containing processed data.

        Returns:
            Dictionary with 'path' key containing the CSV file path.
        """
        csv_path = self._base_dir
        if self._split:
            csv_path = csv_path / urlsafe_b64encode(state.patient_id.encode()).decode()

        csv_path.mkdir(parents=True, exist_ok=True)
        csv_path = csv_path / f"{self._task_name}.csv"

        df = pd.DataFrame([  # TODO: handle empty processed_data / df
            item.model_dump()
            for item in state.processed_data
        ])
        df["patient_id"] = state.patient_id

        df.to_csv(
            csv_path,
            index=False,
            mode="a",
            header=not csv_path.exists(),
        )

        return {
            "path": str(csv_path)
        }
