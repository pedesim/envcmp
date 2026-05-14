"""Parser for .env files."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, Optional, Tuple


ENV_LINE_RE = re.compile(
    r"^\s*(?P<key>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?P<value>.*)$"
)
COMMENT_RE = re.compile(r"^\s*#")


def _strip_quotes(value: str) -> str:
    """Remove surrounding single or double quotes from a value."""
    for quote in ('"', "'"):
        if value.startswith(quote) and value.endswith(quote) and len(value) >= 2:
            return value[1:-1]
    return value


def parse_env_file(path: str | Path) -> Dict[str, str]:
    """Parse a .env file and return a dict of key-value pairs.

    Args:
        path: Path to the .env file.

    Returns:
        Ordered dictionary of environment variable names to their values.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If a line cannot be parsed.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f".env file not found: {path}")

    result: Dict[str, str] = {}

    with path.open(encoding="utf-8") as fh:
        for lineno, raw_line in enumerate(fh, start=1):
            line = raw_line.rstrip("\n")

            # Skip blank lines and comments
            if not line.strip() or COMMENT_RE.match(line):
                continue

            match = ENV_LINE_RE.match(line)
            if not match:
                raise ValueError(
                    f"Invalid syntax on line {lineno} of {path}: {line!r}"
                )

            key = match.group("key")
            value = _strip_quotes(match.group("value").strip())
            result[key] = value

    return result


def parse_env_string(text: str) -> Dict[str, str]:
    """Parse .env content from a string.

    Args:
        text: Raw .env file content.

    Returns:
        Dictionary of environment variable names to their values.
    """
    result: Dict[str, str] = {}

    for lineno, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()

        if not line or COMMENT_RE.match(line):
            continue

        match = ENV_LINE_RE.match(line)
        if not match:
            raise ValueError(f"Invalid syntax on line {lineno}: {line!r}")

        key = match.group("key")
        value = _strip_quotes(match.group("value").strip())
        result[key] = value

    return result
