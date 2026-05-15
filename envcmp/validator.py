"""Validate .env files against a reference schema or required key list."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set


@dataclass
class ValidationIssue:
    key: str
    message: str
    severity: str = "error"  # "error" | "warning"

    def __repr__(self) -> str:
        return f"ValidationIssue({self.severity}: {self.key!r} — {self.message})"


@dataclass
class ValidationResult:
    issues: List[ValidationIssue] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return not any(i.severity == "error" for i in self.issues)

    @property
    def errors(self) -> List[ValidationIssue]:
        return [i for i in self.issues if i.severity == "error"]

    @property
    def warnings(self) -> List[ValidationIssue]:
        return [i for i in self.issues if i.severity == "warning"]


class Validator:
    """Check an env dict against required keys and optional allowed-keys allowlist."""

    def __init__(
        self,
        required_keys: Optional[List[str]] = None,
        allowed_keys: Optional[List[str]] = None,
        warn_empty: bool = True,
    ) -> None:
        self.required_keys: Set[str] = set(required_keys or [])
        self.allowed_keys: Optional[Set[str]] = (
            set(allowed_keys) if allowed_keys is not None else None
        )
        self.warn_empty = warn_empty

    def validate(self, env: Dict[str, str]) -> ValidationResult:
        """Run all checks and return a ValidationResult."""
        result = ValidationResult()

        # Check required keys are present
        for key in sorted(self.required_keys):
            if key not in env:
                result.issues.append(
                    ValidationIssue(key=key, message="Required key is missing", severity="error")
                )

        for key, value in env.items():
            # Warn on empty values
            if self.warn_empty and value == "":
                result.issues.append(
                    ValidationIssue(key=key, message="Value is empty", severity="warning")
                )

            # Error on keys not in the allowlist
            if self.allowed_keys is not None and key not in self.allowed_keys:
                result.issues.append(
                    ValidationIssue(
                        key=key,
                        message="Key is not in the allowed keys list",
                        severity="error",
                    )
                )

        return result
