"""CLI entry point for the file-watching subcommand."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List

from envcmp.pipeline import PipelineConfig
from envcmp.reporter import Reporter
from envcmp.watcher import WatchEvent, Watcher


def _on_event(event: WatchEvent, reporter: Reporter, quiet: bool) -> None:
    """Handle a WatchEvent by printing a diff report to stdout."""
    if not quiet:
        print(f"\n[envcmp] Change detected in {event.path}")
    output = reporter.render(event.result.diff)
    if output:
        print(output)
    else:
        if not quiet:
            print("  (no visible differences)")


def build_watch_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envcmp watch",
        description="Watch two .env files and print diffs on change.",
    )
    parser.add_argument("file_a", type=Path, help="Base .env file")
    parser.add_argument("file_b", type=Path, help="Target .env file")
    parser.add_argument(
        "--interval",
        type=float,
        default=2.0,
        metavar="SECONDS",
        help="Polling interval in seconds (default: 2.0)",
    )
    parser.add_argument(
        "--mask-secrets",
        action="store_true",
        default=True,
        help="Mask secret values in output (default: on)",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable ANSI colour output",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        default=False,
        help="Suppress informational messages",
    )
    return parser


def main(argv: List[str] | None = None) -> int:
    parser = build_watch_parser()
    args = parser.parse_args(argv)

    for p in (args.file_a, args.file_b):
        if not p.exists():
            print(f"error: file not found: {p}", file=sys.stderr)
            return 1

    config = PipelineConfig(mask_secrets=args.mask_secrets)
    reporter = Reporter(use_color=not args.no_color, mask_secrets=args.mask_secrets)

    def callback(event: WatchEvent) -> None:
        _on_event(event, reporter, quiet=args.quiet)

    watcher = Watcher(
        paths=[args.file_a, args.file_b],
        callback=callback,
        config=config,
        interval=args.interval,
    )

    if not args.quiet:
        print(f"[envcmp] Watching {args.file_a} vs {args.file_b} (interval={args.interval}s)")
        print("[envcmp] Press Ctrl+C to stop.")

    try:
        watcher.start()
    except KeyboardInterrupt:
        if not args.quiet:
            print("\n[envcmp] Stopped.")

    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
