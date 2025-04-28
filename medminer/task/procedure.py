from textwrap import dedent

from medminer.task import Task, register_task
from medminer.tools import save_csv, search_snomed_procedures


@register_task
class ProcedureTask(Task):
    name = "procedure"
    verbose_name = "Procedures"
    prompt = dedent(
        """\
        Given a medical course of a patient, extract all given procedures and save all information as csv. The procedures can be in any language. The medical course is usually in the format of bullet points. Every procedure should have a single row, if there are multiple procedures that can be extracted from a single piece of text, split them up. These are the steps you should follow to complete the task:

        1. Extract a part of the text that contains a procedure. The procedure can be in any language. This is the `procedure_reference` column.
        2. If you suspect that the procedure_reference is an acronym, try to expand it from the context of the note you are working on. Do this in the original language. If you are not sure, leave it as is. This is the `procedure_expanded` column. If it is not an acronym, you can skip this step.
        3. Translate the procedures to English if necessary and infer the `procedure_translated` column. Use the procedure_expanded column if it is available. If not, use the `procedure_reference` column. Strictly avoid using acronyms in this column. This is the `procedure_translated` column.
        4. Extract the relevant procedure as a string and remove everything that is not relevant. This is the `procedure` column.
        5. Extract the date of the procedure. If not applicable, write an empty string. This is the `date` column.
        6. Use the `search_snomed_procedures` tool to find SNOMED CT concepts for the extracted procedures. Add the SNOMED CT ID and fully specified name (FSN) to the output. You will get back a list of dictionaries with the following keys: ids and fsn. Usually the first candidate is the best choice, but you can decide otherwise if you have reasonable grounds for another decision if you compare the extracted information with the returned descriptions from the snomed server. If there are no codes, write an empty string. This is the `snomed_id` and `snomed_fsn` columns.

        Example 1:
        Input: "Colonoscopy performed on 2023-04-15"
        Output: [
            {"patient_id": 1, "procedure_reference": "Colonoscopy performed on 2023-04-15",
            "procedure_expanded": "", "procedure_translated": "Colonoscopy", "procedure": "Colonoscopy", "date": "2023-04-15", "snomed_id": "73761001", "snomed_fsn": "Colonoscopy (procedure)"},
            ]

        Example 2:
        Input: "Gastroscopy and biopsy conducted on 2023-03-10"
        Output: [
            {"patient_id": 2, "procedure_reference": "Gastroscopy and biopsy conducted on 2023-03-10", "procedure_expanded": "","procedure_translated": "Gastroscopy", "procedure": "Gastroscopy", "date": "2023-03-10", "snomed_id": "43210008", "snomed_fsn": "Gastroscopy (procedure)"},
            {"patient_id": 2, "procedure_reference": "Gastroscopy and biopsy conducted on 2023-03-10", "procedure_translated": "Biopsy", "procedure": "Biopsy", "date": "2023-03-10", "snomed_id": "274441001", "snomed_fsn": "Biopsy (procedure)"}
        ]

        Example 3:
        Input: "cMRT 11.09."
        Output: [
            {"patient_id": 3, "procedure_reference": "cMRT 11.09.", "procedure_expanded": "kranielle magnet resonanztomographie", "procedure_translated": "Cranial MRI", "procedure": "Cranial MRI", "date": "11.09.", "snomed_id": "431855005", "snomed_fsn": "Magnetic resonance imaging of brain (procedure)"}

        Columns:
        - patient_id: The patient ID.
        - procedure_reference: The original text containing the procedure.
        - procedure_expanded: The expanded procedure text if applicable. If not, write an empty string.
        - procedure_translated: The translated procedure text.
        - procedure: The medical procedure.
        - date: The date of the procedure. If not applicable, write an empty string.
        - snomed_id: The SNOMED CT ID of the procedure.
        - snomed_fsn: The fully specified name (FSN) of the procedure in SNOMED CT.
        """
    )
    tools = [save_csv, search_snomed_procedures]
