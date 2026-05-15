"""Export diff results to various file formats (JSON, CSV, Markdown)."""

from __future__ import annotations

import csv
import io
import json
from typing import Optional

from envcmp.differ import DiffResult, DiffStatus


class Exporter:
    """Serialises a DiffResult to a chosen output format."""

    SUPPORTED_FORMATS = ("json", "csv", "markdown")

    def __init__(self, result: DiffResult, include_unchanged: bool = False) -> None:
        self.result = result
        self.include_unchanged = include_unchanged

    def _entries(self):
        if self.include_unchanged:
            return self.result.all_entries()
        return [
            e for e in self.result.all_entries()
            if e.status != DiffStatus.UNCHANGED
        ]

    def to_json(self, indent: int = 2) -> str:
        """Return a JSON string representation of the diff."""
        rows = [
            {
                "key": e.key,
                "status": e.status.value,
                "value_a": e.value_a,
                "value_b": e.value_b,
            }
            for e in self._entries()
        ]
        return json.dumps(rows, indent=indent)

    def to_csv(self) -> str:
        """Return a CSV string representation of the diff."""
        buf = io.StringIO()
        writer = csv.DictWriter(
            buf, fieldnames=["key", "status", "value_a", "value_b"]
        )
        writer.writeheader()
        for e in self._entries():
            writer.writerow(
                {
                    "key": e.key,
                    "status": e.status.value,
                    "value_a": e.value_a if e.value_a is not None else "",
                    "value_b": e.value_b if e.value_b is not None else "",
                }
            )
        return buf.getvalue()

    def to_markdown(self) -> str:
        """Return a Markdown table representation of the diff."""
        lines = [
            "| Key | Status | Value A | Value B |",
            "| --- | ------ | ------- | ------- |",
        ]
        for e in self._entries():
            va = e.value_a if e.value_a is not None else ""
            vb = e.value_b if e.value_b is not None else ""
            lines.append(f"| {e.key} | {e.status.value} | {va} | {vb} |")
        return "\n".join(lines)

    def export(self, fmt: str) -> str:
        """Dispatch to the correct serialiser based on *fmt*."""
        fmt = fmt.lower()
        if fmt == "json":
            return self.to_json()
        if fmt == "csv":
            return self.to_csv()
        if fmt == "markdown":
            return self.to_markdown()
        raise ValueError(
            f"Unsupported format {fmt!r}. Choose from: {self.SUPPORTED_FORMATS}"
        )
