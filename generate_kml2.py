#!/usr/bin/env python
"""Writing a Google Earth KML file for earthquake displacement animation.  Each 10Hz GPS file represents
measurements at a unique station.  All displacements are plotted as lines that change orientation and length
with the X/Y/Z displacement"""

from glob import glob
import pandas as pd
from collections import OrderedDict
import simplekml
from stations import station_coords
from displacement import read_file

def kmlCoords(coords):
    return ','.join([str(x) for x in coords])

def absoluteChange(orig, delta):
    return ','.join([str(x+y) for x, y in zip(orig, delta)])

def main():
    kml = simplekml.Kml(name='GPS Sensor displacement for Kaikoura Earthquake 14 Nov 2016', open=1)


    # TODO: set at 10 for actual speed
    freq = 100.0 # frequency in Hz to play back.
    samp_rate = 1.0/freq # Google Earth wants duration (sample rate) between measurements
    hscale = 0.001 # horizontal scaling factor to multiply displacement by.  Current in Lat/lon which makes no sense, need to change!
    vector_evel = 50
    cols = ['sec-past-eq', 'n(cm)', 'e(cm)', 'u(cm)']
    skiprows = [1]

    filenames = glob('*.reformat')
    # filenames = ['10hz-318.DHU.hanm.LC.reformat', '10hz-318.DHU.kaik.LC.reformat']
    station_info = station_coords()

    horiz_anim = kml.newgxtour(name="Play horizontal displacement animation")
    horiz_playlist = horiz_anim.newgxplaylist()

    datasets = OrderedDict() # store all dataframes in this dict, station_id:data.
    hvects = OrderedDict() # store all vector objects to be updated later

    for filename in filenames:
        # print filename
        station = filename.split('.')[2].upper()

        # get the data for this station name as a Pandas dataframe
        data = read_file(filename, cols, skiprows)
        data.set_index('sec-past-eq')

        # normalise the data so we're starting at 0.  Could be smarter and average this over a certain time period...
        # data = data - data.iloc[0]
        data['n(cm)'][:] = (data['n(cm)'] - data['n(cm)'][0]) * hscale
        data['e(cm)'][:] = (data['e(cm)'] - data['e(cm)'][0]) * hscale

        # # Add a point with a label for the GPS station
        station_lonlat = [float(station_info[station]['lon']), float(station_info[station]['lat']), vector_evel]
        station_pt = kml.newpoint(name=station, coords=[station_lonlat])
        station_pt.style.iconstyle.scale = 0.3
        station_pt.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/paddle/red-stars-lv.png'

        # Add a zero length line for horizontal displacement, which will be modified later to make the animation
        hvect = kml.newlinestring(name='station X')
        hvect.coords = [station_lonlat, station_lonlat]
        hvect.style.linestyle.width = 5
        hvect.style.linestyle.color = simplekml.Color.white
        hvect.altitudemode = simplekml.AltitudeMode.relativetoground

        # save the dataframe for concatenation later
        datasets[station] = data
        hvects[station] = hvect

    # contact and sort all the data based on time.  Avoids joining and filling gaps.  The data appear to have the same time
    # samples anyway but this handles both cases
    allData = pd.concat(datasets.values(), keys=datasets.keys())
    allData = allData.swaplevel(0, 1).sort('sec-past-eq')

    # iterate over all the indicies (with corresponding times), then iterate over station names and add a wait in between each timestep.
    for idx in allData.index.levels[0]:
        # for idx in indexes:
        timestep = allData.loc[idx]
        for station_name, row in timestep.iterrows():
            # coords need to be in lon, lat, elev
            delta = row.loc[['e(cm)', 'n(cm)', 'u(cm)']]

            # end point for vector should be at same elev at start.  TODO: handle this differently...
            delta['u(cm)'] = 0

            # station_name = indexes[1]
            station_lonlat = [float(station_info[station_name]['lon']), float(station_info[station_name]['lat']), vector_evel]
            vect = hvects[station_name]
            animatedupdate = horiz_playlist.newgxanimatedupdate(gxduration=samp_rate)
            updateStr = '<LineString targetId="{0}"><coordinates>{1} {2}</coordinates></LineString>'
            animatedupdate.update.change = updateStr.format(vect.id, kmlCoords(station_lonlat), absoluteChange(station_lonlat, delta))

        wait = horiz_playlist.newgxwait(gxduration=samp_rate)


    wait = horiz_playlist.newgxwait(gxduration=samp_rate)

    kml.save("test.kml")


    #     print index, station_name
    # for indexes, row in allData.iterrows():
    #     # coords need to be in lon, lat, elev
    #     delta = row[['e(cm)', 'n(cm)', 'u(cm)']]
    #
    #     # end point for vector should be at same elev at start
    #     delta['u(cm)'] = 0
    #
    #     station_name = indexes[1]
    #     vect = hvects[station_name]
    #     animatedupdate = horiz_playlist.newgxanimatedupdate(gxduration=samp_rate)
    #     updateStr = '<LineString targetId="{0}"><coordinates>{1} {2}</coordinates></LineString>'
    #     animatedupdate.update.change = updateStr.format(vect.id, kmlCoords(station_lonlat), absoluteChange(station_lonlat, delta))
    #
    #     wait = horiz_playlist.newgxwait(gxduration=samp_rate)
    #
    #
    # wait = horiz_playlist.newgxwait(gxduration=samp_rate)
    #
    # kml.save("test.kml")


if __name__ == '__main__':
    main()