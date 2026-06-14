"""
Core EXIF extraction and GPS parsing logic.

This module reads EXIF metadata from image files, converts GPS coordinates
from the EXIF degree/minute/second format into decimal degrees, and flags
metadata fields that carry privacy or operational-security implications.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image
from PIL.ExifTags import GPSTAGS, TAGS


# EXIF tags that commonly carry sensitive information. These are surfaced
# in the privacy report so an analyst (or an end user auditing their own
# photos) can see what a file is quietly revealing.
SENSITIVE_TAGS = {
    "GPSInfo": "Precise location where the photo was taken",
    "DateTimeOriginal": "Exact date and time the photo was captured",
    "DateTime": "File modification timestamp",
    "Make": "Camera or phone manufacturer",
    "Model": "Specific device model",
    "Software": "Operating system / software version on the device",
    "SerialNumber": "Camera body serial number (uniquely identifying)",
    "LensSerialNumber": "Lens serial number",
    "HostComputer": "Device that captured or processed the image",
    "ImageUniqueID": "Device-generated unique identifier for the image",
}


@dataclass
class GPSData:
    """Parsed GPS information extracted from EXIF."""

    latitude: float | None = None
    longitude: float | None = None
    altitude: float | None = None
    timestamp: str | None = None

    @property
    def has_coordinates(self) -> bool:
        return self.latitude is not None and self.longitude is not None

    @property
    def decimal_string(self) -> str | None:
        """Coordinates formatted for pasting into a mapping service."""
        if not self.has_coordinates:
            return None
        return f"{self.latitude:.6f}, {self.longitude:.6f}"

    @property
    def maps_url(self) -> str | None:
        """A Google Maps link that drops a pin on the location."""
        if not self.has_coordinates:
            return None
        return f"https://www.google.com/maps?q={self.latitude:.6f},{self.longitude:.6f}"


@dataclass
class ExifReport:
    """Full result of analyzing a single image."""

    path: Path
    has_exif: bool = False
    gps: GPSData = field(default_factory=GPSData)
    raw_tags: dict[str, Any] = field(default_factory=dict)
    sensitive_findings: dict[str, str] = field(default_factory=dict)

    @property
    def privacy_risk(self) -> str:
        """A coarse risk label based on what was found."""
        if self.gps.has_coordinates:
            return "HIGH"
        if self.sensitive_findings:
            return "MEDIUM"
        if self.has_exif:
            return "LOW"
        return "NONE"


def _ratio_to_float(value: Any) -> float:
    """Convert an EXIF rational (or tuple) into a float."""
    try:
        # Pillow may return an IFDRational, a tuple (num, den), or a number.
        if isinstance(value, tuple) and len(value) == 2:
            return float(value[0]) / float(value[1])
        return float(value)
    except (TypeError, ZeroDivisionError, ValueError):
        return 0.0


def _dms_to_decimal(dms: Any, ref: str) -> float | None:
    """
    Convert degrees/minutes/seconds to decimal degrees.

    EXIF stores GPS as three rationals (deg, min, sec) plus a reference
    (N/S/E/W). South and West are negative.
    """
    try:
        degrees = _ratio_to_float(dms[0])
        minutes = _ratio_to_float(dms[1])
        seconds = _ratio_to_float(dms[2])
    except (TypeError, IndexError):
        return None

    decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)

    if ref in ("S", "W"):
        decimal = -decimal

    return round(decimal, 6)


def _parse_gps(gps_ifd: dict[str, Any]) -> GPSData:
    """Pull latitude, longitude, altitude, and timestamp out of the GPS IFD."""
    gps = GPSData()

    lat = gps_ifd.get("GPSLatitude")
    lat_ref = gps_ifd.get("GPSLatitudeRef")
    lon = gps_ifd.get("GPSLongitude")
    lon_ref = gps_ifd.get("GPSLongitudeRef")

    if lat and lat_ref:
        gps.latitude = _dms_to_decimal(lat, lat_ref)
    if lon and lon_ref:
        gps.longitude = _dms_to_decimal(lon, lon_ref)

    altitude = gps_ifd.get("GPSAltitude")
    if altitude is not None:
        alt_value = _ratio_to_float(altitude)
        # GPSAltitudeRef == 1 means below sea level.
        if gps_ifd.get("GPSAltitudeRef") == 1:
            alt_value = -alt_value
        gps.altitude = round(alt_value, 2)

    date_stamp = gps_ifd.get("GPSDateStamp")
    time_stamp = gps_ifd.get("GPSTimeStamp")
    if date_stamp and time_stamp:
        try:
            h = int(_ratio_to_float(time_stamp[0]))
            m = int(_ratio_to_float(time_stamp[1]))
            s = int(_ratio_to_float(time_stamp[2]))
            gps.timestamp = f"{date_stamp} {h:02d}:{m:02d}:{s:02d} UTC"
        except (TypeError, IndexError, ValueError):
            gps.timestamp = str(date_stamp)

    return gps


def _decode_value(value: Any) -> Any:
    """Make EXIF values JSON-serializable and human-readable."""
    if isinstance(value, bytes):
        try:
            return value.decode("utf-8", errors="replace").strip("\x00").strip()
        except Exception:
            return repr(value)
    if isinstance(value, tuple):
        return [_decode_value(v) for v in value]
    # IFDRational and similar -> float
    try:
        if hasattr(value, "numerator") and hasattr(value, "denominator"):
            return _ratio_to_float(value)
    except Exception:
        pass
    return value


def analyze_image(path: str | Path) -> ExifReport:
    """
    Analyze a single image file and return a structured report.

    Raises FileNotFoundError if the path does not exist, and ValueError if
    the file cannot be opened as an image.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"No such file: {path}")

    report = ExifReport(path=path)

    try:
        with Image.open(path) as img:
            exif = img.getexif()
    except Exception as exc:  # noqa: BLE001 - surface a clean error to the caller
        raise ValueError(f"Could not read image '{path}': {exc}") from exc

    if not exif:
        return report

    report.has_exif = True

    # Walk the top-level EXIF tags.
    for tag_id, value in exif.items():
        tag_name = TAGS.get(tag_id, str(tag_id))
        if tag_name == "GPSInfo":
            # GPSInfo is itself an IFD; expand it.
            gps_ifd_raw = exif.get_ifd(tag_id)
            gps_ifd = {
                GPSTAGS.get(k, str(k)): _decode_value(v)
                for k, v in gps_ifd_raw.items()
            }
            report.raw_tags["GPSInfo"] = gps_ifd
            report.gps = _parse_gps(gps_ifd)
        else:
            report.raw_tags[tag_name] = _decode_value(value)

    # Flag anything sensitive that is actually present.
    for tag_name, description in SENSITIVE_TAGS.items():
        if tag_name in report.raw_tags or (
            tag_name == "GPSInfo" and report.gps.has_coordinates
        ):
            report.sensitive_findings[tag_name] = description

    return report
