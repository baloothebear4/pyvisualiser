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
        self += AlbumArtFrame(platform, self.coords, (0.31, 1.0),align=('right','middle'))
        self += MetaDataFrame(platform, self.coords, (0.38, 0.6), align=('centre','middle'), theme=THEME)
        self += PlayProgressFrame(platform, self.coords, (0.38, 0.05), align=('centre','bottom'), theme=THEME)
        self += VU2chHorzFrame(platform, self.coords, scalers=(0.3, 1.0), align=('left','top'), theme=THEME)

class TrackVisScreen(Frame):   # comprises volume on the left, spectrum on the right
    @property
    def title(self): return 'Visualiser, Roon Album Art, Metadata and progress bar'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        Frame.__init__(self, platform)
        THEME = 'blue'
        self += AlbumArtFrame(platform, self.coords, (0.31, 1.0),align=('left','middle'))
        self += MetaDataFrame(platform, self.coords, (0.38, 0.6), align=('centre','middle'), theme=THEME)
        self += Diamondiser(platform, self.coords, 'left', scalers=(0.31, 1.0), align=('right','middle'), theme=THEME)
        self += PlayProgressFrame(platform, self.coords, (0.38, 0.05), align=('centre','bottom'), theme=THEME)

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
        # self += ArtistArtFrame(platform, self.coords, (0.2, 1.0),align=('left','middle'))
        self += MetaDataFrame(platform, self.coords, (0.33, 0.2), align=('centre','top'), theme=THEME, show=ARTIST)
        self += MetaDataFrame(platform, self.coords, (0.33, 0.2), align=('left','top'), theme=THEME, show=TRACK)        # self += ArtistArtFrame(platform, self.coords, (0.2, 1.0),align=('left','middle'))
        self += MetaDataFrame(platform, self.coords, (0.33, 0.2), align=('right','top'), theme=THEME, show=ALBUM)
        self += CircleModulator(platform, self.coords, 'mono', scalers=(0.6, 0.6), align=('centre','middle'), theme=THEME)
        self += PlayProgressFrame(platform, self.coords, (1.0, 0.05), align=('centre','bottom'), theme=THEME)

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
        # self += ArtistArtFrame(platform, self.coords, (0.2, 1.0),align=('left','middle'))
        self += MetaDataFrame(platform, self.coords,  (0.66, 0.5), align=('centre','top'), theme=THEME)
        self += Diamondiser(platform, self.coords,  'left', scalers=(0.7, 0.7), align=('right','top'), theme=THEME)
        self += PlayProgressFrame(platform, self.coords,  (1.0, 0.05), align=('centre','bottom'), theme=THEME)
        self += SamplesFrame(platform, self.coords,  scalers=(1.0, 0.5), align=('left','bottom'), theme=THEME)
        # self += VUFlipFrame(platform, self.coords, scalers=(0.5, 0.5), align=('left','top'), orient='horz', flip=True, theme=THEME)
        # self += OscilogrammeBar(platform, self.coords, 'mono', (0.66,0.5), align=('left','top'), barsize_pc=0.5, led_gap=0)
        # self += OscilogrammeBar(platform, self.coords, 'mono', (0.33,0.5), align=('left','bottom'), flip=True, barsize_pc=0.5, led_gap=0)

class SamplesFrame(Frame):
    """ Volume/Source on left - Spectrum on left - one channel """
    def __init__(self, platform, bounds, scalers=(1.0, 1.0), align=('centre','middle'), theme='std'):
        Frame.__init__(self, platform, bounds, scalers=scalers, align=align)
        self += OscilogrammeBar(platform, self.coords,  'mono', (1.0,0.5), align=('left','top'), barsize_pc=0.5, led_gap=0)
        self += OscilogrammeBar(platform, self.coords,  'mono', (1.0,0.5), align=('left','bottom'), flip=True, barsize_pc=0.5, led_gap=0)

