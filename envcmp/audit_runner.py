"""Convenience runner that loads an env source and returns an AuditReport."""

from dataclasses import dataclass
from typing import Optional

from envcmp.loader import EnvSource, load_from_file, load_from_string
from envcmp.auditor import Auditor, AuditReport
from envcmp.masker import SecretMasker


@dataclass
class AuditRunConfig:
    """Configuration for an audit run."""
    source: EnvSource
    extra_secret_patterns: Optional[list] = None


def run_audit(config: AuditRunConfig) -> AuditReport:
    """Run an audit against the given EnvSource and return an AuditReport."""
    patterns = config.extra_secret_patterns or []
    masker = SecretMasker(extra_patterns=patterns) if patterns else SecretMasker()
    auditor = Auditor(masker=masker)
    return auditor.audit(config.source.data)


def audit_file(path: str, label: Optional[str] = None, extra_secret_patterns: Optional[list] = None) -> AuditReport:
    """Load an env file and audit it."""
    source = load_from_file(path, label=label)
    config = AuditRunConfig(source=source, extra_secret_patterns=extra_secret_patterns)
    return run_audit(config)


def audit_string(text: str, label: Optional[str] = None, extra_secret_patterns: Optional[list] = None) -> AuditReport:
    """Parse an env string and audit it."""
    source = load_from_string(text, label=label)
    config = AuditRunConfig(source=source, extra_secret_patterns=extra_secret_patterns)
    return run_audit(config)


def format_audit_report(report: AuditReport, use_color: bool = False) -> str:
    """Render an AuditReport as a human-readable string."""
    if report.is_clean:
        return "Audit passed — no issues found.\n"

    lines = []
    severity_prefix = {
        "error": "[ERROR]  ",
        "warning": "[WARN]   ",
        "info": "[INFO]   ",
    }
    color_map = {
        "error": "\033[31m",
        "warning": "\033[33m",
        "info": "\033[36m",
    }
    reset = "\033[0m"

    for finding in report.findings:
        prefix = severity_prefix.get(finding.severity, "[?]      ")
        line = f"{prefix}{finding.key}: {finding.message}"
        if use_color:
            color = color_map.get(finding.severity, "")
            line = f"{color}{line}{reset}"
        lines.append(line)

    summary = f"\n{len(report.errors)} error(s), {len(report.warnings)} warning(s).\n"
    lines.append(summary)
    return "\n".join(lines)
