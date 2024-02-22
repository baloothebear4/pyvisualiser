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
from subframes import *
import time

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

        Frame.__init__(self, platform, theme='ocean', background='background')

        self += AlbumArtFrame(self  , scalers=(0.31, 1.0),align=('right','middle')) #m, outline={'colour_index':'light'})
        self += MetaDataFrame(self  , scalers=(0.38, 0.8), align=('centre','middle'))
        self += PlayProgressFrame(self  , scalers=(0.38, 0.05), align=('centre','bottom'))
        self += VU2chHorzFrame(self  , scalers=(0.3, 1.0), align=('left','top'))

class TrackVisScreen(Frame):   # comprises volume on the left, spectrum on the right
    @property
    def title(self): return 'Visualiser, Roon Album Art, Metadata and progress bar'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        Frame.__init__(self, platform, theme='blue')

        self += AlbumArtFrame(self  , scalers=(0.31, 1.0),align=('left','middle'))
        self += MetaDataFrame(self  , scalers=(0.38, 0.8), align=('centre','middle'))
        self += Diamondiser(self  , 'left', scalers=(0.31, 1.0), align=('right','middle'))
        self += PlayProgressFrame(self  , scalers=(0.38, 0.05), align=('centre','bottom'))

class TrackVisScreen2(Frame):   # comprises volume on the left, spectrum on the right
    @property
    def title(self): return 'Complex Visualiser, Roon Album Art, Metadata and progress bar'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        Frame.__init__(self, platform, theme='tea')

        ARTIST = {'artist': {'colour':'foreground', 'align': ('centre', 'middle'), 'scalers': (1.0, 0.5)}}
        TRACK  = {'track' : {'colour':'mid', 'align': ('centre', 'middle'), 'scalers': (1.0, 0.5)}}
        ALBUM  = {'track' : {'colour':'mid', 'align': ('centre', 'middle'), 'scalers': (1.0, 0.5)}}
        # self += ArtistArtFrame(self  , (0.2, 1.0),align=('left','middle'))
        self += MetaDataFrame(self  , scalers=(0.33, 0.2), align=('centre','top'), show=ARTIST)
        self += MetaDataFrame(self  , scalers=(0.33, 0.2), align=('left','top'), show=TRACK)        # self += ArtistArtFrame(self  , (0.2, 1.0),align=('left','middle'))
        self += MetaDataFrame(self  , scalers=(0.33, 0.2), align=('right','top'), show=ALBUM)
        self += CircleModulator(self  , 'mono', scalers=(1.0,1.0), align=('centre','middle'))
        self += PlayProgressFrame(self  , scalers=(1.0, 0.05), align=('centre','bottom'))

class TrackVisScreen3(Frame):   # comprises volume on the left, spectrum on the right
    @property
    def title(self): return 'Oscillograme Bar, Complex Visualiser, Roon Album Art, Metadata and progress bar'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        Frame.__init__(self, platform, theme='std')

        ARTIST = {'artist': {'colour':'foreground', 'align': ('centre', 'top')}}
        TRACK  = {'track' : {'colour':'mid', 'align': ('centre', 'top')}}
        ALBUM  = {'track' : {'colour':'mid', 'align': ('centre', 'top')}}
        # self += ArtistArtFrame(self  , (0.2, 1.0),align=('left','middle'))
        self += MetaDataFrame(self  ,  scalers=(0.5, 0.5), align=('centre','top'))
        self += Diamondiser(self  ,  'left', scalers=(0.7, 0.7), align=('right','top'))
        self += PlayProgressFrame(self  ,  scalers=(1.0, 0.05), align=('centre','bottom'))
        self += SamplesFrame(self  ,  scalers=(1.0, 0.5), align=('left','bottom'))

        # self += VUFlipFrame(self  , scalers=(0.5, 0.5), align=('left','top'), orient='horz', flip=True)
        # self += OscilogrammeBar(self  , 'mono', scalers=(0.66,0.5), align=('left','top'), barsize_pc=0.5, led_gap=0)
        # self += OscilogrammeBar(self  , 'mono', scalers=(0.33,0.5), align=('left','bottom'), flip=True, barsize_pc=0.5, led_gap=0)

