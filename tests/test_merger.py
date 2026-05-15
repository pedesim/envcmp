"""Tests for envcmp.merger."""

import pytest

from envcmp.loader import EnvSource
from envcmp.merger import ConflictStrategy, MergeResult, merge


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _src(data: dict, label: str = "src") -> EnvSource:
    src = EnvSource(label=label)
    src.data = data
    return src


# ---------------------------------------------------------------------------
# Basic merging
# ---------------------------------------------------------------------------

def test_merge_disjoint_sources():
    base = _src({"A": "1"}, "base")
    other = _src({"B": "2"}, "other")
    result = merge(base, other)
    assert result.merged == {"A": "1", "B": "2"}


def test_merge_identical_sources():
    base = _src({"A": "1", "B": "2"})
    other = _src({"A": "1", "B": "2"})
    result = merge(base, other)
    assert result.merged == {"A": "1", "B": "2"}
    assert not result.has_conflicts


def test_added_keys_tracked():
    base = _src({"A": "1"})
    other = _src({"A": "1", "B": "2"})
    result = merge(base, other)
    assert "B" in result.added_keys


def test_removed_keys_tracked():
    base = _src({"A": "1", "B": "2"})
    other = _src({"A": "1"})
    result = merge(base, other)
    assert "B" in result.removed_keys


def test_removed_keys_excluded_when_flag_false():
    base = _src({"A": "1", "B": "2"})
    other = _src({"A": "1"})
    result = merge(base, other, include_removed=False)
    assert "B" not in result.merged


def test_removed_keys_included_by_default():
    base = _src({"A": "1", "B": "2"})
    other = _src({"A": "1"})
    result = merge(base, other)
    assert "B" in result.merged


# ---------------------------------------------------------------------------
# Conflict strategies
# ---------------------------------------------------------------------------

def test_conflict_detected():
    base = _src({"KEY": "old"})
    other = _src({"KEY": "new"})
    result = merge(base, other)
    assert result.has_conflicts
    assert result.conflicts["KEY"] == ("old", "new")


def test_use_base_strategy_keeps_base_value():
    base = _src({"KEY": "base_val"})
    other = _src({"KEY": "other_val"})
    result = merge(base, other, strategy=ConflictStrategy.USE_BASE)
    assert result.merged["KEY"] == "base_val"


def test_use_other_strategy_keeps_other_value():
    base = _src({"KEY": "base_val"})
    other = _src({"KEY": "other_val"})
    result = merge(base, other, strategy=ConflictStrategy.USE_OTHER)
    assert result.merged["KEY"] == "other_val"


def test_raise_strategy_raises_on_conflict():
    base = _src({"KEY": "base_val"})
    other = _src({"KEY": "other_val"})
    with pytest.raises(ValueError, match="Conflict on key 'KEY'"):
        merge(base, other, strategy=ConflictStrategy.RAISE)


def test_raise_strategy_does_not_raise_when_no_conflict():
    base = _src({"KEY": "same"})
    other = _src({"KEY": "same"})
    result = merge(base, other, strategy=ConflictStrategy.RAISE)
    assert result.merged["KEY"] == "same"


# ---------------------------------------------------------------------------
# MergeResult properties
# ---------------------------------------------------------------------------

def test_merge_result_has_conflicts_false_when_clean():
    result = MergeResult(merged={"A": "1"})
    assert not result.has_conflicts


def test_merge_result_has_conflicts_true_when_present():
    result = MergeResult(merged={}, conflicts={"X": ("a", "b")})
    assert result.has_conflicts
