"""Command-line interface for envcmp."""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from envcmp.loader import load_from_file
from envcmp.pipeline import PipelineConfig, run


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envcmp",
        description="Diff and audit .env files across environments with secret masking.",
    )
    parser.add_argument("file_a", metavar="FILE_A", help="Baseline .env file")
    parser.add_argument("file_b", metavar="FILE_B", help="Target .env file")
    parser.add_argument(
        "--label-a", default=None, metavar="LABEL", help="Display label for FILE_A"
    )
    parser.add_argument(
        "--label-b", default=None, metavar="LABEL", help="Display label for FILE_B"
    )
    parser.add_argument(
        "--show-unchanged",
        action="store_true",
        default=False,
        help="Include unchanged keys in the report",
    )
    parser.add_argument(
        "--no-mask",
        action="store_true",
        default=False,
        help="Disable secret masking (show raw values)",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable ANSI color output",
    )
    parser.add_argument(
        "--secret-pattern",
        action="append",
        default=[],
        metavar="PATTERN",
        dest="secret_patterns",
        help="Additional substring patterns to treat as secrets (repeatable)",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Entry point for the CLI.

    Returns:
        Exit code: 0 if no differences, 1 if differences found, 2 on error.
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        source_a = load_from_file(args.file_a, label=args.label_a)
        source_b = load_from_file(args.file_b, label=args.label_b)
    except (FileNotFoundError, ValueError) as exc:
        print(f"envcmp: error: {exc}", file=sys.stderr)
        return 2

    config = PipelineConfig(
        show_unchanged=args.show_unchanged,
        mask_secrets=not args.no_mask,
        color=not args.no_color,
        extra_secret_patterns=args.secret_patterns,
    )

    result = run(source_a, source_b, config)
    print(result.report)

    has_diff = any(
        e for e in result.diff.entries
        if e.status.name != "UNCHANGED"
    )
    return 1 if has_diff else 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
