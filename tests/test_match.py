"""Tests for matched/missing keyword logic (synonym-aware)."""

import pytest

from resume_analyzer.match import compute_matched_and_missing


def test_all_matched() -> None:
    resume = {"python", "api", "sql"}
    target = {"python", "api", "sql"}
    matched, missing = compute_matched_and_missing(resume, target)
    assert set(matched) == {"python", "api", "sql"}
    assert missing == []


def test_all_missing() -> None:
    resume = {"python"}
    target = {"java", "go", "rust"}
    matched, missing = compute_matched_and_missing(resume, target)
    assert matched == []
    assert set(missing) == {"go", "java", "rust"}


def test_synonym_python_python3() -> None:
    resume = {"python"}
    target = {"python3"}
    matched, missing = compute_matched_and_missing(resume, target)
    assert "python" in matched
    assert "python3" not in missing


def test_synonym_js_javascript() -> None:
    resume = {"javascript"}
    target = {"js"}
    matched, missing = compute_matched_and_missing(resume, target)
    assert len(matched) >= 1
    assert "js" not in missing or "javascript" in matched


def test_sql_nosql_not_matched() -> None:
    """SQL in target, NoSQL in resume: must not count as match."""
    resume = {"nosql"}
    target = {"sql"}
    matched, missing = compute_matched_and_missing(resume, target)
    assert "sql" in missing
    assert "sql" not in matched


def test_empty_target() -> None:
    resume = {"python"}
    target: set[str] = set()
    matched, missing = compute_matched_and_missing(resume, target)
    assert matched == []
    assert missing == []


def test_empty_resume() -> None:
    resume: set[str] = set()
    target = {"python", "api"}
    matched, missing = compute_matched_and_missing(resume, target)
    assert matched == []
    assert set(missing) == {"api", "python"}
