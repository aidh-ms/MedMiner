import gradio as gr

from medminer.ui.api import TaskType, process_files, process_sql, process_text

with gr.Blocks(
    title="MedMiner",
) as demo:
    title = gr.Markdown(
        """
        # MedMiner
        A tool for extracting information from medical text in natural langauage.
        """
    )
    with gr.Row():
        with gr.Column(scale=1):
            input_text = gr.Markdown("## Input")
            tasks_input = gr.CheckboxGroup(
                label="Task",
                info="Select the task you want to perform.",
                choices=TaskType.list(),
            )

            with gr.Tab("Files"):
                files_tab_text = gr.Markdown("Upload a file to extract information from it.")
                files_input = gr.Files(label="Upload a files", file_types=[".txt", ".csv"], file_count="multiple")
                process_files_btn = gr.Button("Process Files")

            with gr.Tab("SQL"):
                sql_tab_text = gr.Markdown("Enter a SQL query to extract information from a database.")
                sql_input = gr.Textbox(label="SQL Query", placeholder="SELECT patient_id, text FROM patient_notes")
                process_sql_btn = gr.Button("Process SQL")

            with gr.Tab("Text"):
                text_tab_text = gr.Markdown("Enter a text to extract information from it.")
                text_input = gr.Textbox(label="Text", placeholder="Enter text here", lines=25)
                process_text_btn = gr.Button("Process Text")

        with gr.Column(scale=1):
            output_text = gr.Markdown("## Output")

            output_data = gr.Dataframe()

        process_files_btn.click(process_files, inputs=[files_input, tasks_input], outputs=[output_data])
        process_sql_btn.click(process_sql, inputs=[sql_input, tasks_input], outputs=[output_data])
        process_text_btn.click(process_text, inputs=[text_input, tasks_input], outputs=[output_data])


demo.launch()
