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

    def __init__(self, platform):
        Frame.__init__(self, platform)
        THEME = 'red'
        self += AlbumArtFrame(self  , scalers=(0.31, 1.0),align=('right','middle'))
        self += MetaDataFrame(self  , scalers=(0.38, 0.6), align=('centre','middle'), theme=THEME)
        self += PlayProgressFrame(self  , scalers=(0.38, 0.05), align=('centre','bottom'), theme=THEME)
        self += VU2chHorzFrame(self  , scalers=(0.3, 1.0), align=('left','top'), theme=THEME)

class TrackVisScreen(Frame):   # comprises volume on the left, spectrum on the right
    @property
    def title(self): return 'Visualiser, Roon Album Art, Metadata and progress bar'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        Frame.__init__(self, platform)
        THEME = 'blue'
        self += AlbumArtFrame(self  , scalers=(0.31, 1.0),align=('left','middle'))
        self += MetaDataFrame(self  , scalers=(0.38, 0.6), align=('centre','middle'), theme=THEME)
        self += Diamondiser(self  , 'left', scalers=(0.31, 1.0), align=('right','middle'), theme=THEME)
        self += PlayProgressFrame(self  , scalers=(0.38, 0.05), align=('centre','bottom'), theme=THEME)

class TrackVisScreen2(Frame):   # comprises volume on the left, spectrum on the right
    @property
    def title(self): return 'Complex Visualiser, Roon Album Art, Metadata and progress bar'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        Frame.__init__(self, platform)
        THEME  = 'std'
        ARTIST = {'artist': {'colour':'foreground', 'align': ('centre', 'top')}}
        TRACK  = {'track' : {'colour':'mid', 'align': ('centre', 'top')}}
        ALBUM  = {'track' : {'colour':'mid', 'align': ('centre', 'top')}}
        # self += ArtistArtFrame(self  , (0.2, 1.0),align=('left','middle'))
        self += MetaDataFrame(self  , scalers=(0.33, 0.2), align=('centre','top'), theme=THEME, show=ARTIST)
        self += MetaDataFrame(self  , scalers=(0.33, 0.2), align=('left','top'), theme=THEME, show=TRACK)        # self += ArtistArtFrame(self  , (0.2, 1.0),align=('left','middle'))
        self += MetaDataFrame(self  , scalers=(0.33, 0.2), align=('right','top'), theme=THEME, show=ALBUM)
        self += CircleModulator(self  , 'mono', scalers=(0.6, 0.6), align=('centre','middle'), theme=THEME)
        self += PlayProgressFrame(self  , scalers=(1.0, 0.05), align=('centre','bottom'), theme=THEME)

class TrackVisScreen3(Frame):   # comprises volume on the left, spectrum on the right
    @property
    def title(self): return 'Oscillograme Bar, Complex Visualiser, Roon Album Art, Metadata and progress bar'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        Frame.__init__(self, platform)
        THEME  = 'std'
        ARTIST = {'artist': {'colour':'foreground', 'align': ('centre', 'top')}}
        TRACK  = {'track' : {'colour':'mid', 'align': ('centre', 'top')}}
        ALBUM  = {'track' : {'colour':'mid', 'align': ('centre', 'top')}}
        # self += ArtistArtFrame(self  , (0.2, 1.0),align=('left','middle'))
        self += MetaDataFrame(self  ,  scalers=(0.66, 0.5), align=('centre','top'), theme=THEME)
        self += Diamondiser(self  ,  'left', scalers=(0.7, 0.7), align=('right','top'), theme=THEME)
        self += PlayProgressFrame(self  ,  scalers=(1.0, 0.05), align=('centre','bottom'), theme=THEME)
        self += SamplesFrame(self  ,  scalers=(1.0, 0.5), align=('left','bottom'), theme=THEME)
        # self += VUFlipFrame(self  , scalers=(0.5, 0.5), align=('left','top'), orient='horz', flip=True, theme=THEME)
        # self += OscilogrammeBar(self  , 'mono', scalers=(0.66,0.5), align=('left','top'), barsize_pc=0.5, led_gap=0)
        # self += OscilogrammeBar(self  , 'mono', scalers=(0.33,0.5), align=('left','bottom'), flip=True, barsize_pc=0.5, led_gap=0)

