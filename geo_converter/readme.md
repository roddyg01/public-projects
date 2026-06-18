# geo converter

a simple coordinate conversion and plotting tool written in python.

converts between:

* decimal degrees
* dms (degrees, minutes, seconds)
* utm
* mgrs

plots coordinates on an interactive map and exports the result as `map.html`.

this tool exists to quickly move between common geospatial formats and visualize the result without opening a gis application.

## install

```sh
git clone https://github.com/yourname/geo_converter
cd geo_converter

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

## run

```sh
python converter.py
```

follow the prompts and enter either decimal degree coordinates or an mgrs coordinate.

a map will be generated automatically:

```sh
open map.html
```

## example

```text
latitude: 38.8895
longitude: -77.0353
```

output:

```text
mgrs: 18suj2339407395

utm zone: 18
easting: 323394.00
northing: 4307395.00
```

## dependencies

* pyproj
* mgrs
* folium

## future improvements

* coordinate history logging
* multi-point plotting
* batch conversion from csv
* additional map layers
* simple gui

## disclaimer

learning project focused on geospatial analysis workflows and coordinate systems commonly encountered in mapping and geoint work.
