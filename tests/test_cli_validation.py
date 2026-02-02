"""Tests for CLI input validation (invalid --format, etc.)."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from resume_analyzer.cli import app

runner = CliRunner()


def test_invalid_format_exits_with_error() -> None:
    """Invalid --format must exit with code 1 and error message."""
    resume = Path(__file__).parent.parent / "examples" / "sample_resume.txt"
    job = Path(__file__).parent.parent / "examples" / "sample_jd.txt"
    if not resume.exists() or not job.exists():
        return  # skip if examples missing
    result = runner.invoke(
        app,
        ["analyze", "--resume", str(resume), "--job", str(job), "--format", "invalid"],
    )
    assert result.exit_code == 1
    assert "format" in result.output.lower() or "json" in result.output.lower()
