from textwrap import dedent

from medminer.task import Task
from medminer.tools import save_csv

procedure_task = Task(
    name="procedure",
    prompt=dedent(
        """\
        Given a medical course of a patient, extract all given procedures and save all information as csv. The procedures should be translated to english. The medical course is usually in the format of bullet points. Every procedure should have a single row, if there are multiple procedures that can be extracted from a single piece of text, split them up. These are the steps you should follow to complete the task:
        1. extract a part of the text that contains a procedure. The procedure can be in any language. This is the procedure_reference column.
        2. translate the procedures to english if necessary and infer the procedure_translated column.
        3. Extract the relevant procedure as a string and loose everything that is not relevant. This is the procedure column.
        4. Extract the date of the procedure. If not applicable, write an empty string.
        Make a column for each procedure.

        save the the following columns:
        - patient_id: The patient ID.
        - date: The date of the procedure. if not applicable, write an empty string.
        - procedure: The medical procedure.
        """
    ),
    tools=[save_csv],
)
