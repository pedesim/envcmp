"""Tests for envcmp.validator."""

import pytest

from envcmp.validator import ValidationIssue, ValidationResult, Validator


# ---------------------------------------------------------------------------
# ValidationResult helpers
# ---------------------------------------------------------------------------

def test_result_is_valid_when_no_issues():
    result = ValidationResult()
    assert result.is_valid is True


def test_result_invalid_when_error_present():
    result = ValidationResult(issues=[ValidationIssue(key="FOO", message="missing", severity="error")])
    assert result.is_valid is False


def test_result_valid_when_only_warnings():
    result = ValidationResult(issues=[ValidationIssue(key="FOO", message="empty", severity="warning")])
    assert result.is_valid is True


def test_errors_and_warnings_filtered_correctly():
    issues = [
        ValidationIssue(key="A", message="err", severity="error"),
        ValidationIssue(key="B", message="warn", severity="warning"),
    ]
    result = ValidationResult(issues=issues)
    assert len(result.errors) == 1
    assert len(result.warnings) == 1


# ---------------------------------------------------------------------------
# Validator — required keys
# ---------------------------------------------------------------------------

def test_missing_required_key_is_error():
    v = Validator(required_keys=["DATABASE_URL"])
    result = v.validate({})
    assert not result.is_valid
    assert any(i.key == "DATABASE_URL" for i in result.errors)


def test_present_required_key_no_error():
    v = Validator(required_keys=["DATABASE_URL"])
    result = v.validate({"DATABASE_URL": "postgres://localhost/db"})
    assert result.is_valid


def test_multiple_missing_required_keys():
    v = Validator(required_keys=["A", "B", "C"])
    result = v.validate({"A": "1"})
    missing = {i.key for i in result.errors}
    assert missing == {"B", "C"}


# ---------------------------------------------------------------------------
# Validator — empty value warnings
# ---------------------------------------------------------------------------

def test_empty_value_produces_warning_by_default():
    v = Validator()
    result = v.validate({"FOO": ""})
    assert result.is_valid  # warning, not error
    assert any(i.key == "FOO" for i in result.warnings)


def test_empty_value_no_warning_when_disabled():
    v = Validator(warn_empty=False)
    result = v.validate({"FOO": ""})
    assert result.issues == []


# ---------------------------------------------------------------------------
# Validator — allowed keys
# ---------------------------------------------------------------------------

def test_unknown_key_is_error_when_allowlist_set():
    v = Validator(allowed_keys=["KNOWN"])
    result = v.validate({"KNOWN": "ok", "UNKNOWN": "bad"})
    assert not result.is_valid
    assert any(i.key == "UNKNOWN" for i in result.errors)


def test_all_keys_allowed_no_error():
    v = Validator(allowed_keys=["A", "B"])
    result = v.validate({"A": "1", "B": "2"})
    assert result.is_valid


def test_no_allowlist_does_not_flag_unknown_keys():
    v = Validator()
    result = v.validate({"ANYTHING": "value"})
    assert result.is_valid


# ---------------------------------------------------------------------------
# ValidationIssue repr
# ---------------------------------------------------------------------------

def test_issue_repr_contains_key_and_message():
    issue = ValidationIssue(key="SECRET", message="Required key is missing")
    r = repr(issue)
    assert "SECRET" in r
    assert "Required key is missing" in r
