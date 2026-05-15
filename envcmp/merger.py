"""Merge two EnvSource objects into a single dict with conflict resolution."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional

from envcmp.loader import EnvSource


class ConflictStrategy(str, Enum):
    """How to handle keys present in both sources with different values."""

    USE_BASE = "use_base"        # Keep the value from the base (first) source
    USE_OTHER = "use_other"      # Keep the value from the other (second) source
    RAISE = "raise"              # Raise a ValueError on any conflict


@dataclass
class MergeResult:
    """Result of merging two EnvSource objects."""

    merged: Dict[str, str]
    conflicts: Dict[str, tuple] = field(default_factory=dict)  # key -> (base_val, other_val)
    added_keys: list = field(default_factory=list)    # keys only in other
    removed_keys: list = field(default_factory=list)  # keys only in base

    @property
    def has_conflicts(self) -> bool:
        return bool(self.conflicts)


def merge(
    base: EnvSource,
    other: EnvSource,
    strategy: ConflictStrategy = ConflictStrategy.USE_BASE,
    include_removed: bool = True,
) -> MergeResult:
    """Merge *other* into *base* and return a MergeResult.

    Args:
        base: The primary EnvSource.
        other: The secondary EnvSource whose keys are merged in.
        strategy: How to resolve keys that exist in both with different values.
        include_removed: When True, keys only in *base* are kept in the merged
                         output.  When False they are omitted.

    Returns:
        MergeResult with the merged dict and metadata about conflicts.
    """
    merged: Dict[str, str] = {}
    conflicts: Dict[str, tuple] = {}
    added_keys = []
    removed_keys = []

    all_keys = set(base.data) | set(other.data)

    for key in sorted(all_keys):
        in_base = key in base.data
        in_other = key in other.data

        if in_base and in_other:
            base_val = base.data[key]
            other_val = other.data[key]
            if base_val == other_val:
                merged[key] = base_val
            else:
                conflicts[key] = (base_val, other_val)
                if strategy == ConflictStrategy.RAISE:
                    raise ValueError(
                        f"Conflict on key '{key}': "
                        f"base={base_val!r} other={other_val!r}"
                    )
                elif strategy == ConflictStrategy.USE_OTHER:
                    merged[key] = other_val
                else:  # USE_BASE
                    merged[key] = base_val

        elif in_other:
            merged[key] = other.data[key]
            added_keys.append(key)

        else:  # only in base
            removed_keys.append(key)
            if include_removed:
                merged[key] = base.data[key]

    return MergeResult(
        merged=merged,
        conflicts=conflicts,
        added_keys=added_keys,
        removed_keys=removed_keys,
    )
