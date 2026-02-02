"""Tests for API input validation (max length, empty body, missing target)."""

from __future__ import annotations

from fastapi.testclient import TestClient

from api.main import (
    MAX_JOB_DESCRIPTION_LENGTH,
    MAX_KEYWORD_LENGTH,
    MAX_KEYWORDS_ITEMS,
    MAX_RESUME_LENGTH,
    app,
)

client = TestClient(app)


def test_analyze_empty_resume_rejected() -> None:
    """Empty or whitespace-only resume_text must return 422 or 400."""
    resp = client.post(
        "/analyze",
        json={"resume_text": "", "job_description": "Python required"},
    )
    assert resp.status_code in (400, 422)
    assert "resume" in resp.text.lower()


def test_analyze_whitespace_resume_rejected() -> None:
    resp = client.post(
        "/analyze",
        json={"resume_text": "   \n\t  ", "job_description": "Python"},
    )
    assert resp.status_code in (400, 422)


def test_analyze_missing_target_rejected() -> None:
    """No job_description, role_title, or keywords must return 400."""
    resp = client.post(
        "/analyze",
        json={"resume_text": "Python developer", "job_description": None, "role_title": None, "keywords": None},
    )
    assert resp.status_code == 400
    assert "at least one" in resp.text.lower() or "job_description" in resp.text.lower()


def test_analyze_empty_job_and_keywords_rejected() -> None:
    """job_description empty string and keywords [] should still require at least one non-empty target."""
    resp = client.post(
        "/analyze",
        json={"resume_text": "Python", "job_description": "", "keywords": []},
    )
    assert resp.status_code == 400


def test_analyze_valid_request_succeeds() -> None:
    resp = client.post(
        "/analyze",
        json={"resume_text": "Python developer", "job_description": "Python and API"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "result" in data
    assert "readable_summary" in data
    assert "overall_score" in data["result"]


def test_analyze_resume_over_max_length_rejected() -> None:
    """Resume text over MAX_RESUME_LENGTH must return 422."""
    long_resume = "x" * (MAX_RESUME_LENGTH + 1)
    resp = client.post(
        "/analyze",
        json={"resume_text": long_resume, "job_description": "Python"},
    )
    assert resp.status_code == 422


def test_analyze_job_over_max_length_rejected() -> None:
    long_jd = "y" * (MAX_JOB_DESCRIPTION_LENGTH + 1)
    resp = client.post(
        "/analyze",
        json={"resume_text": "Python", "job_description": long_jd},
    )
    assert resp.status_code == 422


def test_analyze_keywords_over_max_items_rejected() -> None:
    keywords = ["python"] * (MAX_KEYWORDS_ITEMS + 1)
    resp = client.post(
        "/analyze",
        json={"resume_text": "Python", "keywords": keywords},
    )
    assert resp.status_code == 422


def test_analyze_keyword_over_max_length_rejected() -> None:
    long_keyword = "a" * (MAX_KEYWORD_LENGTH + 1)
    resp = client.post(
        "/analyze",
        json={"resume_text": "Python", "keywords": [long_keyword]},
    )
    assert resp.status_code == 422
