import os
from enum import StrEnum
from pathlib import Path

import pandas as pd
from smolagents import AzureOpenAIServerModel

from medminer.task import diagnose_task, history_task, medication_task


class TaskType(StrEnum):
    MEDICATION = "Medication"
    DIAGNOSIS = "Diagnosis"
    PROCEDURE = "Procedure"
    MEDICAL_HISTORY = "Medical history"

    @staticmethod
    def list() -> list[str]:
        return list(map(lambda t: t.value, TaskType))  # type: ignore[attr-defined]


def process_docs(docs: list[str], tasks: list[str]) -> pd.DataFrame:
    """
    Process a list of documents with the specified tasks.

    Parameters
    ----------
    docs : list[str]
        List of documents to process.
    tasks : list[str]
        List of tasks to perform on the documents.

    Returns
    -------
    list[str]
        List of processed documents.
    """

    def _get_task(task_name: str):  # type: ignore[no-untyped-def]
        match task_name:
            case TaskType.MEDICATION:
                return medication_task
            case TaskType.DIAGNOSIS:
                return diagnose_task
            case TaskType.MEDICAL_HISTORY:
                return history_task
            case _:
                raise ValueError(f"Unknown task: {task_name}")

    task_name = tasks[0]  # todo add suport for multiple tasks
    task = _get_task(task_name)

    model = AzureOpenAIServerModel(
        model_id=os.environ.get("AZURE_OPENAI_MODEL", ""),
        azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT", ""),
        api_key=os.environ.get("AZURE_OPENAI_API_KEY", ""),
        api_version=os.environ.get("OPENAI_API_VERSION", ""),
    )

    for doc in docs:
        task.run(model, doc)

    match task_name:
        case TaskType.MEDICATION:
            return pd.read_csv(Path(__file__).parent.parent.parent / "result" / "medication.csv")
        case TaskType.DIAGNOSIS:
            return pd.read_csv(Path(__file__).parent.parent.parent / "result" / "diagnose.csv")
        case TaskType.MEDICAL_HISTORY:
            return pd.read_csv(Path(__file__).parent.parent.parent / "result" / "history.csv")
        case _:
            raise ValueError(f"Unknown task: {task_name}")


def process_files(files: list | None, tasks: list[str]) -> pd.DataFrame:
    """
    Process a list of files with the specified tasks.

    Parameters
    ----------
    files : list
        List of file paths to process.
    tasks : list[str]
        List of tasks to perform on the files.

    Returns
    -------
    pd.DataFrame
        DataFrame containing the processed text.
    """
    if files is None or not tasks:
        return pd.DataFrame()

    docs = []

    for file_name in files:
        with open(file_name, "r") as file:
            # Add destinction between csv and txt files
            docs.append(file.read())

    return process_docs(docs, tasks)


def process_sql(sql: str, tasks: list[str]) -> pd.DataFrame:
    """
    Process a SQL query with the specified tasks.

    Parameters
    ----------
    sql : str
        SQL query to process.
    tasks : list[str]
        List of tasks to perform on the SQL query.
    """
    return pd.DataFrame()


def process_text(text: str, tasks: list[str]) -> pd.DataFrame:
    """
    Process a text with the specified tasks.

    Parameters
    ----------
    text : str
        Text to process.
    tasks : list[str]
        List of tasks to perform on the text.

    Returns
    -------
    pd.DataFrame
        DataFrame containing the processed text.
    """
    return process_docs([text], tasks)
