#!/usr/bin/env python
"""
 All top level screens.  Screens are comprised of Frames

 Part of mVista preDAC2 project

 v3.0 Baloothebear4 Dec 2023


"""

# from    framecore import Frame, Geometry
# from    textwrap import shorten, wrap
# import  os
# from    displaydriver import Screen, Bar, Text, Box

from frames import *
# from frametest import *

"""
Screen classes - these are top level frames comprising frames of frames at full display size
"""

""" Visualiser Screens combined from multiple elements """

class TrackScreen(Frame):   # comprises volume on the left, spectrum on the right
    @property
    def title(self): return 'Roon Album Art, Metadata and progress bar - Trackscreen'

    @property
    def type(self): return 'Test'

    def __init__(self, platform, display):
        Frame.__init__(self, display.boundary, platform, display)
        THEME = 'red'
        self += AlbumArtFrame(display.boundary, platform, display, (0.31, 1.0),Halign='right')
        self += MetaDataFrame(display.boundary, platform, display, (0.38, 0.6), Halign='centre', Valign='middle', theme=THEME)
        self += PlayProgressFrame(display.boundary, platform, display, (0.38, 0.05), Halign='centre', Valign='bottom', theme=THEME)
        self += VU2chHorzFrame(display.boundary, platform, display, scalers=(0.3, 1.0), Halign='left', Valign='top', theme=THEME)

class TrackVisScreen(Frame):   # comprises volume on the left, spectrum on the right
    @property
    def title(self): return 'Visualiser, Roon Album Art, Metadata and progress bar'

    @property
    def type(self): return 'Test'

    def __init__(self, platform, display):
        Frame.__init__(self, display.boundary, platform, display)
        THEME = 'blue'
        self += AlbumArtFrame(display.boundary, platform, display, (0.31, 1.0),Halign='left')
        self += MetaDataFrame(display.boundary, platform, display, (0.38, 0.6), Halign='centre', Valign='middle', theme=THEME)
        self += Diamondiser(display.boundary, platform, display, 'left', scalers=(0.31, 1.0), Halign='right', Valign='middle', theme=THEME)
        self += PlayProgressFrame(display.boundary, platform, display, (0.38, 0.05), Halign='centre', Valign='bottom', theme=THEME)

class TrackVisScreen2(Frame):   # comprises volume on the left, spectrum on the right
    @property
    def title(self): return 'Complex Visualiser, Roon Album Art, Metadata and progress bar'

    @property
    def type(self): return 'Test'

    def __init__(self, platform, display):
        Frame.__init__(self, display.boundary, platform, display)
        THEME  = 'std'
        ARTIST = {'artist': {'colour':'foreground', 'Valign': 'top', 'Halign': 'centre'}}
        TRACK  = {'track' : {'colour':'mid', 'Valign': 'top', 'Halign': 'centre'}}
        ALBUM  = {'track' : {'colour':'mid', 'Valign': 'top', 'Halign': 'centre'}}
        # self += ArtistArtFrame(display.boundary, platform, display, (0.2, 1.0),Halign='left', Valign='middle')
        self += MetaDataFrame(display.boundary, platform, display, (0.33, 0.2), Halign='centre', Valign='top', theme=THEME, show=ARTIST)
        self += MetaDataFrame(display.boundary, platform, display, (0.33, 0.2), Halign='left', Valign='top', theme=THEME, show=TRACK)        # self += ArtistArtFrame(display.boundary, platform, display, (0.2, 1.0),Halign='left', Valign='middle')
        self += MetaDataFrame(display.boundary, platform, display, (0.33, 0.2), Halign='right', Valign='top', theme=THEME, show=ALBUM)
        self += CircleModulator(display.boundary, platform, display, 'mono', scalers=(0.6, 0.6), Halign='centre', Valign='middle', theme=THEME)
        self += PlayProgressFrame(display.boundary, platform, display, (1.0, 0.05), Halign='centre', Valign='bottom', theme=THEME)

