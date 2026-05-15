"""Tests for envcmp.pipeline."""

from __future__ import annotations

import pytest

from envcmp.differ import DiffStatus
from envcmp.loader import load_from_string
from envcmp.pipeline import PipelineConfig, run


@pytest.fixture()
def source_a():
    return load_from_string(
        "APP_ENV=staging\nDB_PASSWORD=secret123\nFEATURE_X=true\n",
        label="staging",
    )


@pytest.fixture()
def source_b():
    return load_from_string(
        "APP_ENV=production\nDB_PASSWORD=hunter2\nNEW_KEY=added\n",
        label="production",
    )


class TestRunDefaults:
    def test_returns_pipeline_result(self, source_a, source_b):
        result = run(source_a, source_b)
        assert result.diff is not None
        assert isinstance(result.report, str)

    def test_changed_key_in_diff(self, source_a, source_b):
        result = run(source_a, source_b)
        statuses = {e.key: e.status for e in result.diff.entries}
        assert statuses["APP_ENV"] == DiffStatus.CHANGED

    def test_added_key_in_diff(self, source_a, source_b):
        result = run(source_a, source_b)
        statuses = {e.key: e.status for e in result.diff.entries}
        assert statuses["NEW_KEY"] == DiffStatus.ADDED

    def test_removed_key_in_diff(self, source_a, source_b):
        result = run(source_a, source_b)
        statuses = {e.key: e.status for e in result.diff.entries}
        assert statuses["FEATURE_X"] == DiffStatus.REMOVED


class TestSecretMasking:
    def test_password_masked_in_diff(self, source_a, source_b):
        result = run(source_a, source_b, PipelineConfig(mask_secrets=True))
        entry = next(e for e in result.diff.entries if e.key == "DB_PASSWORD")
        assert entry.value_a != "secret123"
        assert entry.value_b != "hunter2"

    def test_masking_disabled_shows_values(self, source_a, source_b):
        result = run(source_a, source_b, PipelineConfig(mask_secrets=False))
        entry = next(e for e in result.diff.entries if e.key == "DB_PASSWORD")
        assert entry.value_a == "secret123"
        assert entry.value_b == "hunter2"


class TestReportContent:
    def test_report_contains_added_key(self, source_a, source_b):
        result = run(source_a, source_b, PipelineConfig(color=False))
        assert "NEW_KEY" in result.report

    def test_report_contains_labels(self, source_a, source_b):
        result = run(source_a, source_b, PipelineConfig(color=False))
        assert "staging" in result.report
        assert "production" in result.report

    def test_unchanged_hidden_by_default(self, source_a, source_b):
        same = load_from_string("SHARED=value\n", label="a")
        same2 = load_from_string("SHARED=value\n", label="b")
        result = run(same, same2, PipelineConfig(color=False, show_unchanged=False))
        assert "SHARED" not in result.report

    def test_unchanged_shown_when_requested(self, source_a, source_b):
        same = load_from_string("SHARED=value\n", label="a")
        same2 = load_from_string("SHARED=value\n", label="b")
        result = run(same, same2, PipelineConfig(color=False, show_unchanged=True))
        assert "SHARED" in result.report


class TestExtraSecretPatterns:
    def test_extra_pattern_masks_value(self):
        src_a = load_from_string("CUSTOM_CRED=abc123\n", label="a")
        src_b = load_from_string("CUSTOM_CRED=xyz789\n", label="b")
        cfg = PipelineConfig(mask_secrets=True, extra_secret_patterns=["cred"])
        result = run(src_a, src_b, cfg)
        entry = next(e for e in result.diff.entries if e.key == "CUSTOM_CRED")
        assert entry.value_a != "abc123"
