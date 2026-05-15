"""Audit .env files for common security and quality issues."""

from dataclasses import dataclass, field
from typing import List, Dict
from envcmp.masker import SecretMasker


@dataclass
class AuditFinding:
    key: str
    severity: str  # 'error', 'warning', 'info'
    message: str

    def __repr__(self) -> str:
        return f"AuditFinding(key={self.key!r}, severity={self.severity!r}, message={self.message!r})"


@dataclass
class AuditReport:
    findings: List[AuditFinding] = field(default_factory=list)

    @property
    def errors(self) -> List[AuditFinding]:
        return [f for f in self.findings if f.severity == "error"]

    @property
    def warnings(self) -> List[AuditFinding]:
        return [f for f in self.findings if f.severity == "warning"]

    @property
    def is_clean(self) -> bool:
        return len(self.errors) == 0 and len(self.warnings) == 0


class Auditor:
    """Audits a parsed env dict for security and quality issues."""

    EMPTY_SECRET_MSG = "Secret key has an empty value — may indicate a misconfiguration."
    PLACEHOLDER_PATTERNS = ("changeme", "todo", "fixme", "replace", "example", "your_")

    def __init__(self, masker: SecretMasker = None):
        self._masker = masker or SecretMasker()

    def audit(self, env: Dict[str, str]) -> AuditReport:
        report = AuditReport()
        for key, value in env.items():
            self._check_empty_secret(report, key, value)
            self._check_placeholder(report, key, value)
            self._check_whitespace_value(report, key, value)
        return report

    def _check_empty_secret(self, report: AuditReport, key: str, value: str) -> None:
        if self._masker.is_secret(key) and value.strip() == "":
            report.findings.append(
                AuditFinding(key=key, severity="error", message=self.EMPTY_SECRET_MSG)
            )

    def _check_placeholder(self, report: AuditReport, key: str, value: str) -> None:
        lower_val = value.lower()
        for pattern in self.PLACEHOLDER_PATTERNS:
            if pattern in lower_val:
                report.findings.append(
                    AuditFinding(
                        key=key,
                        severity="warning",
                        message=f"Value looks like a placeholder (contains {pattern!r}).",
                    )
                )
                break

    def _check_whitespace_value(self, report: AuditReport, key: str, value: str) -> None:
        if value != value.strip() and value.strip() != "":
            report.findings.append(
                AuditFinding(
                    key=key,
                    severity="warning",
                    message="Value contains leading or trailing whitespace.",
                )
            )
