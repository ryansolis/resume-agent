"""Input/output models for the analyzer."""

from __future__ import annotations

from pydantic import BaseModel, Field


class KeywordRank(BaseModel):
    """A keyword with its rank (1-based)."""

    term: str
    rank: int


class AnalyzeInput(BaseModel):
    """API/CLI input: resume + job description or role + keywords."""

    resume_text: str = Field(..., description="Plain text resume")
    job_description: str | None = Field(None, description="Full job description text")
    role_title: str | None = Field(None, description="Role title when using keyword list")
    keywords: list[str] | None = Field(None, description="Target keywords when not using full JD")


class AnalysisResult(BaseModel):
    """Structured analysis output."""

    top_keywords: list[KeywordRank] = Field(..., description="Top extracted keywords from resume (ranked)")
    matched_keywords: list[str] = Field(..., description="Keywords in both resume and target")
    missing_keywords: list[str] = Field(..., description="Target keywords not found in resume")
    confidence_notes: list[str] = Field(..., description="Human-readable confidence/context notes")
    overall_score: float = Field(..., ge=0, le=100, description="Deterministic score 0–100")
    score_breakdown: dict[str, float | int | str] = Field(
        default_factory=dict,
        description="Explainable breakdown: matched_count, target_count, formula inputs",
    )


def format_readable_summary(result: AnalysisResult) -> str:
    """Produce a human-readable summary from the result."""
    lines = [
        "=== Resume Analysis Summary ===",
        "",
        f"Overall score: {result.overall_score:.0f}/100",
        "",
        "Top keywords (resume):",
    ]
    for kr in result.top_keywords[:15]:
        lines.append(f"  {kr.rank}. {kr.term}")
    matched_preview = ", ".join(sorted(result.matched_keywords)[:20]) + ("..." if len(result.matched_keywords) > 20 else "")
    missing_preview = ", ".join(sorted(result.missing_keywords)[:20]) + ("..." if len(result.missing_keywords) > 20 else "")
    lines.extend([
        "",
        f"Matched ({len(result.matched_keywords)}): " + (matched_preview or "(none)"),
        "",
        f"Missing ({len(result.missing_keywords)}): " + (missing_preview or "(none)"),
        "",
        "Confidence notes:",
    ])
    for note in result.confidence_notes:
        lines.append(f"  • {note}")
    lines.append("")
    return "\n".join(lines)
