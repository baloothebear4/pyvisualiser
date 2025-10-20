#!/usr/bin/env python
"""
 All top level screens.  Screens are comprised of Frames

 Part of mVista preDAC2 project

 v3.0 Baloothebear4 Dec 2023


"""

"""
Working throught the frames that work and the ones that don't:
ArtistScreen, --> renders at 47fps, 16,s loop. OK
StereoSpectrumSplitScreen --> slow, 24 fps 
TrackScreen  --> 47fps. looks good, but the meta data sucks. Artist and Album are scaled too big
MetaVUScreen --> Tesxt is squashed and is not laying out well
BigDialsScreen --> multiple overlays and only 30fps -> spect looks very cool

TrackSpectrumScreen, TrackSpectrumScreen2, TrackSpectrumScreen3, TrackSpectrumScreen4, \
            TrackOscScreen, TrackVisScreen, TrackVisScreen2, TrackVisScreen3, TrackVUMeterScreen, TrackVUMeterScreen2  )

"""

from    frames import *
from    subframes import *
from    framecore import Frame, ColFramer, RowFramer


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

        self += AlbumArtFrame(self  , scalers=(0.31, 1.0),align=('right','middle'), outline={'colour_index':'dark'})
        self += MetaDataFrame(self  , scalers=(0.38, 1.0), align=('centre','middle'))
        # self += PlayProgressFrame(self  , scalers=(0.38, 0.05), align=('centre','bottom'))
        self += VU2chHorzFrame(self  , scalers=(0.3, 1.0), align=('left','top'))

class TrackVisScreen(Frame):   # comprises volume on the left, spectrum on the right
    @property
    def title(self): return 'Visualiser, Roon Album Art, Metadata and progress bar'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        Frame.__init__(self, platform, theme='blue')

        self += AlbumArtFrame(self  , scalers=(0.31, 1.0),align=('left','middle'))
        self += MetaDataFrame(self  , scalers=(0.38, 1.0), align=('centre','middle'))
        self += Diamondiser(self  , 'left', scalers=(0.31, 1.0), align=('right','middle'))
        # self += PlayProgressFrame(self  , scalers=(0.38, 0.05), align=('centre','bottom'))

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
        self += MetaData(self  , 'artist', scalers=(0.33, 0.2), align=('centre','top'))
        self += MetaData(self  , 'track', scalers=(0.33, 0.2), align=('centre', 'middle'))        # self += ArtistArtFrame(self  , (0.2, 1.0),align=('left','middle'))
        self += MetaData(self  , 'album', scalers=(0.33, 0.2), align=('centre', 'bottom'))
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
        ALBUM  = {'album' : {'colour':'mid', 'align': ('centre', 'top')}}
        # self += ArtistArtFrame(self  , (0.2, 1.0),align=('left','middle'))
        subframe = RowFramer(self)
        subframe += SamplesFrame(subframe,  scalers=(1.0, 1.0))
        subframe += MetaData(subframe,  'track', colour='foreground')
        subframe += MetaData(subframe,  'artist', colour='mid', scalers=(1.0,0.8))
        # self += Diamondiser(self  ,  'left', scalers=(0.7, 0.7), align=('right','top'))

        subframe += PlayProgressFrame(subframe,  scalers=(1.0, 1.0))


        # self += VUFlipFrame(self  , scalers=(0.5, 0.5), align=('left','top'), orient='horz', flip=True)
        # self += OscilogrammeBar(self  , 'mono', scalers=(0.66,0.5), align=('left','top'), barsize_pc=0.5, led_gap=0)
        # self += OscilogrammeBar(self  , 'mono', scalers=(0.33,0.5), align=('left','bottom'), flip=True, barsize_pc=0.5, led_gap=0)