class SamplesFrame(Frame):
    """ Volume/Source on left - Spectrum on left - one channel """
    def __init__(self, parent, scalers=(1.0, 1.0), align=('centre','middle'), theme='std'):
        Frame.__init__(self, parent, scalers=scalers, align=align)
        self += OscilogrammeBar(self  ,  'mono', scalers=(1.0,0.5), align=('left','top'), barsize_pc=0.5, led_gap=0)
        self += OscilogrammeBar(self  ,  'mono', scalers=(1.0,0.5), align=('left','bottom'), flip=True, barsize_pc=0.5, led_gap=0)

class TrackSpectrumScreen(Frame):   # comprises volume on the left, spectrum on the right
    @property
    def title(self): return 'Spectrum Analyser, Roon Album Art, Metadata and progress bar'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        Frame.__init__(self, platform)
        THEME = 'blue'
        self += AlbumArtFrame(self  , scalers=(0.31, 1.0), align=('right','middle'))
        self += MetaDataFrame(self  , scalers=(0.38, 0.6), align=('centre','middle'), theme=THEME)
        self += PlayProgressFrame(self  , scalers=(0.38, 0.05), align=('centre','bottom'), theme=THEME)
        self += SpectrumFrame(self  ,  'right', scalers=(0.31, 0.5), align=('left','bottom'), flip=True, led_gap=2, peak_h=0, radius=2, theme=THEME, barw_min=5, bar_space=0.6)
        self += SpectrumFrame(self  ,  'left', scalers=(0.31, 0.5), align=('left','top'), flip=False, led_gap=2, peak_h=0,radius=2, theme=THEME, barw_min=5, bar_space=0.6)

class TrackSpectrumScreen2(Frame):   # comprises volume on the left, spectrum on the right
    @property
    def title(self): return 'Spectrum Analyser 2, Roon Album Art, Metadata and progress bar'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        Frame.__init__(self, platform)
        THEME = 'white'
        self += MetaArtFrame(self  ,  scalers=(0.5, 1.0),align=('right','middle'))
        self += PlayProgressFrame(self  ,  scalers=(0.66, 0.05), align=('left','bottom'), theme=THEME)
        self += SpectrumFrame(self  ,  'right', scalers=(0.5, 0.5), align=('left','bottom'), flip=True, led_gap=0, peak_h=1, radius=0, tip=True, theme=THEME, barw_min=3, bar_space=2)
        self += SpectrumFrame(self  ,  'left', scalers=(0.5, 0.5), align=('left','top'), flip=False, led_gap=0, peak_h=1,radius=0, tip=True, theme=THEME, barw_min=3, bar_space=2 )

class MetaArtFrame(Frame):
    """ Volume/Source on left - Spectrum on left - one channel """
    def __init__(self, parent, scalers=(1.0, 1.0), align=('centre','middle'), theme='std'):
        Frame.__init__(self, parent, scalers=scalers, align=align)
        self += AlbumArtFrame(self  ,  scalers=(0.62, 1.0),align=('right','middle'))
        self += MetaDataFrame(self  ,  scalers=(0.38, 1.0), align=('left','middle'), theme=theme)

