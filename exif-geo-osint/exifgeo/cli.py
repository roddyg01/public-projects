"""
Command-line interface for exifgeo.

Usage examples:
    exifgeo photo.jpg
    exifgeo photo.jpg --json
    exifgeo ~/Pictures --recursive
    exifgeo photo.jpg --verbose
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .core import analyze_image
from .report import to_json, to_terminal

# Image extensions we will attempt to read in directory mode.
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".tif", ".tiff", ".png", ".heic", ".webp"}


def _gather_images(target: Path, recursive: bool) -> list[Path]:
    """Collect image files from a file or directory target."""
    if target.is_file():
        return [target]

    if target.is_dir():
        globber = target.rglob if recursive else target.glob
        return sorted(
            p for p in globber("*") if p.suffix.lower() in IMAGE_EXTENSIONS
        )

    return []


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="exifgeo",
        description=(
            "Extract EXIF metadata and GPS coordinates from images, and flag "
            "fields with privacy or operational-security implications."
        ),
        epilog=(
            "Built for defensive privacy auditing and OSINT research. "
            "Only analyze images you are authorized to inspect."
        ),
    )
    parser.add_argument(
        "target",
        help="Image file or directory of images to analyze.",
    )
    parser.add_argument(
        "-j",
        "--json",
        action="store_true",
        help="Emit machine-readable JSON instead of a terminal report.",
    )
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="When TARGET is a directory, descend into subdirectories.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Include the full metadata dump in the terminal report.",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable ANSI colors (useful when redirecting to a file).",
    )
    parser.add_argument(
        "--gps-only",
        action="store_true",
        help="Only print files that contain GPS coordinates.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    target = Path(args.target).expanduser()
    images = _gather_images(target, args.recursive)

    if not images:
        print(f"No images found at: {target}", file=sys.stderr)
        return 1

    # Color only when writing to an interactive terminal.
    use_color = sys.stdout.isatty() and not args.no_color

    json_reports = []
    exit_code = 0

    for image_path in images:
        try:
            report = analyze_image(image_path)
        except (FileNotFoundError, ValueError) as exc:
            print(f"[skip] {image_path}: {exc}", file=sys.stderr)
            exit_code = 1
            continue

        if args.gps_only and not report.gps.has_coordinates:
            continue

        if args.json:
            json_reports.append(report)
        else:
            print(to_terminal(report, use_color=use_color, verbose=args.verbose))

    if args.json:
        # Emit a single JSON array for batch mode, or one object for a single file.
        if len(json_reports) == 1:
            print(to_json(json_reports[0]))
        else:
            payloads = [to_json(r) for r in json_reports]
            print("[\n" + ",\n".join(payloads) + "\n]")

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
