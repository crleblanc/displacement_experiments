#!/usr/bin/env python
"""Second attempt at writing KML for earthquake displacement.  Using simplekml which will hopefully be, well, simpler"""

from glob import glob
import simplekml
from stations import station_coords
from displacement import read_file

def kmlCoords(coords):
    return ','.join([str(x) for x in coords])

def absoluteChange(orig, delta):
    return ','.join([str(x+y) for x, y in zip(orig, delta)])

def main():
    kml = simplekml.Kml(name='GPS Sensor displacement for Kaikoura Earthquake 14 Nov 2016', open=1)

    samp_rate = 0.1 # duration between samples
    freq = 1.0/samp_rate
    hscale = 0.01 # horizontal scaling factor to multiply displacement by
    vector_evel = 1000
    cols = ['dNorth', 'dEast', 'dHeight']
    skiprows = [1]
    # if args.format == 'LC':
    #     cols = ['dNorth', 'dEast', 'dHeight']
    #     skiprows = [1]
    # else:
    #     cols = ['n(cm)', 'e(cm)', 'u(cm)']
    #     skiprows = None


    filenames = glob('*.LC')
    station_info = station_coords()

    horiz_anim = kml.newgxtour(name="Play horizontal displacement animation")
    horiz_playlist = horiz_anim.newgxplaylist()

    for filename in filenames:
        print filename
        station = filename.split('.')[2].upper()

        # get the data for this station name as a Pandas dataframe
        data = read_file(filename, cols, skiprows)

        # normalise the data so we're starting at 0.  Could be smarter and average this over a certain time period...
        data = data - data.iloc[0]

        # # Add a point with a label for the GPS station
        station_lonlat = [float(station_info[station]['lon']), float(station_info[station]['lat']), vector_evel]
        station_pt = kml.newpoint(name=station, coords=[station_lonlat])
        station_pt.style.iconstyle.scale = 1.0
        station_pt.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/paddle/red-stars-lv.png'

        # Add a zero length line for horizontal displacement, which will be modified later to make the animation
        hvect = kml.newlinestring(name='station X')
        hvect.coords = [station_lonlat, station_lonlat]
        hvect.style.linestyle.width = 5
        hvect.style.linestyle.color = simplekml.Color.white
        hvect.altitudemode = simplekml.AltitudeMode.relativetoground

        data[cols[0]] *= hscale
        data[cols[1]] *= hscale

        for idx, row in data.iterrows():

            delta = (row[0], row[1], 0) # fix the elevation for this display, just horizontals.
            # delta = [x for x in row]
            # print station_lonlat
            # print delta
            # print kmlCoords(station_lonlat)
            # print absoluteChange(station_lonlat, delta)
            # print '--'

            animatedupdate = horiz_playlist.newgxanimatedupdate(gxduration=freq)
            updateStr = '<LineString targetId="{0}"><coordinates>{1} {2}</coordinates></LineString>'
            animatedupdate.update.change = updateStr.format(hvect.id, kmlCoords(station_lonlat), absoluteChange(station_lonlat, row))

            wait = horiz_playlist.newgxwait(gxduration=freq)

        # ln = kml.newlinestring(name='A LineString')
        # ln.coords = [station_lonlat, [173.533658856, -42.52546696906044, 0]]
        # ln.style.linestyle.width = 10
        # ln.style.linestyle.color = simplekml.Color.red
        # ln.altitudemode = simplekml.AltitudeMode.relativetoground
        #
        # tour = kml.newgxtour(name="Play displacement animation")
        # playlist = tour.newgxplaylist()
        #
        # for i, delta in enumerate([[0, 10, 0], [0, 100, 0], [0, 10, 0], [0, -10, 0]]):
        #
        #     animatedupdate = playlist.newgxanimatedupdate(gxduration=0.2)
        #     updateStr = '<LineString targetId="{0}"><coordinates>{1} {2}</coordinates></LineString>'
        #     print station_lonlat
        #     print delta
        #     print kmlCoords(station_lonlat)
        #     print absoluteChange(station_lonlat, delta)
        #     print '--'
        #     animatedupdate.update.change = updateStr.format(ln.id, kmlCoords(station_lonlat), absoluteChange(station_lonlat, delta))
        #
        #     wait = playlist.newgxwait(gxduration=0.2)


        wait = horiz_playlist.newgxwait(gxduration=freq)

    kml.save("test.kml")


if __name__ == '__main__':
    main()