class TrackVisScreen3(Frame):   # comprises volume on the left, spectrum on the right
    @property
    def title(self): return 'Oscillograme Bar, Complex Visualiser, Roon Album Art, Metadata and progress bar'

    @property
    def type(self): return 'Test'

    def __init__(self, platform, display):
        Frame.__init__(self, display.boundary, platform, display)
        THEME  = 'std'
        ARTIST = {'artist': {'colour':'foreground', 'Valign': 'top', 'Halign': 'centre'}}
        TRACK  = {'track' : {'colour':'mid', 'Valign': 'top', 'Halign': 'centre'}}
        ALBUM  = {'track' : {'colour':'mid', 'Valign': 'top', 'Halign': 'centre'}}
        # self += ArtistArtFrame(display.boundary, platform, display, (0.2, 1.0),Halign='left', Valign='middle')
        self += MetaDataFrame(self.coords, platform, display, (0.66, 0.5), Halign='centre', Valign='top', theme=THEME)
        self += Diamondiser(self.coords, platform, display, 'left', scalers=(0.7, 0.7), Halign='right', Valign='top', theme=THEME)
        self += PlayProgressFrame(self.coords, platform, display, (1.0, 0.05), Halign='centre', Valign='bottom', theme=THEME)
        self += SamplesFrame(self.coords, platform, display, scalers=(1.0, 0.5), Halign='left', Valign='bottom', theme=THEME)
        # self += VUFlipFrame(display.boundary, platform, display, scalers=(0.5, 0.5), Halign='left', Valign='top', orient='horz', flip=True, theme=THEME)
        # self += OscilogrammeBar(display.boundary, platform, display, 'mono', (0.66,0.5), Halign='left', Valign='top', barsize_pc=0.5, led_gap=0)
        # self += OscilogrammeBar(display.boundary, platform, display, 'mono', (0.33,0.5), Halign='left', Valign='bottom', flip=True, barsize_pc=0.5, led_gap=0)

class SamplesFrame(Frame):
    """ Volume/Source on left - Spectrum on left - one channel """
    def __init__(self, bounds, platform, display, scalers=(1.0, 1.0), Valign='middle', Halign='centre', theme='std'):
        Frame.__init__(self, bounds, platform, display, scalers=scalers, Valign=Valign, Halign=Halign)
        self += OscilogrammeBar(self.coords, platform, display, 'mono', (1.0,0.5), Halign='left', Valign='top', barsize_pc=0.5, led_gap=0)
        self += OscilogrammeBar(self.coords, platform, display, 'mono', (1.0,0.5), Halign='left', Valign='bottom', flip=True, barsize_pc=0.5, led_gap=0)

class TrackSpectrumScreen(Frame):   # comprises volume on the left, spectrum on the right
    @property
    def title(self): return 'Spectrum Analyser, Roon Album Art, Metadata and progress bar'

    @property
    def type(self): return 'Test'

    def __init__(self, platform, display):
        Frame.__init__(self, display.boundary, platform, display)
        THEME = 'blue'
        self += AlbumArtFrame(display.boundary, platform, display, (0.31, 1.0),Halign='right')
        self += MetaDataFrame(display.boundary, platform, display, (0.38, 0.6), Halign='centre', Valign='middle', theme=THEME)
        self += PlayProgressFrame(display.boundary, platform, display, (0.38, 0.05), Halign='centre', Valign='bottom', theme=THEME)
        self += SpectrumFrame(self.coords, platform, display, 'right', (0.31, 0.5), V='bottom', H='left', flip=True, led_gap=2, peak_h=0, radius=2, theme=THEME, barw_min=5, bar_space=0.6)
        self += SpectrumFrame(self.coords, platform, display, 'left', (0.31, 0.5), V='top', H='left', flip=False, led_gap=2, peak_h=0,radius=2, theme=THEME, barw_min=5, bar_space=0.6)

class TrackSpectrumScreen2(Frame):   # comprises volume on the left, spectrum on the right
    @property
    def title(self): return 'Spectrum Analyser 2, Roon Album Art, Metadata and progress bar'

    @property
    def type(self): return 'Test'

    def __init__(self, platform, display):
        Frame.__init__(self, display.boundary, platform, display)
        THEME = 'white'
        self += MetaArtFrame(self.coords, platform, display, (0.5, 1.0),Halign='right', Valign='middle')
        self += PlayProgressFrame(self.coords, platform, display, (0.66, 0.05), Halign='left', Valign='bottom', theme=THEME)
        self += SpectrumFrame(self.coords, platform, display, 'right', (0.5, 0.5), V='bottom', H='left', flip=True, led_gap=0, peak_h=1, radius=0, tip=True, theme=THEME, barw_min=3, bar_space=2)
        self += SpectrumFrame(self.coords, platform, display, 'left', (0.5, 0.5), V='top', H='left', flip=False, led_gap=0, peak_h=1,radius=0, tip=True, theme=THEME, barw_min=3, bar_space=2 )

