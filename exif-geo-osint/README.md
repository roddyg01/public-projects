# exif-geo-osint

A command-line tool (`exifgeo`) that reads EXIF metadata from images, pulls out GPS coordinates, and flags fields that leak personal or device information.

> **For lawful, ethical research only.** Only analyze images you own or are authorized to inspect. The data this tool surfaces — location, timestamps, device details — is sensitive. Use it to protect privacy, not to violate it.

## What it does

- Reads EXIF data from any image Pillow can open (JPEG, TIFF, PNG, WebP). HEIC files are picked up in folder scans but need an extra Pillow plugin to open.
- Converts GPS coordinates from degrees/minutes/seconds to decimal and builds a Google Maps link.
- Flags sensitive fields when present: GPS, timestamps, make, model, software version, serial numbers, host computer, and unique image ID.
- Rates each image's privacy risk:
  - `HIGH` — GPS coordinates present
  - `MEDIUM` — other sensitive fields present
  - `LOW` — EXIF present, nothing sensitive
  - `NONE` — no EXIF
- Scans a whole folder, with an option to recurse and an option to show only images with GPS.
- Outputs a terminal report or JSON.
- Runs locally. It makes no network calls.

## Why it's useful

Photos straight off a phone often carry the exact spot they were taken, the time, and the device. Most people don't know that. Run this before you post a photo to see what it gives away. In OSINT work, it's a quick first pass on images you're allowed to examine.

## Requirements

- Python 3.9+
- Pillow (see `requirements.txt`)

## How to run it

```bash
git clone https://github.com/roddyg01/public-projects.git
cd public-projects/exif-geo-osint
pip install .
```

That installs the `exifgeo` command. To run it without installing:

```bash
pip install -r requirements.txt
python -m exifgeo.cli photo.jpg
```

Usage:

```bash
exifgeo photo.jpg                       # one image
exifgeo ~/Pictures --recursive --gps-only   # folder, only images with GPS
exifgeo photo.jpg --json                # JSON output
exifgeo photo.jpg --verbose             # include every EXIF tag
```

| Flag | Description |
|------|-------------|
| `-j`, `--json` | Output JSON instead of a terminal report. |
| `-r`, `--recursive` | Include subfolders when the target is a folder. |
| `-v`, `--verbose` | Include the full metadata dump. |
| `--gps-only` | Only show images that have GPS coordinates. |
| `--no-color` | Turn off colors. |

Run the tests:

```bash
python -m unittest discover -s tests -v
```

## Example output

A test image tagged with the Eiffel Tower's coordinates:

```
============================================================
  EXIF / Geolocation Report
  photo.jpg
============================================================

  Privacy risk: [HIGH]

  LOCATION
  ------------------------------
  Coordinates : 48.858400, 2.294500
  Altitude    : 330.0 m
  Map         : https://www.google.com/maps?q=48.858400,2.294500

  SENSITIVE FIELDS PRESENT
  ------------------------------
  ! GPSInfo: Precise location where the photo was taken
  ! DateTime: File modification timestamp
  ->  2024:05:01 14:22:10
  ! Make: Camera or phone manufacturer
  ->  Apple
  ! Model: Specific device model
  ->  iPhone 13
  ! Software: Operating system / software version on the device
  ->  17.4

============================================================
```

An image with no metadata:

```
  Privacy risk: [NONE]

  No EXIF metadata found. This file has been stripped or never had any.
```

## License

MIT — see [LICENSE](LICENSE).