class TrackSpectrumScreen(Frame):   # comprises volume on the left, spectrum on the right
    @property
    def title(self): return 'Spectrum Analyser, Roon Album Art, Metadata and progress bar'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        Frame.__init__(self, platform, theme='blue')

        subframe = Frame(self, scalers=(0.45,1.0),align=('centre', 'bottom'))
        self += MetaDataFrame(self  , scalers=(0.33, 1.0), align=('centre','middle'))
        # self += PlayProgressFrame(self  , scalers=(0.33, 0.05), align=('centre','bottom'))

        self += AlbumArtFrame(self  , scalers=(0.31, 1.0), align=('right','middle'))
        # self += SpectrumFrame(self  ,  'right', scalers=(0.33, 0.5), align=('left','bottom'), flip=True, led_gap=2, peak_h=0, radius=2, barw_min=5, bar_space=0.6)
        # self += SpectrumFrame(self  ,  'left', scalers=(0.33, 0.5), align=('left','top'), flip=False, led_gap=2, peak_h=0,radius=2, barw_min=5, bar_space=0.6)
        self += SpectrumFrame(self  ,  'mono', scalers=(0.33, 1.0), align=('left','bottom'), flip=False, led_gap=2, peak_h=2, radius=2, barw_min=5, bar_space=0.6)

class TrackSpectrumScreen2(Frame):   # comprises volume on the left, spectrum on the right
    @property
    def title(self): return 'Spectrum Analyser 2, Roon Album Art, Metadata and progress bar'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        Frame.__init__(self, platform, theme= 'white')

        cols = ColFramer(self)
        # spectrum = Frame(cols)
        # spectrum += SpectrumFrame(spectrum  ,  'right', scalers=(1.0, 0.5), align=('left','bottom'), flip=True, led_gap=0, peak_h=1, radius=0, tip=True, barw_min=3, bar_space=2)
        # spectrum += SpectrumFrame(spectrum  ,  'left', scalers=(1.0, 0.5), align=('left','top'), flip=False, led_gap=0, peak_h=1,radius=0, tip=True, barw_min=3, bar_space=2 )
        cols += StereoSpectrumFrame(cols)
        artoutline = {'colour_index':'background', 'width':5}
        cols += ArtistArtFrame(cols  , scalers=(0.8,1.0),align=('left','middle'), opacity=100, outline=artoutline)
        cols += MetaDataFrame(cols  ,  scalers=(1.0, 1.0),align=('right','middle'))
        # self += PlayProgressFrame(self  ,  scalers=(0.5, 0.05), align=('left','bottom'))

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

        self += MetaDataFrame(self  , scalers=(1.0, 0.2))
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
        spectrumframe = Frame(self, scalers=(0.7,1.0), align=('left', 'top'))
        spectrumframe += SpectrumFrame(spectrumframe  ,  'right', scalers=(1.0, 0.5), align=('centre','bottom'), led_gap=0, flip=True, barw_min=3, bar_space=0.5, tip=True )
        spectrumframe += SpectrumFrame(spectrumframe  ,  'left', scalers=(1.0, 0.5), align=('centre','top'), led_gap=0, barw_min=3, bar_space=0.5, tip=True )
        # self += MetaData(self  , 'artist', scalers=(0.3, 0.5), align=('right','top'))
        # self += MetaData(self  , 'track', scalers=(0.3, 0.5), align=('right','bottom'))
        # self += PlayProgressFrame(self  , scalers=(0.7, 0.05), align=('left','bottom'))
        self += spectrumframe
        meta = RowFramer(self, scalers=(0.3,1.0), align=('right','middle'))
        meta += MetaData(meta  , 'track', colour='mid') # scalers=(0.5, 1.0), align=('right','top'))
        meta +=ArtistArtFrame(meta,  opacity=120)
        meta += MetaData(meta  , 'artist', colour='dark') #scalers=(0.5, 1.0), align=('right','bottom'))


class TrackSpectrumScreen4(Frame):   # comprises volume on the left, spectrum on the right
    @property
    def title(self): return 'Spectrum Analyser 4, Artist & progress bar'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        Frame.__init__(self, platform, theme= 'ocean')

        ARTIST = {'artist': {'colour':'foreground', 'align': ('centre', 'top'), 'scalers': (1.0, 1.0)}}

        subframe = Frame(self, scalers=(0.8,0.5), align=('centre', 'top'))

        # self += ArtistArtFrame(self, scalers=(0.6, 0.6),align=('centre','middle'), opacity=120)
        self += AlbumArtFrame(self,  scalers=(1.0, 0.7),align=('right','middle'), opacity=255, outline={'colour_index':'light'})
        self += PlayProgressFrame(self,  scalers=(0.9, 0.05), align=('centre','bottom'))

        spectrumframe = Frame(self, scalers=(0.7,0.8), align=('left', 'middle'))
        self += SpectrumFrame(spectrumframe,  'right', scalers=(1.0, 0.5), align=('left','bottom'), flip=True, led_gap=5, peak_h=3, radius=0, tip=False, barw_min=15, bar_space=0.5)
        self += SpectrumFrame(spectrumframe,  'left', scalers=(1.0, 0.5), align=('left','top'), flip=False, led_gap=5, peak_h=3,radius=0, tip=False, barw_min=15, bar_space=0.5 )
        self += MetaData(self, 'track', scalers=(1.0, 0.2), align=('centre','top'))
        

