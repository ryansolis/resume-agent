"""Tests for keyword extraction and ranking."""

import pytest

from resume_analyzer.extract import extract_keywords, extract_keyword_set


def test_extract_keywords_ranking() -> None:
    text = "python python api api api backend"
    ranked = extract_keywords(text, top_n=10)
    assert len(ranked) >= 2
    # api count 3, python count 2
    assert ranked[0][0] == "api"
    assert ranked[0][1] == 3
    assert ranked[1][0] == "python"
    assert ranked[1][1] == 2


def test_extract_keyword_set() -> None:
    text = "Python and API and python"
    s = extract_keyword_set(text)
    assert "python" in s
    assert "api" in s
    assert len(s) == 2


def test_extract_empty() -> None:
    assert extract_keywords("") == []
    assert extract_keyword_set("") == set()


def test_extract_special_tokens_preserved() -> None:
    text = "C++ Node.js .NET developer"
    s = extract_keyword_set(text)
    assert "c++" in s
    assert "node.js" in s
    assert ".net" in s
    assert "developer" in s
