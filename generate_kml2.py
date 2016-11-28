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
from pyproj import Proj

def kmlCoords(coords):
    return ','.join([str(x) for x in coords])

def addDistanceToCoords(coords, lengths):
    """Return a comma delimted string of 'lon,lat,elev' with the distances (m) in the lengths argument added to the (lon,lat,elev) coordinates in coords"""
    p = Proj(proj='utm',zone='59G',ellps='WGS84')
    x,y = p(coords[0], coords[1])
    lon, lat = p(x + lengths[0], y + lengths[1], inverse=True)
    new_coords = [str(lon), str(lat), str(coords[2])]

    return ','.join(new_coords)

def main():
    kml = simplekml.Kml(name='GPS Sensor displacement for Kaikoura Earthquake 14 Nov 2016', open=1)

    freq = 1.0 # frequency in Hz to play back.
    samp_rate = 1.0/freq # Google Earth wants duration (sample rate) between measurements
    hscale = 50.0 # horizontal scaling factor to multiply displacement by
    vscale = 50.0 # vertical scaling factor to multiply displacement by
    vector_evel = 200
    # cols = ['sec-past-eq', 'dNorth', 'dEast', 'u(cm)']
    # skiprows = [1]
    cols = ['dNorth', 'dEast', 'dHeight']
    skiprows = [1]

    filenames = glob('*.LC')
    station_info = station_coords()

    horiz_anim = kml.newgxtour(name="Play timeline")
    horiz_playlist = horiz_anim.newgxplaylist()

    datasets = OrderedDict() # store all dataframes in this dict, station_id:data.
    hvects = OrderedDict() # store all horiz vector objects to be updated later
    vvects = OrderedDict() # store all vert vector objects to be updated later

    for filename in filenames:
        # print filename
        station = filename.split('.')[2].upper()

        # get the data for this station name as a Pandas dataframe
        data = read_file(filename, cols, skiprows)
        data = data.reset_index(drop=True)

        # normalise the data so we're starting at 0.  Could be smarter and average this over a certain time period...
        # data = data - data.iloc[0]
        data[cols[0]][:] = (data[cols[0]] - data[cols[0]][0]) * hscale
        data[cols[1]][:] = (data[cols[1]] - data[cols[1]][0]) * hscale
        data[cols[2]][:] = (data[cols[2]] - data[cols[2]][0]) * vscale

        # # Add a point with a label for the GPS station
        station_lonlat = [float(station_info[station]['lon']), float(station_info[station]['lat']), vector_evel]
        station_pt = kml.newpoint(name=station, coords=[station_lonlat])
        station_pt.style.iconstyle.scale = 0.3
        station_pt.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/paddle/red-stars-lv.png'

        # Add a zero length line for horizontal displacement, which will be modified later to make the animation
        hvect = kml.newlinestring(name=station+'_horizontal_vector')
        hvect.coords = [station_lonlat, station_lonlat]
        hvect.style.linestyle.width = 5
        hvect.style.linestyle.color = simplekml.Color.white
        hvect.altitudemode = simplekml.AltitudeMode.relativetoground
        hvects[station] = hvect

        # Add a zero length line for vertical displacement, also modified later
        vvect = kml.newlinestring(name=station+'_vertical_vector')
        vvect.coords = [station_lonlat, station_lonlat]
        vvect.style.linestyle.width = 5
        vvect.style.linestyle.color = simplekml.Color.red
        vvect.altitudemode = simplekml.AltitudeMode.relativetoground
        vvects[station] = vvect

        # save the dataframe for concatenation later
        datasets[station] = data

    # contact and sort all the data based on time.  Avoids joining and filling gaps.  The data appear to have the same time
    # samples anyway but this handles both cases
    allData = pd.concat(datasets.values(), keys=datasets.keys())
    allData = allData.swaplevel(0, 1).sort()

    # iterate over all the indicies (with corresponding times), then iterate over station names and add a wait in between each timestep.
    for idx in allData.index.levels[0]:

        changes = []

        # for idx in indexes:
        timestep = allData.loc[idx]
        for station_name, row in timestep.iterrows():
            # coords need to be in lon, lat, elev
            h_delta = row.loc[[cols[1], cols[0], cols[2]]]

            # end point for vector should be at same elev at start.
            h_delta[cols[2]] = 0

            # update the horizontal vector
            station_lonlat = [float(station_info[station_name]['lon']), float(station_info[station_name]['lat']), vector_evel]
            station_kml_coords = kmlCoords(station_lonlat)
            h_vect = hvects[station_name]
            h_update = '<LineString targetId="{0}"><coordinates>{1} {2}</coordinates></LineString>'
            changes.append(h_update.format(h_vect.id, station_kml_coords, addDistanceToCoords(station_lonlat, h_delta)))

            # update the vertical vector TODO: if negative make it blue
            v_vect = vvects[station_name]
            v_delta = [0, row.loc[cols[2]], 0]
            v_update = '<LineString targetId="{0}"><coordinates>{1} {2}</coordinates></LineString>'
            changes.append(v_update.format(v_vect.id, station_kml_coords, addDistanceToCoords(station_lonlat, v_delta)))

            if v_delta[1] < 0:
                colour = 'ffff0000' # blue
            else:
                colour = 'ff0000ff' # red

            changes.append('<LineStyle targetId="%s"><color>%s</color></LineStyle>' % (v_vect.style.linestyle.id, colour))

        # if idx == 3: return

        animatedupdate = horiz_playlist.newgxanimatedupdate(gxduration=samp_rate)
        animatedupdate.update.change = ''.join(changes)

        wait = horiz_playlist.newgxwait(gxduration=samp_rate)


    wait = horiz_playlist.newgxwait(gxduration=samp_rate)

    kml.save("test.kml")
    # kml.savekmz("test.kmz")

if __name__ == '__main__':
    main()