#!/usr/bin/env python
"""Second attempt at writing KML for earthquake displacement.  Using simplekml which will hopefully be, well, simpler"""

import simplekml

kml = simplekml.Kml(name='GPS Sensor displacement for Kaikoura Earthquake 14 Nov 2016', open=1)

# pnt = kml.newpoint(coords=[(170.144,-43.605)])
# pnt.style.iconstyle.scale = 1.0

# Adding a line, as a poor man's arrow.  I guess we could make an arrow from several segments as a func...
# TODO: start with a line of length zero (no displacement), use a func to modify it's length based on n/e.  Make it a vector.  Could do 3D
ln = kml.newlinestring(name='A LineString')
ln.coords = [(170.12, -43.65, 1000), (170.14, -43.60, 1000)]
ln.style.linestyle.width = 1
ln.style.linestyle.color = simplekml.Color.red
ln.altitudemode = simplekml.AltitudeMode.relativetoground

tour = kml.newgxtour(name="Play me!")
playlist = tour.newgxplaylist()

# soundcue = playlist.newgxsoundcue()
# soundcue.href = "http://code.google.com/p/simplekml/source/browse/samples/drum_roll_1.wav"
# soundcue.gxdelayedstart = 2

animatedupdate = playlist.newgxanimatedupdate(gxduration=1.0)
animatedupdate.update.change = '<LineStyle targetId="{0}"><width>500.0</width></LineStyle>'.format(ln.style.linestyle.id)

wait = playlist.newgxwait(gxduration=1.0)
animatedupdate2 = playlist.newgxanimatedupdate(gxduration=1.0)
animatedupdate2.update.change = '<LineStyle targetId="{0}"><width>1.0</width></LineStyle>'.format(ln.style.linestyle.id)

# flyto = playlist.newgxflyto(gxduration=0.1)
# flyto.camera.longitude = 170.157
# flyto.camera.latitude = -43.671
# flyto.camera.altitude = 9700
# flyto.camera.heading = -6.333
# flyto.camera.tilt = 33.5
# flyto.camera.roll = 0

wait = playlist.newgxwait(gxduration=2.0)

kml.save("tut_tours.kml")