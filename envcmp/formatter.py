"""Structured output formatters for envcmp diff results (JSON, CSV)."""

from __future__ import annotations

import csv
import io
import json
from typing import Literal

from envcmp.differ import DiffResult, DiffStatus

OutputFormat = Literal["json", "csv"]


class Formatter:
    """Serialises a DiffResult to a structured text format."""

    def __init__(self, fmt: OutputFormat = "json", include_unchanged: bool = False) -> None:
        if fmt not in ("json", "csv"):
            raise ValueError(f"Unsupported format: {fmt!r}. Choose 'json' or 'csv'.")
        self.fmt = fmt
        self.include_unchanged = include_unchanged

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def render(self, result: DiffResult) -> str:
        """Return the diff result serialised as *fmt* text."""
        entries = self._visible_entries(result)
        if self.fmt == "json":
            return self._to_json(entries)
        return self._to_csv(entries)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _visible_entries(self, result: DiffResult) -> list[dict]:
        rows = []
        for entry in result.entries:
            if entry.status == DiffStatus.UNCHANGED and not self.include_unchanged:
                continue
            rows.append({
                "key": entry.key,
                "status": entry.status.value,
                "value_a": entry.value_a,
                "value_b": entry.value_b,
            })
        return rows

    @staticmethod
    def _to_json(rows: list[dict]) -> str:
        return json.dumps(rows, indent=2)

    @staticmethod
    def _to_csv(rows: list[dict]) -> str:
        buf = io.StringIO()
        fieldnames = ["key", "status", "value_a", "value_b"]
        writer = csv.DictWriter(buf, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        return buf.getvalue()
