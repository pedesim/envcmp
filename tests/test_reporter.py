"""Tests for envcmp.reporter."""

from __future__ import annotations

import io

import pytest

from envcmp.differ import diff
from envcmp.masker import SecretMasker
from envcmp.reporter import Reporter


@pytest.fixture()
def reporter() -> Reporter:
    return Reporter(color=False, show_unchanged=False)


def _render(reporter: Reporter, base: dict, target: dict) -> str:
    """Diff base vs target and return the rendered output as a string."""
    result = diff(base, target)
    stream = io.StringIO()
    reporter.render(result, stream)
    return stream.getvalue()


def test_added_key_shown(reporter):
    output = _render(reporter, {}, {"NEW_KEY": "value"})
    assert "+ NEW_KEY=value" in output


def test_removed_key_shown(reporter):
    output = _render(reporter, {"OLD_KEY": "value"}, {})
    assert "- OLD_KEY=value" in output


def test_changed_key_shown(reporter):
    output = _render(reporter, {"KEY": "old"}, {"KEY": "new"})
    assert "~ KEY" in output
    assert "'old'" in output
    assert "'new'" in output


def test_unchanged_hidden_by_default(reporter):
    output = _render(reporter, {"KEY": "same"}, {"KEY": "same"})
    assert "KEY" not in output
    assert "No differences found." in output


def test_unchanged_shown_when_requested():
    r = Reporter(color=False, show_unchanged=True)
    output = _render(r, {"KEY": "same"}, {"KEY": "same"})
    assert "  KEY=same" in output


def test_secret_value_masked(reporter):
    output = _render(reporter, {}, {"DB_PASSWORD": "supersecret"})
    assert "supersecret" not in output
    assert "***" in output


def test_no_differences_message(reporter):
    output = _render(reporter, {"A": "1"}, {"A": "1"})
    assert "No differences found." in output


def test_summary_counts():
    r = Reporter(color=False)
    result = diff({"OLD": "x"}, {"NEW": "y"})
    stream = io.StringIO()
    r.summary(result, stream)
    text = stream.getvalue()
    assert "1 added" in text
    assert "1 removed" in text
    assert "0 changed" in text


def test_color_codes_present_when_enabled():
    r = Reporter(color=True, show_unchanged=False)
    output = _render(r, {}, {"ADDED": "val"})
    assert "\033[" in output


def test_color_codes_absent_when_disabled(reporter):
    output = _render(reporter, {}, {"ADDED": "val"})
    assert "\033[" not in output


def test_keys_sorted_alphabetically(reporter):
    output = _render(reporter, {}, {"ZEBRA": "1", "ALPHA": "2", "MIDDLE": "3"})
    positions = {key: output.index(key) for key in ("ALPHA", "MIDDLE", "ZEBRA")}
    assert positions["ALPHA"] < positions["MIDDLE"] < positions["ZEBRA"]


def test_changed_key_secret_masked(reporter):
    """Changed secret values should be masked in both old and new positions."""
    output = _render(reporter, {"DB_PASSWORD": "old_secret"}, {"DB_PASSWORD": "new_secret"})
    assert "old_secret" not in output
    assert "new_secret" not in output
    assert "***" in output
