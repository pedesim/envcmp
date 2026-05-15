"""Tests for envcmp.exporter."""

from __future__ import annotations

import csv
import io
import json

import pytest

from envcmp.differ import DiffEntry, DiffResult, DiffStatus
from envcmp.exporter import Exporter


@pytest.fixture()
def result() -> DiffResult:
    entries = [
        DiffEntry(key="APP_ENV", status=DiffStatus.CHANGED, value_a="dev", value_b="prod"),
        DiffEntry(key="DB_HOST", status=DiffStatus.REMOVED, value_a="localhost", value_b=None),
        DiffEntry(key="NEW_KEY", status=DiffStatus.ADDED, value_a=None, value_b="hello"),
        DiffEntry(key="STABLE", status=DiffStatus.UNCHANGED, value_a="same", value_b="same"),
    ]
    return DiffResult(entries=entries)


@pytest.fixture()
def exporter(result) -> Exporter:
    return Exporter(result)


# ── JSON ──────────────────────────────────────────────────────────────────────

def test_json_excludes_unchanged_by_default(exporter):
    data = json.loads(exporter.to_json())
    keys = [row["key"] for row in data]
    assert "STABLE" not in keys


def test_json_includes_unchanged_when_requested(result):
    exp = Exporter(result, include_unchanged=True)
    data = json.loads(exp.to_json())
    keys = [row["key"] for row in data]
    assert "STABLE" in keys


def test_json_entry_has_expected_fields(exporter):
    data = json.loads(exporter.to_json())
    assert data[0].keys() == {"key", "status", "value_a", "value_b"}


def test_json_changed_entry_values(exporter):
    data = json.loads(exporter.to_json())
    changed = next(r for r in data if r["key"] == "APP_ENV")
    assert changed["value_a"] == "dev"
    assert changed["value_b"] == "prod"
    assert changed["status"] == "changed"


# ── CSV ───────────────────────────────────────────────────────────────────────

def test_csv_has_header(exporter):
    output = exporter.to_csv()
    assert output.splitlines()[0] == "key,status,value_a,value_b"


def test_csv_excludes_unchanged_by_default(exporter):
    output = exporter.to_csv()
    assert "STABLE" not in output


def test_csv_removed_entry_has_empty_value_b(exporter):
    reader = csv.DictReader(io.StringIO(exporter.to_csv()))
    removed = next(r for r in reader if r["key"] == "DB_HOST")
    assert removed["value_b"] == ""


# ── Markdown ──────────────────────────────────────────────────────────────────

def test_markdown_has_header_row(exporter):
    output = exporter.to_markdown()
    assert "| Key | Status | Value A | Value B |" in output


def test_markdown_excludes_unchanged_by_default(exporter):
    output = exporter.to_markdown()
    assert "STABLE" not in output


def test_markdown_contains_changed_key(exporter):
    output = exporter.to_markdown()
    assert "APP_ENV" in output


# ── dispatch ──────────────────────────────────────────────────────────────────

def test_export_dispatches_json(exporter):
    assert exporter.export("json") == exporter.to_json()


def test_export_dispatches_csv(exporter):
    assert exporter.export("csv") == exporter.to_csv()


def test_export_dispatches_markdown(exporter):
    assert exporter.export("markdown") == exporter.to_markdown()


def test_export_raises_on_unknown_format(exporter):
    with pytest.raises(ValueError, match="Unsupported format"):
        exporter.export("xml")
