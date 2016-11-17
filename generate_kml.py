#!/usr/bin/env python

# TODO: Read GPS data from input files and generate a KML file that will show displacement over time using
# vectors in 3D.


from lxml import etree
from pykml.parser import Schema
from pykml.factory import KML_ElementMaker as KML
from pykml.factory import GX_ElementMaker as GX

# TODO: create a new IconStyle for each station.  Use AnimatedUpdate to update each station.  Updates seem to happen concurrently
# Yes they do, so loop over all stations and apply updates.  Duration should be equal to actual duration

doc = KML.kml(
    KML.Document(
        KML.name("gx:AnimatedUpdate example"),
        KML.Style(
            KML.IconStyle(
                KML.scale(1.0),
                KML.Icon(
                    KML.href("http://maps.google.com/mapfiles/kml/pushpin/ylw-pushpin.png"),
                ),
                id="mystyle"
            ),
            id="pushpin"
        ),
        KML.Style(
            KML.IconStyle(
                KML.scale(1.0),
                KML.Icon(
                    KML.href("http://maps.google.com/mapfiles/kml/pushpin/ylw-pushpin.png"),
                ),
                id="mystyle2"
            ),
            id="pushpin2"
        ),
        KML.Placemark(
            KML.name("Pin on a mountaintop"),
            KML.styleUrl("#pushpin"),
            KML.Point(
                KML.coordinates("170.1435558771009,-43.60505741890396,0")
            ),
            id="mountainpin1"
        ),
        KML.Placemark(
            KML.name("Pin2 on a mountaintop"),
            KML.styleUrl("#pushpin2"),
            KML.Point(
                KML.coordinates("170.1440558771009,-43.60535741890396,0")
            ),
            id="mountainpin2"
        ),
        GX.Tour(
            KML.name("Play me!"),
            GX.Playlist(
                # GX.FlyTo(
                #     GX.duration(1.0),
                #     # GX.flyToMode("bounce"),
                #     KML.Camera(
                #         KML.longitude(170.157),
                #         KML.latitude(-43.671),
                #         KML.altitude(9700),
                #         KML.heading(-6.333),
                #         KML.tilt(33.5),
                #     )
                # ),
                GX.AnimatedUpdate(
                    GX.duration(1),
                    KML.Update(
                        KML.targetHref(),
                        KML.Change(
                            KML.IconStyle(
                                KML.scale(10.0),
                                targetId="mystyle"
                            )
                        )
                    )
                ),
                # GX.Wait(
                #     GX.duration(1.0)
                # ),
                GX.AnimatedUpdate(
                    GX.duration(1),
                    KML.Update(
                        KML.targetHref(),
                        KML.Change(
                            KML.IconStyle(
                                KML.scale(0.3),
                                targetId="mystyle2"
                            )
                        )
                    )
                ),
                # animations appear to proceed during this Wait period
                GX.Wait(
                    GX.duration(1.0)
                )
            )
        )
    )
)

print etree.tostring(doc, pretty_print=True)

schema = Schema('kml22gx.xsd')
#import ipdb; ipdb.set_trace()
schema.validate(doc)

# output a KML file (named based on the Python script)
#outfile = file(__file__.rstrip('.py')+'.kml','w')
#outfile.write(etree.tostring(doc, pretty_print=True))