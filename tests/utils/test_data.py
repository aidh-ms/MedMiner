from medminer.utils.data import Document


def test_document_content() -> None:
    doc = Document(
        patient_id="12345",
        text="This is a sample medical document.\nIt contains multiple lines.",
    )
    expected_content = "Patient: 12345\nThis is a sample medical document.\nIt contains multiple lines.\n"
    assert doc.content == expected_content
