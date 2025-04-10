from textwrap import dedent

from medminer.task import Task
from medminer.tools.csv import save_csv
from medminer.tools.diagnosis import extract_diagnosis_data, lookup_icd11

history_task = Task(
    name="history",
    prompt=dedent(
        """
        Given a medical history of a patient, extract all given diagnoses and save all information as csv. The diagnosis should be translated to english. The medical history is usually in the format of a sentence or a paragraph. Every diagnosis should have a single row, if there are multiple diagnosis that can be extracted from a single piece of text, split them up. These are the steps you should follow to complete the task:
        1. extract a part of the text that contains a diagnosis. The diagnosis can be in any language. This is the diagnosis_reference column.
        2. translate the diagnoses to english if necessary and infer the diagnosis_translated column.
        3. Extract the relevant diagnosis as a string and loose everything that is not relevant. This is the diagnosis column.
        4. Extract the month and year of the medical history for that diagnosis. If not applicable, write an empty string.

        Example 1:
        Input: "schwere Herzinsuffizienz, 2. Grad, NYHA II, ED 07/2023"
        Output: [{"patient_id": 1, "diagnosis_reference": "schwere chronische Herzinsuffizienz, 2. Grad, NYHA II", "diagnosis_translated": "severe chronic heart failure, 2nd degree, NYHA II", "diagnosis": "chronic heart failure", "month": "7", "year": "2023"}]

        Example 2:
        Input: "Myocardial Infarction"
        Output: [{"patient_id": 2, "diagnosis_reference": "Myocardial Infarction", "diagnosis_translated": "Myocardial Infarction", "diagnosis": "Myocardial Infarction", "month": "", "year": ""}]        

        Example 3:
        Input: "Lungenteilresektion rechts bei Lungenmetastasen eines Kolonkarzinoms, 2023-07-01"
        Output: [
            {"patient_id": 3, "diagnosis_reference": "Lungenteilresektion rechts bei Lungenmetastasen eines Kolonkarzinoms", "diagnosis_translated": "Lung resection due to lung metastases of colon cancer", "diagnosis": "colon cancer", "month": "7", "year": "2023"},
            {"patient_id": 3, "diagnosis_reference": "Lungenteilresektion rechts bei Lungenmetastasen eines Kolonkarzinoms", "diagnosis_translated": "Lung resection due to lung metastases of colon cancer", "diagnosis": "lung metastasis", "month": "7", "year": "2023"}
        ]
        
        5. After you extracted the diagnosis, use the diagnosis string to look up the ICD-11 code for the diagnosis. If there are multiple codes, choose the candidate that you think fits the best to the translated diagnosis. Usually, the first candidate with a score of 1 is the best choice, but you can decide otherwise if you have reasonable grounds for another decision. If there are no codes, write an empty string.

        save the the following columns:
        - patient_id: The patient ID.
        - diagnosis_reference: The diagnosis of the medical history found in the text.
        - diagnosis_translated: The corrected diagnosis of the medical history, translated to english.
        - diagnosis: The extracted diagnosis.
        - month: The month of the medical history. if not applicable, write an empty string.
        - year: The year of the medical history. if not applicable, write an empty string.
        - icd11_code: The ICD-11 code for the diagnosis. If there are no codes, write an empty string.
        """
    ),
    tools=[save_csv, extract_diagnosis_data, lookup_icd11],
)
