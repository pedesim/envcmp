"""Snapshot support: save and load env state for later comparison."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Optional


@dataclass
class Snapshot:
    label: str
    data: Dict[str, str]
    captured_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    source_path: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "label": self.label,
            "captured_at": self.captured_at,
            "source_path": self.source_path,
            "data": self.data,
        }

    @classmethod
    def from_dict(cls, raw: dict) -> "Snapshot":
        return cls(
            label=raw["label"],
            data=raw["data"],
            captured_at=raw.get("captured_at", ""),
            source_path=raw.get("source_path"),
        )

    def __repr__(self) -> str:
        return f"Snapshot(label={self.label!r}, keys={len(self.data)}, captured_at={self.captured_at!r})"


def save_snapshot(snapshot: Snapshot, path: str) -> None:
    """Persist a snapshot to a JSON file."""
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(snapshot.to_dict(), fh, indent=2)


def load_snapshot(path: str) -> Snapshot:
    """Load a snapshot from a JSON file."""
    with open(path, "r", encoding="utf-8") as fh:
        raw = json.load(fh)
    return Snapshot.from_dict(raw)


def snapshot_from_env_source(source) -> Snapshot:
    """Create a Snapshot from an EnvSource instance."""
    return Snapshot(
        label=source.label,
        data=dict(source.data),
        source_path=str(source.path) if source.path else None,
    )
