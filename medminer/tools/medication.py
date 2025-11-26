"""
This module contains various tools for extracting and processing medical data.
"""
import re
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
        >>> medication_names = ["aspirin (acetylsalicylic acid)", "paracetamol (acetaminophen)"]
        >>> get_rxcui(medication_names)
        {
            "aspirin": {"12345": ["RXNORM"]},
            "paracetamol": {"67890": ["RXNORM"]},
        }

    Args:
        medication_names: A list of all corrected medication names.

    Returns:
        A dictionary containing the medication information (e.g. rxcui and supporting sources).
    """
    NAME_REGEX = re.compile(r"\(.*\)")
    data: dict[str, dict] = {}

    base_url = "https://rxnav.nlm.nih.gov/REST/"
    with httpx.Client(base_url=base_url) as client:
        for medication_name in medication_names:
            rxcuis = defaultdict(list)

            # First try to get an exact match
            exact = (
                client.get(
                    "rxcui.json",
                    params={
                        "name": NAME_REGEX.sub("", medication_name).strip(),
                    },
                )
                .json()
                .get("idGroup", {})
                .get("rxnormId", [])
            )
            for cand in exact:
                rxcuis[cand].append("RXNORM")

            if exact:
                data[medication_name] = dict(rxcuis)
                continue

            # If no exact match found, try to get an approximate match
            candidates = (
                client.get(
                    "approximateTerm.json",
                    params={
                        "term": medication_name,
                    },
                )
                .json()
                .get("approximateGroup", {})
                .get("candidate", [])
            )
            for cand in candidates:
                if cand["rank"] != "1":
                    continue

                rxcuis[cand["rxcui"]].append(cand["source"])

            data[medication_name] = dict(rxcuis)

    return data


def get_codes(
    rxcui: str,
    name: str,
) -> list[str]:
    """
    Get medication codes for a given rxcui.

    Args:
        rxcui: A rxcui.
        name: The name of he code.

    Returns:
        A list of medication codes.
    """
    base_url = f"https://rxnav.nlm.nih.gov/REST/rxcui/{rxcui}/"
    with httpx.Client(base_url=base_url) as client:
        codes = (
            client.get("allProperties.json", params={"prop": "Codes"})
            .json()
            .get("propConceptGroup", {})
            .get("propConcept", [])
        )
        return [code["propValue"] for code in codes if code["propName"].lower() == name.lower()]


@tool
def get_atc(
    rxcuis: list[str],
) -> dict[str, str]:
    """
    Get medication information for a given list of rxcuis.

    Args:
        rxcuis: A list of corrected rxcuis.

    Example:
        >>> rxcuis = ["12345", "67890"]
        >>> get_atc(rxcuis)
        {
            "12345": "B01AC06;A01AD05",
            "67890": "N02BA01",
        }

    Returns:
        A dictionary containing the medication information (e.g. ATC Code).
    """
    return {rxcui: ";".join(get_codes(rxcui, "ATC")) for rxcui in rxcuis}


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
