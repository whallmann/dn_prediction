# dn_prediction
Day and Night markers in a api.v2.sondehub.org/tawhiri output format KML for visiting in G-Earth

## What is this python script for?

You like to start your own Balloons for a world trip. Your battery source are solar panels. So you 
like to make a prediction for the next few days and like to see on the map when the sun gets down or will come back.

I wrote this python program (my first).  It uses the https://api.v2.sondehub.org/tawhiri API described by 
[Astrohardy](https://astrohardy.de/radiosonde/predictapi.html). 

You give some data needed for a prediction and get a CSV (or KML) back.

The program here asks you this parameters and make a call to the API.

Then enrich the Datapoints in the output for START, FLOATLEVEL, SUNSET and SUNDOWN Markers (see picture).

![Google-Earth Hardcopy](https://github.com/whallmann/dn_prediction/blob/main/pictures/photo_2024-12-16_18-10-16.jpg)

## Change log
- Param /c inputs from last prediction endpoint the coordinats as new start point if you do not enter new coordinates
- FTP Upload possible: remark line ftp_upload if not nessesery. Otherwise fill out the destination, user and pw for an upload. This ist good for fast access by Browser Link and fast open a App to show the flight path visually


## Installation
- you need a virtual environment .venv (help is for unix)
  - cd /path/to/ur/project
  - python3 -m venv .venv
  - source .venv/bin/activate  (venv text is prefix on prompt)
  - pip install -r requirements.txt
  - _or_
  - pip install packetname_u_need
- We use some modules if shown as unknown: install it "pip install xxxx":
  - import urllib.request
  - import requests
  - import csv
  - import numpy as np
  - import simplekml
  - from datetime import datetime
  - from astral import Observer
  - from astral.sun import elevation

## Usage
- Start program by:  python3 test.py
- Enter requested informations (no input check yet)
- All Input will be safed for next start. Values are in [ ] and will be reused if only RETURN is pushed
- Some debug infos will be show that it works well. 
- If Error-Messages appear you entered some wrong data for the API. Check them and try again. API can only predict for about 4-5 days, so make your range smaller.
- Console output:
```
=========================================================
Create KML file with sun markers based on prediction path
=========================================================
Start date [yyyy-mm-dd] [2024-12-17]:
Start time UTC [hh:mm] [09:00]:
Location start in decimal [logtitude] [49.09]:
Location start in decimal [latitude] [8.07]:
Height of start location in meters [223]:
Float altitude in meters [8500]:
Ascent rate in meters/second [0.4]:
End date [yyyy-mm-dd] [2024-12-20]:
End time UTC [hh:mm] [09:00]:
Filled URL:
https://api.v2.sondehub.org/tawhiri?profile=float_profile&launch_datetime=2024-12-17T09:00:00Z&stop_datetime=2024-12-20T09:00:00Z&launch_latitude=49.09&launch_longitude=8.07&launch_altitude=223&ascent_rate=0.4&float_altitude=8500&format=csv
---
Datei erfolgreich heruntergeladen und als 'test.csv' gespeichert.
Daten erfolgreich eingelesen. Anzahl der Einträge: 374
Erstes Datum: 2024-12-17 09:00:00+00:00
Erste Latitude: 49.09
Erste Longitude: 8.07
Erste Altitude: 223.0
Anzahl Elemente: 374
Letztes Datum: 2024-12-20 09:00:00.937500+00:00
Der Übergang findet bei Index 173 statt.
KML-Datei 'test.kml' wurde erfolgreich erstellt.
Sonnenhöhe am 2024-12-17 09:00:00+00:00: 10.83°
```

