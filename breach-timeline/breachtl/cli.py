"""
Command-line interface for breachtl.

Examples:
    # Landscape view of the entire breach catalog (no key needed):
    python -m breachtl.cli --landscape

    # Filter the catalog to a single year:
    python -m breachtl.cli --landscape --year 2019

    # Look up a specific address (requires an HIBP API key):
    python -m breachtl.cli --account you@example.com --key YOUR_KEY

    # Work entirely offline from a cached catalog file:
    python -m breachtl.cli --landscape --from-file catalog.json
"""

from __future__ import annotations

import argparse
import json
import os
import sys

from .core import (
    HIBPError,
    TimelineAnalysis,
    fetch_account_breaches,
    fetch_all_breaches,
    load_breaches_from_file,
)
from .report import render_account_detail, render_summary, render_timeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="breachtl",
        description=(
            "Build a timeline and exposure analysis from Have I Been Pwned "
            "breach data. Works on the public breach catalog with no key, or "
            "on a specific email address when an API key is supplied."
        ),
        epilog="Only look up addresses you own or are authorized to investigate.",
    )

    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--landscape",
        action="store_true",
        help="Analyze the full public breach catalog (no API key required).",
    )
    mode.add_argument(
        "--account",
        metavar="EMAIL",
        help="Analyze breaches for a specific email address (requires --key).",
    )

    parser.add_argument(
        "--key",
        help="HIBP API key. Falls back to the HIBP_API_KEY environment variable.",
    )
    parser.add_argument(
        "--from-file",
        metavar="PATH",
        help="Load breach data from a cached JSON file instead of the network.",
    )
    parser.add_argument(
        "--year",
        type=int,
        help="Restrict the analysis to a single calendar year.",
    )
    parser.add_argument(
        "--exposes-passwords",
        action="store_true",
        help="Only include breaches that exposed passwords.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON instead of the rendered report.",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable ANSI colors.",
    )
    return parser


def _resolve_key(args: argparse.Namespace) -> str | None:
    return args.key or os.environ.get("HIBP_API_KEY")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    use_color = sys.stdout.isatty() and not args.no_color

    # --- Acquire the breach list based on mode. ---
    try:
        if args.from_file:
            breaches = load_breaches_from_file(args.from_file)
        elif args.account:
            key = _resolve_key(args)
            if not key:
                print(
                    "An API key is required for --account. Pass --key or set "
                    "HIBP_API_KEY.",
                    file=sys.stderr,
                )
                return 2
            breaches = fetch_account_breaches(args.account, key)
        else:
            breaches = fetch_all_breaches(_resolve_key(args))
    except HIBPError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except (OSError, ValueError) as exc:
        print(f"Error reading data: {exc}", file=sys.stderr)
        return 1

    # --- Apply filters. ---
    if args.year is not None:
        breaches = [b for b in breaches if b.year == args.year]
    if args.exposes_passwords:
        breaches = [b for b in breaches if b.exposes_passwords]

    analysis = TimelineAnalysis(breaches)

    # --- Output. ---
    if args.json:
        payload = {
            "total": analysis.total,
            "accounts_exposed": analysis.total_accounts_exposed,
            "severity": analysis.severity_breakdown(),
            "by_year": {
                str(year): len(items) for year, items in analysis.by_year().items()
            },
            "data_classes": dict(analysis.data_class_frequency()),
            "breaches": [
                {
                    "name": b.name,
                    "title": b.title,
                    "date": b.breach_date,
                    "pwn_count": b.pwn_count,
                    "severity": b.severity,
                    "data_classes": b.data_classes,
                }
                for b in analysis.sorted_by_date()
            ],
        }
        print(json.dumps(payload, indent=2))
        return 0

    if args.account:
        print(render_account_detail(breaches, args.account, use_color=use_color))
        print(render_summary(analysis, use_color=use_color))
    else:
        print(render_timeline(analysis, use_color=use_color))
        print(render_summary(analysis, use_color=use_color))

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BrokenPipeError:
        # Output was piped to a command that closed early (e.g. `head`).
        # Suppress the noisy traceback and exit cleanly.
        sys.stderr.close()
        raise SystemExit(0)