class MetaArtFrame(Frame):
    """ Volume/Source on left - Spectrum on left - one channel """
    def __init__(self, bounds, platform, display, scalers=(1.0, 1.0), Valign='middle', Halign='centre', theme='std'):
        Frame.__init__(self, bounds, platform, display, scalers=scalers, Valign=Valign, Halign=Halign)
        self += AlbumArtFrame(self.coords, platform, display, (0.62, 1.0),Halign='right', Valign='middle')
        self += MetaDataFrame(self.coords, platform, display, (0.38, 1.0), Halign='left', Valign='middle', theme=theme)

class TrackSpectrumScreen3(Frame):   # comprises volume on the left, spectrum on the right
    @property
    def title(self): return 'Full Spectrum Analyser, Roon Album Art, Metadata and progress bar'

    @property
    def type(self): return 'Test'

    def __init__(self, platform, display):
        Frame.__init__(self, display.boundary, platform, display)
        THEME = 'std'
        # self += AlbumArtFrame(display.boundary, platform, display, (0.31, 0.93),Halign='right', Valign='top')
        ARTIST = {'artist': {'colour':'mid', 'Valign': 'top', 'Halign': 'centre'}}
        TRACK  = {'track' : {'colour':'mid', 'Valign': 'top', 'Halign': 'centre'}}
        # self += ArtistArtFrame(display.boundary, platform, display, (0.2, 1.0),Halign='left', Valign='middle')
        self += MetaDataFrame(display.boundary, platform, display, (0.45, 0.2), Halign='left', Valign='top', theme=THEME, show=ARTIST)
        self += MetaDataFrame(display.boundary, platform, display, (0.45, 0.2), Halign='right', Valign='top', theme=THEME, show=TRACK)
        self += PlayProgressFrame(display.boundary, platform, display, (1.0, 0.05), Halign='centre', Valign='bottom', theme=THEME)
        self += SpectrumFrame(self.coords, platform, display, 'right', (1.0, 0.5), V='bottom', H='centre', led_gap=0, flip=True, barw_min=3, bar_space=0.5, tip=True, theme=THEME )
        self += SpectrumFrame(self.coords, platform, display, 'left', (1.0, 0.5), V='top', H='centre', led_gap=0, barw_min=3, bar_space=0.5, tip=True, theme=THEME )

class TrackVUMeterScreen(Frame):   # comprises volume on the left, spectrum on the right
    @property
    def title(self): return 'VU Meters, Roon Album Art, Metadata and progress bar'

    @property
    def type(self): return 'Test'

    def __init__(self, platform, display):
        Frame.__init__(self, display.boundary, platform, display)
        THEME = 'blue'
        # self += AlbumArtFrame(display.boundary, platform, display, (0.25, 0.93),Halign='right', Valign='middle')
        self += ArtistArtFrame(display.boundary, platform, display, (0.4, 0.5),Halign='left', Valign='top')
        self += MetaDataFrame(display.boundary, platform, display, (0.4, 0.5), Halign='left', Valign='bottom', theme=THEME)
        self += PlayProgressFrame(display.boundary, platform, display, (0.6, 0.05), Halign='right', Valign='bottom', theme=THEME)
        # self += VUMeterFrame1(display.boundary, platform, display, scalers=(0.5,0.7), Valign='middle', Halign='centre')
        self += VUMeterImageFrame(display.boundary, platform, display, type='blueVU', scalers=(0.6,1.0), Valign='top', Halign='right')

