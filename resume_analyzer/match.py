"""Matched and missing keywords (synonym-aware)."""

from __future__ import annotations

from resume_analyzer.synonyms import all_canonical_forms, normalize_for_match


def compute_matched_and_missing(
    resume_keywords: set[str],
    target_keywords: set[str],
) -> tuple[list[str], list[str]]:
    """
    Returns (matched_keywords, missing_keywords).
    Matched: target terms that have at least one synonym/variant in resume.
    Missing: target terms that have no match in resume.
    """
    matched: list[str] = []
    missing: list[str] = []
    for t in target_keywords:
        forms = all_canonical_forms(t)
        if any(f in resume_keywords or _resume_has_form(resume_keywords, forms) for f in forms):
            matched.append(normalize_for_match(t))
        else:
            missing.append(normalize_for_match(t))
    return (sorted(set(matched)), sorted(set(missing)))


def _resume_has_form(resume_keywords: set[str], target_forms: set[str]) -> bool:
    """True if any resume keyword is a synonym of any target form."""
    for r in resume_keywords:
        r_forms = all_canonical_forms(r)
        if r_forms & target_forms:
            return True
    return False
