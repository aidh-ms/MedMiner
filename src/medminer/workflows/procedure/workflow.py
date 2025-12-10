"""Procedure extraction workflow implementation.

This module defines the workflow for extracting procedure information from medical
documents and enriching it with SNOMED CT codes using the Snowstorm API.
"""

from textwrap import dedent

from medminer.workflows.base.workflow import BaseExtractionWorkflow
from medminer.workflows.procedure.node import SnomedProcedureLookup
from medminer.workflows.procedure.schema import ProcedureState
from medminer.workflows.registry import register_workflow


@register_workflow
class ProcedureExtractionWorkflow(BaseExtractionWorkflow[ProcedureState]):
    """Workflow for extracting and enriching procedure data from medical documents.

    This workflow extracts procedure information using an LLM and then enriches it
    with standardized SNOMED CT codes via the Snowstorm API.

    Attributes:
        prompt: The LLM prompt instructing how to extract procedure information.
        process_nodes: Tuple of processing nodes (SnomedProcedureLookup) to enrich the data.
    """
    prompt = dedent("""\
        Given a doctors letter containing none or multiple procedures, extract all procedures and their relevant information.

        Values to extract:
        - reference: The procedure as it appears in the text.
        - name: The name of the procedure.
        - name_translated: The name of the procedure translated to English.
        - search_term: A search term that can be used to find the procedure in SNOMED CT.
        - year: The year the procedure was performed. if no year is given, return -1.
        - month: The month the procedure was performed. if no month is given, return -1.
        - day: The day the procedure was performed. if no day is given, return -1.
    """)
    process_nodes = (
        SnomedProcedureLookup,
    )
