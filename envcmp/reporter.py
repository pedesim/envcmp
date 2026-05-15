"""Formats and renders diff results for human-readable output."""

from __future__ import annotations

from typing import TextIO
import sys

from envcmp.differ import DiffResult, DiffStatus
from envcmp.masker import SecretMasker

_STATUS_SYMBOLS = {
    DiffStatus.ADDED: "+",
    DiffStatus.REMOVED: "-",
    DiffStatus.CHANGED: "~",
    DiffStatus.UNCHANGED: " ",
}

_STATUS_COLORS = {
    DiffStatus.ADDED: "\033[32m",    # green
    DiffStatus.REMOVED: "\033[31m",  # red
    DiffStatus.CHANGED: "\033[33m",  # yellow
    DiffStatus.UNCHANGED: "",
}

_RESET = "\033[0m"


class Reporter:
    """Renders a DiffResult to a stream."""

    def __init__(
        self,
        masker: SecretMasker | None = None,
        color: bool = True,
        show_unchanged: bool = False,
    ) -> None:
        self.masker = masker or SecretMasker()
        self.color = color
        self.show_unchanged = show_unchanged

    def _colorize(self, text: str, status: DiffStatus) -> str:
        if not self.color:
            return text
        prefix = _STATUS_COLORS.get(status, "")
        return f"{prefix}{text}{_RESET}" if prefix else text

    def _format_entry(self, entry) -> str | None:
        if entry.status == DiffStatus.UNCHANGED and not self.show_unchanged:
            return None

        symbol = _STATUS_SYMBOLS[entry.status]
        key = entry.key

        old_val = self.masker.mask(key, entry.old_value) if entry.old_value is not None else None
        new_val = self.masker.mask(key, entry.new_value) if entry.new_value is not None else None

        if entry.status == DiffStatus.ADDED:
            line = f"{symbol} {key}={new_val}"
        elif entry.status == DiffStatus.REMOVED:
            line = f"{symbol} {key}={old_val}"
        elif entry.status == DiffStatus.CHANGED:
            line = f"{symbol} {key}: {old_val!r} -> {new_val!r}"
        else:
            line = f"{symbol} {key}={new_val}"

        return self._colorize(line, entry.status)

    def render(self, result: DiffResult, stream: TextIO = sys.stdout) -> None:
        """Write the formatted diff to *stream*."""
        lines_written = 0
        for entry in sorted(result.entries, key=lambda e: e.key):
            formatted = self._format_entry(entry)
            if formatted is not None:
                stream.write(formatted + "\n")
                lines_written += 1

        if lines_written == 0:
            stream.write("No differences found.\n")

    def summary(self, result: DiffResult, stream: TextIO = sys.stdout) -> None:
        """Write a one-line summary of counts."""
        stream.write(
            f"Summary: {result.added_count} added, "
            f"{result.removed_count} removed, "
            f"{result.changed_count} changed.\n"
        )
