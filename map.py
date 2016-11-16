#!/usr/bin/env python

from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
from stations import getStationCoords

# Attempt to animate the GPS tensors in time to visualise the earthquake deformation


def main():

    stationInfo = getStationCoords()
    #print stationInfo

    # TODO: use matplotlib to start off with (slow) and animate it over every row in the data, making a map for horizontal and vertical diffs
    m = Basemap(projection='mill', resolution='c', llcrnrlon=170.0, llcrnrlat=-46.0, urcrnrlon=177.0, urcrnrlat=-39.0, lon_0=180)
    # m.bluemarble()
    m.shadedrelief()

    # TODO: for now plot markers at each station.  Later animate this as tensors, sequentially through input files (many!).  Use scatter instead of plot, use an array of points.
    for station in ('cmbl', 'hanm', 'hoki', 'kaik', 'maha', 'mrbl', 'with', 'yald'):
        info = stationInfo[station.upper()]
        print station, info
        #m.plot(float(info['lat']), float(info['lon']), marker='*')
        print m(float(info['lon']), float(info['lat']))
        x, y = m(float(info['lon']), float(info['lat']))
        m.scatter(x, y, 30, marker='o', color='k')

    plt.show()


if __name__ == '__main__':
    main()