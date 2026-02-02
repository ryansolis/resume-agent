"""Tests for deterministic scoring and confidence notes."""

import pytest

from resume_analyzer.score import compute_score


def test_score_full_match() -> None:
    score, breakdown, notes = compute_score(matched_count=10, target_count=10)
    assert score == 100.0
    assert breakdown["matched_count"] == 10
    assert breakdown["target_count"] == 10
    assert any("Strong" in n for n in notes)


def test_score_half_match() -> None:
    score, breakdown, notes = compute_score(matched_count=5, target_count=10)
    assert score == 50.0
    assert any("Moderate" in n or "overlap" in n.lower() for n in notes)


def test_score_zero_match() -> None:
    score, breakdown, notes = compute_score(matched_count=0, target_count=10)
    assert score == 0.0
    assert any("No keyword overlap" in n for n in notes)


def test_score_zero_target() -> None:
    score, breakdown, notes = compute_score(matched_count=0, target_count=0)
    assert score == 0.0
    assert any("No target keywords" in n for n in notes)


def test_score_deterministic() -> None:
    s1, _, _ = compute_score(7, 10)
    s2, _, _ = compute_score(7, 10)
    assert s1 == s2 == 70.0


def test_score_capped_at_100() -> None:
    # If we pass more matched than target (shouldn't happen in practice), cap at 100
    score, _, _ = compute_score(matched_count=15, target_count=10)
    assert score == 100.0
