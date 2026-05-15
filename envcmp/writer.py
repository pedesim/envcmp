"""Write exported diff output to a file or stdout."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional, Union

from envcmp.differ import DiffResult
from envcmp.exporter import Exporter

_PathLike = Union[str, Path]

_FORMAT_EXTENSIONS: dict[str, str] = {
    ".json": "json",
    ".csv": "csv",
    ".md": "markdown",
    ".markdown": "markdown",
}


def _infer_format(path: Path) -> Optional[str]:
    """Guess the export format from the file extension, or return None."""
    return _FORMAT_EXTENSIONS.get(path.suffix.lower())


def write(
    result: DiffResult,
    *,
    fmt: str = "json",
    output: Optional[_PathLike] = None,
    include_unchanged: bool = False,
) -> None:
    """Serialise *result* and write it to *output* (or stdout).

    Parameters
    ----------
    result:
        The diff result to export.
    fmt:
        One of ``"json"``, ``"csv"``, or ``"markdown"``.
        Ignored when *output* is supplied and its extension is recognised.
    output:
        Destination file path.  When *None* the content is written to stdout.
    include_unchanged:
        Whether unchanged keys should be included in the export.
    """
    exporter = Exporter(result, include_unchanged=include_unchanged)

    if output is not None:
        dest = Path(output)
        resolved_fmt = _infer_format(dest) or fmt
        content = exporter.export(resolved_fmt)
        dest.write_text(content, encoding="utf-8")
    else:
        content = exporter.export(fmt)
        sys.stdout.write(content)
        if not content.endswith("\n"):
            sys.stdout.write("\n")
