"""CLI for resume analyzer."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import typer

from resume_analyzer.analyzer import analyze_and_summary
from resume_analyzer.models import AnalysisResult

app = typer.Typer(help="Resume Analyzer — evaluate resume vs. job description or keyword list.")


def _load_text(path: Path | None, stdin_if_missing: bool = False) -> str:
    if path is None:
        if stdin_if_missing and not sys.stdin.isatty():
            return sys.stdin.read()
        return ""
    if not path.exists():
        typer.echo(f"Error: file not found: {path}", err=True)
        raise typer.Exit(1)
    return path.read_text(encoding="utf-8", errors="replace")


@app.command()
def analyze(
    resume: str = typer.Option(..., "--resume", "-r", help="Path to resume (.txt) or - for stdin"),
    job: Path | None = typer.Option(None, "--job", "-j", help="Path to job description (.txt)"),
    role: str | None = typer.Option(None, "--role", help="Role title (when not using full JD)"),
    keywords: str | None = typer.Option(None, "--keywords", "-k", help="Comma-separated target keywords"),
    format_output: str = typer.Option("both", "--format", "-f", help="Output: json | summary | both"),
    output_path: Path | None = typer.Option(None, "--output", "-o", help="Write result to file (default: stdout)"),
) -> None:
    """Analyze resume against job description or role + keywords."""
    if format_output not in ("json", "summary", "both"):
        typer.echo("Error: --format must be one of: json, summary, both.", err=True)
        raise typer.Exit(1)
    use_stdin = resume.strip() == "-"
    resume_text = sys.stdin.read() if use_stdin else _load_text(Path(resume))
    if not resume_text.strip():
        typer.echo("Error: no resume text provided.", err=True)
        raise typer.Exit(1)

    job_description: str | None = None
    if job:
        job_description = _load_text(job)
    keyword_list: list[str] | None = None
    if keywords:
        keyword_list = [k.strip() for k in keywords.split(",") if k.strip()]

    if not job_description and not keyword_list and not role:
        typer.echo("Error: provide --job, and/or --role and/or --keywords.", err=True)
        raise typer.Exit(1)

    result, summary = analyze_and_summary(
        resume_text=resume_text,
        job_description=job_description or None,
        role_title=role,
        keywords=keyword_list,
    )

    out_parts: list[str] = []
    if format_output in ("json", "both"):
        out_parts.append(result.model_dump_json(indent=2))
    if format_output in ("summary", "both"):
        if out_parts:
            out_parts.append("")
        out_parts.append(summary)

    output = "\n".join(out_parts)
    if output_path:
        output_path.write_text(output, encoding="utf-8")
        typer.echo(f"Wrote result to {output_path}")
    else:
        typer.echo(output)


@app.command()
def version() -> None:
    """Show version."""
    typer.echo("1.0.0")


if __name__ == "__main__":
    app()
