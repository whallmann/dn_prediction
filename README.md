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