class SamplesFrame(Frame):
    """ Volume/Source on left - Spectrum on left - one channel """
    def __init__(self, parent, scalers=(1.0, 1.0), align=('centre','middle'), theme='std'):
        Frame.__init__(self, parent, scalers=scalers, align=align)
        self += OscilogrammeBar(self  ,  'left', scalers=(1.0,0.5), align=('left','top'), barsize_pc=0.5, led_gap=0,barw_min=2)
        self += OscilogrammeBar(self  ,  'right', scalers=(1.0,0.5), align=('left','bottom'), flip=True, barsize_pc=0.5, led_gap=0, barw_min=2)

class TrackSpectrumScreen(Frame):   # comprises volume on the left, spectrum on the right
    @property
    def title(self): return 'Spectrum Analyser, Roon Album Art, Metadata and progress bar'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        Frame.__init__(self, platform, theme='blue')

        subframe = Frame(self, scalers=(0.45,1.0),align=('centre', 'bottom'))
        self += MetaDataFrame(self  , scalers=(0.33, 0.8), align=('centre','middle'))
        self += PlayProgressFrame(self  , scalers=(0.38, 0.05), align=('centre','bottom'))

        self += AlbumArtFrame(self  , scalers=(0.31, 1.0), align=('right','middle'))
        self += SpectrumFrame(self  ,  'right', scalers=(0.33, 0.5), align=('left','bottom'), flip=True, led_gap=2, peak_h=0, radius=2, barw_min=5, bar_space=0.6)
        self += SpectrumFrame(self  ,  'left', scalers=(0.33, 0.5), align=('left','top'), flip=False, led_gap=2, peak_h=0,radius=2, barw_min=5, bar_space=0.6)

class TrackSpectrumScreen2(Frame):   # comprises volume on the left, spectrum on the right
    @property
    def title(self): return 'Spectrum Analyser 2, Roon Album Art, Metadata and progress bar'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        Frame.__init__(self, platform, theme= 'white')

        self += ArtistArtFrame(self  , scalers=(0.5,1.0),align=('left','middle'), opacity=50)
        self += MetaArtFrame(self  ,  scalers=(0.5, 1.0),align=('right','middle'))
        self += PlayProgressFrame(self  ,  scalers=(0.5, 0.05), align=('left','bottom'))
        self += SpectrumFrame(self  ,  'right', scalers=(0.5, 0.5), align=('left','bottom'), flip=True, led_gap=0, peak_h=1, radius=0, tip=True, barw_min=3, bar_space=2)
        self += SpectrumFrame(self  ,  'left', scalers=(0.5, 0.5), align=('left','top'), flip=False, led_gap=0, peak_h=1,radius=0, tip=True, barw_min=3, bar_space=2 )


class MetaArtFrame(Frame):
    """ A subframe to nicely wrap the Metadata around the Art on the left """
    def __init__(self, parent, scalers=None, align=None, theme='std'):
        Frame.__init__(self, parent, scalers=scalers, align=align)

        # SHOW = { 'artist': {'colour': 'foreground', 'align': ('centre','top'),   'scalers': (1.0, 0.33) }, \
        #          'track': {'colour' : 'light',      'align': ('centre','bottom'), 'scalers': (1.0, 0.33)}, \
        #          'album': {'colour' : 'mid',        'align': ('centre','middle'), 'scalers': (1.0, 0.33)} }
        ARTIST = {'artist': {'colour':'foreground', 'align': ('right', 'middle'), 'scalers': (1.0, 1.0)}}
        TRACK  = {'track' : {'colour':'light', 'align': ('right', 'middle'), 'scalers': (1.0, 1.0)}}
        ALBUM  = {'album' : {'colour':'mid',   'align': ('right','middle'), 'scalers': (1.0, 1.0)} }

        self += MetaDataFrame(self  , scalers=(1.0, 0.2), align=('right','top'), show=ARTIST)
        self += MetaDataFrame(self  , scalers=(0.6, 0.6), align=('right','middle'), show=ALBUM)
        self += MetaDataFrame(self  , scalers=(1.0, 0.2), align=('right','bottom'), show=TRACK)
        self += AlbumArtFrame(self  ,  scalers=(0.4, 1.0),align=('left','middle'), outline={'colour_index':'light'})

        # print("MetaArtFrame.__init__")

