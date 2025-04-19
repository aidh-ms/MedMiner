from dataclasses import dataclass
from textwrap import dedent, indent


@dataclass
class Document:
    patient_id: str
    text: str

    @property
    def content(self) -> str:
        return dedent(
            f"""\
            Patient: {self.patient_id}\n{indent(self.text, " " * 4 * 3)}
            """
        )
