
#!/usr/bin/env python
#
#   prediction with day and night markers
#
import urllib.request
import requests
import csv
import numpy as np
import simplekml
from datetime import datetime
from astral import Observer
from astral.sun import elevation


class Constants:
   # org   source_url = "https://api.v2.sondehub.org/tawhiri?profile=float_profile&launch_datetime=2024-12-17T08:50Z&stop_datetime=2024-12-20T08:50Z&launch_latitude=49.885&launch_longitude=8.0735&launch_altitude=223&ascent_rate=0.4&float_altitude=8500&format=csv"
   source_url = "https://api.v2.sondehub.org/tawhiri?profile=float_profile&launch_datetime=@@usr_date_start@@T@@usr_date_start_time@@:00Z&stop_datetime=@@usr_date_end@@T@@usr_date_end_time@@:00Z&launch_latitude=@@usr_loc_start_lon@@&launch_longitude=@@usr_loc_start_lat@@&launch_altitude=@@usr_loc_start_height@@&ascent_rate=@@usr_ascent@@&float_altitude=@@usr_float_alt@@&format=csv"
   local_filename = "test.csv"

# --------------------------------------------------

def download_file(url, local_filename):
    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print(f"Datei erfolgreich heruntergeladen und als '{local_filename}' gespeichert.")
    except requests.exceptions.RequestException as e:
        print(f"Fehler beim Herunterladen der Datei: {e}")

# --------------------------------------------------

def read_csv_to_arrays(filename):
    # Initialisierung der dynamischen Arrays
    datetime_array = []
    latitude_array = []
    longitude_array = []
    altitude_array = []

    try:
        with open(filename, 'r') as csvfile:
            csvreader = csv.DictReader(csvfile)

            for row in csvreader:
                # Konvertierung und Hinzufügen der Daten zu den entsprechenden Arrays
                datetime_array.append(datetime.fromisoformat(row['datetime'].replace("Z","+00:00")))
                latitude_array.append(float(row['latitude']))
                longitude_array.append(float(row['longitude']))
                altitude_array.append(float(row['altitude']))

        print(f"Daten erfolgreich eingelesen. Anzahl der Einträge: {len(datetime_array)}")
        return datetime_array, latitude_array, longitude_array, altitude_array

    except FileNotFoundError:
        print(f"Die Datei {filename} wurde nicht gefunden.")
    except KeyError as e:
        print(f"Fehler: Die Spalte {e} fehlt in der CSV-Datei.")
    except ValueError as e:
        print(f"Fehler beim Konvertieren der Daten: {e}")
    except Exception as e:
        print(f"Ein unerwarteter Fehler ist aufgetreten: {e}")

    return None, None, None, None

# --------------------------------------------------

def find_interval_change(datetime_data):
    # Berechne die Differenzen zwischen aufeinanderfolgenden Zeitstempeln
    time_diffs = np.diff(datetime_data)

    # Konvertiere die Differenzen in Minuten
    diff_minutes = time_diffs.astype('timedelta64[m]').astype(int)

    # Finde den ersten Index, wo die Differenz nicht mehr 2 Minuten beträgt
    change_index = np.where(diff_minutes != 2)[0]

    if len(change_index) > 0:
        return change_index[0] + 1  # +1, weil np.diff die Länge um 1 reduziert
    else:
        return None  # Falls kein Wechsel gefunden wurde


# --------------------------------------------------