class TrackSpectrumScreen3(Frame):   # comprises volume on the left, spectrum on the right
    @property
    def title(self): return 'Full Spectrum Analyser, Roon Album Art, Metadata and progress bar'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        Frame.__init__(self, platform, theme = 'std')

        # self += AlbumArtFrame(self  , (0.31, 0.93),align=('right','top'))
        ARTIST = {'artist': {'colour':'light', 'align': ('centre', 'middle'), 'scalers': (1.0, 0.5)}}
        TRACK  = {'track' : {'colour':'mid', 'align': ('centre', 'middle'), 'scalers': (1.0, 0.5)}}
        # self += ArtistArtFrame(self  , (0.2, 1.0),align=('left','middle'))
        self += MetaDataFrame(self  , scalers=(0.45, 0.5), align=('right','top'), show=ARTIST)
        self += MetaDataFrame(self  , scalers=(0.45, 0.5), align=('right','bottom'), show=TRACK)
        self += PlayProgressFrame(self  , scalers=(1.0, 0.05), align=('centre','bottom'))
        self += SpectrumFrame(self  ,  'right', scalers=(1.0, 0.5), align=('centre','bottom'), led_gap=0, flip=True, barw_min=3, bar_space=0.5, tip=True )
        self += SpectrumFrame(self  ,  'left', scalers=(1.0, 0.5), align=('centre','top'), led_gap=0, barw_min=3, bar_space=0.5, tip=True )

class TrackSpectrumScreen4(Frame):   # comprises volume on the left, spectrum on the right
    @property
    def title(self): return 'Spectrum Analyser 4, Artist & progress bar'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        Frame.__init__(self, platform, theme= 'ocean')

        ARTIST = {'artist': {'colour':'foreground', 'align': ('right', 'top'), 'scalers': (1.0, 1.0)}}

        subframe = Frame(self, scalers=(0.8,0.5), align=('centre', 'top'))

        # self += ArtistArtFrame(self, scalers=(0.6, 0.6),align=('centre','middle'), opacity=120)
        self += AlbumArtFrame(self,  scalers=(1.0, 0.7),align=('right','middle'), opacity=255, outline={'colour_index':'light'})
        self += PlayProgressFrame(self,  scalers=(0.9, 0.05), align=('centre','bottom'))
        self += SpectrumFrame(self,  'right', scalers=(0.8, 0.5), align=('left','bottom'), flip=True, led_gap=5, peak_h=3, radius=0, tip=True, barw_min=3, bar_space=5)
        self += SpectrumFrame(self,  'left', scalers=(0.8, 0.5), align=('left','top'), flip=False, led_gap=5, peak_h=3,radius=0, tip=True, barw_min=3, bar_space=5 )
        self += MetaDataFrame(self, scalers=(0.5, 0.2), align=('right','top'), show=ARTIST)
        

class TrackVUMeterScreen(Frame):   # comprises volume on the left, spectrum on the right
    @property
    def title(self): return 'VU Meters, Roon Album Art, Metadata and progress bar'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        Frame.__init__(self, platform, theme= 'blue')

        # self += AlbumArtFrame(self  , scalers=(0.25, 0.93),align=('right','middle'))
        subframe1 = Frame(self,scalers=(0.5,0.50), align=('left','top'))
        subframe2 = Frame(self,scalers=(0.5,0.50), align=('left','bottom'))
        subframe3 = Frame(self,scalers=(0.5,0.95), align=('right','top'))
        self += ArtistArtFrame(subframe1  , scalers=(1.0,0.95),align=('centre','middle'), outline={'colour_index':'foreground'})
        self += MetaDataFrame(subframe2  , scalers=(1.0, 0.95), align=('centre','top'))
        self += VUMeterImageFrame(subframe3  , type='blueVU', scalers=(0.95,1.0), align=('centre','middle'),outline={'colour_index':'light'})
        self += PlayProgressFrame(self  , scalers=(0.5, 0.05), align=('right','bottom'))