class TrackVUMeterScreen2(Frame):   # comprises volume on the left, spectrum on the right
    @property
    def title(self): return 'Analogue VU Meters, Diamondiser, Roon Album Art, Metadata and progress bar'

    @property
    def type(self): return 'Test'

    def __init__(self, platform, display):
        Frame.__init__(self, display.boundary, platform, display)
        THEME     = 'meter1'
        NEEDLE    = { 'width':4, 'colour': 'foreground', 'length': 0.8, 'radius_pc': 1.0 }
        ENDSTOPS  = (3*PI/4, 5*PI/4)  #Position of endstop if not the edge of the frame
        PIVOT     = -0.5
        # self += AlbumArtFrame(display.boundary, platform, display, (0.25, 0.93),Halign='right', Valign='middle')
        # self += AlbumArtFrame(display.boundary, platform, display, (0.3, 0.3),Halign='centre', Valign='top')
        self += MetaDataFrame(display.boundary, platform, display, (0.3, 0.5), Halign='centre', Valign='middle', theme=THEME)
        self += PlayProgressFrame(display.boundary, platform, display, (1.0, 0.05), Halign='centre', Valign='bottom', theme=THEME)

        self += VUMeter(self.coords, platform, display, 'left', scalers=(0.35, 0.85), Valign='middle', Halign='left', pivot=PIVOT, arcs={}, endstops=ENDSTOPS, needle=NEEDLE)
        self += VUMeter(self.coords, platform, display, 'right', scalers=(0.35, 0.85), Valign='middle', Halign='right', pivot=PIVOT, arcs={}, endstops=ENDSTOPS, needle=NEEDLE)

        # self += VUMeterFrame1(display.boundary, platform, display, scalers=(0.7,0.7), Valign='middle', Halign='left')
        # self += Diamondiser(display.boundary, platform, display, 'left', scalers=(0.3, 1.0), Halign='right', Valign='middle', theme=THEME)


""" VU Meters """
VUMETERS = ['blueVU', 'goldVU', 'blackVU', 'rainVU', 'redVU', 'vintVU', 'whiteVU', 'greenVU']

class VUImageScreen(Frame):
    """ VU meters left and right - based on an image background"""
    @property
    def title(self): return 'VU meters with image background'

    @property
    def type(self): return 'VU Image'

    def __init__(self, platform, display, type='blueVU'):

        Frame.__init__(self, display.boundary, platform, display)
        self += VUMeterImageFrame(display.boundary, platform, display, type=type, scalers=(0.5,0.5), Valign='top', Halign='left')



""" Spectrum Analyser based Screens """


class SpectrumScreen(Frame):
    """ Volume/Source on left - Spectrum on left - one channel """
    def __init__(self, platform, display):
        Frame.__init__(self, display.boundary, platform, display)
        self += VolumeSourceFrame(display.boundary, platform, display, 0.2, 'right')
        self += SpectrumFrame(display.boundary, platform, display, 'left', (0.8,1.0), H='centre')
        self.check()

class StereoSpectrumLRScreen(Frame):
    """ Volume/Source on left - Spectrum on left - one channel """
    def __init__(self, platform, display):
        Frame.__init__(self, display.boundary, platform, display)
        self += Spectrum2chFrame(display.boundary, platform, display, (1.0,1.0), H='centre')
        self.check()

class FullSpectrumOffsetScreen(Frame):
    """ Volume/Source on left - Spectrum on left - one channel """
    def __init__(self, platform, display):
        Frame.__init__(self, display.boundary, platform, display)
        self += SpectrumStereoOffsetFrame(display.boundary, platform, display, (1.0,1.0), H='centre')
        self.check()

class StereoSpectrumScreen(Frame):
    """ Volume/Source on left - Stereo Spectrum overlaid """
    def __init__(self, platform, display):
        Frame.__init__(self, display.boundary, platform, display)
        # self += VolumeSourceFrame(display.boundary, platform, display, 0.3, 'right')
        self += SpectrumStereoFrame(display.boundary, platform, display, (1.0,1.0), H='centre')
        self.check()

class StereoSpectrumSplitScreen(Frame):
    """ Volume/Source on left - Stereo Spectrum overlaid """
    def __init__(self, platform, display):
        Frame.__init__(self, display.boundary, platform, display)
        # self += VolumeSourceFrame(display.boundary, platform, display, 0.3, 'right')
        self += SpectrumStereoSplitFrame(display.boundary, platform, display, (1.0,1.0), H='centre')
        self.check()

"""
    SpectrumFrame API:
    # def __init__(self, bounds, platform, display, channel, scale, V='bottom', H='left', right_offset=0, theme='std', flip=False, \
    #                 led_h=5, led_gap=1, peak_h=1, col_mode='h', radius=0, bar_space=0.5, barw_min=12, barw_max=20, tip=False, decay=DECAY):
"""
class MonoSpectrumScreen(Frame):
    """ Volume/Source on left - Stereo Spectrum overlaid """
    def __init__(self, platform, display):
        Frame.__init__(self, display.boundary, platform, display)
        # def __init__(self, bounds, platform, display, channel, scale, V='bottom', H='left', right_offset=0, colour='white'):
        self += SpectrumFrame(display.boundary, platform, display, 'left', (1.0, 1.0), led_gap=0, barw_min=2, tip=True)
        self.check()