def create_kml_line(datetime_data, latitude_data, longitude_data, altitude_data, change_index):
    kml = simplekml.Kml()

    # Erstelle eine Linie (LineString)
    linestring = kml.newlinestring(name="Flugbahn")

    # Füge die Koordinaten zur Linie hinzu
    coordinates = []
    last_sun_altitude = sun_elevation = get_sun_elevation(datetime_data[0], latitude_data[0],  longitude_data[0])
    for i, (lat, lon, alt) in enumerate(zip(latitude_data, longitude_data, altitude_data)):
        coordinates.append((lon, lat, alt))
        if i > 0:
            sun_altitude = sun_elevation = get_sun_elevation(datetime_data[i], latitude_data[i],  longitude_data[i])
            if last_sun_altitude < 0 and sun_altitude >=0: 
               # Einen neuen Punkt (Marker) hinzufügen
               pnt = kml.newpoint(name="SunSet", description=f"Sunset at {datetime_data[i]}", coords=[(lon, lat, alt)])
               # Optionale Anpassungen
               pnt.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/shapes/sunny.png'
               pnt.style.iconstyle.scale = 1.2
               pnt.style.labelstyle.color = simplekml.Color.red

            if last_sun_altitude >= 0 and sun_altitude <0: 
               # Einen neuen Punkt (Marker) hinzufügen
               pnt = kml.newpoint(name="Night", description=f"Sundown at {datetime_data[i]}", coords=[(lon, lat, alt)])
               # Optionale Anpassungen
               pnt.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/paddle/orange-stars.png'
               pnt.style.iconstyle.scale = 1.2
               pnt.style.labelstyle.color = simplekml.Color.red
	    # alten Wert merken
            last_sun_altitude = sun_altitude
        if i == 0:
            # Einen neuen Punkt (Marker) hinzufügen
            pnt = kml.newpoint(name="Startplatz", description=f"{datetime_data[i]}\nSun angle: {last_sun_altitude}", coords=[(lon, lat, alt)])
            # Optionale Anpassungen
            pnt.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/shapes/homegardenbusiness.png'
            pnt.style.iconstyle.scale = 1.2
            pnt.style.labelstyle.color = simplekml.Color.yellow
        elif i == change_index:
            # Einen neuen Punkt (Marker) hinzufügen
            pnt = kml.newpoint(name="Floating", description=f"Float level reached at:\n{datetime_data[i]}", coords=[(lon, lat, alt)])
            # Optionale Anpassungen
            pnt.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/paddle/F.png'
            pnt.style.iconstyle.scale = 1.2
            pnt.style.labelstyle.color = simplekml.Color.red
        elif i == len(latitude_data)-1:
            # Einen neuen Punkt (Marker) hinzufügen
            pnt = kml.newpoint(name="End Projection", description=f"Projection end:\n{datetime_data[i]}\n{lon}\n{lat}",  coords=[(lon, lat, alt)])
            # Optionale Anpassungen
            pnt.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/paddle/pause.png'
            pnt.style.iconstyle.scale = 1.2
            pnt.style.labelstyle.color = simplekml.Color.blue

    linestring.coords = coordinates

    # Setze Eigenschaften der Linie
    linestring.extrude = 1
    linestring.altitudemode = simplekml.AltitudeMode.absolute
    linestring.style.linestyle.width = 4
    linestring.style.linestyle.color = simplekml.Color.blue

    # Speichere die KML-Datei
    kml.save("test.kml")

    print("KML-Datei 'test.kml' wurde erfolgreich erstellt.")


# --------------------------------------------------

def get_sun_elevation(date, lat, lon):
    observer = Observer(latitude=lat, longitude=lon)
    return elevation(observer, date)

# --------------------------------------------------

