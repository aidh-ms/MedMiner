import pytest

from medminer.tools.procedure import SNOMEDTool


@pytest.mark.vcr
def test_snomed_tool() -> None:
    tool = SNOMEDTool(
        snowstorm_base_url="http://snowstorm:8080",
        snowstorm_edition="MAIN",
    )

    procedures = tool.forward(
        term="Cranial Computed Tomography",
        synonyms={"Cranial": "Head"},
        keywords=["CT"],
    )

    assert len(procedures) > 0
    assert procedures[0].get("fsn") == "Computed tomography of head (procedure)"
    assert procedures[0].get("id") == "303653007"