class TrackVUMeterScreen2(Frame):   # comprises volume on the left, spectrum on the right
    @property
    def title(self): return 'Analogue VU Meters, Roon Album Art, Metadata and progress bar'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        Frame.__init__(self, platform, theme= 'meter1')
  
        NEEDLE    = { 'width':4, 'colour': 'foreground', 'length': 0.8, 'radius_pc': 1.0 }
        ENDSTOPS  = (3*PI/4, 5*PI/4)  #Position of endstop if not the edge of the frame
        PIVOT     = -0.5
        # self += AlbumArtFrame(self  , (0.25, 0.93),align=('right','middle'))
        # self += AlbumArtFrame(self  , (0.3, 0.3),align=('centre','top'))
        self += MetaDataFrame(self  , scalers=(0.3, 0.8), align=('centre','middle'))
        self += ArtistArtFrame(self  , scalers=(1.0,1.0),align=('centre','middle'), opacity=40)
        self += PlayProgressFrame(self  , scalers=(1.0, 0.05), align=('centre','bottom'))
        self += VUMeter(self  ,  'left', scalers=(0.35, 0.85), align=('left','middle'), pivot=PIVOT, arcs={}, endstops=ENDSTOPS, needle=NEEDLE)
        self += VUMeter(self  ,  'right', scalers=(0.35, 0.85), align=('right','middle'), pivot=PIVOT, arcs={}, endstops=ENDSTOPS, needle=NEEDLE)

        # self += VUMeterFrame1(self  , scalers=(0.7,0.7), align=('left','middle'))
        # self += Diamondiser(self  , 'left', scalers=(0.3, 1.0), align=('right','middle'))

class TrackOscScreen(Frame):   # comprises volume on the left, spectrum on the right
    @property
    def title(self): return 'Oscillogram, Roon Album Art, Metadata and progress bar'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        Frame.__init__(self, platform, theme= 'red')
 
        subframe = Frame(self, scalers=(0.4, 1.0), align=('right','middle'))
        self += VU2chFrame(subframe, scalers=(0.2, 1.0), align=('left','middle'))
        # self += AlbumArtFrame(subframe, (1.0, 1.0),align=('right','middle'))

        self += ArtistArtFrame(self, scalers=(0.6,1.0),align=('left','middle'), opacity=100)
        self += MetaDataFrame(self, scalers=(0.3, 0.8), align=('right','middle'))
        self += PlayProgressFrame(self, scalers=(0.6, 0.05), align=('left','bottom'))

        self += Oscilogramme(self, 'mono', scalers=(0.6, 1.0), align=('left','middle'))

