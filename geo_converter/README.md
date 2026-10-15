# geo_converter

A small Python tool that converts coordinates between formats and plots them on a map.

## What it does

You enter a point as decimal degrees or as an MGRS string. It prints the same point in:

- decimal degrees
- MGRS
- UTM (zone, easting, northing)
- DMS (degrees, minutes, seconds)

Then it saves an interactive map with a pin on the point as `map.html`.

## Why it's useful

Mapping and GEOINT work mixes coordinate formats all the time. This converts between the common ones and shows you the spot, without opening a GIS application.

## Requirements

- Python 3
- pyproj, mgrs, folium, packaging (see `requirements.txt`)

## How to run it

```bash
git clone https://github.com/roddyg01/public-projects.git
cd public-projects/geo_converter

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

python converter.py
```

Choose `1` for decimal degrees or `2` for MGRS, then enter the coordinates. Open the map when it's done:

```bash
open map.html
```

## Example output

Input: decimal degrees, `38.8895`, `-77.0353`

```
Results
--------------------------------
Latitude : 38.8895
Longitude: -77.0353
MGRS     : 18SUJ2347806483
UTM Zone : 18
Easting  : 323478.06
Northing : 4306483.24
DMS      : 38°53'22.20" , -77°2'7.08"

Map saved as map.html
```

## Ideas for later

- coordinate history log
- multiple points on one map
- batch conversion from CSV
- more map layers
- a simple GUI

## Note

A learning project for working with coordinate systems used in mapping and GEOINT.
