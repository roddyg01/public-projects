# exifgeo

A command-line tool for extracting EXIF metadata and GPS coordinates from images, and flagging the fields that carry privacy or operational-security implications.

Most people have no idea how much their photos reveal. A single image straight off a phone can contain the exact GPS coordinates where it was taken, the precise timestamp, the device model, and sometimes a uniquely identifying serial number. `exifgeo` surfaces all of it in a clean report so you can see what a file is quietly giving away — whether you're auditing your own photos before posting them or doing open-source research on images you're authorized to inspect.

## Features

- GPS extraction — converts EXIF degree/minute/second coordinates into decimal degrees and generates a ready-to-click map link.
- Privacy risk scoring — each image is rated `NONE` / `LOW` / `MEDIUM` / `HIGH` based on what it exposes.
- Sensitive-field flagging — highlights device serial numbers, timestamps, software versions, and other identifying metadata.
- Batch and recursive scanning — point it at a whole directory and filter for only the images that carry location data.
- JSON output — machine-readable output for piping into other tools or pipelines.
- Zero network calls — everything runs locally. The tool never uploads or transmits the images it reads.

## Installation

```bash
git clone https://github.com/YOUR_USERNAME/exif-geo-osint.git
cd exif-geo-osint
pip install .
```

Or run it directly without installing:

```bash
pip install Pillow
python -m exifgeo.cli photo.jpg
```

## Usage

Analyze a single image:

```bash
exifgeo photo.jpg
```

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
  ! Make: Camera or phone manufacturer
  ! Model: Specific device model
============================================================
```

Scan a directory and show only images that contain GPS data:

```bash
exifgeo ~/Pictures --recursive --gps-only
```

Emit JSON for use in another tool:

```bash
exifgeo photo.jpg --json
```

Show the complete metadata dump:

```bash
exifgeo photo.jpg --verbose
```

### Options

| Flag | Description |
|------|-------------|
| `-j`, `--json` | Output machine-readable JSON instead of a terminal report. |
| `-r`, `--recursive` | Descend into subdirectories when the target is a folder. |
| `-v`, `--verbose` | Include the full metadata dump in the report. |
| `--gps-only` | Only display images that contain GPS coordinates. |
| `--no-color` | Disable ANSI colors (useful when redirecting output to a file). |

## Why this exists

This started as a way to demonstrate, concretely, how location metadata leaks through ordinary photos. The same capability cuts two ways: defensively, it lets you audit what your own images expose before you share them; in research, it's a building block for open-source investigation work. The privacy-risk scoring and sensitive-field flagging are there to make the "so what" obvious at a glance rather than burying it in a wall of raw tags.

## Responsible use

Only analyze images you own or are authorized to inspect. This tool reads metadata that is already present in files you provide — it does not bypass any protection or access anything remotely — but the information it surfaces (precise location, timestamps, device identifiers) is sensitive by nature. Use it to protect privacy, not to violate it.

## Running the tests

```bash
python -m unittest discover -s tests -v
```

## License

MIT — see [LICENSE](LICENSE).
