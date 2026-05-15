"""Loader module for envcmp — resolves and loads .env files from disk or strings."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, Optional, Union

from envcmp.parser import parse_env_file, parse_env_string


class EnvSource:
    """Represents a loaded environment source with a label and parsed variables."""

    def __init__(self, label: str, data: Dict[str, str], path: Optional[Path] = None):
        self.label = label
        self.data = data
        self.path = path

    def __repr__(self) -> str:  # pragma: no cover
        return f"EnvSource(label={self.label!r}, keys={list(self.data.keys())})"


def load_from_file(path: Union[str, Path], label: Optional[str] = None) -> EnvSource:
    """Load an EnvSource from a file path.

    Args:
        path: Path to the .env file.
        label: Optional display label; defaults to the file name.

    Returns:
        An EnvSource with parsed key/value pairs.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the path is a directory.
    """
    resolved = Path(path).expanduser().resolve()

    if not resolved.exists():
        raise FileNotFoundError(f"Env file not found: {resolved}")
    if resolved.is_dir():
        raise ValueError(f"Path is a directory, not a file: {resolved}")

    data = parse_env_file(str(resolved))
    display_label = label if label is not None else resolved.name
    return EnvSource(label=display_label, data=data, path=resolved)


def load_from_string(content: str, label: str = "<string>") -> EnvSource:
    """Load an EnvSource from a raw .env-formatted string.

    Args:
        content: Raw .env file contents.
        label: Display label for this source.

    Returns:
        An EnvSource with parsed key/value pairs.
    """
    data = parse_env_string(content)
    return EnvSource(label=label, data=data, path=None)


def load_from_env(label: str = "<environment>", prefix: Optional[str] = None) -> EnvSource:
    """Load an EnvSource from the current process environment.

    Args:
        label: Display label for this source.
        prefix: If given, only include variables starting with this prefix.

    Returns:
        An EnvSource populated from os.environ.
    """
    env = dict(os.environ)
    if prefix:
        env = {k: v for k, v in env.items() if k.startswith(prefix)}
    return EnvSource(label=label, data=env, path=None)
