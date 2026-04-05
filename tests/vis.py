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

from pyvisualiser.visualisers.vumeters import *
from pyvisualiser.visualisers.metadata import *
from pyvisualiser.visualisers.spectrum import *
from pyvisualiser.visualisers.oscillogramme import *


from   screens import *
from   screens2 import *
from   screens3 import *
from   VUscreens import *
from   testscreens import *
from   test_api_coverage import *
from   test_advanced_visuals import *
from   gltest import *
from   pyvisualiser import ScreenController
import platform



""" Screen types are:   Control for utility messages like vol change,  Test to exercise functionality, Base for mixed visual displays """
# TestVUMetersScreen, TestVUScreen,  
# TestScreen, TestVUImageScreen1, TestVisualiserScreen, TestVUMetersScreen, TestVUScreen, TestSpectrumScreen, TestScreen,\
# TestVUScreen, TestVUImageScreen1, TestVUImageScreen2, TestVUMetersScreen, TestSpectrumScreen 

# SCREENS = ( ColAlignedScreen, TrackVUMeterScreen21 )
ALLSCREENS = ( MinSpectrumArt, TrackScreen, TrackSpectrumScreen, TrackSpectrumScreen2,\
            TrackSpectrumScreen3, TrackSpectrumScreen4, \
            TrackOscScreen, TrackVisScreen, TrackVisScreen2, TrackVisScreen3, TrackVUMeterScreen, TrackVUMeterScreen2, \
            ArtMetaSpectrumScreen, MinSpectrumArt, ColAlignedScreen  )
# SCREENS = (F7,F6,F5, F8)#, F4, F5, F7)# F5)#F4, F3, F1, F2)#F5, F3)ColAlignedScreen, ColAlignedScreen) #TrackVUMeterScreen, ArtMetaSpectrumScreen, TrackVUMeterScreen2, ArtistScreen, MetaVUScreen , TrackOscScreen,TrackVisScreen3, MinSpectrumArt, TrackSpectrumScreen3, TrackSpectrumScreen, TrackSpectrumScreen2)
# SCREENS = (ColAlignedScreen, TrackVUMeterScreen2) #, ArtistScreen, MetaVUScreen , TrackOscScreen,TrackVisScreen3, TrackSpectrumScreen3, TrackVUMeterScreen,MinSpectrumArt)

ART_SCREENS= (ArtistScreen, ImageTestScreen, ReflectionTestScreen)

SPECTRUM_TEST_SCREENS= (StereoSpectrumLRScreen, FullSpectrumOffsetScreen, StereoSpectrumScreen, StereoSpectrumSplitScreen, \
                        MonoSpectrumScreen, MonoSpectrumLEDScreen, MixedLEDScreen)

VU_TEST_SCREENS= (TrackVUMeterScreen2, VUImageScreen, VUScreen, VUVScreen, TestVUImageScreen1, TestVUImageScreen2, \
                  TestVUMetersScreen, TestVisualiserScreen, TestSpectrumScreen, TestVUScreen)
VU_BAR_TEST_SCREENS = (VUScreen, VUVScreen, TestVUScreen, IntensityTestScreen)
GEO_TEST_SCREENS= (ColAlignedScreen, RowAlignedScreen, \
                   F1, F2,  F3, F4, F5, F6, F7, F8 )

VU_METER_SCREENS = (VUTestScreen1,  VUTestScreen2,VUImageScreen, VUVintageScreen, VUModernScreen, VUTungstenScreen, VUNeedleStylesScreen,VUNeedleEffectsScreen, TestVUMetersScreen, TestVUImageScreen1, TestVUImageScreen2)
#,
TEST_SCREENS = (AmbientGlowTunerScreen, AdvancedVisualsScreen, APICoverageScreen, BarParametersTestScreen, VUVScreen, IntensityTestScreen, OutlineGlowTestScreen )

MAIN_SCREENS= (TrackScreen, TrackVisScreen, TrackVisScreen2, TrackVisScreen3, TrackSpectrumScreen, \
               TrackSpectrumScreen2, MetaArtFrame, TrackSpectrumScreen3, TrackSpectrumScreen4,\
               TrackVUMeterScreen, TrackVUMeterScreen2, TrackVUMeterScreen21, TrackOscScreen,\
               )  

