import pytest

from medminer.tools.medication import (
    get_atc,
    get_rxcui,
    get_va,
)


@pytest.mark.vcr
def test_get_rxcui() -> None:
    medication_names = [
        "aspirin (acetylsalicylic acid)",
        "paracetaml (acetaminophen)",  # Typo intentional in name to test robustness
    ]

    rxcuis = get_rxcui(medication_names)
    assert isinstance(rxcuis, dict)
    assert rxcuis.get("aspirin (acetylsalicylic acid)") == {"1191": ["RXNORM"]}
    assert rxcuis.get("paracetaml (acetaminophen)", {}).get("161")


@pytest.mark.vcr
def test_get_atc() -> None:
    rxcuis = ["1191", "161"]

    atc_codes = get_atc(rxcuis)
    assert isinstance(atc_codes, dict)
    assert atc_codes.get("1191") == "A01AD05;B01AC06;N02BA01"
    assert atc_codes.get("161") == "N02BE01"


@pytest.mark.vcr
def test_get_va() -> None:
    rxcuis = ["1191", "161"]

    va_info = get_va(rxcuis)
    assert isinstance(va_info, dict)
    assert "1191" in va_info
    assert "161" in va_info
