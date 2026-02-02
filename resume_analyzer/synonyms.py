"""Synonym expansion for matching (e.g. Python ↔ Python 3, JS ↔ JavaScript)."""

from __future__ import annotations

# Canonical term -> set of variants (including canonical). Order matters for normalize_for_match (first wins).
SYNONYM_MAP: dict[str, set[str]] = {
    "python": {"python", "python3", "python 3"},
    "node.js": {"node.js", "nodejs", "javascript", "js"},
    "javascript": {"javascript", "js", "node.js", "nodejs"},
    "typescript": {"typescript", "ts"},
    "c#": {"c#", "csharp", ".net"},
    ".net": {".net", "c#", "csharp"},
    "react": {"react", "reactjs", "react.js"},
    "kubernetes": {"kubernetes", "k8s"},
    "machine learning": {"machine learning", "ml", "machine-learning", "machinelearning"},
    "machinelearning": {"machinelearning", "machine learning", "ml", "machine-learning"},
    "postgresql": {"postgresql", "postgres"},
    "mongodb": {"mongodb", "mongo"},
    "elasticsearch": {"elasticsearch", "elastic search"},
    "aws": {"aws", "amazon web services"},
    "gcp": {"gcp", "google cloud", "google cloud platform"},
}


def _build_term_to_canonical() -> dict[str, str]:
    """Map every variant to a canonical term (first in SYNONYM_MAP)."""
    out: dict[str, str] = {}
    for canonical, variants in SYNONYM_MAP.items():
        for v in variants:
            if v not in out:
                out[v] = canonical
    return out


_TERM_TO_CANONICAL = _build_term_to_canonical()


def expand_to_canonical(term: str) -> set[str]:
    """
    Return the set of canonical forms for this term (for matching).
    If term is a known variant, returns {canonical}. Otherwise returns {term}.
    """
    term_lower = term.lower().strip()
    canonical = _TERM_TO_CANONICAL.get(term_lower)
    if canonical is not None:
        return SYNONYM_MAP.get(canonical, {canonical}) | {term_lower}
    return {term_lower}


def all_canonical_forms(term: str) -> set[str]:
    """All forms that should count as a match for this term (term + synonyms)."""
    term_lower = term.lower().strip()
    canonical = _TERM_TO_CANONICAL.get(term_lower, term_lower)
    return SYNONYM_MAP.get(canonical, {canonical}) | {term_lower}


def sets_overlap(a: set[str], b: set[str]) -> bool:
    """True if any form of a matches any form of b (synonym-aware)."""
    for t in a:
        forms_a = all_canonical_forms(t)
        for s in b:
            forms_b = all_canonical_forms(s)
            if forms_a & forms_b:
                return True
    return False


def normalize_for_match(term: str) -> str:
    """Canonical form for display (e.g. 'nodejs' -> 'node.js')."""
    term_lower = term.lower().strip()
    return _TERM_TO_CANONICAL.get(term_lower, term_lower)