FULL_SCREENS = (Screen1, Screen2, Screen3, Screen4, Screen5, Screen6, Screen7)
#subframes.py
#
SUBFRAMES = (TrackScreen, TrackVisScreen, TrackVisScreen2, TrackVisScreen3, TrackSpectrumScreen, \
             TrackSpectrumScreen2, MetaArtFrame, TrackSpectrumScreen3, TrackSpectrumScreen4, TrackVUMeterScreen, \
             TrackVUMeterScreen2, TrackVUMeterScreen21, TrackOscScreen, MinSpectrumArt, \
             ArtMetaSpectrumScreen, BigDialsScreen2, ArtistScreen, VU2chFrame, VUFlipFrame, \
             VUHorzFrame, VU2chHorzFrame, MetaDataFrame, ArtistMetaDataFrame, \
             StereoSpectrumFrame, MetaMiniSpectrumFrame, SamplesFrame)

#frames.py
#
BASE_FRAMES = (TextFrame, PlayProgressFrame, ArtFrame, MetaImages, MetaData,\
               VUMeter, VUFrame, SpectrumFrame, OscilogrammeBar, Oscilogramme,\
               Octaviser, CircleModulator, Diamondiser)

SUBFRAMES2 = (Spectrum2chFrame, SpectrumStereoFrame,  SpectrumStereoLRFrame,  SpectrumStereoSplitFrame,\
              SpectrumStereoOffsetFrame, VUMeterFrame1, VUMeterFrame2, VUMeterFrame3, VUMeterFrame4, VUMeterImageFrame)   

GLSCREENS  = (GLTestScreen1, GLTestScreen2, GLmeshScreen)

# SCREENS = FULL_SCREENS+MAIN_SCREENS+ART_SCREENS +GEO_TEST_SCREENS+SPECTRUM_TEST_SCREENS+VU_TEST_SCREENS
# SCREENS = (ProgressScreen, ArtistScreen,F4, TrackVUMeterScreen2)
# SCREENS = (TrackVUMeterScreen2, VUImageScreen, VUScreen, VUVScreen, \
#                    TestVUScreen)+ART_SCREENS+GEO_TEST_SCREENS
# SCREENS = (ShadowTestScreen, ) + FULL_SCREENS
# SCREENS = VU_BAR_TEST_SCREENS + FULL_SCREENS
# SCREENS= (F7, F8) + VU_BAR_TEST_SCREENS + FULL_SCREENS



TEST_SCREENS2 = (BackgroundEffectsScreen0, BackgroundEffectsScreen1, BackgroundEffectsScreen2, AmbientGlowTunerScreen,OutlineGlowTestScreen,ProfileTestScreen, \
                 AudioTestScreen, BarEffectsTestScreen, LEDtestScreen, GlowTestScreen)
# SCREENS = VU_METER_SCREENS+ (AmbientGlowTunerScreen,OutlineGlowTestScreen, BackgroundEffectsScreen1, BackgroundEffectsScreen2, F1, BarEffectsTestScreen, LEDtestScreen, GlowTestScreen)
HERO_SCREENS  = (H1,H2,H3)

SCREENS =   HERO_SCREENS + TEST_SCREENS2 + GLSCREENS + SPECTRUM_TEST_SCREENS+(SamplesFrame,Screen7, VUTestScreen1,  VUTestScreen2,VUImageScreen)#+VU_TEST_SCREENS


""" 
    Determine the underlying hardware plaform - NB: Pi is assumed to use the KMS graphics driver 
    the loopback and roon zones are all configured by the user to match their system
""" 

PI_PLATFORM  = { "gfx": "pi_kms", "loopback":"loopin", "roon_zone":"pre3" }
MAC_PLATFORM = { "gfx": "gl", "loopback":"BlackHole 2ch", "roon_zone":"MacViz" }
# Warning.filterwarnings("ignore", category=UserWarning, message=".*pkg_resources is deprecated.*")

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
    from pyvisualiser.styles.profiles import ProfileManager
    from pyvisualiser.styles.presets import EmbeddedHiFiProfile
    ProfileManager.set_profile(EmbeddedHiFiProfile)

    visualiser = ScreenController(SCREENS, hw_platform=machine() )

    try:
        visualiser.run()
    except KeyboardInterrupt:
        visualiser.stop()
