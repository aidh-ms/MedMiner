"""
This module contains the MedicationTask class, which is used to extract and process medication data from text.
"""

from textwrap import dedent

from medminer.task import Task, register_task
from medminer.tools import CSVTool, extract_medication_data, get_atc, get_rxcui


@register_task
class MedicationTask(Task):
    name = "medication"
    verbose_name = "Medication"
    prompt = dedent(
        """\
        Given a list of medications, save all medications for the patient as csv. The medications can be in any language. The medications are usually in the format of a list of medications, with dosage and unit as well as their dosage timings (e.g. 1-0-1-0 for moring and evening but not noon or night). Every medication should have a single row, if there are multiple medications that can be extracted from a single piece of text, e.g. a combined medication, split them up. These are the steps you should follow to complete the task:

        To complete the task make the following steps:
        1. Extract the medications from the text. The medication can be in any language. This is the medication_reference column.
        2. If the medication name is not in english, translate it to english and infer the medication_translated column. Correct any misspellings in the process. Use the following format "Brand name or medication name (active ingredient)". e.g. "Aspirin (acetylsalicylic acid)".
        3. Extract the active ingredient of the medication and loose everything that is not relevant. This is the active_ingredient column.
        4. Extract the dose of the medication. This should only contain the numeric value. This is the dose column.
        5. Extract the unit of the dose (e.g. ml, mg, ...). If possible, use mg. If not applicable, write an empty string. This is the unit column.
        6. Extract the route (e.g. oral) of administration of the medication. If not applicable, write an empty string. This is the route column.
        7. Extract the frequency of the medication. This is the frequency column. If not applicable, write an empty string. The frequency can be in the format of "1-0-1-0" for morning and evening but not noon or night. If needed translate to english (e.g. b.B. translate to "as needed"). If the medication is taken "as needed", write "as needed".
        8. Extract the frequency code of the medication. This is the frequency_code column. If not applicable, write an empty string. Use only the following codes:
            - Q<int:hours>H: Every <int> hours (e.g. Q8H: Every 8 hours)
            - Q<int:days>D: Every <int> days (e.g. Q1D: Every 1 day)
            - Q<int:weeks>W: Every <int> weeks (e.g. Q1W: Every 1 week)
            - BID: Twice a day (e.g. 1-0-1-0)
            - TID: Three times a day (e.g. 1-1-1-0)
            - QID: Four times a day (e.g. 1-1-1-1)
            - QD: Once a day (used for medications that are taken once a day, e.g. 0-1-0 and doesn't fit AM/PM)
            - AM: In the morning (1-0-0-0)
            - PM: In the evening (0-0-1-0)
            - PRN: As needed
            - NaF: Not a frequency (e.g. for medications that are not taken regularly)
        9. get the RXCUI for all medications. Use the active ingredient of the medications. If there are multiple RXCUI codes, choose the one that fits the best to the translated medication. Usually, the first candidate with a score of 1 is the best choice, but you can decide otherwise if you have reasonable grounds for another decision. If there are no codes, write an empty string.
        10. get the ATC code for all medications. Use the rxcui of the medications.
        11. save the medication information as csv with the columns defined below.

        ---
        Example 1:
        Input: "Aspirin 100mg 1-0-1-0"
        Output: [
            {
                "patient_id": 1,
                "medication_reference":
                "Aspirin 100mg",
                "medication_name": "Aspirin",
                "medication_translated": "Aspirin (acetylsalicylic acid)",
                "active_ingredient": "acetylsalicylic acid",
                "dose": 100,
                "unit": "mg",
                "route": "",
                "frequency": "1-0-1-0",
                "frequency_code": "BID",
                "rxcui": "",
                "atc_code": "",
            }
        ]
        Example 2:
        Input: "Paracetamol 500mg 1-0-0-0"
        Output: [
            {
                "patient_id": 2,
                "medication_reference": "Paracetamol 500mg",
                "medication_name": "Paracetamol",
                "medication_translated": "Paracetamol (acetaminophen)",
                "active_ingredient": "acetaminophen",
                "dose": 500,
                "unit": "mg",
                "route": "",
                "frequency": "1-0-0-0",
                "frequency_code": "AM",
                "rxcui": "",
                "atc_code": "",
            }
        ]
        Example 3:
        Input: "Ibuprofen 400mg 1-1-0-0 (Oral)"
        Output: [
            {
                "patient_id": 3,
                "medication_reference": "Ibuprofen 400mg",
                "medication_name": "Ibuprofen",
                "medication_translated": "Ibuprofen (ibuprofen)",
                "active_ingredient": "ibuprofen",
                "dose": 400,
                "unit": "mg",
                "route": "Oral",
                "frequency": "1-1-0-0",
                "frequency_code": "BID",
                "rxcui": "",
                "atc_code": ""
            }
        ]
        Example 4:
        Input: "Piperacillin/Tazobactam 1g/1g 1-0-1-0"
        Output: [
            {
                "patient_id": 4,
                "medication_reference": "Piperacillin/Tazobactam 1g/1g",
                "medication_name": "Piperacillin",
                "medication_translated": "Piperacillin (piperacillin)",
                "active_ingredient": "piperacillin",
                "dose": 1000,
                "unit": "mg",
                "route": "",
                "frequency": "1-0-1-0",
                "frequency_code": "BID",
                "rxcui": "",
                "atc_code": "",
            },
            {
                "patient_id": 4,
                "medication_reference": "Piperacillin/Tazobactam 1g/1g",
                "medication_name": "Tazobactam",
                "medication_translated": "Tazobactam (tazobactam)",
                "active_ingredient": "tazobactam",
                "dose": 1000,
                "unit": "mg",
                "route": "",
                "frequency": "1-0-1-0",
                "frequency_code": "BID",
                "rxcui": "",
                "atc_code": "",
            }
        ]
        Example 5:
        Input: "Tilidin 5mg bB"
        Output: [
            {
                "patient_id": 5,
                "medication_reference": "Tilidin 5mg bB",
                "medication_name": "Tilidin",
                "medication_translated": "Tilidin (tilidine)",
                "active_ingredient": "tilidine",
                "dose": 5,
                "unit": "mg",
                "route": "",
                "frequency": "",
                "frequency_code": "NaF",
                "rxcui": "",
                "atc_code": "",
            }
        ]
        Example 6:
        Input: "Amlodipin 5mg"
        Output: [
            {
                "patient_id": 6,
                "medication_reference": "Amlodipin 5mg",
                "medication_name": "Amlodipin",
                "medication_translated": "Amlodipine (amlodipine)",
                "active_ingredient": "amlodipine",
                "dose": 5,
                "unit": "mg",
                "route": "",
                "frequency": "",
                "frequency_code": "NaF",
                "rxcui": "",
                "atc_code": "",
            }
        ]
        ---

        Columns:
        - patient_id: The patient ID.
        - medication_reference: The medication name in the document.
        - medication_name: The name of the medication in the document without dose, unit or additional information.
        - medication_translated: The corrected name of the medication, translated to english. Use the following format "Brand name or medication name (active ingredient)". e.g. "Aspirin (acetylsalicylic acid)".
        - active_ingredient: The active ingredient of the medication. if not applicable, write an empty string.
        - dose: The dose of the medication. this sould only contain the numeric value.
        - unit: The unit of the dose (e.g. ml, mg, ...). if not applicable, write an empty string.
        - route: The route of administration of the medication. if not applicable, write an empty string.
        - frequency: The raw frequency text of the medication. if not applicable, write an empty string.
        - frequency_code: The frequency code of the medication. if not applicable, write an empty string.
        - rxcui: The RXCUI of the medication. if not applicable, write an empty string.
        - atc_code: The ATC codes of the medication. if not applicable, write an empty string.
        """
    )
    tools = [CSVTool, extract_medication_data, get_rxcui, get_atc]
