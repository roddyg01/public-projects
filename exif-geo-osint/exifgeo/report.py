"""
Output formatting for ExifReport objects.

Two formats are supported: a colorized, human-readable terminal report and
a machine-readable JSON structure suitable for piping into other tools.
"""

from __future__ import annotations

import json
from typing import Any

from .core import ExifReport


# ANSI color codes. Kept minimal and disabled automatically when output is
# not a TTY (handled by the caller passing use_color=False).
class _C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[31m"
    YELLOW = "\033[33m"
    GREEN = "\033[32m"
    CYAN = "\033[36m"
    MAGENTA = "\033[35m"


_RISK_COLORS = {
    "HIGH": _C.RED,
    "MEDIUM": _C.YELLOW,
    "LOW": _C.CYAN,
    "NONE": _C.DIM,
}


def _c(text: str, color: str, use_color: bool) -> str:
    if not use_color:
        return text
    return f"{color}{text}{_C.RESET}"


def to_json(report: ExifReport) -> str:
    """Serialize a report to a JSON string."""
    payload: dict[str, Any] = {
        "file": str(report.path),
        "has_exif": report.has_exif,
        "privacy_risk": report.privacy_risk,
        "gps": {
            "latitude": report.gps.latitude,
            "longitude": report.gps.longitude,
            "altitude_m": report.gps.altitude,
            "timestamp": report.gps.timestamp,
            "decimal": report.gps.decimal_string,
            "maps_url": report.gps.maps_url,
        },
        "sensitive_findings": report.sensitive_findings,
        "all_tags": report.raw_tags,
    }
    return json.dumps(payload, indent=2, default=str)


def to_terminal(report: ExifReport, use_color: bool = True, verbose: bool = False) -> str:
    """Build a human-readable terminal report."""
    lines: list[str] = []

    lines.append("")
    lines.append(_c("=" * 60, _C.DIM, use_color))
    lines.append(_c(f"  EXIF / Geolocation Report", _C.BOLD, use_color))
    lines.append(_c(f"  {report.path.name}", _C.CYAN, use_color))
    lines.append(_c("=" * 60, _C.DIM, use_color))

    # Risk banner.
    risk = report.privacy_risk
    risk_color = _RISK_COLORS.get(risk, _C.RESET)
    lines.append("")
    lines.append(
        "  Privacy risk: " + _c(f"[{risk}]", risk_color + _C.BOLD, use_color)
    )

    if not report.has_exif:
        lines.append("")
        lines.append(
            _c("  No EXIF metadata found. ", _C.GREEN, use_color)
            + "This file has been stripped or never had any."
        )
        lines.append(_c("=" * 60, _C.DIM, use_color))
        lines.append("")
        return "\n".join(lines)

    # GPS section.
    lines.append("")
    lines.append(_c("  LOCATION", _C.BOLD, use_color))
    lines.append(_c("  " + "-" * 30, _C.DIM, use_color))
    if report.gps.has_coordinates:
        lines.append(
            f"  Coordinates : "
            + _c(report.gps.decimal_string or "", _C.RED + _C.BOLD, use_color)
        )
        if report.gps.altitude is not None:
            lines.append(f"  Altitude    : {report.gps.altitude} m")
        if report.gps.timestamp:
            lines.append(f"  GPS time    : {report.gps.timestamp}")
        lines.append(
            f"  Map         : "
            + _c(report.gps.maps_url or "", _C.CYAN, use_color)
        )
    else:
        lines.append(_c("  No GPS coordinates embedded.", _C.GREEN, use_color))

    # Sensitive findings.
    if report.sensitive_findings:
        lines.append("")
        lines.append(_c("  SENSITIVE FIELDS PRESENT", _C.BOLD, use_color))
        lines.append(_c("  " + "-" * 30, _C.DIM, use_color))
        for tag, description in report.sensitive_findings.items():
            value = report.raw_tags.get(tag)
            shown = ""
            if value is not None and tag != "GPSInfo":
                shown = _c(f"  ->  {value}", _C.DIM, use_color)
            lines.append(f"  {_c('!', _C.YELLOW, use_color)} {tag}: {description}")
            if shown:
                lines.append(shown)

    # Full tag dump (verbose only).
    if verbose:
        lines.append("")
        lines.append(_c("  ALL METADATA", _C.BOLD, use_color))
        lines.append(_c("  " + "-" * 30, _C.DIM, use_color))
        for tag, value in sorted(report.raw_tags.items()):
            if tag == "GPSInfo":
                continue
            lines.append(f"  {tag}: {_c(str(value), _C.DIM, use_color)}")

    lines.append("")
    lines.append(_c("=" * 60, _C.DIM, use_color))
    lines.append("")
    return "\n".join(lines)
