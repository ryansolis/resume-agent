"""Orchestration: run pipeline and return AnalysisResult."""

from __future__ import annotations

from resume_analyzer.extract import extract_keyword_set, extract_keywords
from resume_analyzer.match import compute_matched_and_missing
from resume_analyzer.models import AnalysisResult, KeywordRank, format_readable_summary
from resume_analyzer.normalize import normalize_text, tokenize_without_stopwords
from resume_analyzer.score import compute_score


def _target_keywords_from_jd(job_description: str, top_n: int = 50) -> set[str]:
    """Extract unique keywords from job description."""
    return extract_keyword_set(job_description)


def _target_keywords_from_list(keywords: list[str]) -> set[str]:
    """Normalize and dedupe provided keyword list."""
    out: set[str] = set()
    for k in keywords:
        if not k or not isinstance(k, str):
            continue
        normalized = normalize_text(k)
        tokens = tokenize_without_stopwords(normalized)
        for t in tokens:
            if len(t) >= 2:
                out.add(t)
    return out


def analyze(
    resume_text: str,
    job_description: str | None = None,
    role_title: str | None = None,
    keywords: list[str] | None = None,
    top_n_keywords: int = 30,
) -> AnalysisResult:
    """
    Analyze resume against target role.
    Target is either job_description (full JD text) or role_title + keywords.
    """
    resume_text = resume_text or ""
    target_keywords: set[str] = set()
    if job_description and job_description.strip():
        target_keywords = _target_keywords_from_jd(job_description, top_n=top_n_keywords * 2)
    if keywords:
        target_keywords |= _target_keywords_from_list(keywords)
    if role_title and role_title.strip():
        target_keywords |= _target_keywords_from_list([role_title])

    resume_keywords_set = extract_keyword_set(resume_text)
    top_ranked = extract_keywords(resume_text, top_n=top_n_keywords)
    matched, missing = compute_matched_and_missing(resume_keywords_set, target_keywords)
    score, breakdown, confidence_notes = compute_score(len(matched), max(1, len(target_keywords)))

    top_keywords = [KeywordRank(term=t, rank=i + 1) for i, (t, _) in enumerate(top_ranked)]

    return AnalysisResult(
        top_keywords=top_keywords,
        matched_keywords=matched,
        missing_keywords=missing,
        confidence_notes=confidence_notes,
        overall_score=score,
        score_breakdown=breakdown,
    )


def analyze_and_summary(
    resume_text: str,
    job_description: str | None = None,
    role_title: str | None = None,
    keywords: list[str] | None = None,
) -> tuple[AnalysisResult, str]:
    """Run analyze and return (result, readable_summary)."""
    result = analyze(resume_text=resume_text, job_description=job_description, role_title=role_title, keywords=keywords)
    return (result, format_readable_summary(result))
