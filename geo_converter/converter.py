from pyproj import Transformer
import mgrs
import folium

m = mgrs.MGRS()

# conversion functions

def dd_to_mgrs(lat, lon):
    return m.toMGRS(lat, lon).decode()

def mgrs_to_dd(mgrs_coord):
    lat, lon = m.toLatLon(mgrs_coord)
    return lat, lon

def dd_to_utm(lat, lon):

    zone = int((lon + 180) / 6) + 1

    hemisphere = "north" if lat >= 0 else "south"

    transformer = Transformer.from_crs(
        "EPSG:4326",
        f"+proj=utm +zone={zone} +{hemisphere}",
        always_xy=True
    )

    easting, northing = transformer.transform(lon, lat)

    return zone, easting, northing

def utm_to_dd(zone, easting, northing):

    transformer = Transformer.from_crs(
        f"+proj=utm +zone={zone}",
        "EPSG:4326",
        always_xy=True
    )

    lon, lat = transformer.transform(easting, northing)

    return lat, lon

# -----------------------------
# DMS Conversion
# -----------------------------

def decimal_to_dms(decimal):

    degrees = int(decimal)

    minutes_float = abs(decimal - degrees) * 60

    minutes = int(minutes_float)

    seconds = (minutes_float - minutes) * 60

    return degrees, minutes, seconds

# -----------------------------
# Map Plotting
# -----------------------------

def create_map(lat, lon):

    fmap = folium.Map(
        location=[lat, lon],
        zoom_start=12
    )

    folium.Marker(
        [lat, lon],
        popup=f"{lat}, {lon}"
    ).add_to(fmap)

    fmap.save("map.html")

# -----------------------------
# Main Program
# -----------------------------

print("\nCoordinate Converter & Plotter")
print("--------------------------------")
print("1. Decimal Degrees")
print("2. MGRS")

choice = input("\nChoose format: ")

if choice == "1":

    lat = float(input("Latitude: "))
    lon = float(input("Longitude: "))

elif choice == "2":

    mgrs_coord = input("MGRS: ")

    lat, lon = mgrs_to_dd(mgrs_coord)

else:
    print("Invalid option")
    exit()

print("\nResults")
print("--------------------------------")

print(f"Latitude : {lat}")
print(f"Longitude: {lon}")

print(f"MGRS     : {dd_to_mgrs(lat, lon)}")

zone, easting, northing = dd_to_utm(lat, lon)

print(f"UTM Zone : {zone}")
print(f"Easting  : {easting:.2f}")
print(f"Northing : {northing:.2f}")

lat_dms = decimal_to_dms(lat)
lon_dms = decimal_to_dms(lon)

print(
    f"DMS      : "
    f"{lat_dms[0]}°{lat_dms[1]}'{lat_dms[2]:.2f}\" , "
    f"{lon_dms[0]}°{lon_dms[1]}'{lon_dms[2]:.2f}\""
)

create_map(lat, lon)

print("\nMap saved as map.html")