def mainprogram():
    print("=========================================================")
    print("Create KML file with sun markers based on prediction path")
    print("=========================================================")
    # check if user input saved before
    saved_data = {}
    try:
        with open("user_data.txt", "r") as file:
            for line in file:
                key, value = line.strip().split(": ")
                saved_data[key] = value
    except FileNotFoundError:
        pass

    # Input from user

    # ---- > validerungsbeispiel für ein Datum
    #import re

    #while True:
    #    date = input("Datum (DD.MM.YYYY): ")
    #    if re.match(r'\d{2}\.\d{2}\.\d{4}', date):
    #        break
    #    print("Ungültiges Format. Bitte versuchen Sie es erneut.")

    usr_date_start=input(f"Start date [yyyy-mm-dd] [{saved_data.get('usr_date_start', '')}]: ")
    if usr_date_start=='':
       usr_date_start=saved_data.get('usr_date_start', '')

    usr_date_start_time=input(f"Start time UTC [hh:mm] [{saved_data.get('usr_date_start_time', '')}]: ")
    if usr_date_start_time=='':
       usr_date_start_time=saved_data.get('usr_date_start_time', '')

    usr_loc_start_lon=input(f"Location start in decimal [logtitude] [{saved_data.get('usr_loc_start_lon', '')}]: ")
    if usr_loc_start_lon=='':
       usr_loc_start_lon=saved_data.get('usr_loc_start_lon', '')

    usr_loc_start_lat=input(f"Location start in decimal [latitude] [{saved_data.get('usr_loc_start_lat', '')}]: ")
    if usr_loc_start_lat=='':
       usr_loc_start_lat=saved_data.get('usr_loc_start_lat', '')

    usr_loc_start_height=input(f"Height of start location in meters [{saved_data.get('usr_loc_start_height', '')}]: ")
    if usr_loc_start_height=='':
       usr_loc_start_height=saved_data.get('usr_loc_start_height', '')

    usr_float_alt=input(f"Float altitude in meters [{saved_data.get('usr_float_alt', '')}]: ")
    if usr_float_alt=='':
       usr_float_alt=saved_data.get('usr_float_alt', '')

    usr_ascent=input(f"Ascent rate in meters/second [{saved_data.get('usr_ascent', '')}]: ")
    if usr_ascent=='':
       usr_ascent=saved_data.get('usr_ascent', '')

    usr_date_end=input(f"End date [yyyy-mm-dd] [{saved_data.get('usr_date_end', '')}]: ")
    if usr_date_end=='':
       usr_date_end=saved_data.get('usr_date_end', '')

    usr_date_end_time=input(f"End time UTC [hh:mm] [{saved_data.get('usr_date_end_time', '')}]: ")
    if usr_date_end_time=='':
       usr_date_end_time=saved_data.get('usr_date_end_time', '')

    # Check if values are ok / converting?
    # Write to file 
    with open("user_data.txt", "w") as file:
        file.write(f"usr_date_start: {usr_date_start}\n")
        file.write(f"usr_date_start_time: {usr_date_start_time}\n")
        file.write(f"usr_loc_start_lon: {usr_loc_start_lon}\n")
        file.write(f"usr_loc_start_lat: {usr_loc_start_lat}\n")
        file.write(f"usr_loc_start_height: {usr_loc_start_height}\n")
        file.write(f"usr_float_alt: {usr_float_alt}\n")
        file.write(f"usr_ascent: {usr_ascent}\n")
        file.write(f"usr_date_end: {usr_date_end}\n")
        file.write(f"usr_date_end_time: {usr_date_end_time}\n")

    # print("Source URL: ")
    # print(Constants.source_url)
    # Werte einsetzen
    source_url_filled = Constants.source_url
    source_url_filled = source_url_filled.replace("@@usr_date_start@@",usr_date_start)
    source_url_filled = source_url_filled.replace("@@usr_date_start_time@@",usr_date_start_time)
    source_url_filled = source_url_filled.replace("@@usr_loc_start_lon@@",usr_loc_start_lon)
    source_url_filled = source_url_filled.replace("@@usr_loc_start_lat@@",usr_loc_start_lat)
    source_url_filled = source_url_filled.replace("@@usr_loc_start_height@@",usr_loc_start_height)
    source_url_filled = source_url_filled.replace("@@usr_float_alt@@",usr_float_alt)
    source_url_filled = source_url_filled.replace("@@usr_ascent@@",usr_ascent);
    source_url_filled = source_url_filled.replace("@@usr_date_end@@",usr_date_end)
    source_url_filled = source_url_filled.replace("@@usr_date_end_time@@",usr_date_end_time)
    print("Filled URL: ")
    print(source_url_filled)
    print("---")

    # Datei herunterladen
    download_file(source_url_filled, Constants.local_filename)
    datetime_data, latitude_data, longitude_data, altitude_data = read_csv_to_arrays(Constants.local_filename)

    if datetime_data:
       print(f"Erstes Datum: {datetime_data[0]}")
       print(f"Erste Latitude: {latitude_data[0]}")
       print(f"Erste Longitude: {longitude_data[0]}")
       print(f"Erste Altitude: {altitude_data[0]}")

       print(f"Anzahl Elemente: {len(datetime_data)}")

       print(f"Letztes Datum: {datetime_data[len(datetime_data)-1]}")
       # wechsel von 2 Minuten auf 20 Minuten?  Ab diesem Index ist Float Altitude erreicht
       index = find_interval_change(datetime_data)
       if index is not None:
         print(f"Der Übergang findet bei Index {index} statt.")
       else:
         print("Kein Übergang gefunden.")
       create_kml_line(datetime_data, latitude_data, longitude_data, altitude_data, index)
       # Beispielaufruf
       sun_elevation = get_sun_elevation(datetime_data[0], latitude_data[0],  longitude_data[0])
       print(f"Sonnenhöhe am {datetime_data[0]}: {sun_elevation:.2f}°")

# --------------------------------------------------

if __name__ == "__main__":
    mainprogram()

 
