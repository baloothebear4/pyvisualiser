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

from   screens import *
from   testscreens import *
from   screenhandler import ScreenController
import platform


""" Screen types are:   Control for utility messages like vol change,  Test to exercise functionality, Base for mixed visual displays """
# TestVUMetersScreen, TestVUScreen,  
# TestScreen, TestVUImageScreen1, TestVisualiserScreen, TestVUMetersScreen, TestVUScreen, TestSpectrumScreen, TestScreen,\
# TestVUScreen, TestVUImageScreen1, TestVUImageScreen2, TestVUMetersScreen, TestSpectrumScreen 

# SCREENS = ( ColAlignedScreen, TrackVUMeterScreen21 )
# SCREENS = ( MetaVUScreen, SpectrumBaseArt, MinSpectrumArt, ArtistScreen, TrackScreen, TrackSpectrumScreen, TrackSpectrumScreen2,\
#             TrackSpectrumScreen3, TrackSpectrumScreen4, \
#             TrackOscScreen, TrackVisScreen, TrackVisScreen2, TrackVisScreen3, TrackVUMeterScreen, TrackVUMeterScreen2, \
#             ArtMetaSpectrumScreen, MinSpectrumArt, SpectrumBaseArt, ColAlignedScreen  )
SCREENS = (ArtMetaSpectrumScreen, TrackVUMeterScreen2, ArtistScreen, MetaVUScreen , TrackOscScreen,TrackVisScreen3, MinSpectrumArt, TrackSpectrumScreen3, TrackVUMeterScreen, TrackSpectrumScreen, TrackSpectrumScreen2)
# SCREENS = (ColAlignedScreen, TrackVUMeterScreen2) #, ArtistScreen, MetaVUScreen , TrackOscScreen,TrackVisScreen3, TrackSpectrumScreen3, TrackVUMeterScreen,MinSpectrumArt)

""" 
    Determine the underlying hardware plaform - NB: Pi is assumed to use the KMS graphics driver 
    the loopback and roon zones are all configured by the user to match their system
""" 

PI_PLATFORM  = { "gfx": "pi_kms", "loopback":"loopin", "roon_zone":"pre3" }
MAC_PLATFORM = { "gfx": "mac", "loopback":"BlackHole 2ch", "roon_zone":"MacViz" }

def machine():
    uname = platform.uname()
    if uname.system == "Darwin":
        return MAC_PLATFORM
    elif uname.system == "Linux":
        if "rpi" in uname.release:
            return PI_PLATFORM
        else:
            return MAC_PLATFORM
    else:
        return MAC_PLATFORM
    
if __name__ == "__main__":

    visualiser = ScreenController(SCREENS, hw_platform=machine() )

    try:
        visualiser.run()
    except KeyboardInterrupt:
        visualiser.stop()
