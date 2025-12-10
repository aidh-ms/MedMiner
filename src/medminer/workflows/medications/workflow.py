"""Medication extraction workflow implementation.

This module defines the workflow for extracting medication information from medical
documents and enriching it with RxNorm and ATC codes using the RxNav API.
"""

from textwrap import dedent

from medminer.workflows.base.workflow import BaseExtractionWorkflow
from medminer.workflows.medications.node import RxNavLookup
from medminer.workflows.medications.schema import MedicationState
from medminer.workflows.registry import register_workflow


@register_workflow
class MedicationExtractionWorkflow(BaseExtractionWorkflow[MedicationState]):
    """Workflow for extracting and enriching medication data from medical documents.

    This workflow extracts medication information using an LLM and then enriches it
    with standardized RxNorm and ATC codes via the RxNav API.

    Attributes:
        prompt: The LLM prompt instructing how to extract medication information.
        process_nodes: Tuple of processing nodes (RxNavLookup) to enrich the data.
    """
    prompt = dedent("""\
        Given a doctors letter containing none or multiple medications, extract all medications and their relevant information.

        Values to extract:
        - reference: The medication as it appears in the text with all details (e.g. dosage, unit, frequency).
        - name: The name of the medication (brand name or generic name).
        - name_translated: The name of the medication translated to English without any additional details.
        - active_ingredient: The active ingredient of the medication.
        - dose: The numeric value of the dose. if no dose is given, return -1.
        - unit: The unit of the dose (e.g. mg, ml). If no unit is given, return an empty string.
        - route: The route of administration (e.g. oral, intravenous). If no route is given, return an empty string.
        - frequency: The frequency of the medication (e.g. 1-0-1-0, as needed). If no frequency is given, empty string.
        - frequency_code: The frequency code of the medication (e.g. BID, Q8H). Use the following codes:
            * Q<int:hours>H: Every <int> hours (e.g. Q8H: Every 8 hours)
            * Q<int:days>D: Every <int> days (e.g. Q1D: Every 1 day)
            * Q<int:weeks>W: Every <int> weeks (e.g. Q1W: Every 1 week)
            * BID: Twice a day (e.g. 1-0-1-0)
            * TID: Three times a day (e.g. 1-1-1-0)
            * QID: Four times a day (e.g. 1-1-1-1)
            * QD: Once a day (used for medications that are taken once a day, e.g. 0-1-0 and doesn't fit AM/PM)
            * AM: In the morning (1-0-0-0)
            * PM: In the evening (0-0-1-0)
            * PRN: As needed
            * NaF: Not a frequency (e.g. for medications that are not taken regularly)
    """)
    process_nodes = (
        RxNavLookup,
    )
