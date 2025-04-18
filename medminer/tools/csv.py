from csv import DictWriter
from itertools import chain
from pathlib import Path

from smolagents import tool


@tool
def save_csv(
    task_name: str,
    data: list[dict],
) -> str:
    """
    Saves data to a csv file.

    Args:
        task_name: The name of the task.
        data: A list of dictionaries containing the data to save.
            All dictionaries must have the same keys.

    Returns:
        A message indicating where the data was saved.

    Example:
        >>> data = [
        ...     {"patient_id": 1, "medication_name": "Aspirin"},
        ...     {"patient_id": 2, "medication_name": "Paracetamol"},
        ... ]
        >>> save_csv("medication", data)
        "Saved data for task medication to /path/to/result/medication.csv"
    """
    if isinstance(data, list) and not data:
        return "No data to save."

    # small hack to get all keys from all dictionaries to have all possible columns
    fieldnames = dict.fromkeys(chain.from_iterable([d.keys() for d in data])).keys()
    file_path = Path(__file__).parent.parent.parent / "result" / f"{task_name}.csv"
    if not file_path.parent.exists():
        file_path.parent.mkdir(parents=True)

    with open(file_path, "a") as csvfile:
        writer = DictWriter(csvfile, fieldnames=fieldnames)

        if file_path.exists() and file_path.stat().st_size == 0:
            writer.writeheader()

        for row in data:
            writer.writerow(row)

    return f"Saved data for task {task_name} to {file_path}"
