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
SCREENS = ( MetaVUScreen, SpectrumBaseArt, MinSpectrumArt, TrackScreen, TrackSpectrumScreen, TrackSpectrumScreen2,\
            TrackSpectrumScreen3, TrackSpectrumScreen4, \
            TrackOscScreen, TrackVisScreen, TrackVisScreen2, TrackVisScreen3, TrackVUMeterScreen, TrackVUMeterScreen2, \
            ArtMetaSpectrumScreen, MinSpectrumArt, SpectrumBaseArt, ColAlignedScreen  )
# SCREENS = (F7,F6,F5, F8)#, F4, F5, F7)# F5)#F4, F3, F1, F2)#F5, F3)ColAlignedScreen, ColAlignedScreen) #TrackVUMeterScreen, ArtMetaSpectrumScreen, TrackVUMeterScreen2, ArtistScreen, MetaVUScreen , TrackOscScreen,TrackVisScreen3, MinSpectrumArt, TrackSpectrumScreen3, TrackSpectrumScreen, TrackSpectrumScreen2)
# SCREENS = (ColAlignedScreen, TrackVUMeterScreen2) #, ArtistScreen, MetaVUScreen , TrackOscScreen,TrackVisScreen3, TrackSpectrumScreen3, TrackVUMeterScreen,MinSpectrumArt)

ART_SCREENS= (ArtistScreen, ImageTestScreen)

SPECTRUM_TEST_SCREENS= (StereoSpectrumLRScreen, FullSpectrumOffsetScreen, StereoSpectrumScreen, StereoSpectrumSplitScreen, \
                        MonoSpectrumScreen, MonoSpectrumLEDScreen, MixedLEDScreen)

VU_TEST_SCREENS= (TrackVUMeterScreen2, VUImageScreen, VUScreen, VUVScreen, TestVUImageScreen1, TestVUImageScreen2, \
                  TestVUMetersScreen, TestVisualiserScreen, TestSpectrumScreen, TestVUScreen)

GEO_TEST_SCREENS= (ColAlignedScreen, RowAlignedScreen, \
                   F1, F2,  F3, F4, F5, F6, F7, F8 )

MAIN_SCREENS= (TrackScreen, TrackVisScreen, TrackVisScreen2, TrackVisScreen3, TrackSpectrumScreen, \
               TrackSpectrumScreen2, MetaArtFrame, TrackSpectrumScreen3, TrackSpectrumScreen4,\
               TrackVUMeterScreen, TrackVUMeterScreen2, TrackVUMeterScreen21, TrackOscScreen,\
               SpectrumBaseArt, MinSpectrumArt, ArtMetaSpectrumScreen, BigDialsScreen2, MetaVUScreen, ArtistScreen)  

#subframes.py
#
SUBFRAMES = (TrackScreen, TrackVisScreen, TrackVisScreen2, TrackVisScreen3, TrackSpectrumScreen, \
             TrackSpectrumScreen2, MetaArtFrame, TrackSpectrumScreen3, TrackSpectrumScreen4, TrackVUMeterScreen, \
             TrackVUMeterScreen2, TrackVUMeterScreen21, TrackOscScreen, SpectrumBaseArt, MinSpectrumArt, \
             ArtMetaSpectrumScreen, BigDialsScreen2, MetaVUScreen, ArtistScreen, VU2chFrame, VUFlipFrame, \
             VUHorzFrame, VU2chHorzFrame, MetaDataFrame, ArtistMetaDataFrame, \
             StereoSpectrumFrame, MetaMiniSpectrumFrame, SamplesFrame)

#frames.py
#
BASE_FRAMES = (TextFrame, PlayProgressFrame, ArtFrame, MetaImages, MetaData,\
               VUMeter, VUFrame, SpectrumFrame, OscilogrammeBar, Oscilogramme,\
               Octaviser, CircleModulator, Diamondiser)

SUBFRAMES2 = (Spectrum2chFrame, SpectrumStereoFrame,  SpectrumStereoLRFrame,  SpectrumStereoSplitFrame,\
              SpectrumStereoOffsetFrame, VUMeterFrame1, VUMeterFrame2, VUMeterFrame3, VUMeterFrame4, VUMeterImageFrame)   

SCREENS = MAIN_SCREENS+ART_SCREENS +GEO_TEST_SCREENS+SPECTRUM_TEST_SCREENS+VU_TEST_SCREENS
# # SCREENS = (ArtistScreen,F4)
# SCREENS = (TrackVUMeterScreen2, VUImageScreen, VUScreen, VUVScreen, \
#                    TestVUScreen)+ART_SCREENS
# SCREENS = GEO_TEST_SCREENS


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
