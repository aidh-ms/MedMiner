"""
This module contains various tools for extracting and processing medical data.
"""

from collections import defaultdict

import httpx
from smolagents import tool


@tool
def extract_medication_data(
    data: list[dict],
) -> list[dict]:
    """
    Adds extracted data to the task memory.

    Args:
        data: A list of dictionaries containing the data to save.
            All dictionaries must have the following keys.
            - patient_id: The patient ID.
            - medication_name: The name of the medication in the document without dose, unit or additional information.
            - medication_name_corrected: Use the following format "Brand name or medication name (active ingredient)". e.g. "Aspirin (acetylsalicylic acid)" and correct any spelling errors.
            - dose: The dose of the medication. this sould only contain the numeric value.
            - unit: The unit of the dose (e.g. ml, mg, ...). if not applicable, write an empty string.
            - route: The route of administration of the medication. if not applicable, write an empty string.
            - frequency: The raw frequency text of the medication. if not applicable, write an empty string.
            - frequency_code: The frequency code of the medication. if not applicable, write an empty string.

    Returns:
        A message indicating where the data was saved.

    Example:
        >>> data = [
        ...     {"patient_id": 1, "medication_name": "Aspirin"},
        ...     {"patient_id": 2, "medication_name": "Paracetamol"},
        ... ]
        >>> extract_medication_data("medication", data)
    """
    return data


@tool
def get_rxcui(medication_names: list[str]) -> dict:
    """
    Get medication information for a given list of medication names.

    Example:
        >>> medication_names = ["Aspirin", "Paracetamol"]
        >>> get_rxcui(medication_names)
        {
            "Aspirin": {"12345": ["RXNORM"]},
            "Paracetamol": {"67890": ["RXNORM"]},
        }

    Args:
        medication_names: A list of corrected medication names.

    Returns:
        A dictionary containing the medication information (e.g. rxcui and supporting sources).
    """
    data: dict[str, dict] = {}

    base_url = "https://rxnav.nlm.nih.gov/REST/"
    with httpx.Client(base_url=base_url) as client:
        for medication_name in medication_names:
            params = {
                "term": medication_name,
            }

            rxcuis = defaultdict(list)

            for cand in (
                client.get("approximateTerm.json", params=params)
                .json()
                .get("approximateGroup", {})
                .get("candidate", [])
            ):
                if cand["rank"] != "1":
                    continue

                rxcuis[cand["rxcui"]].append(cand["source"])

            data[medication_name] = dict(rxcuis)

    return data


@tool
def get_atc(
    rxcuis: list[str],
) -> dict:
    """
    Get medication information for a given list of rxcuis.

    Args:
        rxcuis: A list of corrected rxcuis.

    Returns:
        A dictionary containing the medication information (e.g. ATC Code).
    """
    data: dict[str, dict[str, str]] = {}

    base_url = "https://rxnav.nlm.nih.gov/REST/"
    with httpx.Client(base_url=base_url) as client:
        for rxcui in rxcuis:
            params = {
                "rxcui": rxcui,
            }
            atc = next(
                (
                    cand
                    for cand in (
                        client.get("rxclass/class/byRxcui.json", params=params)
                        .json()
                        .get("rxclassDrugInfoList", {})
                        .get("rxclassDrugInfo", [])
                    )
                    if "atc" in cand["relaSource"].lower()
                ),
                None,
            )

            if not atc:
                data[rxcui] = {}
                continue

            concept = atc.get("rxclassMinConceptItem", {})

            if not concept:
                data[rxcui] = {}
                continue

            data[rxcui] = {
                "atc_id": concept.get("classId"),
                "atc_name": concept.get("className"),
                "atc_type": concept.get("classType"),
            }

    return data


@tool
def get_va(
    rxcuis: list[str],
) -> dict:
    """
    Get medication va information for a given list of rxcuis.

    Args:
        rxcuis: A list of corrected rxcuis.

    Returns:
        A dictionary containing the medication information (e.g. VA Code).
    """
    data: dict[str, dict[str, str]] = {}

    base_url = "https://rxnav.nlm.nih.gov/REST/"
    with httpx.Client(base_url=base_url) as client:
        for rxcui in rxcuis:
            params = {
                "rxcui": rxcui,
            }
            atc = next(
                (
                    cand
                    for cand in (
                        client.get("rxclass/class/byRxcui.json", params=params)
                        .json()
                        .get("rxclassDrugInfoList", {})
                        .get("rxclassDrugInfo", [])
                    )
                    if "va" in cand["relaSource"].lower()
                ),
                None,
            )

            if not atc:
                data[rxcui] = {}
                continue

            concept = atc.get("rxclassMinConceptItem", {})

            if not concept:
                data[rxcui] = {}
                continue

            data[rxcui] = {
                "va_id": concept.get("classId"),
                "va_name": concept.get("className"),
            }

    return data