class TrackVUMeterScreen(Frame):   # comprises volume on the left, spectrum on the right
    @property
    def title(self): return 'VU Meters, Roon Album Art, Metadata and progress bar'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        Frame.__init__(self, platform, theme= 'blue')

        # self += AlbumArtFrame(self  , scalers=(0.25, 0.93),align=('right','middle'))
        subframe1 = ColFramer(self)
        subframe2 = RowFramer(subframe1)
        # subframe3 = Frame(self,scalers=(0.5,0.95), align=('right','top'))
        subframe2 += ArtistArtFrame(subframe2  , scalers=(1.0,1.0),align=('centre','middle'), outline={'colour_index':'foreground'})
        subframe2 += MetaDataFrame(subframe2  , scalers=(1.0, 1.0), align=('centre','top'))
        subframe1 += VUMeterImageFrame(subframe1  , type='blueVU', scalers=(0.95,1.0), align=('centre','middle'),outline={'colour_index':'light'})
        # self += PlayProgressFrame(self  , scalers=(0.5, 0.05), align=('right','bottom'))

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
        OUTLINE={'colour_index':'light', 'width':2, 'opacity': 200, 'radius': 20}
        # self += AlbumArtFrame(self  , (0.25, 0.93),align=('right','middle'))
        # self += AlbumArtFrame(self  , (0.3, 0.3),align=('centre','top'))
        # self += MetaDataFrame(self  , scalers=(0.3, 1.0), align=('centre','middle'))
        # # self += ArtistArtFrame(self  , scalers=(1.0,1.0),align=('centre','middle'), opacity=40)
        # # self += PlayProgressFrame(self  , scalers=(0.3, 0.05), align=('centre','bottom'))
        # self += VUMeter(self  ,  'left', scalers=(0.3, 0.9), align=('left','top'), pivot=PIVOT, arcs={}, endstops=ENDSTOPS, needle=NEEDLE,outline=OUTLINE) #, background='mid')
        # self += VUMeter(self  ,  'right', scalers=(0.3, 0.9), align=('right','top'), pivot=PIVOT, arcs={}, endstops=ENDSTOPS, needle=NEEDLE,outline=OUTLINE) #,background='mid')
        cols = ColFramer(self)
        cols += VUMeter(cols  ,  'left', square=True, scalers=(0.9, 0.9), align=('left','top'), pivot=PIVOT, arcs={}, endstops=ENDSTOPS, needle=NEEDLE,outline=OUTLINE) #, background='mid')
        cols += MetaDataFrame(cols  ,  scalers=(1.0, 1.0), align=('centre','middle'))
        cols += VUMeter(cols  ,  'right', square=True, scalers=(0.9, 0.9), align=('right','top'), pivot=PIVOT, arcs={}, endstops=ENDSTOPS, needle=NEEDLE,outline=OUTLINE) #,background='mid')


