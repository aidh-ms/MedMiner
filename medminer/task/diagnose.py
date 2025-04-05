from textwrap import dedent

from medminer.task import Task
from medminer.tools import save_csv

diagnose_task = Task(
    name="diagnose",
    prompt=dedent(
        """\
        Given a icu stay protocol of a patient, save all information as csv.
        Make a column for each diagnosis.

        save the the following columns:
        - patient_id: The patient ID.
        - diagnosis: A single diagnosis of the medical history.
        """
    ),
    tools=[save_csv],
)