class TrackSpectrumScreen(Frame):   # comprises volume on the left, spectrum on the right
    @property
    def title(self): return 'Spectrum Analyser, Roon Album Art, Metadata and progress bar'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        Frame.__init__(self, platform)
        THEME = 'blue'
        self += AlbumArtFrame(platform, self.coords, (0.31, 1.0), align=('right','middle'))
        self += MetaDataFrame(platform, self.coords, (0.38, 0.6), align=('centre','middle'), theme=THEME)
        self += PlayProgressFrame(platform, self.coords, (0.38, 0.05), align=('centre','bottom'), theme=THEME)
        self += SpectrumFrame(platform, self.coords,  'right', (0.31, 0.5), align=('left','bottom'), flip=True, led_gap=2, peak_h=0, radius=2, theme=THEME, barw_min=5, bar_space=0.6)
        self += SpectrumFrame(platform, self.coords,  'left', (0.31, 0.5), align=('left','top'), flip=False, led_gap=2, peak_h=0,radius=2, theme=THEME, barw_min=5, bar_space=0.6)

class TrackSpectrumScreen2(Frame):   # comprises volume on the left, spectrum on the right
    @property
    def title(self): return 'Spectrum Analyser 2, Roon Album Art, Metadata and progress bar'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        Frame.__init__(self, platform)
        THEME = 'white'
        self += MetaArtFrame(platform, self.coords,  (0.5, 1.0),align=('right','middle'))
        self += PlayProgressFrame(platform, self.coords,  (0.66, 0.05), align=('left','bottom'), theme=THEME)
        self += SpectrumFrame(platform, self.coords,  'right', (0.5, 0.5), align=('left','bottom'), flip=True, led_gap=0, peak_h=1, radius=0, tip=True, theme=THEME, barw_min=3, bar_space=2)
        self += SpectrumFrame(platform, self.coords,  'left', (0.5, 0.5), align=('left','top'), flip=False, led_gap=0, peak_h=1,radius=0, tip=True, theme=THEME, barw_min=3, bar_space=2 )

class MetaArtFrame(Frame):
    """ Volume/Source on left - Spectrum on left - one channel """
    def __init__(self, platform, bounds, scalers=(1.0, 1.0), align=('centre','middle'), theme='std'):
        Frame.__init__(self, platform, bounds, scalers=scalers, align=align)
        self += AlbumArtFrame(platform, self.coords,  (0.62, 1.0),align=('right','middle'))
        self += MetaDataFrame(platform, self.coords,  (0.38, 1.0), align=('left','middle'), theme=theme)

class TrackSpectrumScreen3(Frame):   # comprises volume on the left, spectrum on the right
    @property
    def title(self): return 'Full Spectrum Analyser, Roon Album Art, Metadata and progress bar'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        Frame.__init__(self, platform)
        THEME = 'std'
        # self += AlbumArtFrame(platform, self.coords, (0.31, 0.93),align=('right','top'))
        ARTIST = {'artist': {'colour':'mid', 'align': ('centre', 'top')}}
        TRACK  = {'track' : {'colour':'mid', 'align': ('centre', 'top')}}
        # self += ArtistArtFrame(platform, self.coords, (0.2, 1.0),align=('left','middle'))
        self += MetaDataFrame(platform, self.coords, (0.45, 0.2), align=('left','top'), theme=THEME, show=ARTIST)
        self += MetaDataFrame(platform, self.coords, (0.45, 0.2), align=('right','top'), theme=THEME, show=TRACK)
        self += PlayProgressFrame(platform, self.coords, (1.0, 0.05), align=('centre','bottom'), theme=THEME)
        self += SpectrumFrame(platform, self.coords,  'right', (1.0, 0.5), align=('centre','bottom'), led_gap=0, flip=True, barw_min=3, bar_space=0.5, tip=True, theme=THEME )
        self += SpectrumFrame(platform, self.coords,  'left', (1.0, 0.5), align=('centre','top'), led_gap=0, barw_min=3, bar_space=0.5, tip=True, theme=THEME )