class TrackVUMeterScreen21(Frame):   # comprises volume on the left, spectrum on the right
    @property
    def title(self): return 'Analogue VU Meters, Roon Album Art, Metadata and progress bar'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        super().__init__(platform, theme= 'meter1')
  
        NEEDLE    = { 'width':4, 'colour': 'foreground', 'length': 0.8, 'radius_pc': 1.0 }
        ENDSTOPS  = (3*PI/4, 5*PI/4)  #Position of endstop if not the edge of the frame
        PIVOT     = -0.5
        OUTLINE={'colour_index':'light', 'width':2, 'opacity': 200, 'radius': 20}
        # self += AlbumArtFrame(self  , (0.25, 0.93),align=('right','middle'))
        # self += AlbumArtFrame(self  , (0.3, 0.3),align=('centre','top'))

        colframe = ColFramer(self, padding=0.01, scalers=(1.0, 1.0), align=('centre','top'), background='dark')

        # colframe += AlbumArtFrame(colframe)

        # centreframe = RowFramer(colframe, background='dark', padding=0.0)

        # self += PlayProgressFrame(self  , scalers=(1.0, 0.1), align=('centre','bottom'))
 
        # colframes += VUMeter(colframes  ,  'right', scalers=(0.3, 0.9), align=('right','top'), pivot=PIVOT, arcs={}, endstops=ENDSTOPS, needle=NEEDLE,outline=OUTLINE) #,background='mid')
        # colframe += Frame(colframe  , scalers=(0.5, 1.0), background='light', outline={'colour_index':'alert'})
        # colframe += Frame(colframe  , background='mid')
        # colframe += Frame(colframe  ,  scalers=(1.0, 0.3), align=('left','top'), background='foreground')
        colframe  += VUMeter(colframe,  'left',  scalers=(1.0, 1.0), pivot=PIVOT, arcs={}, endstops=ENDSTOPS, needle=NEEDLE,outline=OUTLINE) #, background='mid')
        colframe  += MetaDataFrame(colframe )
        colframe  += VUMeter(colframe,  'right', scalers=(1.0, 1.0), pivot=PIVOT, arcs={}, endstops=ENDSTOPS, needle=NEEDLE,outline=OUTLINE) #,background='mid')
  
        # colframe   += ArtistArtFrame(colframe, opacity=100)

        print("TrackVUMeterScreen21 > colframe", colframe.framestr())
 
 
        # self += VUMeterFrame1(self  , scalers=(0.7,0.7), align=('left','middle'))
        # self += Diamondiser(self  , 'left', scalers=(0.3, 1.0), align=('right','middle'))        

class TrackOscScreen(Frame):   # comprises volume on the left, spectrum on the right
    @property
    def title(self): return 'Oscillogram, Roon Album Art, Metadata and progress bar'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        Frame.__init__(self, platform, theme= 'red')
        self.create()

    def create(self):
        subframe = ColFramer(self, scalers=(1.0, 0.7), align=('right','top'))
        # led_h=5, led_gap=1,barsize_pc=0.7, theme=None
        subframe += MetaDataFrame(subframe, scalers=(1.0, 1.0))
        subframe += ArtistArtFrame(subframe, scalers=(1.0,1.0), opacity=100)
        subframe += VU2chFrame(subframe, scalers=(0.1, 1.0), align=('right','middle'), led_h=7, led_gap=2,barsize_pc=0.1, outline={'colour_index':'foreground', 'width':0})
        # self += AlbumArtFrame(subframe, (1.0, 1.0),align=('right','middle'))


        # self += PlayProgressFrame(self, scalers=(0.6, 0.05), align=('left','bottom'))

        self += Oscilogramme(self, 'mono', scalers=(1.0, 0.3), align=('left','bottom'))

class SpectrumBaseArt(Frame):   # comprises volume on the left, spectrum on the right
    @property
    def title(self): return 'Base spectrum screen with al'

    @property
    def type(self): return 'Visualiser and metadata'

    def __init__(self, platform):
        Frame.__init__(self, platform, theme= 'space')

        # colframe  = ColFramer(self, scalers=(1.0,1.0), align=('right','middle'), padding=0.1)
        rowframe   = RowFramer(self, scalers=(0.67,1.0), align=('left','middle'), padding=0.0)
        rowframe += MetaData(rowframe, 'track', align=('centre','top'))
        rowframe += SpectrumFrame(rowframe,  'mono', scalers=(1.0,1.0), align=('left','bottom'), flip=False, led_gap=5, peak_h=3,radius=4, tip=True, barw_min=3, bar_space=1 )
        # subframe += MetaDataFrame(subframe, scalers=(1.0, 1.0))

        outline={'colour_index':'light', 'width':5, 'opacity': 200, 'radius': 20}
        self += AlbumArtFrame(self, scalers=(0.33, 1.0),align=('right','middle'))

        # self += Lightback(self, scalers=(0.64,0.64), align=('centre','middle'), colour_index='dark', flip=True)

        # self += VUMeter(self, 'right', scalers=(0.5, 1.0), align=('right', 'bottom'), \
        #                 pivot=0, endstops=(PI/4, 7*PI/4), marks=MARKS, arcs=ARCS,annotate=ANNOTATE,)

 
        # subframe  = RowFramer(self, scalers=(0.7, 0.2), align=('left','top'), padding=0.1)

 

        # self += PlayProgressFrame(self  , scalers=(0.68, 0.05), align=('left','bottom'))

