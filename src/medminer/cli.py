"""MedMiner command-line interface.

This module provides the CLI for MedMiner, enabling users to extract medical information
from documents using various extraction workflows via command-line commands.
"""

import sys
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from medminer.conf import settings
from medminer.conf.global_settings import OpenAIModelSettings
from medminer.utils.models import load_model
from medminer.workflows.base.schema import DoctorsLetterState
from medminer.workflows.registry import registry

app = typer.Typer(
    name="medminer",
    help="Extract medical information from doctor's letters using LLM-powered workflows.",
    add_completion=False,
)
console = Console()
error_console = Console(stderr=True)


@app.command()
def extract(
    workflow: Annotated[
        str,
        typer.Argument(help="Name of the extraction workflow to use (e.g., 'medication_extraction_workflow')"),
    ],
    path: Annotated[
        Path,
        typer.Argument(
            help="Path to directory containing doctor's letters (*.txt files) or a single letter file",
            exists=True,
        ),
    ],
    # Model settings
    model_provider: Annotated[
        str | None,
        typer.Option("--model-provider", help="Model provider (e.g., 'openai')"),
    ] = None,
    model: Annotated[
        str | None,
        typer.Option("--model", help="Model name (e.g., 'gpt-4')"),
    ] = None,
    api_key: Annotated[
        str | None,
        typer.Option("--api-key", help="API key for the model provider"),
    ] = None,
    base_url: Annotated[
        str | None,
        typer.Option("--base-url", help="Base URL for the model API"),
    ] = None,
    # Storage settings
    base_dir: Annotated[
        Path | None,
        typer.Option("--base-dir", help="Base directory for storing extracted data (CSV files)"),
    ] = None,
    split_patient: Annotated[
        bool,
        typer.Option("--split-patient/--no-split-patient", help="Whether to split output files by patient ID"),
    ] = False,
    # SNOMED settings
    snomed_base_url: Annotated[
        str | None,
        typer.Option("--snomed-base-url", help="Base URL for the SNOMED Snowstorm server"),
    ] = None,
    # ICD-11 settings
    icd_client_id: Annotated[
        str | None,
        typer.Option("--icd-client-id", help="Client ID for ICD-11 API"),
    ] = None,
    icd_client_secret: Annotated[
        str | None,
        typer.Option("--icd-client-secret", help="Client Secret for ICD-11 API"),
    ] = None,
) -> None:
    """Extract medical information from doctor's letters using a specified workflow.

    Args:
        workflow: Name of the extraction workflow to use.
        path: Path to directory containing doctor's letters or a single letter file.
        model_provider: Optional model provider override.
        model: Optional model name override.
        api_key: Optional API key override.
        base_url: Optional base URL override.
        base_dir: Optional base directory for output files.
        split_patient: Whether to split output files by patient ID.
        snomed_base_url: Optional SNOMED Snowstorm server URL.
        icd_client_id: Optional ICD-11 API client ID.
        icd_client_secret: Optional ICD-11 API client secret.
    """
    # Update global settings with CLI arguments
    # Model settings
    if any([model_provider, model, api_key, base_url]):
        model_settings = {}

        # Start with existing settings if available
        if settings.MODEL:
            model_settings["model_provider"] = settings.MODEL.model_provider
            model_settings["model"] = settings.MODEL.model
            model_settings["api_key"] = settings.MODEL.api_key
            model_settings["base_url"] = settings.MODEL.base_url

        # Override with CLI arguments
        if model_provider:
            model_settings["model_provider"] = model_provider
        if model:
            model_settings["model"] = model
        if api_key:
            model_settings["api_key"] = api_key
        if base_url:
            model_settings["base_url"] = base_url

        settings.MODEL = OpenAIModelSettings(**model_settings)

    # Storage settings
    if base_dir:
        settings.BASE_DIR = base_dir
    if split_patient:
        settings.SPLIT_PATIENT = split_patient

    # SNOMED settings
    if snomed_base_url:
        settings.SNOWSTORM_BASE_URL = snomed_base_url

    # ICD-11 settings
    if icd_client_id:
        settings.ICD_CLIENT_ID = icd_client_id
    if icd_client_secret:
        settings.ICD_CLIENT_SECRET = icd_client_secret

    # Get workflow from registry
    workflow_class = registry.get(workflow)
    if workflow_class is None:
        error_console.print(f"[red]Error:[/red] Workflow '{workflow}' not found in registry.")
        error_console.print(f"\nAvailable workflows: {', '.join(registry.keys())}")
        sys.exit(1)

    # Load doctor's letters
    if path.is_file():
        files = [path]
    elif path.is_dir():
        files = [*path.glob("*.txt")]
        if not files:
            error_console.print(f"[red]Error:[/red] No .txt files found in directory: {path}")
            sys.exit(1)
    else:
        error_console.print(f"[red]Error:[/red] Path is neither a file nor a directory: {path}")
        sys.exit(1)

    # Create states
    console.print(f"[cyan]Loading {len(files)} doctor's letter(s)...[/cyan]")
    states = [
        DoctorsLetterState(patient_id=file.stem, letter=file.read_text())
        for file in files
    ]

    # Initialize model and workflow
    console.print(f"[cyan]Initializing workflow: {workflow}[/cyan]")
    try:
        llm_model = load_model()
        assert workflow_class is not None
        workflow_instance = workflow_class(model=llm_model)
    except Exception as e:
        error_console.print(f"[red]Error initializing workflow:[/red] {e}")
        sys.exit(1)

    # Run workflow
    console.print(f"[cyan]Processing {len(states)} letter(s)...[/cyan]")
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Extracting information...", total=None)
        try:
            results = workflow_instance.run_many(states)
            progress.update(task, completed=True)
        except Exception as e:
            error_console.print(f"\n[red]Error during extraction:[/red] {e}")
            sys.exit(1)

    # Report results
    output_dir = settings.BASE_DIR / workflow_instance.name if settings.BASE_DIR else Path.cwd() / workflow_instance.name
    console.print(f"[green]✓[/green] Successfully processed {len(results)} letter(s)")
    console.print(f"[green]✓[/green] Results saved to: {output_dir}")


@app.command()
def list() -> None:
    """List all available extraction workflows."""
    workflows = registry.keys()
    if not workflows:
        console.print("[yellow]No workflows registered.[/yellow]")
        return

    console.print("[cyan]Available workflows:[/cyan]")
    for name in sorted(workflows):
        workflow_class = registry.get(name)
        if workflow_class:
            console.print(f"  {name}")


@app.command()
def ui(
    share: Annotated[
        bool,
        typer.Option("--share", help="Create a public share link"),
    ] = False,
    server_name: Annotated[
        str,
        typer.Option("--server-name", help="Server host name"),
    ] = "127.0.0.1",
    server_port: Annotated[
        int,
        typer.Option("--server-port", help="Server port"),
    ] = 7860,
) -> None:
    """Launch the Gradio web interface for MedMiner.

    Args:
        share: Whether to create a public share link.
        server_name: Server host name.
        server_port: Server port.
    """
    pass # TODO: Implement UI launch functionality


def main() -> None:
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
