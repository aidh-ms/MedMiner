from pathlib import Path
from tempfile import TemporaryDirectory

from medminer.tools.csv import CSVTool


def test_test_csv_tool() -> None:
    with TemporaryDirectory() as temp_dir:
        tool = CSVTool(
            session_id="test_session",
            task_name="medication",
            base_dir=Path(temp_dir),
        )

        data = [
            {"patient_id": 1, "medication_name": "Aspirin"},
            {"patient_id": 2, "medication_name": "Paracetamol"},
        ]

        _ = tool.forward(task_name="medication", data=data)

        expected_path = Path(temp_dir) / "test_session" / "medication.csv"

        assert Path(expected_path).exists()

        with open(expected_path, "r") as f:
            content = f.read()
            assert content == "patient_id,medication_name\n1,Aspirin\n2,Paracetamol\n"
