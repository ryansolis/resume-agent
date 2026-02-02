"""Tests for normalization and tokenization (C++, Node.js, .NET, SQL, NoSQL, etc.)."""

import pytest

from resume_analyzer.normalize import normalize_text, tokenize, tokenize_without_stopwords


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("", ""),
        ("  hello   world  ", "hello world"),
        ("Hello World", "hello world"),
        ("C++", "c++"),
        ("Node.js", "node.js"),
        (".NET", ".net"),
        ("SQL", "sql"),
        ("NoSQL", "nosql"),
    ],
)
def test_normalize_text(raw: str, expected: str) -> None:
    assert normalize_text(raw) == expected


def test_normalize_empty_and_none() -> None:
    assert normalize_text("") == ""
    assert normalize_text("   ") == ""


@pytest.mark.parametrize(
    "text,expected_tokens",
    [
        ("C++ developer", ["c++", "developer"]),
        ("Node.js and JavaScript", ["node.js", "javascript"]),
        (".NET framework", [".net", "framework"]),
        ("SQL and NoSQL databases", ["sql", "nosql", "databases"]),
        ("Python Python3 python", ["python", "python", "python"]),
        ("I use nodejs daily", ["node.js", "daily"]),
        ("PYTHON", ["python"]),
        ("  extra   spaces  ", ["extra", "spaces"]),
        ("REST API", ["rest", "api"]),
        ("HTML CSS JSON", ["html", "css", "json"]),
    ],
)
def test_tokenize_special_tech_terms(text: str, expected_tokens: list[str]) -> None:
    got = tokenize(text)
    assert got == expected_tokens


def test_tokenize_sql_vs_nosql_distinct() -> None:
    """SQL and NoSQL must remain distinct (not synonyms)."""
    assert "sql" in tokenize("SQL")
    assert "nosql" in tokenize("NoSQL")
    assert tokenize("SQL") != tokenize("NoSQL")


def test_tokenize_c_plus_plus_single_token() -> None:
    assert tokenize("C++") == ["c++"]
    assert tokenize("experienced in C++") == ["experienced", "c++"]


def test_tokenize_node_dot_js_single_token() -> None:
    assert tokenize("Node.js") == ["node.js"]
    assert "node.js" in tokenize("Node.js backend")


def test_tokenize_dot_net_single_token() -> None:
    assert tokenize(".NET") == [".net"]
    assert ".net" in tokenize("C# and .NET")


def test_tokenize_empty() -> None:
    assert tokenize("") == []
    assert tokenize("   ") == []


def test_tokenize_stopwords_removed_in_tokenize_without_stopwords() -> None:
    # tokenize() still may include stopwords in some edge paths; tokenize_without_stopwords filters.
    toks = tokenize_without_stopwords("the python and the api")
    assert "the" not in toks
    assert "and" not in toks
    assert "python" in toks
    assert "api" in toks