class MonoSpectrumLEDScreen(Frame):
    """ Volume/Source on left - Stereo Spectrum overlaid """
    def __init__(self, platform, display):
        Frame.__init__(self, display.boundary, platform, display)
        # def __init__(self, bounds, platform, display, channel, scale, V='bottom', H='left', right_offset=0, colour='white'):
        self += SpectrumFrame(display.boundary, platform, display, 'left', (1.0, 1.0), peak_h=2, led_gap=2, led_h=4, barw_min=6, bar_space=0.2, theme='leds')
        self.check()

class MixedLEDScreen(Frame):
    """ Volume/Source on left - Stereo Spectrum overlaid """
    def __init__(self, platform, display):
        Frame.__init__(self, display.boundary, platform, display)
        # def __init__(self, bounds, platform, display, channel, scale, V='bottom', H='left', right_offset=0, colour='white'):
        self += SpectrumFrame(display.boundary, platform, display, 'right', (0.8, 1.0), H='right', peak_h=2, led_gap=3, led_h=5, barw_min=6, bar_space=0.2, theme='leds')
        self += VU2chFrame(display.boundary, platform, display, scalers=(0.2, 1.0), Halign='left', Valign='top', orient='vert', flip=False, theme='leds', led_gap=3, led_h=5)




""" System Utility screens """

class MainScreen(Frame):
    """ Vol/source in centre - spectrum left and right """
    def __init__(self, platform, display):
        Frame.__init__(self, display.boundary, platform, display)
        self += SpectrumFrame(self.coords, platform, display, 'left', 0.3 )
        self += dbVolumeSourceFrame(display.boundary, platform, display, 0.4, 'centre')
        self += SpectrumFrame(self.coords, platform, display, 'right', 0.3 )

class ScreenTitle(Frame):
    def __init__(self, platform, display):
        Frame.__init__(self, display.boundary, platform, display)
        self += MenuFrame(display.boundary, platform, display, 'top', 1.0, 'very very long screen title')
        self.check()

class WelcomeScreen(Frame):
    """ Startup screen """
    text = "Welcome to SRC Visualiser"
    def __init__(self, platform, display):
        Frame.__init__(self, display.boundary, platform, display)
        # def __init__(self, bounds, platform, display, Valign='top', scalers=(1.0, 1.0), text='Default Text', Halign='centre', fontsize=0):
        self += TextFrame( display.boundary, platform, display, Valign='middle', scalers=(1.0, 1.0), text=WelcomeScreen.text)

class ShutdownScreen(Frame):
    """ Startup screen """
    text = "Loved the music"

    def __init__(self, platform, display):
        Frame.__init__(self, display.boundary, platform, display)
        # def __init__(self, bounds, platform, display, Valign='top', scalers=(1.0, 1.0), text='Default Text', Halign='centre', fontsize=0):
        self += TextFrame( display.boundary, platform, display, 'top', 1.0, ShutdownScreen.text)

class ScreenSaver(Frame):
    """ force the screen to go blank """
    def __init__(self, platform, display):
        Frame.__init__(self, display.boundary, platform, display)
        self += TextFrame( display.boundary, platform, display, 'top', 1.0, '')

class VolChangeScreen(Frame):
    def __init__(self, platform, display):
        Frame.__init__(self, display.boundary, platform, display)
        self += VolumeAmountFrame(display.boundary, platform, display, 0.6)
        self += VolumeSourceFrame(display.boundary, platform, display, 0.4, 'right')
        self.check()

class RecordingScreen(Frame):
    def __init__(self, platform, display):
        Frame.__init__(self, display.boundary, platform, display)
        self += RecordFrame( display.boundary, platform, display, 0.3)
        self += VolumeSourceFrame(display.boundary, platform, display, 0.4, 'right')
        self.check()

class RecordFinishScreen(Frame):
    def __init__(self, platform, display):
        Frame.__init__(self, display.boundary, platform, display)
        self += TextFrame( display.boundary, platform, display, 'top', 0.5, 'Recording saved to')
        self += RecordEndFrame( display.boundary, platform, display, 'bottom', 0.5)
        self.check()

