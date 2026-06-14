"""
exifgeo - EXIF metadata and geolocation extraction for privacy auditing and OSINT.
"""

from .core import ExifReport, GPSData, analyze_image
from .report import to_json, to_terminal

__version__ = "0.1.0"
__all__ = [
    "analyze_image",
    "ExifReport",
    "GPSData",
    "to_json",
    "to_terminal",
]
