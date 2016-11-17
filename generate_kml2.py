#!/usr/bin/env python
"""Second attempt at writing KML for earthquake displacement.  Using simplekml which will hopefully be, well, simpler"""

import simplekml


def kmlCoords(coords):
    return ','.join([str(x) for x in coords])

def absoluteChange(orig, delta):
    return ','.join([str(x+y) for x, y in zip(orig, delta)])


kml = simplekml.Kml(name='GPS Sensor displacement for Kaikoura Earthquake 14 Nov 2016', open=1)

# pnt = kml.newpoint(coords=[(170.144,-43.605)])
# pnt.style.iconstyle.scale = 1.0

# example station coodinates, lon, lat, elev.
station_coords = [170.12, -43.65, 1000]

# Adding a line, as a poor man's arrow.  I guess we could make an arrow from several segments as a func...
# TODO: start with a line of length zero (no displacement), use a func to modify it's length based on n/e.  Make it a vector.  Could do 3D
ln = kml.newlinestring(name='A LineString')
ln.coords = [station_coords, station_coords]
ln.style.linestyle.width = 10
ln.style.linestyle.color = simplekml.Color.red
ln.altitudemode = simplekml.AltitudeMode.relativetoground

tour = kml.newgxtour(name="Play displacement animation")
playlist = tour.newgxplaylist()

for i, delta in enumerate([[0, 0.3, 0], [0, 0.1, 0], [0, 0.5, 0], [0, -0.2, 0]]):

    animatedupdate = playlist.newgxanimatedupdate(gxduration=0.2)
    updateStr = '<LineString targetId="{0}"><coordinates>{1} {2}</coordinates></LineString>'
    animatedupdate.update.change = updateStr.format(ln.id, kmlCoords(station_coords), absoluteChange(station_coords, delta))

    wait = playlist.newgxwait(gxduration=0.2)

wait = playlist.newgxwait(gxduration=0.1)

kml.save("test.kml")