class TrackVUMeterScreen(Frame):   # comprises volume on the left, spectrum on the right
    @property
    def title(self): return 'VU Meters, Roon Album Art, Metadata and progress bar'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        Frame.__init__(self, platform)
        THEME = 'blue'
        # self += AlbumArtFrame(platform, self.coords, (0.25, 0.93),align=('right','middle'))
        self += ArtistArtFrame(platform, self.coords, (0.4, 0.5),align=('left','top'))
        self += MetaDataFrame(platform, self.coords, (0.4, 0.5), align=('left','bottom'), theme=THEME)
        self += PlayProgressFrame(platform, self.coords, (0.6, 0.05), align=('right','bottom'), theme=THEME)
        # self += VUMeterFrame1(platform, self.coords, scalers=(0.5,0.7), align=('centre','middle'))
        self += VUMeterImageFrame(platform, self.coords, type='blueVU', scalers=(0.6,1.0), align=('right','top'))

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
        # self += AlbumArtFrame(platform, self.coords, (0.25, 0.93),align=('right','middle'))
        # self += AlbumArtFrame(platform, self.coords, (0.3, 0.3),align=('centre','top'))
        self += MetaDataFrame(platform, self.coords, (0.3, 0.5), align=('centre','middle'), theme=THEME)
        self += PlayProgressFrame(platform, self.coords, (1.0, 0.05), align=('centre','bottom'), theme=THEME)

        self += VUMeter(platform, self.coords,  'left', scalers=(0.35, 0.85), align=('left','middle'), pivot=PIVOT, arcs={}, endstops=ENDSTOPS, needle=NEEDLE)
        self += VUMeter(platform, self.coords,  'right', scalers=(0.35, 0.85), align=('right','middle'), pivot=PIVOT, arcs={}, endstops=ENDSTOPS, needle=NEEDLE)

        # self += VUMeterFrame1(platform, self.coords, scalers=(0.7,0.7), align=('left','middle'))
        # self += Diamondiser(platform, self.coords, 'left', scalers=(0.3, 1.0), align=('right','middle'), theme=THEME)


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
        self += VUMeterImageFrame(platform, self.coords, type=type, scalers=(0.5,0.5), align=('left','top'))



""" Spectrum Analyser based Screens """


class SpectrumScreen(Frame):
    """ Volume/Source on left - Spectrum on left - one channel """
    def __init__(self, platform):
        Frame.__init__(self, platform)
        self += VolumeSourceFrame(platform, self.coords, 0.2, 'right')
        self += SpectrumFrame(platform, self.coords, 'left', (0.8,1.0), align=('centre','middle'))
        self.check()

class StereoSpectrumLRScreen(Frame):
    """ Volume/Source on left - Spectrum on left - one channel """
    def __init__(self, platform):
        Frame.__init__(self, platform)
        self += Spectrum2chFrame(platform, self.coords, (1.0,1.0), align=('centre','middle'))
        self.check()

class FullSpectrumOffsetScreen(Frame):
    """ Volume/Source on left - Spectrum on left - one channel """
    def __init__(self, platform):
        Frame.__init__(self, platform)
        self += SpectrumStereoOffsetFrame(platform, self.coords, (1.0,1.0), align=('centre','middle'))
        self.check()

class StereoSpectrumScreen(Frame):
    """ Volume/Source on left - Stereo Spectrum overlaid """
    def __init__(self, platform):
        Frame.__init__(self, platform)
        # self += VolumeSourceFrame(platform, self.coords, 0.3, 'right')
        self += SpectrumStereoFrame(platform, self.coords, (1.0,1.0), align=('centre','middle'))
        self.check()

class StereoSpectrumSplitScreen(Frame):
    """ Volume/Source on left - Stereo Spectrum overlaid """
    def __init__(self, platform):
        Frame.__init__(self, platform)
        # self += VolumeSourceFrame(platform, self.coords, 0.3, 'right')
        self += SpectrumStereoSplitFrame(platform, self.coords, (1.0,1.0), align=('centre','middle'))
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
        self += SpectrumFrame(platform, self.coords, 'left', (1.0, 1.0), led_gap=0, barw_min=2, tip=True)
        self.check()

