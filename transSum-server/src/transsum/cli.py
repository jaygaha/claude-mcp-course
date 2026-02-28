"""
transSum CLI — Command-Line Interface.

Provides three commands:
    transsum summarize  — Summarize a document or inline text
    transsum translate  — Translate a document or inline text
    transsum config     — Show current configuration

Usage:
    transsum summarize report.pdf
    transsum summarize --text "Long article content here..."
    transsum translate paper.txt --language French
    transsum translate --text "Hello world" -l Japanese -p anthropic
    transsum config
"""

from __future__ import annotations

import asyncio
import logging
import os
import sys

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from transsum.config import Settings, ModelProvider, get_settings
from transsum.models.factory import create_adapter
from transsum.processing.loader import DocumentLoader
from transsum.processing.chunker import TextChunker
from transsum.processing.pipeline import ProcessingPipeline, TaskType, PipelineResult

console = Console()

# Helpers

def _setup_logging(level: str) -> None:
    """Configure structured logging for the CLI session."""
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s │ %(name)-24s │ %(levelname)-7s │ %(message)s",
        datefmt="%H:%M:%S",
    )


def _apply_overrides(
    provider: str | None = None,
    model: str | None = None,
) -> Settings:
    """
    Build Settings with CLI flag overrides.

    CLI flags take precedence over .env values. We set them as
    env vars so Pydantic picks them up during validation.
    """
    if provider:
        os.environ["MODEL_PROVIDER"] = provider
    if model:
        active = provider or os.environ.get("MODEL_PROVIDER", "ollama")
        if active == "ollama":
            os.environ["OLLAMA_MODEL"] = model
        else:
            os.environ["ANTHROPIC_MODEL"] = model
    return get_settings()


def _print_header(document, settings: Settings, task: TaskType, language: str = "") -> None:
    """Print the pre-processing info panel."""
    details = (
        f"[bold]{document.summary_line}[/bold]\n"
        f"Provider: [cyan]{settings.model_provider}[/cyan]  •  "
        f"Task: [green]{task.value}[/green]"
    )
    if task == TaskType.TRANSLATE:
        details += f"  •  Target: [yellow]{language}[/yellow]"

    console.print()
    console.print(Panel(details, title="📄 transSum", border_style="blue"))


def _print_result(result: PipelineResult) -> None:
    """Print the formatted result panel and stats."""
    console.print()
    console.print(Panel(
        Markdown(result.output),
        title=f"✅ {result.task.value.title()} Complete",
        border_style="green",
        padding=(1, 2),
    ))

    # Stats line
    prompt_tok = result.usage.get("prompt_tokens", "?")
    comp_tok = result.usage.get("completion_tokens", "?")
    console.print(
        f"\n[dim]Model: {result.model}  •  "
        f"Provider: {result.provider}  •  "
        f"Chunks: {result.chunks_processed}  •  "
        f"Tokens: {prompt_tok}↑ {comp_tok}↓[/dim]\n"
    )


async def _execute(
    settings: Settings,
    document,
    task: TaskType,
    language: str = "English",
) -> None:
    """Run the pipeline with progress spinner and formatted output."""
    adapter = create_adapter(settings)
    chunker = TextChunker(settings.chunk_size, settings.chunk_overlap)
    pipeline = ProcessingPipeline(adapter, chunker)

    try:
        _print_header(document, settings, task, language)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True,
        ) as progress:
            task_id = progress.add_task(description="Processing with LLM…", total=None)

            def _update_status(msg: str) -> None:
                progress.update(task_id, description=msg)

            result = await pipeline.run(
                document, task, language=language, on_progress=_update_status,
            )

        _print_result(result)

    except RuntimeError as exc:
        console.print(f"\n[bold red]Error:[/bold red] {exc}\n")
        sys.exit(1)
    finally:
        await adapter.close()


# Click Command Group