class MinSpectrumArt(Frame):   # comprises volume on the left, spectrum on the right
    @property
    def title(self): return 'Base spectrum screen with al'

    @property
    def type(self): return 'Visualiser and metadata'

    def __init__(self, platform):
        Frame.__init__(self, platform, theme= 'std')

        colframe = ColFramer(self ) # for album art with padding
        colframe += StereoSpectrumFrame(colframe)
        colframe += MetaDataFrame(colframe)  #, scalers=(1.0,1.0), align=('centre','top'))
        colframe += AlbumArtFrame(colframe)  #, outline={'colour_index':'light', 'width':5, 'opacity': 200, 'radius': 20})

        # subframe2= Frame(self, scalers=(0.7, 0.8), align=('right','top'))     # for playprogress and Meta data 

        # self += PlayProgressFrame(subframe2  , scalers=(0.9, 0.075), align=('centre','bottom'))
        
        # subframe3= Frame(self, scalers=(0.7, 0.2), align=('right','bottom'))     # for playprogress and Meta data 
        # colframe += SpectrumFrame(colframe,  'mono', flip=False, led_gap=0, peak_h=1,radius=0, tip=False, barw_min=1, bar_space=2, col_mode='horz' )


class ArtMetaSpectrumScreen(Frame):   # comprises volume on the left, spectrum on the right
    @property
    def title(self): return 'Base spectrum screen with al'

    @property
    def type(self): return 'Visualiser and metadata'

    def __init__(self, platform):
        Frame.__init__(self, platform, theme= 'std')

        # colframe = ColFramer(self, padding =0.00, background='dark' ) # for album art with padding
        # colframe += AlbumArtFrame(colframe, scalers=(1.0,1.0))  #, outline={'colour_index':'light', 'width':5, 'opacity': 200, 'radius': 20})
        # colframe += MetaMiniSpectrumFrame(colframe, scalers=(1.0,1.0), justify='left')
        # rowframe    = RowFramer(self, scalers=(0.67,0.8), align=('right','top'), padding =0.00, background='dark' ) # for album art with padding
        self       += AlbumArtFrame(self, scalers=(0.33,1.0), align=('left','middle'))  #, outline={'colour_index':'light', 'width':5, 'opacity': 200, 'radius': 20})
        self   += MetaDataFrame(self, scalers=(0.67,0.8), align=('right','top'), justify='left')
        self   += SpectrumFrame(self,'mono', scalers=(0.67, 0.2), align=('right','bottom'), flip=False, led_gap=0, peak_h=1,radius=0, tip=False, barw_min=1, bar_space=2, col_mode='horz' )

class BigDialsScreen2(Frame):   # comprises volume on the left, spectrum on the right
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
        Frame.__init__(self, platform, theme= 'hifi')
        self.create()
        """
            Central panel of artist with horz VUs below, progress below
            Diamondiser top left
            Album art top right
            Split out meta data
        
        """

    def create(self):
        colframe = ColFramer(self)
        # albumframe   = Frame(self, scalers=(0.33, 0.8), align=('right','top'))
 
        colframe += Diamondiser(colframe,  'mono')
        colframe += MetaDataFrame(colframe)
        colframe += AlbumArtFrame(colframe, scalers=(0.95,0.95), outline={'colour_index':'light', 'width':5, 'opacity': 255, 'radius': 20})

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
 
        cols = ColFramer(self)
        cols += AlbumArtFrame(cols, scalers=(0.9,1.0),align=('left','middle'), outline={'colour_index':'dark', 'width':7, 'opacity': 255, 'radius': 0})
        cols += ArtistMetaDataFrame(cols)
        cols += VUFlipFrame(cols, scalers=(0.5,1.0))