class MonoSpectrumLEDScreen(Frame):
    """ Volume/Source on left - Stereo Spectrum overlaid """
    def __init__(self, platform):
        Frame.__init__(self, platform)
        # def __init__(self, platform, bounds, channel, scale, align=('left','bottom'), right_offset=0, colour='white'):
        self += SpectrumFrame(platform, self.coords, 'left', (1.0, 1.0), peak_h=2, led_gap=2, led_h=4, barw_min=6, bar_space=0.2, theme='leds')
        self.check()

class MixedLEDScreen(Frame):
    """ Volume/Source on left - Stereo Spectrum overlaid """
    def __init__(self, platform):
        Frame.__init__(self, platform)
        # def __init__(self, platform, bounds, channel, scale, align=('left','bottom'), right_offset=0, colour='white'):
        self += SpectrumFrame(platform, self.coords, 'right', (0.8, 1.0), align=('right','middle'), peak_h=2, led_gap=3, led_h=5, barw_min=6, bar_space=0.2, theme='leds')
        self += VU2chFrame(platform, self.coords, scalers=(0.2, 1.0), align=('left','top'), orient='vert', flip=False, theme='leds', led_gap=3, led_h=5)




""" System Utility screens """
""" old preamp screens that need refactoring """
# class MainScreen(Frame):
#     """ Vol/source in centre - spectrum left and right """
#     def __init__(self, platform):
#         Frame.__init__(self, platform)
#         self += SpectrumFrame(platform, self.coords,  'left', 0.3 )
#         self += dbVolumeSourceFrame(platform, self.coords, 0.4, 'centre')
#         self += SpectrumFrame(platform, self.coords,  'right', 0.3 )
#
# class ScreenTitle(Frame):
#     def __init__(self, platform):
#         Frame.__init__(self, platform)
#         self += MenuFrame(platform, self.coords, 'top', 1.0, 'very very long screen title')
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
#         self += VolumeAmountFrame(platform, self.coords, 0.6)
#         self += VolumeSourceFrame(platform, self.coords, 0.4, 'right')
#         self.check()
#
# class RecordingScreen(Frame):
#     def __init__(self, platform):
#         Frame.__init__(self, platform)
#         self += RecordFrame( platform, 0.3)
#         self += VolumeSourceFrame(platform, self.coords, 0.4, 'right')
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
#         self += dbVolumeSourceFrame(platform, self.coords, 0.4, 'right')
#         self += SourceIconFrame(platform, self.coords, 0.6, 'left')
#         self.check()
#
# class SourceVUVolScreen(Frame):
#     def __init__(self, platform):
#         Frame.__init__(self, platform)
#         self += dbVolumeSourceFrame(platform, self.coords, 0.4, 'right')
#         self += VUV2chFrame(platform, self.coords, 0.3, 'centre')
#         self += SourceIconFrame(platform, self.coords, 0.3, 'left')
#         self.check()

""" Horizontal VU bar meter """
class VUScreen(Frame):   # comprises volume on the left, spectrum on the right
    def __init__(self, platform):
        Frame.__init__(self, platform)
        # self += VolumeSourceFrame(platform, self.coords, 0.4, 'right')
        # def __init__(self, platform, bounds, scalers, align=('left','bottom')):
        self += VU2chHorzFrame(platform, self.coords, (1.0, 1.0), align=('centre', 'top'))
        self.check()

class VUVScreen(Frame):   # comprises volume on the left, spectrum on the right
    def __init__(self, platform):
        Frame.__init__(self, platform)
        # self += dbVolumeSourceFrame(platform, self.coords, 0.5, 'right')
        # self += SpectrumFrame(platform, self.coords, 'right', (0.7, 1.0), align=('right','middle'), led_gap=0, barw_min=2, tip=True)
        self += VU2chFrame(platform, self.coords, scalers=(0.3, 0.5), align=('left','top'), orient='vert', flip=True)
        self += VUFlipFrame(platform, self.coords, scalers=(0.5, 0.5), align=('right','bottom'), orient='vert', flip=True)
        self.check()

