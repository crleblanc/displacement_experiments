#!/usr/bin/env python
"""Writing a Google Earth KML file for earthquake displacement animation.  Each 10Hz GPS file represents
measurements at a unique station.  All displacements are plotted as lines that change orientation and length
with the X/Y/Z displacement"""

from glob import glob
import pandas as pd
from collections import OrderedDict
import simplekml
from stations import station_coords
from pyproj import Proj

def kmlCoords(coords):
    """Convert from a sequence of floats to a comma delimited string"""
    return ','.join([str(x) for x in coords])

def distanceVector(coords, lengths):
    """Return a comma delimted string of 'lon,lat,elev' with the distances (m) in the lengths argument added to the
    (lon,lat,elev) coordinates in coords"""
    # would be much faster to operate on all coords at once, as numpy arrays.  Hardcoding to UTM zone 59G (NZ)
    p = Proj(proj='utm', zone='59G', ellps='WGS84')
    x,y = p(coords[0], coords[1])
    lon, lat = p(x + lengths[0], y + lengths[1], inverse=True)

    return kmlCoords((lon, lat, coords[2]))


class QuakeAnimation(object):

    def __init__(self, title=None, freq=1.0, hscale=50.0, vscale=50.0, vector_elev=200.0):
        self.kml = simplekml.Kml(name=title, open=1)
        self.freq = freq # frequency in Hz to play back.
        self.samp_rate = 1.0/self.freq # Google Earth wants duration (sample rate) between measurements
        self.hscale = hscale # horizontal scaling factor to multiply displacement by (units are in mm so it's actually hscale * 1000)
        self.vscale = vscale # vertical scaling factor to multiply displacement by
        self.vector_evel = vector_elev
        self.all_station_info = station_coords()
        self.stations_used = []
        self.cols = None
        self.data = None
        self.hvects = OrderedDict() # store all horiz vector objects
        self.vvects = OrderedDict() # store all vert vector objects

    def read_csvs(self, csv_files, column_names=None, skip_rows=None):
        """Read a list (or tuple) of CSV files (strings or URLs) using Pandas and store internally in a single large DataFrame"""
        datasets = OrderedDict() # store all dataframes in this dict, station_id:data.

        if column_names is None:
            self.cols = ['dNorth', 'dEast', 'dHeight']

        if skip_rows is None:
            skip_rows = [1]

        for filename in csv_files:
            # print filename
            station = filename.split('.')[2].upper()

            # get the data for this station name as a Pandas dataframe
            data = pd.read_csv(filename, delim_whitespace=True, usecols=self.cols, skiprows=skip_rows)
            # drop any junk
            data = data.dropna()
            # using a normal integer index starting from 0
            data = data.reset_index(drop=True)

            # normalise the data so we're starting at 0.  Could be smarter and average this over a certain time period...
            data[self.cols[0]][:] = (data[self.cols[0]] - data[self.cols[0]][0]) * self.hscale
            data[self.cols[1]][:] = (data[self.cols[1]] - data[self.cols[1]][0]) * self.hscale
            data[self.cols[2]][:] = (data[self.cols[2]] - data[self.cols[2]][0]) * self.vscale

            # save the dataframe for concatenation later
            datasets[station] = data

            self.stations_used.append(station)

        self.data = pd.concat(datasets.values(), keys=datasets.keys())
        self.data = self.data.swaplevel(0, 1).sort()

    def _create_objects(self):
        """Create all starting objects.  Some of them will be modified later by the animate method"""
        for station in self.stations_used:
            # # Add a point with a label for the GPS station
            station_lonlat = [float(self.all_station_info[station]['lon']), float(self.all_station_info[station]['lat']), self.vector_evel]
            station_pt = self.kml.newpoint(name=station, coords=[station_lonlat])
            station_pt.style.iconstyle.scale = 0.3
            station_pt.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/paddle/red-stars-lv.png'

            # Add a zero length line for horizontal displacement, which will be modified later to make the animation
            hvect = self.kml.newlinestring(name=station+'_horizontal_vector')
            hvect.coords = [station_lonlat, station_lonlat]
            hvect.style.linestyle.width = 5
            hvect.style.linestyle.color = simplekml.Color.white
            hvect.altitudemode = simplekml.AltitudeMode.relativetoground
            self.hvects[station] = hvect

            # Add a zero length line for vertical displacement, also modified later
            vvect = self.kml.newlinestring(name=station+'_vertical_vector')
            vvect.coords = [station_lonlat, station_lonlat]
            vvect.style.linestyle.width = 5
            vvect.style.linestyle.color = simplekml.Color.red
            vvect.altitudemode = simplekml.AltitudeMode.relativetoground
            self.vvects[station] = vvect

    def animate(self):
        """Create the kml animation from the data read using the read_csvs method.  Write to the output_file (string)"""

        self._create_objects()
        tour = self.kml.newgxtour(name="Play timeline")
        horiz_playlist = tour.newgxplaylist()

        # iterate over all the indicies (with corresponding times), then iterate over station names and add a wait in between each timestep.
        for idx in self.data.index.levels[0]:

            changes = []

            # for idx in indexes:
            timestep = self.data.loc[idx]
            for station_name, row in timestep.iterrows():
                # coords need to be in lon, lat, elev
                h_delta = row.loc[[self.cols[1], self.cols[0], self.cols[2]]]

                # end point for vector should be at same elev at start.
                h_delta[self.cols[2]] = 0

                # update the horizontal vector
                station_lonlat = [float(self.all_station_info[station_name]['lon']),
                                  float(self.all_station_info[station_name]['lat']),
                                  self.vector_evel]
                station_kml_coords = kmlCoords(station_lonlat)
                h_vect = self.hvects[station_name]
                h_update = '<LineString targetId="{0}"><coordinates>{1} {2}</coordinates></LineString>'
                changes.append(h_update.format(h_vect.id,
                                               station_kml_coords,
                                               distanceVector(station_lonlat, h_delta)))

                # update the vertical vector
                v_vect = self.vvects[station_name]
                v_delta = [0, row.loc[self.cols[2]], 0]
                v_update = '<LineString targetId="{0}"><coordinates>{1} {2}</coordinates></LineString>'
                changes.append(v_update.format(v_vect.id, station_kml_coords, distanceVector(station_lonlat, v_delta)))

                if v_delta[1] < 0:
                    colour = simplekml.Color.blue
                else:
                    colour = simplekml.Color.red

                changes.append('<LineStyle targetId="%s"><color>%s</color></LineStyle>' % (v_vect.style.linestyle.id, colour))

            animatedupdate = horiz_playlist.newgxanimatedupdate(gxduration=self.samp_rate)
            animatedupdate.update.change = ''.join(changes)

            wait = horiz_playlist.newgxwait(gxduration=self.samp_rate)

        wait = horiz_playlist.newgxwait(gxduration=self.samp_rate)

    def savekml(self, output_file):
        self.kml.save(output_file)

    def savekmz(self, output_file):
        self.kml.savekmz(output_file)

def main():
    anim = QuakeAnimation(title='GPS Sensor displacement for Kaikoura Earthquake, 14 Nov 2016')
    anim.read_csvs(glob('*.LC'))
    anim.animate()
    anim.savekml('test.kml')
    anim.savekmz('test.kmz')

if __name__ == '__main__':
    main()