class SourceVolScreen(Frame):   # comprises volume on the left, spectrum on the right
    def __init__(self, platform, display):
        Frame.__init__(self, display.boundary, platform, display)
        self += dbVolumeSourceFrame(display.boundary, platform, display, 0.4, 'right')
        self += SourceIconFrame(display.boundary, platform, display, 0.6, 'left')
        self.check()

class SourceVUVolScreen(Frame):
    def __init__(self, platform, display):
        Frame.__init__(self, display.boundary, platform, display)
        self += dbVolumeSourceFrame(display.boundary, platform, display, 0.4, 'right')
        self += VUV2chFrame(display.boundary, platform, display, 0.3, 'centre')
        self += SourceIconFrame(display.boundary, platform, display, 0.3, 'left')
        self.check()

""" Horizontal VU bar meter """
class VUScreen(Frame):   # comprises volume on the left, spectrum on the right
    def __init__(self, platform, display):
        Frame.__init__(self, display.boundary, platform, display)
        # self += VolumeSourceFrame(display.boundary, platform, display, 0.4, 'right')
        # def __init__(self, bounds, platform, display, scalers, Valign='bottom', Halign='left'):
        self += VU2chHorzFrame(display.boundary, platform, display, (1.0, 1.0), Valign='top', Halign='centre')
        self.check()

class VUVScreen(Frame):   # comprises volume on the left, spectrum on the right
    def __init__(self, platform, display):
        Frame.__init__(self, display.boundary, platform, display)
        # self += dbVolumeSourceFrame(display.boundary, platform, display, 0.5, 'right')
        # self += SpectrumFrame(display.boundary, platform, display, 'right', (0.7, 1.0), H='right', led_gap=0, barw_min=2, tip=True)
        self += VU2chFrame(display.boundary, platform, display, scalers=(0.3, 0.5), Halign='left', Valign='top', orient='vert', flip=True)
        self += VUFlipFrame(display.boundary, platform, display, scalers=(0.5, 0.5), Halign='right', Valign='bottom', orient='vert', flip=True)
        self.check()

class PlayerScreen(Frame):   # comprises volume on the left, spectrum on the right
    def __init__(self, platform, display):
        Frame.__init__(self, display.boundary, platform, display)
        self += VolumeSourceFrame(display.boundary, platform, display, 0.2, 'right')
        self += MetaDataFrame(display.boundary, platform, display, 0.8, 'left')
        self.check()



"""
Test Code
"""

VUMETERS = ['blueVU', 'goldVU', 'blackVU', 'rainVU', 'redVU', 'vintVU', 'whiteVU', 'greenVU']
class TestVUImageScreen1(Frame):
    """ VU meters left and right - based on an image background"""
    @property
    def title(self): return 'Test multiple VU meters with image backgrounds'

    @property
    def type(self): return 'Test'

    def __init__(self, platform, display, type=None):

        Frame.__init__(self, display.boundary, platform, display)

        self += VUMeterImageFrame(display.boundary, platform, display, type='blueVU', scalers=(0.5,0.5), Valign='top', Halign='left')
        self += VUMeterImageFrame(display.boundary, platform, display, type='goldVU', scalers=(0.5,0.5), Valign='bottom', Halign='left')
        self += VUMeterImageFrame(display.boundary, platform, display, type='blackVU', scalers=(0.5,0.5), Valign='top', Halign='right')
        self += VUMeterImageFrame(display.boundary, platform, display, type='rainVU', scalers=(0.5,0.5), Valign='bottom', Halign='right')
        # self += VUMeterImageFrame(display.boundary, platform, display, type='redVU', scalers=(0.5,0.5), Valign='top', Halign='left')
        # self += VUMeterImageFrame(display.boundary, platform, display, type='vintVU', scalers=(0.5,0.5), Valign='bottom', Halign='left')
        # self += VUMeterImageFrame(display.boundary, platform, display, type='whiteVU', scalers=(0.5,0.5), Valign='top', Halign='right')
        # self += VUMeterImageFrame(display.boundary, platform, display, type='greenVU', scalers=(0.5,0.5), Valign='bottom', Halign='right')