class TrackSpectrumScreen3(Frame):   # comprises volume on the left, spectrum on the right
    @property
    def title(self): return 'Full Spectrum Analyser, Roon Album Art, Metadata and progress bar'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        Frame.__init__(self, platform)
        THEME = 'std'
        # self += AlbumArtFrame(self  , (0.31, 0.93),align=('right','top'))
        ARTIST = {'artist': {'colour':'mid', 'align': ('centre', 'top')}}
        TRACK  = {'track' : {'colour':'mid', 'align': ('centre', 'top')}}
        # self += ArtistArtFrame(self  , (0.2, 1.0),align=('left','middle'))
        self += MetaDataFrame(self  , scalers=(0.45, 0.2), align=('left','top'), theme=THEME, show=ARTIST)
        self += MetaDataFrame(self  , scalers=(0.45, 0.2), align=('right','top'), theme=THEME, show=TRACK)
        self += PlayProgressFrame(self  , scalers=(1.0, 0.05), align=('centre','bottom'), theme=THEME)
        self += SpectrumFrame(self  ,  'right', scalers=(1.0, 0.5), align=('centre','bottom'), led_gap=0, flip=True, barw_min=3, bar_space=0.5, tip=True, theme=THEME )
        self += SpectrumFrame(self  ,  'left', scalers=(1.0, 0.5), align=('centre','top'), led_gap=0, barw_min=3, bar_space=0.5, tip=True, theme=THEME )

class TrackVUMeterScreen(Frame):   # comprises volume on the left, spectrum on the right
    @property
    def title(self): return 'VU Meters, Roon Album Art, Metadata and progress bar'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        Frame.__init__(self, platform)
        THEME = 'blue'
        # self += AlbumArtFrame(self  , scalers=(0.25, 0.93),align=('right','middle'))
        self += ArtistArtFrame(self  , scalers=(0.4, 0.5),align=('left','top'))
        self += MetaDataFrame(self  , scalers=(0.4, 0.5), align=('left','bottom'), theme=THEME)
        self += PlayProgressFrame(self  , scalers=(0.6, 0.05), align=('right','bottom'), theme=THEME)
        # self += VUMeterFrame1(self  , scalers=(0.5,0.7), align=('centre','middle'))
        self += VUMeterImageFrame(self  , type='blueVU', scalers=(0.6,1.0), align=('right','top'))

class TrackVUMeterScreen2(Frame):   # comprises volume on the left, spectrum on the right
    @property
    def title(self): return 'Analogue VU Meters, Diamondiser, Roon Album Art, Metadata and progress bar'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        Frame.__init__(self, platform)
        THEME     = 'meter1'
        NEEDLE    = { 'width':4, 'colour': 'foreground', 'length': 0.8, 'radius_pc': 1.0 }
        ENDSTOPS  = (3*PI/4, 5*PI/4)  #Position of endstop if not the edge of the frame
        PIVOT     = -0.5
        # self += AlbumArtFrame(self  , (0.25, 0.93),align=('right','middle'))
        # self += AlbumArtFrame(self  , (0.3, 0.3),align=('centre','top'))
        self += MetaDataFrame(self  , scalers=(0.3, 0.5), align=('centre','middle'), theme=THEME)
        self += PlayProgressFrame(self  , scalers=(1.0, 0.05), align=('centre','bottom'), theme=THEME)

        self += VUMeter(self  ,  'left', scalers=(0.35, 0.85), align=('left','middle'), pivot=PIVOT, arcs={}, endstops=ENDSTOPS, needle=NEEDLE)
        self += VUMeter(self  ,  'right', scalers=(0.35, 0.85), align=('right','middle'), pivot=PIVOT, arcs={}, endstops=ENDSTOPS, needle=NEEDLE)

        # self += VUMeterFrame1(self  , scalers=(0.7,0.7), align=('left','middle'))
        # self += Diamondiser(self  , 'left', scalers=(0.3, 1.0), align=('right','middle'), theme=THEME)


""" VU Meters """
VUMETERS = ['blueVU', 'goldVU', 'blackVU', 'rainVU', 'redVU', 'vintVU', 'whiteVU', 'greenVU']

class VUImageScreen(Frame):
    """ VU meters left and right - based on an image background"""
    @property
    def title(self): return 'VU meters with image background'

    @property
    def type(self): return 'VU Image'

    def __init__(self, platform, type='blueVU'):

        Frame.__init__(self, platform)
        self += VUMeterImageFrame(self  , type=type, scalers=(0.5,0.5), align=('left','top'))



""" Spectrum Analyser based Screens """


