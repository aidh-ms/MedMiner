from textwrap import dedent

from medminer.task import Task, register_task
from medminer.tools import SNOMEDTool
from medminer.tools.csv import CSVTool
from medminer.tools.procedure import extract_procedure_data


@register_task
class ProcedureTask(Task):
    name = "procedure"
    verbose_name = "Procedures"
    prompt = dedent(
        """\
        Given a medical course of a patient, extract all given procedures and save all information as csv. The procedures can be in any language. The medical course is usually in the format of bullet points. Every procedure should have a single row, if there are multiple procedures that can be extracted from a single piece of text, split them up. These are the steps you should follow to complete the task:

        To complete the task make the following steps:
        1. Extract the procedures from the text. The procedure can be in any language. This is the `procedure_reference` column.
        2. If the procedure name is not in English, translate it to English and infer the `procedure_corrected` column. Correct any misspellings in the process. Change abbreviations to full words. For example, "CT" should be changed to "Computed Tomography".
        3. Extract the relevant procedure as a search tearm. This is the `procedure_search` column. Separate the words with a space. Remove unnecessary stop words. Use the `search_snomed_procedures` tool to search for SNOMED CT concepts in a snowstorm server.
        4. Extract the relevant procedure as a string and remove everything that is not relevant. This is the `procedure` column.
        5. Extract the date of the procedure. If not applicable, write an empty string. This is the `date` column.
        6. Use the `search_snomed_procedures` tool to find SNOMED CT concepts for the extracted procedures (`procedure_search`). Add the SNOMED CT ID and fully specified name (FSN) to the output. You will get back a list of dictionaries with the following keys: ids and fsn. Usually the first candidate is the best choice, but you can decide otherwise if you have reasonable grounds for another decision if you compare the extracted information with the returned descriptions from the snomed server. If there are no codes, write an empty string. This is the `snomed_id` and `snomed_fsn` columns.

        Example 1:
        Input: "Colonoscopy performed on 2023-04-15"
        Output: [
            {"patient_id": 1, "procedure_reference": "Colonoscopy performed on 2023-04-15", "procedure_corrected": "Colonoscopy", "procedure_search": "Colonoscopy", "procedure": "Colonoscopy", "date": "2023-04-15", "snomed_id": "73761001", "snomed_fsn": "Colonoscopy (procedure)"}
        ]

        Example 2:
        Input: "Gastroscopy and biopsy conducted on 2023-03-10"
        Output: [
            {"patient_id": 2, "procedure_reference": "Gastroscopy and biopsy conducted on 2023-03-10", "procedure_corrected": "Gastroscopy", "procedure_search": "Gastroscopy", "procedure": "Gastroscopy", "date": "2023-03-10", "snomed_id": "43210008", "snomed_fsn": "Gastroscopy (procedure)"},
            {"patient_id": 2, "procedure_reference": "Gastroscopy and biopsy conducted on 2023-03-10", "procedure_corrected": "Biopsy", "procedure_search": "Biopsy", "procedure": "Biopsy", "date": "2023-03-10", "snomed_id": "274441001", "snomed_fsn": "Biopsy (procedure)"}
        ]

        Columns:
        - patient_id: The patient ID.
        - procedure_reference: The original text containing the procedure.
        - procedure_corrected: Translate the procedures to English if necessary and infer the column. Change abbreviations to full words. For example, "CT" should be changed to "Computed Tomography".
        - procedure_search: The relevant procedure as a string. Separate the words with a space.
        - procedure: The procedure.
        - date: The date of the procedure. If not applicable, write an empty string.
        - snomed_id: The SNOMED CT ID of the procedure.
        - snomed_fsn: The fully specified name (FSN) of the procedure in SNOMED CT.
        """
    )
    tools = [CSVTool, SNOMEDTool, extract_procedure_data]
