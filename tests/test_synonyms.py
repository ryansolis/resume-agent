"""Tests for synonym expansion (Python/Python3, JS/JavaScript, .NET/C#, etc.)."""

import pytest

from resume_analyzer.synonyms import all_canonical_forms, expand_to_canonical, normalize_for_match, sets_overlap


@pytest.mark.parametrize(
    "term,expected_contains",
    [
        ("python", "python"),
        ("python3", "python"),
        ("Python 3", "python"),
        ("javascript", "javascript"),
        ("js", "javascript"),
        ("node.js", "node.js"),
        (".net", ".net"),
        ("c#", "c#"),
    ],
)
def test_expand_to_canonical(term: str, expected_contains: str) -> None:
    forms = expand_to_canonical(term)
    assert expected_contains in forms or term.lower() in forms


def test_python_python3_synonym() -> None:
    """Python and Python 3 should match via synonyms."""
    forms_python = all_canonical_forms("python")
    forms_python3 = all_canonical_forms("python3")
    assert forms_python & forms_python3


def test_js_javascript_synonym() -> None:
    forms_js = all_canonical_forms("js")
    forms_js_full = all_canonical_forms("javascript")
    assert forms_js & forms_js_full


def test_node_js_javascript_synonym() -> None:
    forms_node = all_canonical_forms("node.js")
    forms_js = all_canonical_forms("javascript")
    assert forms_node & forms_js


def test_sql_nosql_not_synonym() -> None:
    """SQL and NoSQL must NOT be synonyms."""
    forms_sql = all_canonical_forms("sql")
    forms_nosql = all_canonical_forms("nosql")
    assert not (forms_sql & forms_nosql)


def test_c_sharp_dot_net_synonym() -> None:
    forms_cs = all_canonical_forms("c#")
    forms_dotnet = all_canonical_forms(".net")
    assert forms_cs & forms_dotnet


def test_sets_overlap() -> None:
    assert sets_overlap({"python"}, {"python3"})
    assert sets_overlap({"javascript"}, {"js"})
    assert not sets_overlap({"sql"}, {"nosql"})
    assert sets_overlap({"c#"}, {".net"})


def test_normalize_for_match() -> None:
    assert normalize_for_match("nodejs") == "node.js"
    assert normalize_for_match("Python") == "python"