class SpectrumScreen(Frame):
    """ Volume/Source on left - Spectrum on left - one channel """
    def __init__(self, platform):
        Frame.__init__(self, platform)
        self += VolumeSourceFrame(self  , 0.2, 'right')
        self += SpectrumFrame(self  , 'left', scalers=(0.8,1.0), align=('centre','middle'))
        self.check()

class StereoSpectrumLRScreen(Frame):
    """ Volume/Source on left - Spectrum on left - one channel """
    def __init__(self, platform):
        Frame.__init__(self, platform)
        self += Spectrum2chFrame(self  , scalers=(1.0,1.0), align=('centre','middle'))
        self.check()

class FullSpectrumOffsetScreen(Frame):
    """ Volume/Source on left - Spectrum on left - one channel """
    def __init__(self, platform):
        Frame.__init__(self, platform)
        self += SpectrumStereoOffsetFrame(self  , scalers=(1.0,1.0), align=('centre','middle'))
        self.check()

class StereoSpectrumScreen(Frame):
    """ Volume/Source on left - Stereo Spectrum overlaid """
    def __init__(self, platform):
        Frame.__init__(self, platform)
        # self += VolumeSourceFrame(self  , 0.3, 'right')
        self += SpectrumStereoFrame(self  , scalers=(1.0,1.0), align=('centre','middle'))
        self.check()

class StereoSpectrumSplitScreen(Frame):
    """ Volume/Source on left - Stereo Spectrum overlaid """
    def __init__(self, platform):
        Frame.__init__(self, platform)
        # self += VolumeSourceFrame(self  , 0.3, 'right')
        self += SpectrumStereoSplitFrame(self  , scalers=(1.0,1.0), align=('centre','middle'))
        self.check()

"""
    SpectrumFrame API:
    # def __init__(self, platform, bounds, channel, scale, align=('left','bottom'), right_offset=0, theme='std', flip=False, \
    #                 led_h=5, led_gap=1, peak_h=1, col_mode='h', radius=0, bar_space=0.5, barw_min=12, barw_max=20, tip=False, decay=DECAY):
"""
class MonoSpectrumScreen(Frame):
    """ Volume/Source on left - Stereo Spectrum overlaid """
    def __init__(self, platform):
        Frame.__init__(self, platform)
        # def __init__(self, platform, bounds, channel, scale, align=('left','bottom'), right_offset=0, colour='white'):
        self += SpectrumFrame(self  , 'left', scalers=(1.0, 1.0), led_gap=0, barw_min=2, tip=True)
        self.check()

class MonoSpectrumLEDScreen(Frame):
    """ Volume/Source on left - Stereo Spectrum overlaid """
    def __init__(self, platform):
        Frame.__init__(self, platform)
        # def __init__(self, platform, bounds, channel, scale, align=('left','bottom'), right_offset=0, colour='white'):
        self += SpectrumFrame(self  , 'left', scalers=(1.0, 1.0), peak_h=2, led_gap=2, led_h=4, barw_min=6, bar_space=0.2, theme='leds')
        self.check()

class MixedLEDScreen(Frame):
    """ Volume/Source on left - Stereo Spectrum overlaid """
    def __init__(self, platform):
        Frame.__init__(self, platform)
        # def __init__(self, platform, bounds, channel, scale, align=('left','bottom'), right_offset=0, colour='white'):
        self += SpectrumFrame(self  , 'right', scalers=(0.8, 1.0), align=('right','middle'), peak_h=2, led_gap=3, led_h=5, barw_min=6, bar_space=0.2, theme='leds')
        self += VU2chFrame(self  , scalers=(0.2, 1.0), align=('left','top'), orient='vert', flip=False, theme='leds', led_gap=3, led_h=5)




