"""Keyword extraction and ranking from text."""

from __future__ import annotations

from collections import Counter

from resume_analyzer.normalize import tokenize_without_stopwords

DEFAULT_TOP_N = 30
MIN_TOKEN_LEN = 2


def extract_keywords(text: str, top_n: int = DEFAULT_TOP_N) -> list[tuple[str, int]]:
    """
    Extract ranked keywords from text: tokenize, count, return top_n by frequency.
    Returns list of (term, count) sorted by count descending, then alphabetically.
    """
    if not text:
        return []
    tokens = tokenize_without_stopwords(text)
    tokens = [t for t in tokens if len(t) >= MIN_TOKEN_LEN]
    if not tokens:
        return []
    counts = Counter(tokens)
    # Sort by count desc, then term asc for stability.
    ranked = sorted(counts.items(), key=lambda x: (-x[1], x[0]))
    return ranked[:top_n]


def extract_keyword_set(text: str) -> set[str]:
    """All unique keywords (normalized) from text. Used for matching."""
    if not text:
        return set()
    tokens = tokenize_without_stopwords(text)
    return {t for t in tokens if len(t) >= MIN_TOKEN_LEN}
