"""Tests for envcmp.formatter."""

from __future__ import annotations

import csv
import io
import json

import pytest

from envcmp.differ import DiffEntry, DiffResult, DiffStatus
from envcmp.formatter import Formatter


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def simple_result() -> DiffResult:
    return DiffResult(
        entries=[
            DiffEntry(key="ADDED_KEY", status=DiffStatus.ADDED, value_a=None, value_b="new"),
            DiffEntry(key="REMOVED_KEY", status=DiffStatus.REMOVED, value_a="old", value_b=None),
            DiffEntry(key="CHANGED_KEY", status=DiffStatus.CHANGED, value_a="v1", value_b="v2"),
            DiffEntry(key="SAME_KEY", status=DiffStatus.UNCHANGED, value_a="x", value_b="x"),
        ]
    )


# ---------------------------------------------------------------------------
# JSON format
# ---------------------------------------------------------------------------

def test_json_excludes_unchanged_by_default(simple_result):
    fmt = Formatter(fmt="json")
    data = json.loads(fmt.render(simple_result))
    keys = [row["key"] for row in data]
    assert "SAME_KEY" not in keys


def test_json_includes_unchanged_when_requested(simple_result):
    fmt = Formatter(fmt="json", include_unchanged=True)
    data = json.loads(fmt.render(simple_result))
    keys = [row["key"] for row in data]
    assert "SAME_KEY" in keys


def test_json_contains_all_changed_entries(simple_result):
    fmt = Formatter(fmt="json")
    data = json.loads(fmt.render(simple_result))
    statuses = {row["status"] for row in data}
    assert statuses == {"added", "removed", "changed"}


def test_json_entry_has_expected_fields(simple_result):
    fmt = Formatter(fmt="json")
    data = json.loads(fmt.render(simple_result))
    assert all({"key", "status", "value_a", "value_b"} <= row.keys() for row in data)


def test_json_added_entry_value_a_is_none(simple_result):
    fmt = Formatter(fmt="json")
    data = json.loads(fmt.render(simple_result))
    added = next(r for r in data if r["key"] == "ADDED_KEY")
    assert added["value_a"] is None
    assert added["value_b"] == "new"


# ---------------------------------------------------------------------------
# CSV format
# ---------------------------------------------------------------------------

def test_csv_has_header_row(simple_result):
    fmt = Formatter(fmt="csv")
    first_line = fmt.render(simple_result).splitlines()[0]
    assert first_line == "key,status,value_a,value_b"


def test_csv_excludes_unchanged_by_default(simple_result):
    fmt = Formatter(fmt="csv")
    output = fmt.render(simple_result)
    assert "SAME_KEY" not in output


def test_csv_row_count_matches_visible_entries(simple_result):
    fmt = Formatter(fmt="csv")
    reader = csv.DictReader(io.StringIO(fmt.render(simple_result)))
    rows = list(reader)
    assert len(rows) == 3  # added + removed + changed


def test_csv_includes_unchanged_when_requested(simple_result):
    fmt = Formatter(fmt="csv", include_unchanged=True)
    output = fmt.render(simple_result)
    assert "SAME_KEY" in output


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def test_invalid_format_raises():
    with pytest.raises(ValueError, match="Unsupported format"):
        Formatter(fmt="xml")  # type: ignore[arg-type]