class TestVUImageScreen2(Frame):
    """ VU meters left and right - based on an image background"""
    @property
    def title(self): return 'Test multiple VU meters with image backgrounds'

    @property
    def type(self): return 'Test'

    def __init__(self, platform, display):
        # METERS = ['blueVU', 'goldVU', 'blackVU', 'rainVU', 'redVU', 'vintVU', 'whiteVU', 'greenVU']
        Frame.__init__(self, display.boundary, platform, display)

        # self += VUMeterImageFrame(display.boundary, platform, display, type='blueVU', scalers=(0.5,0.5), Valign='top', Halign='left')
        # self += VUMeterImageFrame(display.boundary, platform, display, type='goldVU', scalers=(0.5,0.5), Valign='bottom', Halign='left')
        # self += VUMeterImageFrame(display.boundary, platform, display, type='blackVU', scalers=(0.5,0.5), Valign='top', Halign='right')
        # self += VUMeterImageFrame(display.boundary, platform, display, type='rainVU', scalers=(0.5,0.5), Valign='bottom', Halign='right')
        self += VUMeterImageFrame(display.boundary, platform, display, type='redVU', scalers=(0.5,0.5), Valign='top', Halign='left')
        self += VUMeterImageFrame(display.boundary, platform, display, type='vintVU', scalers=(0.5,0.5), Valign='bottom', Halign='left')
        self += VUMeterImageFrame(display.boundary, platform, display, type='whiteVU', scalers=(0.5,0.5), Valign='top', Halign='right')
        self += VUMeterImageFrame(display.boundary, platform, display, type='greenVU', scalers=(0.5,0.5), Valign='bottom', Halign='right')

class TestVUMetersScreen(Frame):
    """ Vol/source in centre - VU meters left and right """
    @property
    def title(self): return 'Tests out multiple configurations of Stereo VU Meters'

    @property
    def type(self): return 'Test'

    def __init__(self, platform, display):
        Frame.__init__(self, display.boundary, platform, display)

        self += VUMeterFrame1(display.boundary, platform, display, scalers=(0.5,0.5), Valign='top', Halign='left')
        self += VUMeterFrame2(display.boundary, platform, display, scalers=(0.5,0.5), Valign='bottom', Halign='left')
        self += VUMeterFrame3(self.coords, platform, display, scalers=(0.5,0.5), Valign='top', Halign='right')
        self += VUMeterFrame4(self.coords, platform, display, scalers=(0.5,0.5), Valign='bottom', Halign='right')

        # self += VolumeSourceFrame(display.boundary, platform, display, 0.2, 'centre'

class TestVisualiserScreen(Frame):   # comprises volume on the left, spectrum on the right
    @property
    def title(self): return 'Test multiple configurations of Visualisers'

    @property
    def type(self): return 'Test'

    def __init__(self, platform, display):
        Frame.__init__(self, display.boundary, platform, display)
        self += OscilogrammeBar(display.boundary, platform, display, 'left', (1.0,0.5), Halign='right', Valign='top')
        self += OscilogrammeBar(display.boundary, platform, display, 'right', (1.0,0.5), Halign='right', Valign='bottom', flip=True)
        # self += Diamondiser(display.boundary, platform, display, 'right', (0.5,0.5), Halign='left', Valign='top')
        # # self += Octaviser(display.boundary, platform, display, 'right', (0.5,0.5), H='left', V='bottom')
        # self += CircleModulator(display.boundary, platform, display, 'left', (0.5,0.5), Halign='right', Valign='top')


class TestSpectrumScreen(Frame):   # comprises volume on the left, spectrum on the right
    @property
    def title(self): return 'Tests out multiple configurations of spectrum analysers'

    @property
    def type(self): return 'Test'

    def __init__(self, platform, display):
        Frame.__init__(self, display.boundary, platform, display)
        self += SpectrumStereoSplitFrame(display.boundary, platform, display, (0.5,0.5), H='left', V='top')
        # self += Spectrum2chFrame(display.boundary, platform, display, (0.5,0.5), H='left', V='top')
        self += SpectrumStereoOffsetFrame(display.boundary, platform, display, (0.5,0.5), H='left', V='bottom')
        #
        self += SpectrumFrame(display.boundary, platform, display, 'left', (0.5,0.5), H='right', V='top', peak_h=2, led_gap=2, led_h=4, barw_min=6, bar_space=0.2, theme='leds')
        # #mono
        self += SpectrumFrame(display.boundary, platform, display, 'left', (0.5,0.5), H='right', V='bottom', led_gap=0, barw_min=2, tip=True)