class PlayerScreen(Frame):   # comprises volume on the left, spectrum on the right
    def __init__(self, platform):
        Frame.__init__(self, platform)
        self += VolumeSourceFrame(platform, self.coords, 0.2, 'right')
        self += MetaDataFrame(platform, self.coords, 0.8, 'left')
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

    def __init__(self, platform, type=None):

        Frame.__init__(self, platform)

        self += VUMeterImageFrame(platform, self.coords, type='blueVU', scalers=(0.5,0.5), align=('left','top'))
        self += VUMeterImageFrame(platform, self.coords, type='goldVU', scalers=(0.5,0.5), align=('left','bottom'))
        self += VUMeterImageFrame(platform, self.coords, type='blackVU', scalers=(0.5,0.5), align=('right','top'))
        self += VUMeterImageFrame(platform, self.coords, type='rainVU', scalers=(0.5,0.5), align=('right','bottom'))
        # self += VUMeterImageFrame(platform, self.coords, type='redVU', scalers=(0.5,0.5), align=('left','top'))
        # self += VUMeterImageFrame(platform, self.coords, type='vintVU', scalers=(0.5,0.5), align=('left','bottom'))
        # self += VUMeterImageFrame(platform, self.coords, type='whiteVU', scalers=(0.5,0.5), align=('right','top'))
        # self += VUMeterImageFrame(platform, self.coords, type='greenVU', scalers=(0.5,0.5), align=('right','bottom'))

class TestVUImageScreen2(Frame):
    """ VU meters left and right - based on an image background"""
    @property
    def title(self): return 'Test multiple VU meters with image backgrounds'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        # METERS = ['blueVU', 'goldVU', 'blackVU', 'rainVU', 'redVU', 'vintVU', 'whiteVU', 'greenVU']
        Frame.__init__(self, platform)

        # self += VUMeterImageFrame(platform, self.coords, type='blueVU', scalers=(0.5,0.5), align=('left','top'))
        # self += VUMeterImageFrame(platform, self.coords, type='goldVU', scalers=(0.5,0.5), align=('left','bottom'))
        # self += VUMeterImageFrame(platform, self.coords, type='blackVU', scalers=(0.5,0.5), align=('right','top'))
        # self += VUMeterImageFrame(platform, self.coords, type='rainVU', scalers=(0.5,0.5), align=('right','bottom'))
        self += VUMeterImageFrame(platform, self.coords, type='redVU', scalers=(0.5,0.5), align=('left','top'))
        self += VUMeterImageFrame(platform, self.coords, type='vintVU', scalers=(0.5,0.5), align=('left','bottom'))
        self += VUMeterImageFrame(platform, self.coords, type='whiteVU', scalers=(0.5,0.5), align=('right','top'))
        self += VUMeterImageFrame(platform, self.coords, type='greenVU', scalers=(0.5,0.5), align=('right','bottom'))

class TestVUMetersScreen(Frame):
    """ Vol/source in centre - VU meters left and right """
    @property
    def title(self): return 'Tests out multiple configurations of Stereo VU Meters'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        Frame.__init__(self, platform)

        self += VUMeterFrame1(platform, self.coords, scalers=(0.5,0.5), align=('left','top'))
        self += VUMeterFrame2(platform, self.coords, scalers=(0.5,0.5), align=('left','bottom'))
        self += VUMeterFrame3(platform, self.coords,  scalers=(0.5,0.5), align=('right','top'))
        self += VUMeterFrame4(platform, self.coords,  scalers=(0.5,0.5), align=('right','bottom'))

        # self += VolumeSourceFrame(platform, self.coords, 0.2, 'centre'

class TestVisualiserScreen(Frame):   # comprises volume on the left, spectrum on the right
    @property
    def title(self): return 'Test multiple configurations of Visualisers'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        Frame.__init__(self, platform)
        self += OscilogrammeBar(platform, self.coords, 'left', (1.0,0.5), align=('right','top'))
        self += OscilogrammeBar(platform, self.coords, 'right', (1.0,0.5), align=('right','bottom'), flip=True)
        # self += Diamondiser(platform, self.coords, 'right', (0.5,0.5), align=('left','top'))
        # # self += Octaviser(platform, self.coords, 'right', (0.5,0.5), align=('left','bottom'))
        # self += CircleModulator(platform, self.coords, 'left', (0.5,0.5), align=('right','top'))