""" System Utility screens """
""" old preamp screens that need refactoring """
# class MainScreen(Frame):
#     """ Vol/source in centre - spectrum left and right """
#     def __init__(self, platform):
#         Frame.__init__(self, platform)
#         self += SpectrumFrame(self  ,  'left', 0.3 )
#         self += dbVolumeSourceFrame(self  , 0.4, 'centre')
#         self += SpectrumFrame(self  ,  'right', 0.3 )
#
# class ScreenTitle(Frame):
#     def __init__(self, platform):
#         Frame.__init__(self, platform)
#         self += MenuFrame(self  , 'top', 1.0, 'very very long screen title')
#         self.check()
#
# class WelcomeScreen(Frame):
#     """ Startup screen """
#     text = "Welcome to SRC Visualiser"
#     def __init__(self, platform):
#         Frame.__init__(self, platform)
#         # def __init__(self, platform, bounds, Valign='top', scalers=(1.0, 1.0), text='Default Text', Halign='centre', fontsize=0):
#         self += TextFrame( platform, Valign='middle', scalers=(1.0, 1.0), text=WelcomeScreen.text)
#
# class ShutdownScreen(Frame):
#     """ Startup screen """
#     text = "Loved the music"
#
#     def __init__(self, platform):
#         Frame.__init__(self, platform)
#         # def __init__(self, platform, bounds, Valign='top', scalers=(1.0, 1.0), text='Default Text', Halign='centre', fontsize=0):
#         self += TextFrame( platform, 'top', 1.0, ShutdownScreen.text)
#
# class ScreenSaver(Frame):
#     """ force the screen to go blank """
#     def __init__(self, platform):
#         Frame.__init__(self, platform)
#         self += TextFrame( platform, 'top', 1.0, '')
#
# class VolChangeScreen(Frame):
#     def __init__(self, platform):
#         Frame.__init__(self, platform)
#         self += VolumeAmountFrame(self  , 0.6)
#         self += VolumeSourceFrame(self  , 0.4, 'right')
#         self.check()
#
# class RecordingScreen(Frame):
#     def __init__(self, platform):
#         Frame.__init__(self, platform)
#         self += RecordFrame( platform, 0.3)
#         self += VolumeSourceFrame(self  , 0.4, 'right')
#         self.check()
#
# class RecordFinishScreen(Frame):
#     def __init__(self, platform):
#         Frame.__init__(self, platform)
#         self += TextFrame( platform, 'top', 0.5, 'Recording saved to')
#         self += RecordEndFrame( platform, 'bottom', 0.5)
#         self.check()
#
# class SourceVolScreen(Frame):   # comprises volume on the left, spectrum on the right
#     def __init__(self, platform):
#         Frame.__init__(self, platform)
#         self += dbVolumeSourceFrame(self  , 0.4, 'right')
#         self += SourceIconFrame(self  , 0.6, 'left')
#         self.check()
#
# class SourceVUVolScreen(Frame):
#     def __init__(self, platform):
#         Frame.__init__(self, platform)
#         self += dbVolumeSourceFrame(self  , 0.4, 'right')
#         self += VUV2chFrame(self  , 0.3, 'centre')
#         self += SourceIconFrame(self  , 0.3, 'left')
#         self.check()

""" Horizontal VU bar meter """
class VUScreen(Frame):   # comprises volume on the left, spectrum on the right
    def __init__(self, platform):
        Frame.__init__(self, platform)
        # self += VolumeSourceFrame(self  , 0.4, 'right')
        # def __init__(self, platform, bounds, scalers, align=('left','bottom')):
        self += VU2chHorzFrame(self  , scalers=(1.0, 1.0), align=('centre', 'top'))
        self.check()

class VUVScreen(Frame):   # comprises volume on the left, spectrum on the right
    def __init__(self, platform):
        Frame.__init__(self, platform)
        # self += dbVolumeSourceFrame(self  , 0.5, 'right')
        # self += SpectrumFrame(self  , 'right', (0.7, 1.0), align=('right','middle'), led_gap=0, barw_min=2, tip=True)
        self += VU2chFrame(self  , scalers=(0.3, 0.5), align=('left','top'), orient='vert', flip=True)
        self += VUFlipFrame(self  , scalers=(0.5, 0.5), align=('right','bottom'), orient='vert', flip=True)
        self.check()

