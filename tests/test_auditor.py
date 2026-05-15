"""Tests for envcmp.auditor."""

import pytest
from envcmp.auditor import Auditor, AuditFinding, AuditReport
from envcmp.masker import SecretMasker


@pytest.fixture
def auditor():
    return Auditor()


# --- AuditReport helpers ---

def test_report_is_clean_when_no_findings():
    report = AuditReport()
    assert report.is_clean is True


def test_report_not_clean_with_error():
    report = AuditReport(findings=[AuditFinding("KEY", "error", "bad")])
    assert report.is_clean is False


def test_report_not_clean_with_warning():
    report = AuditReport(findings=[AuditFinding("KEY", "warning", "meh")])
    assert report.is_clean is False


def test_errors_filtered_correctly():
    findings = [
        AuditFinding("A", "error", "e"),
        AuditFinding("B", "warning", "w"),
        AuditFinding("C", "info", "i"),
    ]
    report = AuditReport(findings=findings)
    assert len(report.errors) == 1
    assert report.errors[0].key == "A"


def test_warnings_filtered_correctly():
    findings = [
        AuditFinding("A", "error", "e"),
        AuditFinding("B", "warning", "w"),
    ]
    report = AuditReport(findings=findings)
    assert len(report.warnings) == 1
    assert report.warnings[0].key == "B"


# --- Empty secret detection ---

def test_empty_secret_raises_error(auditor):
    report = auditor.audit({"DB_PASSWORD": ""})
    assert any(f.key == "DB_PASSWORD" and f.severity == "error" for f in report.findings)


def test_non_secret_empty_value_no_error(auditor):
    report = auditor.audit({"APP_NAME": ""})
    assert not any(f.severity == "error" for f in report.findings)


def test_secret_with_value_no_empty_error(auditor):
    report = auditor.audit({"DB_PASSWORD": "s3cr3t"})
    assert not any(f.severity == "error" for f in report.findings)


# --- Placeholder detection ---

def test_changeme_placeholder_warning(auditor):
    report = auditor.audit({"APP_KEY": "changeme"})
    assert any(f.key == "APP_KEY" and f.severity == "warning" for f in report.findings)


def test_todo_placeholder_warning(auditor):
    report = auditor.audit({"WEBHOOK_URL": "TODO"})
    assert any(f.severity == "warning" for f in report.findings)


def test_normal_value_no_placeholder_warning(auditor):
    report = auditor.audit({"APP_ENV": "production"})
    assert not any(f.severity == "warning" for f in report.findings)


# --- Whitespace detection ---

def test_leading_whitespace_warning(auditor):
    report = auditor.audit({"HOST": "  localhost"})
    assert any(f.key == "HOST" and f.severity == "warning" for f in report.findings)


def test_trailing_whitespace_warning(auditor):
    report = auditor.audit({"HOST": "localhost  "})
    assert any(f.key == "HOST" and f.severity == "warning" for f in report.findings)


def test_clean_value_no_whitespace_warning(auditor):
    report = auditor.audit({"HOST": "localhost"})
    assert not any(f.severity == "warning" for f in report.findings)


# --- AuditFinding repr ---

def test_finding_repr():
    f = AuditFinding(key="KEY", severity="error", message="bad")
    assert "KEY" in repr(f)
    assert "error" in repr(f)
