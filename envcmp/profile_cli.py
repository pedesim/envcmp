"""CLI entry-point for the `envcmp profile` sub-command."""
from __future__ import annotations

import argparse
import json
import sys

from envcmp.loader import load_from_file
from envcmp.masker import SecretMasker
from envcmp.profiler import profile


def build_profile_parser(parent: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    description = "Profile a .env file and report key statistics."
    if parent is not None:
        parser = parent.add_parser("profile", help=description)
    else:
        parser = argparse.ArgumentParser(prog="envcmp-profile", description=description)

    parser.add_argument("file", help="Path to the .env file to profile")
    parser.add_argument(
        "--label",
        default=None,
        help="Override the display label for the source (default: file path)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="Output the profile as JSON instead of human-readable text",
    )
    parser.add_argument(
        "--patterns",
        nargs="*",
        default=None,
        metavar="PATTERN",
        help="Additional secret-detection patterns (case-insensitive substrings)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_profile_parser()
    args = parser.parse_args(argv)

    try:
        source = load_from_file(args.file, label=args.label)
    except FileNotFoundError:
        print(f"error: file not found: {args.file}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    masker = SecretMasker(patterns=args.patterns) if args.patterns else SecretMasker()
    report = profile(source, masker=masker)

    if args.as_json:
        payload = {
            "label": report.label,
            "total_keys": report.total_keys,
            "secret_count": report.secret_count,
            "empty_count": report.empty_count,
            "secret_keys": report.secret_keys,
            "empty_keys": report.empty_keys,
            "duplicate_keys": report.duplicate_keys,
        }
        print(json.dumps(payload, indent=2))
    else:
        print(report.summary())

    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