# class PlayerScreen(Frame):   # comprises volume on the left, spectrum on the right
#     def __init__(self, platform):
#         Frame.__init__(self, platform)
#         self += VolumeSourceFrame(self  , 0.2, 'right')
#         self += MetaDataFrame(self  , 0.8, 'left')
#         self.check()



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

    def __init__(self, platform, type=None):

        Frame.__init__(self, platform)

        self += VUMeterImageFrame(self  , type='blueVU', scalers=(0.5,0.5), align=('left','top'))
        self += VUMeterImageFrame(self  , type='goldVU', scalers=(0.5,0.5), align=('left','bottom'))
        self += VUMeterImageFrame(self  , type='blackVU', scalers=(0.5,0.5), align=('right','top'))
        self += VUMeterImageFrame(self  , type='rainVU', scalers=(0.5,0.5), align=('right','bottom'))
        # self += VUMeterImageFrame(self  , type='redVU', scalers=(0.5,0.5), align=('left','top'))
        # self += VUMeterImageFrame(self  , type='vintVU', scalers=(0.5,0.5), align=('left','bottom'))
        # self += VUMeterImageFrame(self  , type='whiteVU', scalers=(0.5,0.5), align=('right','top'))
        # self += VUMeterImageFrame(self  , type='greenVU', scalers=(0.5,0.5), align=('right','bottom'))

class TestVUImageScreen2(Frame):
    """ VU meters left and right - based on an image background"""
    @property
    def title(self): return 'Test multiple VU meters with image backgrounds'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        # METERS = ['blueVU', 'goldVU', 'blackVU', 'rainVU', 'redVU', 'vintVU', 'whiteVU', 'greenVU']
        Frame.__init__(self, platform)

        # self += VUMeterImageFrame(self  , type='blueVU', scalers=(0.5,0.5), align=('left','top'))
        # self += VUMeterImageFrame(self  , type='goldVU', scalers=(0.5,0.5), align=('left','bottom'))
        # self += VUMeterImageFrame(self  , type='blackVU', scalers=(0.5,0.5), align=('right','top'))
        # self += VUMeterImageFrame(self  , type='rainVU', scalers=(0.5,0.5), align=('right','bottom'))
        self += VUMeterImageFrame(self  , type='redVU', scalers=(0.5,0.5), align=('left','top'))
        self += VUMeterImageFrame(self  , type='vintVU', scalers=(0.5,0.5), align=('left','bottom'))
        self += VUMeterImageFrame(self  , type='whiteVU', scalers=(0.5,0.5), align=('right','top'))
        self += VUMeterImageFrame(self  , type='greenVU', scalers=(0.5,0.5), align=('right','bottom'))

class TestVUMetersScreen(Frame):
    """ Vol/source in centre - VU meters left and right """
    @property
    def title(self): return 'Tests out multiple configurations of Stereo VU Meters'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        Frame.__init__(self, platform)

        self += VUMeterFrame1(self  , scalers=(0.5,0.5), align=('left','top'))
        self += VUMeterFrame2(self  , scalers=(0.5,0.5), align=('left','bottom'))
        self += VUMeterFrame3(self  ,  scalers=(0.5,0.5), align=('right','top'))
        self += VUMeterFrame4(self  ,  scalers=(0.5,0.5), align=('right','bottom'))

        # self += VolumeSourceFrame(self  , 0.2, 'centre'

class TestVisualiserScreen(Frame):   # comprises volume on the left, spectrum on the right
    @property
    def title(self): return 'Test multiple configurations of Visualisers'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        Frame.__init__(self, platform)
        self += OscilogrammeBar(self  , 'left', scalers=(1.0,0.5), align=('right','top'))
        self += OscilogrammeBar(self  , 'right', scalers=(1.0,0.5), align=('right','bottom'), flip=True)
        # self += Diamondiser(self  , 'right', (0.5,0.5), align=('left','top'))
        # # self += Octaviser(self  , 'right', (0.5,0.5), align=('left','bottom'))
        # self += CircleModulator(self  , 'left', (0.5,0.5), align=('right','top'))


