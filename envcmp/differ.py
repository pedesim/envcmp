"""Diff two parsed .env dictionaries and report differences."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class DiffStatus(str, Enum):
    ADDED = "added"
    REMOVED = "removed"
    CHANGED = "changed"
    UNCHANGED = "unchanged"


@dataclass
class DiffEntry:
    key: str
    status: DiffStatus
    value_a: Optional[str] = None
    value_b: Optional[str] = None

    def __repr__(self) -> str:
        if self.status == DiffStatus.ADDED:
            return f"[+] {self.key}={self.value_b}"
        if self.status == DiffStatus.REMOVED:
            return f"[-] {self.key}={self.value_a}"
        if self.status == DiffStatus.CHANGED:
            return f"[~] {self.key}: {self.value_a!r} -> {self.value_b!r}"
        return f"[ ] {self.key}={self.value_a}"


@dataclass
class DiffResult:
    entries: List[DiffEntry] = field(default_factory=list)

    @property
    def added(self) -> List[DiffEntry]:
        return [e for e in self.entries if e.status == DiffStatus.ADDED]

    @property
    def removed(self) -> List[DiffEntry]:
        return [e for e in self.entries if e.status == DiffStatus.REMOVED]

    @property
    def changed(self) -> List[DiffEntry]:
        return [e for e in self.entries if e.status == DiffStatus.CHANGED]

    @property
    def unchanged(self) -> List[DiffEntry]:
        return [e for e in self.entries if e.status == DiffStatus.UNCHANGED]

    @property
    def has_differences(self) -> bool:
        return bool(self.added or self.removed or self.changed)


def diff_envs(
    env_a: Dict[str, str],
    env_b: Dict[str, str],
    include_unchanged: bool = False,
) -> DiffResult:
    """Compare two env dictionaries and return a DiffResult.

    Args:
        env_a: Baseline environment mapping (e.g. production).
        env_b: Target environment mapping (e.g. staging).
        include_unchanged: When True, unchanged keys are included in result.

    Returns:
        A DiffResult containing all detected DiffEntry items.
    """
    result = DiffResult()
    all_keys = sorted(set(env_a) | set(env_b))

    for key in all_keys:
        in_a = key in env_a
        in_b = key in env_b

        if in_a and not in_b:
            result.entries.append(DiffEntry(key, DiffStatus.REMOVED, value_a=env_a[key]))
        elif in_b and not in_a:
            result.entries.append(DiffEntry(key, DiffStatus.ADDED, value_b=env_b[key]))
        elif env_a[key] != env_b[key]:
            result.entries.append(
                DiffEntry(key, DiffStatus.CHANGED, value_a=env_a[key], value_b=env_b[key])
            )
        elif include_unchanged:
            result.entries.append(
                DiffEntry(key, DiffStatus.UNCHANGED, value_a=env_a[key], value_b=env_b[key])
            )

    return result