class TestVUScreen(Frame):   # comprises volume on the left, spectrum on the right
    @property
    def title(self): return 'Tests out Bar VU meters of all types'

    @property
    def type(self): return 'Test'

    def __init__(self, platform, display):
        Frame.__init__(self, display.boundary, platform, display)
        # self += VU2chFrame(display.boundary, platform, display, scalers=(0.2, 0.5), Halign='left', Valign='top', orient='vert')
        # self += VU2chFrame(display.boundary, platform, display, scalers=(0.2, 1.0), Halign='left', Valign='bottom', orient='vert', flip=False)
        self += VU2chFrame(display.boundary, platform, display, scalers=(0.25, 1.0), Halign='left', Valign='top', orient='vert', flip=False)
        self += VUFlipFrame(display.boundary, platform, display, scalers=(0.25, 1.0), Halign='right', Valign='bottom', orient='vert', flip=True)
        self += VU2chHorzFrame(display.boundary, platform, display, (0.5, 0.5), Halign='centre', Valign='top',tip=True)
        self += VUFlipFrame(display.boundary, platform, display, scalers=(0.5, 0.5), Halign='centre', Valign='bottom', orient='horz', flip=True)


class TestScreen(Frame):
    @property
    def title(self): return 'Tests out Frames, nesting and components'

    @property
    def type(self): return 'Test'

    def __init__(self, platform, display):
        Frame.__init__(self, display.boundary, platform, display)

        self += SubFrame(bounds=display.boundary, platform=platform, display=display, scalers=(0.5,0.3), Halign='left', Valign='top')
        self += SubFrame(bounds=display.boundary, platform=platform, display=display, scalers=(0.5,0.3), Halign='right', Valign='bottom')
        # self += TestFrame(bounds=display.boundary, platform=platform, display=display, scalers=(1.0, 0.5), Halign='left', Valign='top')
        self += TextFrame(bounds=display.boundary, platform=platform, display=display, scalers=(0.5,0.3), Halign='centre', Valign='middle', text='TextFrame')


class SubFrame(Frame):
    def __init__(self, **kwargs):
        Frame.__init__(self, kwargs['bounds'], kwargs['platform'], kwargs['display'], kwargs['scalers'], kwargs['Valign'], kwargs['Halign'])
        print("SubFrame> ", self.geostr())
        self += TestFrame(bounds=self.coords, platform=kwargs['platform'], display=kwargs['display'], scalers=(0.5, 0.3), Halign='left', Valign='bottom')
        self += TestFrame(bounds=self.coords, platform=kwargs['platform'], display=kwargs['display'], scalers=(0.5, 0.3), Halign='centre', Valign='middle')
        self += TestFrame(bounds=self.coords, platform=kwargs['platform'], display=kwargs['display'], scalers=(0.5, 0.3), Halign='right', Valign='top')
        self += OutlineFrame(bounds=self.coords, platform=kwargs['platform'], display=kwargs['display'], scalers=(1.0, 1.0), Halign='right', Valign='top')

class TestFrame(Frame):
    """ A Frame is a box with coords relative to its enclosing Frame,
        on creation this creates the create, in the orientation and positioning withing the super-Frame
        componenets or subframes are added to this Frame
    """


    # def __init__(self, bounds, platform=None, display=None, scalers=[1.0,1.0], Valign='bottom', Halign='left'):
    def __init__(self, **kwargs):
        Frame.__init__(self, kwargs['bounds'], kwargs['platform'], kwargs['display'], kwargs['scalers'], kwargs['Valign'], kwargs['Halign'])
        self.params  = kwargs
        self.outline = OutlineComponent(self, self.params['display'])
        self.box     = Box(self.params['display'], self.coords, box=(100,100), width=0, Halign='right', Valign='middle')
        self.text    = TextFrame(self.coords, kwargs['platform'], kwargs['display'], scalers=(1.0, 1.0), boxH='right', Halign='centre', Valign='middle', text=kwargs['Halign']+kwargs['Valign'])
        print("TestFrame.__init__>", self.params, self.geostr())

    def draw(self):
        # print("TestFrame.draw>")
        self.outline.draw()
        self.box.draw( (0,0) )
        self.text.draw()
