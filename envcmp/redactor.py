"""Redactor: produce a sanitized copy of an env dict with secrets replaced.

Builds on SecretMasker to provide a higher-level API that returns a new
dictionary (never mutates the original) and records which keys were redacted.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from envcmp.masker import SecretMasker


@dataclass
class RedactResult:
    """Outcome of a redaction pass over an env dictionary."""

    data: Dict[str, str]
    """The sanitized key/value pairs."""

    redacted_keys: List[str] = field(default_factory=list)
    """Keys whose values were replaced with the mask placeholder."""

    @property
    def redacted_count(self) -> int:
        return len(self.redacted_keys)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"RedactResult(redacted={self.redacted_count}, "
            f"total={len(self.data)})"
        )


class Redactor:
    """Sanitize an env mapping, masking secret values."""

    def __init__(self, masker: SecretMasker | None = None) -> None:
        self._masker = masker or SecretMasker()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def redact(self, env: Dict[str, str]) -> RedactResult:
        """Return a :class:`RedactResult` with secrets masked.

        The original *env* mapping is never modified.
        """
        sanitized: Dict[str, str] = {}
        redacted_keys: List[str] = []

        for key, value in env.items():
            if self._masker.is_secret(key):
                sanitized[key] = self._masker.mask(key, value)
                redacted_keys.append(key)
            else:
                sanitized[key] = value

        return RedactResult(data=sanitized, redacted_keys=sorted(redacted_keys))

    def redact_to_dict(self, env: Dict[str, str]) -> Dict[str, str]:
        """Convenience wrapper — return only the sanitized dictionary."""
        return self.redact(env).data