class TestSpectrumScreen(Frame):   # comprises volume on the left, spectrum on the right
    @property
    def title(self): return 'Tests out multiple configurations of spectrum analysers'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        Frame.__init__(self, platform)
        self += SpectrumStereoSplitFrame(self  , scalers=(0.5,0.5), align=('left','top'))
        # self += Spectrum2chFrame(self  , (0.5,0.5), align=('left','top'))
        self += SpectrumStereoOffsetFrame(self  , scalers=(0.5,0.5), align=('left','bottom'))
        #
        self += SpectrumFrame(self  , 'left', scalers=(0.5,0.5), align=('right','top'), peak_h=2, led_gap=2, led_h=4, barw_min=6, bar_space=0.2, theme='leds')
        # #mono
        self += SpectrumFrame(self  , 'left', scalers=(0.5,0.5), align=('right','bottom'), led_gap=0, barw_min=2, tip=True)


class TestVUScreen(Frame):   # comprises volume on the left, spectrum on the right
    @property
    def title(self): return 'Tests out Bar VU meters of all types'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        Frame.__init__(self, platform)
        # self += VU2chFrame(self  , scalers=(0.2, 0.5), align=('left','top'), orient='vert')
        # self += VU2chFrame(self  , scalers=(0.2, 1.0), align=('left','bottom'), orient='vert', flip=False)
        self += VU2chFrame(self  ,  scalers=(0.25, 1.0), align=('left','top'), orient='vert', flip=False)
        self += VUFlipFrame(self  ,  scalers=(0.25, 1.0), align=('right','bottom'), orient='vert', flip=True)
        self += VU2chHorzFrame(self  ,  scalers=(0.5, 0.5), align=('centre','top'),tip=True)
        self += VUFlipFrame(self  ,  scalers=(0.5, 0.5), align=('centre','bottom'), orient='horz', flip=True)


class TestScreen(Frame):
    @property
    def title(self): return 'Tests out Frames, nesting and components'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        Frame.__init__(self, platform)

        self += SubFrame(self  , scalers=(0.5,0.3), align=('left','top'))
        self += SubFrame(self  , scalers=(0.5,0.3), align=('right','bottom'))
        # self += TestFrame(platform, scalers=(1.0, 0.5), align=('left','top'))
        self += TextFrame(self,  scalers=(0.5,0.3), align=('centre','middle'), text='TextFrame')


class SubFrame(Frame):
    def __init__(self, parent, scalers, align):
        Frame.__init__(self, parent, scalers=scalers, align=align)
        # print("SubFrame> ", self.geostr())
        self += TestFrame(self  , scalers=(0.5, 0.3), align=('left','bottom'))
        self += TestFrame(self  , scalers=(0.5, 0.3), align=('centre','middle'))
        self += TestFrame(self  ,scalers=(0.5, 0.3), align=('right','top'))
        self += OutlineFrame(self  , scalers=(1.0, 1.0), align=('right','top'))

class TestFrame(Frame):
    """ A Frame is a box with coords relative to its enclosing Frame,
        on creation this creates the create, in the orientation and positioning withing the super-Frame
        componenets or subframes are added to this Frame
    """

    # def __init__(self, platform, bounds=None, display=None, scalers=[1.0,1.0], align=('left','bottom')):
    def __init__(self, parent, scalers, align):
        Frame.__init__(self, parent, scalers=scalers, align=align)
        # self.outline = Outline(self, platform)
        self.box     = Box(self  , box=(100,50), width=0, align=('right','top'))
        self.text    = TextFrame(self,  scalers=(1.0, 1.0), align=('right','top'), text=align[0]+align[1])
        # print("TestFrame.__init__>",  self.geostr())

    def draw(self):
        # print("TestFrame.draw>")
        # self.outline.draw()
        self.box.draw( (0,0) )
        self.text.draw()
