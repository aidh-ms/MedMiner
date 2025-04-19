import os
import time

import httpx
from smolagents import tool

# --- ICD API Config ---
TOKEN_URL = "https://icdaccessmanagement.who.int/connect/token"
ICD_SEARCH_URL = "https://id.who.int/icd/release/11/2022-02/mms/search"

CLIENT_ID = os.environ.get("ICD_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("ICD_CLIENT_SECRET", "")
SCOPE = "icdapi_access"
GRANT_TYPE = "client_credentials"


_token_cache = {"token": None, "expires_at": 0}


def get_token() -> str:
    """
    Authenticate with the WHO ICD API and return an access token.
    Caches the token for the period it is valid to reduce roundtrip time.
    """
    global _token_cache

    # Check if the cached token is still valid
    if _token_cache["token"] and time.time() < _token_cache["expires_at"]:  # type: ignore[operator]
        return _token_cache["token"]  # type: ignore[return-value]

    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": SCOPE,
        "grant_type": GRANT_TYPE,
    }

    with httpx.Client(verify=True) as client:
        response = client.post(TOKEN_URL, data=payload)
        response.raise_for_status()
        response_data = response.json()
        token = response_data.get("access_token")
        expires_in = response_data.get("expires_in", 3600)  # Default to 1 hour if not provided

        # Cache the token and its expiry time
        _token_cache["token"] = token
        _token_cache["expires_at"] = time.time() + expires_in

        return token  # type: ignore[no-any-return]


@tool
def extract_diagnosis_data(
    data: list[dict],
) -> list[dict]:
    """
    Adds extracted data to the task memory.

    Args:
        data: A list of dictionaries containing the data to save

            All dictionaries must have the following keys.
            - patient_id: The patient ID.
            - diagnosis_reference: The diagnosis of the medical history found in the text.
            - diagnosis_translated: The corrected diagnosis of the medical history, translated to english.
            - diagnosis: The extracted diagnosis.
            - month: The month of the medical history. if not applicable, write an empty string.
            - year: The year of the medical history. if not applicable, write an empty string.

    Returns:
        A message indicating where the data was saved.

    Example:
        >>> data = [
        ...     {"patient_id": 1, "diagnosis": "Myocardial Infarction"},
        ...     {"patient_id": 2, "diagnosis": "colon cancer"},
        ... ]
        >>> extract_diagnosis_data("diagnosis", data)
    """
    return data


@tool
def lookup_icd11(terms: list[str]) -> list[dict]:
    """
    Lookup ICD-11 codes for a list of terms.

    Args:
        terms: A list of terms to search for in the ICD-11 database.

    Returns:
        A list of dictionaries containing the ICD-11 codes and their title and scores.

    Example:
        >>> terms = ["Myocardial Infarction", "colon cancer"]
        >>> lookup_icd11(terms)
    """
    token = get_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Accept-Language": "en",
        "API-Version": "v2",
    }
    with httpx.Client(verify=True) as client:
        results = []
        for term in terms:
            params = {"q": term, "useFlexisearch": "true"}

            response = client.get(ICD_SEARCH_URL, headers=headers, params=params)
            try:
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                print("💥 Token request failed:")
                print("Status:", e.response.status_code)
                print("Response:", e.response.text)
                raise
            data = response.json()
            candidates = [
                {
                    "code": candidate.get("theCode"),
                    "score": candidate.get("score"),
                    "title": candidate.get("title"),
                }
                for candidate in data.get("destinationEntities", [])
            ]
            # filter for score  > 0.3 # TODO: maybe make this a parameter
            candidates = [c for c in candidates if c["score"] > 0.3]
            # sort by score descending
            candidates.sort(key=lambda x: x["score"], reverse=True)

            results.append(
                {
                    "term": term,
                    "candidates": candidates,
                }
            )

    return results
