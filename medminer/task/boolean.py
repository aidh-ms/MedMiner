from textwrap import dedent, indent

from medminer.task import Task, register_task
from medminer.tools.csv import CSVTool
from medminer.tools.settings import ToolSetting


@register_task
class BooleanTask(Task):
    name = "boolean"
    verbose_name = "Filter"
    prompt = dedent(
        """
        Given a medical information of a patient, extract all patients which information match a given filter query. These are the steps you should follow to complete the task:

        1. Check if the medical information of the patient matches the filter query.
        2. save the information as csv with the columns defined below.

        save the the following columns:
        - patient_id: The patient ID.
        - patient_filter: True if the patient information matches the filter query, false otherwise.
        - patient_information: The medical information of the patient that matched the query.
        """
    )
    tools = [CSVTool]

    @classmethod
    def settings(cls) -> list[ToolSetting]:
        settings = super().settings()
        settings.append(ToolSetting(id="boolean_query", label="Filter Query", type=str))
        return settings

    def _buidl_prompt(self, data: str) -> str:
        return dedent(
            f"""\
            Task name: {self.name}
            Prompt: \n{indent(self.prompt, " " * 4 * 5)}

            Filter query: {self._settings.get("boolean_query", "")}

            {"-" * 80}
            Data: \n{indent(data, " " * 4 * 5)}
            """
        )
