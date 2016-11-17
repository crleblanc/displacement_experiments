# fetch locations of GPS stations from https://magma.geonet.org.nz/delta/app

# external dependency, satisfy with "pip install requests" or similar
import requests  # also look at filename, headers = urllib.urlretrieve('http://coastwatch.pfeg.noaa.gov/erddap/tabledap/apdrcArgoAll.nc?longitude,latitude,time&longitude>=0&longitude<=360&latitude>=-90&latitude<=90&time>=2010-01-01&time<=2010-01-08&distinct()')
import xml.etree.ElementTree as ET

# TODO: cache this locally?
def station_coords():
    """Return a dict containing string keys and dict objects.  Objects have keys of : code, network, name, lat, lon, opened.
    code is the short name for the site, lat and lon are in decimal degrees.  See magma.geonet.org.nz/delta/app for more info"""
    r = requests.get('http://magma.geonet.org.nz/ws-delta/site?type=cgps')
    response = {x.attrib['code']: x.attrib for x in ET.fromstring(r.text)}
    return response

    #return [x.attrib for x in ET.fromstring(r.text)]
