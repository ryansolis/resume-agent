"""Deterministic scoring and confidence notes."""

from __future__ import annotations


def compute_score(
    matched_count: int,
    target_count: int,
) -> tuple[float, dict[str, float | int], list[str]]:
    """
    Deterministic score 0–100 and confidence notes.
    Formula: (matched_count / max(1, target_count)) * 100, capped at 100.
    """
    ratio = matched_count / max(1, target_count)
    score = min(100.0, round(ratio * 100, 1))
    breakdown: dict[str, float | int | str] = {
        "matched_count": matched_count,
        "target_count": target_count,
        "formula": "score = (matched_count / max(1, target_count)) * 100, capped at 100",
    }
    notes: list[str] = []
    if target_count == 0:
        notes.append("No target keywords provided; score is 0.")
    elif matched_count == 0:
        notes.append("No keyword overlap; consider adding relevant skills to resume.")
    else:
        if ratio >= 0.8:
            notes.append("Strong overlap with target keywords.")
        elif ratio >= 0.5:
            notes.append("Moderate match; some important terms may be missing.")
        else:
            notes.append("Low overlap; many target keywords are missing from resume.")
    if target_count > 0 and target_count < 5:
        notes.append("Few target keywords were used; score may be more volatile.")
    return (score, breakdown, notes)