class TestSpectrumScreen(Frame):   # comprises volume on the left, spectrum on the right
    @property
    def title(self): return 'Tests out multiple configurations of spectrum analysers'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        Frame.__init__(self, platform)
        self += SpectrumStereoSplitFrame(platform, self.coords, (0.5,0.5), align=('left','top'))
        # self += Spectrum2chFrame(platform, self.coords, (0.5,0.5), align=('left','top'))
        self += SpectrumStereoOffsetFrame(platform, self.coords, (0.5,0.5), align=('left','bottom'))
        #
        self += SpectrumFrame(platform, self.coords, 'left', (0.5,0.5), align=('right','top'), peak_h=2, led_gap=2, led_h=4, barw_min=6, bar_space=0.2, theme='leds')
        # #mono
        self += SpectrumFrame(platform, self.coords, 'left', (0.5,0.5), align=('right','bottom'), led_gap=0, barw_min=2, tip=True)


class TestVUScreen(Frame):   # comprises volume on the left, spectrum on the right
    @property
    def title(self): return 'Tests out Bar VU meters of all types'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        Frame.__init__(self, platform)
        # self += VU2chFrame(platform, self.coords, scalers=(0.2, 0.5), align=('left','top'), orient='vert')
        # self += VU2chFrame(platform, self.coords, scalers=(0.2, 1.0), align=('left','bottom'), orient='vert', flip=False)
        self += VU2chFrame(platform, self.coords,  scalers=(0.25, 1.0), align=('left','top'), orient='vert', flip=False)
        self += VUFlipFrame(platform, self.coords,  scalers=(0.25, 1.0), align=('right','bottom'), orient='vert', flip=True)
        self += VU2chHorzFrame(platform, self.coords,  (0.5, 0.5), align=('centre','top'),tip=True)
        self += VUFlipFrame(platform, self.coords,  scalers=(0.5, 0.5), align=('centre','bottom'), orient='horz', flip=True)


class TestScreen(Frame):
    @property
    def title(self): return 'Tests out Frames, nesting and components'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        Frame.__init__(self, platform)

        self += SubFrame(platform, self.coords, (0.5,0.3), ('left','top'))
        self += SubFrame(platform, self.coords, (0.5,0.3), ('right','bottom'))
        # self += TestFrame(platform, scalers=(1.0, 0.5), align=('left','top'))
        self += TextFrame(self,  (0.5,0.3), ('centre','middle'), text='TextFrame')


class SubFrame(Frame):
    def __init__(self, platform, bounds, scalers, align):
        Frame.__init__(self, platform, bounds, scalers, align)
        # print("SubFrame> ", self.geostr())
        self += TestFrame(platform, self.coords, scalers=(0.5, 0.3), align=('left','bottom'))
        self += TestFrame(platform, self.coords, scalers=(0.5, 0.3), align=('centre','middle'))
        self += TestFrame(platform, self.coords,scalers=(0.5, 0.3), align=('right','top'))
        self += OutlineFrame(platform, self.coords, scalers=(1.0, 1.0), align=('right','top'))

class TestFrame(Frame):
    """ A Frame is a box with coords relative to its enclosing Frame,
        on creation this creates the create, in the orientation and positioning withing the super-Frame
        componenets or subframes are added to this Frame
    """

    # def __init__(self, platform, bounds=None, display=None, scalers=[1.0,1.0], align=('left','bottom')):
    def __init__(self, platform, bounds, scalers, align):
        Frame.__init__(self, platform, bounds, scalers, align)
        # self.outline = Outline(self, platform)
        self.box     = Box(platform, self.coords, box=(100,50), width=0, align=('right','top'))
        self.text    = TextFrame(self,  scalers=(1.0, 1.0), align=('right','top'), text=align[0]+align[1])
        # print("TestFrame.__init__>",  self.geostr())

    def draw(self):
        # print("TestFrame.draw>")
        # self.outline.draw()
        self.box.draw( (0,0) )
        self.text.draw()
