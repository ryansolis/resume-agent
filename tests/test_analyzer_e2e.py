"""End-to-end analyzer tests."""

import pytest

from resume_analyzer.analyzer import analyze
from resume_analyzer.models import AnalysisResult


def test_analyze_job_description() -> None:
    resume = "I am a Python developer with C++ and Node.js experience. REST APIs and SQL."
    jd = "We need Python, JavaScript, and SQL. Experience with REST APIs required."
    result = analyze(resume_text=resume, job_description=jd)
    assert isinstance(result, AnalysisResult)
    assert 0 <= result.overall_score <= 100
    assert "python" in [k.term for k in result.top_keywords] or "python" in result.matched_keywords
    assert "sql" in result.matched_keywords
    assert result.score_breakdown["target_count"] >= 1
    assert result.score_breakdown["matched_count"] >= 1


def test_analyze_keywords_list() -> None:
    resume = "Python API backend developer. PostgreSQL and Docker."
    result = analyze(resume_text=resume, keywords=["python", "api", "postgresql", "kubernetes"])
    assert result.overall_score > 0
    assert "python" in result.matched_keywords
    assert "api" in result.matched_keywords
    assert "postgresql" in result.matched_keywords
    assert "kubernetes" in result.missing_keywords


def test_analyze_sql_vs_nosql_boundary() -> None:
    resume = "NoSQL databases: MongoDB and Redis."
    jd = "SQL and relational databases."
    result = analyze(resume_text=resume, job_description=jd)
    # NoSQL in resume should not match SQL in JD
    assert "sql" in result.missing_keywords or "sql" not in result.matched_keywords


def test_analyze_empty_resume() -> None:
    result = analyze(resume_text="", job_description="Python developer")
    assert result.overall_score == 0.0
    assert result.matched_keywords == []
    assert "python" in result.missing_keywords


def test_analyze_empty_target() -> None:
    result = analyze(resume_text="Python developer", job_description="")
    # No target keywords from empty JD -> score 0
    assert result.overall_score == 0.0


def test_analyze_synonym_python3_in_jd() -> None:
    resume = "I use Python daily."
    jd = "Requirements: Python3 and API skills."
    result = analyze(resume_text=resume, job_description=jd)
    assert "python" in result.matched_keywords or any(k.term == "python" for k in result.top_keywords)
    assert result.overall_score > 0
