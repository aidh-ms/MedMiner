"""Diagnosis extraction workflow implementation.

This module defines the workflow for extracting diagnosis information from medical
documents and enriching it with ICD-11 codes using the WHO ICD API.
"""

from textwrap import dedent

from medminer.workflows.base.workflow import BaseExtractionWorkflow
from medminer.workflows.diagnosis.node import ICDDiagnosisLookup
from medminer.workflows.diagnosis.schema import DiagnosisState
from medminer.workflows.registry import register_workflow


@register_workflow
class DiagnosisExtractionWorkflow(BaseExtractionWorkflow[DiagnosisState]):
    """Workflow for extracting and enriching diagnosis data from medical documents.

    This workflow extracts diagnosis information using an LLM and then enriches it
    with standardized ICD-11 codes via the WHO ICD API.

    Attributes:
        prompt: The LLM prompt instructing how to extract diagnosis information.
        process_nodes: Tuple of processing nodes (ICDDiagnosisLookup) to enrich the data.
    """
    prompt = dedent("""\
        Given a doctors letter containing none or multiple diagnoses, extract all diagnoses and their relevant information.

        Values to extract:
        - reference: The diagnosis as it appears in the text.
        - name: The name of the diagnosis.
        - name_translated: The name of the diagnosis translated to English.
        - year: The year the diagnosis was made. if no year is given, return -1.
        - month: The month the diagnosis was made. if no month is given, return -1.
        - day: The day the diagnosis was made. if no day is given, return -1.
    """)
    process_nodes = (
        ICDDiagnosisLookup,
    )