@click.group()
@click.option(
    "--log-level", "-v",
    default=None,
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
    help="Set logging verbosity (default: WARNING for clean output).",
)
@click.version_option(package_name="transsum")
@click.pass_context
def main(ctx, log_level):
    """
    📄 transSum — Summarize & translate documents with AI.

    Uses Ollama (local) or Anthropic (cloud) models, configured
    via .env file or CLI flags.
    """
    _setup_logging(log_level or "WARNING")


# Command: summarize

@main.command()
@click.argument("file", required=False, type=click.Path(exists=True))
@click.option(
    "--text", "-t",
    help="Inline text to summarize (use instead of a file).",
)
@click.option(
    "--provider", "-p",
    type=click.Choice(["ollama", "anthropic"], case_sensitive=False),
    help="Override the model provider.",
)
@click.option("--model", "-m", help="Override the model name.")
def summarize(file, text, provider, model):
    """
    Summarize a document or inline text.

    \b
    Examples:
        transsum summarize report.pdf
        transsum summarize notes.md --provider anthropic
        transsum summarize --text "Your long text here…"
        transsum summarize paper.txt -m mistral
    """
    if not file and not text:
        console.print(
            "[bold red]Error:[/bold red] Provide a FILE argument "
            "or use --text to pass inline text.\n"
        )
        raise SystemExit(1)

    settings = _apply_overrides(provider, model)
    doc = DocumentLoader.load(file) if file else DocumentLoader.load_text(text)
    asyncio.run(_execute(settings, doc, TaskType.SUMMARIZE))


# Command: translate

@main.command()
@click.argument("file", required=False, type=click.Path(exists=True))
@click.option(
    "--text", "-t",
    help="Inline text to translate (use instead of a file).",
)
@click.option(
    "--language", "-l",
    default="English",
    show_default=True,
    help="Target language for translation.",
)
@click.option(
    "--provider", "-p",
    type=click.Choice(["ollama", "anthropic"], case_sensitive=False),
    help="Override the model provider.",
)
@click.option("--model", "-m", help="Override the model name.")
def translate(file, text, language, provider, model):
    """
    Translate a document or inline text.

    \b
    Examples:
        transsum translate article.txt --language French
        transsum translate --text "Hello world" -l Japanese
        transsum translate paper.pdf -l German -p anthropic
    """
    if not file and not text:
        console.print(
            "[bold red]Error:[/bold red] Provide a FILE argument "
            "or use --text to pass inline text.\n"
        )
        raise SystemExit(1)

    settings = _apply_overrides(provider, model)
    doc = DocumentLoader.load(file) if file else DocumentLoader.load_text(text)
    asyncio.run(_execute(settings, doc, TaskType.TRANSLATE, language=language))


# Command: config

@main.command()
def config():
    """Display current configuration from .env and defaults."""
    settings = get_settings()

    table = Table(
        title="transSum Configuration",
        show_header=True,
        header_style="bold cyan",
        border_style="dim",
        padding=(0, 2),
    )
    table.add_column("Setting", style="bold")
    table.add_column("Value")

    key_display = "🔑 set" if settings.anthropic_api_key else "⚠️  not set"

    table.add_row("Provider", f"[cyan]{settings.model_provider}[/cyan]")
    table.add_row("", "")
    table.add_row("Ollama URL", settings.ollama_base_url)
    table.add_row("Ollama Model", settings.ollama_model)
    table.add_row("", "")
    table.add_row("Anthropic Model", settings.anthropic_model)
    table.add_row("Anthropic Key", key_display)
    table.add_row("", "")
    table.add_row("Chunk Size", f"{settings.chunk_size:,} chars")
    table.add_row("Chunk Overlap", f"{settings.chunk_overlap:,} chars")
    table.add_row("Max Retries", str(settings.max_retries))
    table.add_row("Timeout", f"{settings.request_timeout}s")
    table.add_row("", "")
    table.add_row("Log Level", settings.log_level)
    table.add_row("MCP Port", str(settings.mcp_server_port))

    console.print()
    console.print(table)
    console.print()


# Entry Point

if __name__ == "__main__":
    main()