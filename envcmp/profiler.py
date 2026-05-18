"""Profile an env source: summarise key statistics and patterns."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from envcmp.loader import EnvSource
from envcmp.masker import SecretMasker


@dataclass
class ProfileReport:
    label: str
    total_keys: int
    secret_keys: List[str] = field(default_factory=list)
    empty_keys: List[str] = field(default_factory=list)
    duplicate_keys: List[str] = field(default_factory=list)
    key_lengths: Dict[str, int] = field(default_factory=dict)

    @property
    def secret_count(self) -> int:
        return len(self.secret_keys)

    @property
    def empty_count(self) -> int:
        return len(self.empty_keys)

    def summary(self) -> str:
        lines = [
            f"Profile: {self.label}",
            f"  Total keys   : {self.total_keys}",
            f"  Secret keys  : {self.secret_count}",
            f"  Empty keys   : {self.empty_count}",
            f"  Duplicate keys: {len(self.duplicate_keys)}",
        ]
        if self.empty_keys:
            lines.append(f"  Empty        : {', '.join(self.empty_keys)}")
        if self.duplicate_keys:
            lines.append(f"  Duplicates   : {', '.join(self.duplicate_keys)}")
        return "\n".join(lines)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"ProfileReport(label={self.label!r}, total={self.total_keys}, "
            f"secrets={self.secret_count}, empty={self.empty_count})"
        )


def profile(source: EnvSource, masker: SecretMasker | None = None) -> ProfileReport:
    """Build a ProfileReport for the given EnvSource."""
    if masker is None:
        masker = SecretMasker()

    env = source.data
    seen: Dict[str, int] = {}
    for key in env:
        seen[key] = seen.get(key, 0) + 1

    duplicate_keys = [k for k, count in seen.items() if count > 1]
    secret_keys = [k for k in env if masker.is_secret(k)]
    empty_keys = [k for k, v in env.items() if v == ""]
    key_lengths = {k: len(v) for k, v in env.items()}

    return ProfileReport(
        label=source.label,
        total_keys=len(env),
        secret_keys=secret_keys,
        empty_keys=empty_keys,
        duplicate_keys=duplicate_keys,
        key_lengths=key_lengths,
    )