class BigDialsScreen(Frame):   # comprises volume on the left, spectrum on the right
    @property
    def title(self): return 'Lightback with 270 speedo dial type VU dial'

    @property
    def type(self): return 'Visualiser and metadata'

    def __init__(self, platform):
        Frame.__init__(self, platform, theme= 'space')
        # OUTLINE = { 'width' : 3, 'radius' : 0, 'colour_index' : 'foreground'}
        TICK_W    = 4
        ARCLEN    = 0.9
        NEEDLELEN = 0.9
        TICKLEN   = 0.9        # length marks
        TICK_PC   = 0.20         # lenth of the ticks as PC of the needle
        SCALESLEN = 1.05
        MARKS     = {0.0: {'text':'0', 'width': TICK_W, 'colour': 'mid'},
                     0.14: {'text':'1', 'width': TICK_W, 'colour': 'mid'},
                     0.28: {'text':'2', 'width': TICK_W, 'colour': 'mid'},
                     0.42: {'text':'3', 'width': TICK_W, 'colour': 'mid'},
                     0.56: {'text':'4', 'width': TICK_W, 'colour': 'mid'},
                     0.70: {'text':'5', 'width': TICK_W, 'colour': 'mid'},
                     0.84: {'text':'6', 'width': TICK_W, 'colour': 'mid'},
                     1.0: {'text':'7', 'width': TICK_W, 'colour': 'mid'} }
        ARCS      = {ARCLEN        : {'width': TICK_W//3, 'colour': 'mid'}}
                    #  ARCLEN*0.95   : {'width': TICK_W//3, 'colour': 'mid'},
                    #  ARCLEN*0.97   : {'width': TICK_W//3, 'colour': 'mid'}  }
        ANNOTATE  = { 'Valign':'bottom', 'text':'', 'colour':'mid' }
        NEEDLE    = { 'width':4, 'colour': 'foreground', 'length': NEEDLELEN, 'radius_pc': 1.0 }
    
        self += Lightback(self, scalers=(0.64,0.64), align=('centre','middle'), colour_index='dark', flip=True)
        self += VUMeter(self, 'mono', scalers=(0.7, 0.7), align=('centre', 'middle'), peakmeter=True, ticklen=TICKLEN, scaleslen=SCALESLEN,\
                        pivot=0, endstops=(3*PI/8, 13*PI/8), marks=MARKS, arcs=ARCS, annotate=ANNOTATE, needle=NEEDLE, tick_pc=TICK_PC)
        # self += VUMeter(self, 'right', scalers=(0.5, 1.0), align=('right', 'bottom'), \
        #                 pivot=0, endstops=(PI/4, 7*PI/4), marks=MARKS, arcs=ARCS,annotate=ANNOTATE,)
        subframe = Frame(self,scalers=(0.32, 0.95), align=('right','middle') )
        subframe2= Frame(self, scalers=(0.31, 0.55), align=('left','top'))
        self += AlbumArtFrame(subframe, (1.0, 1.0),align=('centre','middle'), outline={'colour_index':'light', 'width':5, 'opacity': 200, 'radius': 20})
        self += MetaDataFrame(subframe2  , scalers=(0.9,0.9), align=('centre','middle'))
        self += SpectrumFrame(self,  'mono', scalers=(0.68, 0.7), align=('left','bottom'), flip=False, led_gap=5, peak_h=3,radius=4, tip=True, barw_min=3, bar_space=1 )
        self += PlayProgressFrame(self  , scalers=(0.68, 0.05), align=('left','bottom'))

class MetaVUScreen(Frame):   # comprises volume on the left, spectrum on the right
    @property
    def title(self): return 'Horizontal VUs with full meta data'

    @property
    def type(self): return 'Visualiser and metadata'

    def __init__(self, platform):
        Frame.__init__(self, platform, theme= 'ocean')
        """
            Central panel of artist with horz VUs below, progress below
            Diamondiser top left
            Album art top right
            Split out meta data
        
        """

        ARTIST = {'artist': {'colour':'foreground', 'align': ('centre', 'bottom'), 'scalers': (0.33, 1.0)}}
        TRACK  = {'track' : {'colour':'light', 'align': ('centre', 'middle'), 'scalers': (0.6, 1.0)}}
        ALBUM  = {'album' : {'colour':'mid',   'align': ('centre','middle'), 'scalers': (0.6, 1.0)} }

        META = {'track' : {'colour':'light', 'align': ('left', 'middle'), 'scalers': (0.3, 1.0)},
                'album' : {'colour':'mid',   'align': ('right','middle'), 'scalers': (0.3, 1.0)} }
        # 'artist': {'colour':'foreground', 'align': ('centre', 'top'), 'scalers': (1.0, 1.0)},

        albumframe   = Frame(self, scalers=(0.33, 0.8), align=('right','top'))
        self += AlbumArtFrame(albumframe, scalers=(0.95,0.95),align=('centre','bottom'), outline={'colour_index':'light', 'width':5, 'opacity': 255, 'radius': 20})
        self += Diamondiser(self  ,  'mono', scalers=(1.0, 0.7), align=('left','top'))

        self += MetaDataFrame(self  , scalers=(1.0, 0.2), align=('centre','bottom'), show=META)
        self += MetaDataFrame(self  , scalers=(1.0, 0.2), align=('centre','top'), show=ARTIST)
        # self += MetaDataFrame(self  , scalers=(0.33, 0.3), align=('centre','bottom'), show=ARTIST)
        # self += MetaDataFrame(self  , scalers=(0.33, 0.3), align=('right','bottom'), show=ALBUM)
        # self += MetaDataFrame(self  , scalers=(0.33, 0.3), align=('left','bottom'), show=TRACK)

        # self += SpectrumFrame(self,  'mono', scalers=(0.68, 0.7), align=('left','bottom'), flip=False, led_gap=5, peak_h=3,radius=4, tip=True, barw_min=3, bar_space=1 )
        self += PlayProgressFrame(self  , scalers=(1.0, 0.05), align=('centre','bottom'))
        self += ArtistArtFrame(self, scalers=(0.4,0.5),align=('centre','middle'), opacity=255, outline={'colour_index':'light', 'width':5, 'opacity': 255, 'radius': 20})

        # VUFrame API (self, parent, channel, scalers=None, align=None, barsize_pc=0.7, theme=None, flip=False, \
        #             led_h=5, led_gap=1, peak_h=1, radius=0, barw_min=10, barw_max=400, tip=False, decay=VU.DECAY, orient='vert'):
        vusubframe   = Frame(self,scalers=(0.4, 0.3), align=('centre','bottom') )
        self += VUFrame(vusubframe, 'left',  align=('left','middle'), scalers=(0.5, 0.8), orient='horz',flip=True, barsize_pc=0.7,led_h=5, led_gap=1, peak_h=3, radius=3, barw_min=10 )
        self += VUFrame(vusubframe, 'right', align=('right','middle'), scalers=(0.5, 0.8), orient='horz',flip=False, barsize_pc=0.7,led_h=5, led_gap=1, peak_h=3, radius=3, barw_min=10 )

class ArtistScreen(Frame):   # comprises volume on the left, spectrum on the right
    @property
    def title(self): return 'Artist art front and centre'

    @property
    def type(self): return 'Visualiser and metadata'

    def __init__(self, platform):
        Frame.__init__(self, platform, theme= 'zomp')
        """
            Central panel of artist with horz VUs below, progress below
            Album art top right
            Split out meta data
        
        """

        ARTIST = {'artist': {'colour':'light', 'align': ('centre', 'middle'), 'scalers': (1.0, 1.0)}}
        TRACK  = {'track' : {'colour':'light', 'align': ('centre', 'middle'), 'scalers': (0.6, 1.0)}}
        ALBUM  = {'album' : {'colour':'mid',   'align': ('centre','middle'), 'scalers': (0.6, 1.0)} }

        META = {'track' : {'colour':'light', 'align': ('centre', 'bottom'), 'scalers': (1.0, 1.0)},
                'artist' : {'colour':'mid',   'align': ('centre','top'), 'scalers': (1.0, 1.0)} }
        # 'artist': {'colour':'foreground', 'align': ('centre', 'top'), 'scalers': (1.0, 1.0)},

        self += ArtistArtFrame(self, scalers=(1.0,0.85),align=('centre','middle'), opacity=255, outline={'colour_index':'dark', 'width':4, 'opacity': 255, 'radius': 10})
        albumframe   = Frame(self, scalers=(1.0, 0.8), align=('left','middle'))
        self += AlbumArtFrame(self, scalers=(1.0,0.7),align=('left','bottom'), opacity=140, outline={'colour_index':'dark', 'width':5, 'opacity': 230, 'radius': 10})

        # self += MetaDataFrame(self  , scalers=(0.2, 0.2), align=('left','top'), show=META)
        self += MetaDataFrame(self  , scalers=(0.18, 0.3), align=('left','top'), show=ARTIST)
        # self += MetaDataFrame(self  , scalers=(0.33, 0.3), align=('centre','bottom'), show=ARTIST)
        # self += MetaDataFrame(self  , scalers=(0.33, 0.3), align=('right','bottom'), show=ALBUM)
        # self += MetaDataFrame(self  , scalers=(0.33, 0.3), align=('left','bottom'), show=TRACK)

        # self += SpectrumFrame(self,  'mono', scalers=(0.68, 0.7), align=('left','bottom'), flip=False, led_gap=5, peak_h=3,radius=4, tip=True, barw_min=3, bar_space=1 )
        self += PlayProgressFrame(self  , scalers=(0.55, 0.05), align=('centre','bottom'))


        # VUFrame API (self, parent, channel, scalers=None, align=None, barsize_pc=0.7, theme=None, flip=False, \
        #             led_h=5, led_gap=1, peak_h=1, radius=0, barw_min=10, barw_max=400, tip=False, decay=VU.DECAY, orient='vert'):
        vusubframe   = Frame(self,scalers=(0.18, 1.0), align=('right','middle') )
        self += VUFrame(vusubframe, 'left',  align=('centre','bottom'), scalers=(0.6, 0.5), orient='vert',flip=True, barsize_pc=0.7,led_h=5, led_gap=1, peak_h=3, radius=3, barw_min=10 )
        self += VUFrame(vusubframe, 'right', align=('centre','top'), scalers=(0.6, 0.5), orient='vert',flip=False, barsize_pc=0.7,led_h=5, led_gap=1, peak_h=3, radius=3, barw_min=10 )
