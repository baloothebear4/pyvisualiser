"""
    Audio Visualiser programme based on preDAC recorder
    this is a sandpit environment to create ideas for use on preDAC
    but using pygame as a renderer to test on Mac OS

    This version aims to simulate the new display and create a range of visually appealing spectrum
    analysers:  Variables to experiment:
        - smoothing
        - decay profiles
        - peak profiles
        - bars made of rectangles

"""
# from    processaudio import AudioProcessor
# from    roon import Roon
# from    displaydriver import GraphicsDriverMac
from    screens import *
# from    events import Events
# from    framecore import ListNext
from    screenhandler import ScreenController

""" Screen types are:   Control for utility messages like vol change,  Test to exercise functionality, Base for mixed visual displays """
# TestVUMetersScreen, TestVUScreen,  
# TestScreen, TestVUImageScreen1, TestVisualiserScreen, TestVUMetersScreen, TestVUScreen, TestSpectrumScreen, TestScreen,\
# TestVUScreen, TestVUImageScreen1, TestVUImageScreen2, TestVUMetersScreen, TestSpectrumScreen 

SCREENS = ( ArtistScreen, MetaVUScreen, BigDialsScreen, TrackScreen, TrackSpectrumScreen, TrackSpectrumScreen2, TrackSpectrumScreen3, TrackSpectrumScreen4, \
            TrackOscScreen, TrackVisScreen, TrackVisScreen2, TrackVisScreen3, TrackVUMeterScreen, TrackVUMeterScreen2,  )
    
PI_PLATFORM  = { "gfx": "pi_kms", "loopback":"loopin", "roon_zone":"MacViz" }
MAC_PLATFORM = { "gfx": "mac", "loopback":"BlackHole 2ch", "roon_zone":"MacViz" }

if __name__ == "__main__":

    visualiser = ScreenController(SCREENS, hw_platform=PI_PLATFORM )

    try:
        visualiser.run()
    except KeyboardInterrupt:
        visualiser.stop()
