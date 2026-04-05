#!/usr/bin/env python
"""
 All top level screens.  Screens are comprised of Frames

 v1.0 Baloothebear4 Mar 2026


"""


# from pyvisualiser import *
from pyvisualiser.visualisers.vumeters import *
from pyvisualiser.visualisers.metadata import *
from pyvisualiser.visualisers.spectrum import *

from pyvisualiser.styles.presets import *
from pyvisualiser.styles.styles  import *
from pyvisualiser.core.framecore  import Frame, RowFramer, ColFramer


class H1(Frame):   # comprises volume on the left, spectrum on the right
    @property
    def title(self): return 'Hero 1: Analogue VU Meters, Roon Album Art, Metadata and progress bar'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):


        BACKGROUND    = BackgroundStyle(colour='background', ambient_glow=None, \
                                        texture_path='particles.jpg', texture_opacity=0.2, \
                                        reactive_glow=None, starfield=False, cloud=True   )
        
        SimpleOutline         = OutlineStyle(colour='mid', width=1, radius=10, opacity=1.0, glow_intensity=0.0, softness=0.1)
        Frame.__init__(self, platform, background=BACKGROUND, theme= 'hifi', padding=5, outline=None)

        # """ 210 degree dial type VU  """

        # TICK_W    = 2
        # ARCLEN   = 0.7
        # TICKLEN    = ARCLEN
        # SCALE_RADIUS = ARCLEN-0.15
        # MARKS     = {0.00: {'text':'0', 'width': TICK_W, 'colour': 'mid'},
        #              0.14: {'text':'1', 'width': TICK_W, 'colour': 'mid'},
        #              0.28: {'text':'2', 'width': TICK_W, 'colour': 'mid'},
        #              0.42: {'text':'3', 'width': TICK_W, 'colour': 'mid'},
        #              0.56: {'text':'4', 'width': TICK_W, 'colour': 'light'},
        #              0.70: {'text':'5', 'width': TICK_W, 'colour': 'light'},
        #              0.84: {'text':'6', 'width': TICK_W, 'colour': 'alert'},
        #              1.00: {'text':'7', 'width': TICK_W, 'colour': 'alert'} }
        # ARCS      = {ARCLEN : {'width': TICK_W, 'colour': 'alert'} }
        # ANNOTATE  = { 'Valign':'bottom', 'text':'dB', 'colour':'mid' }
        # NEEDLE    = VUNeedleStyle( colour='foreground', width=2, length=ARCLEN, radius_pc=1.0, 
        #                            glow_intensity=0.5, glow_colour='light', tip_glow=True, shadow=True )   
                
        # meter     = VUMeterStyle( pivot=-0.0, endstops=(3*PI/8, 13*PI/8),
        #                           needle=NEEDLE, scale=VUMeterScale(scale_radius=SCALE_RADIUS,tick_length=TICKLEN, marks=MARKS, arcs=ARCS, annotate=None, tick_width=TICK_W))
        # meter     = VUMeterStyle( needle=NEEDLE, scale=VUMeterScale(marks=MARKS, arcs=ARCS, annotate=ANNOTATE, tick_width=TICK_W))
  
        METERPAD  = 0
        NEEDLE    = VUNeedleStyle( colour='foreground', width=2, length=0.8, radius_pc=1.0, 
                                  glow_intensity=0.5, glow_colour='dark', tip_glow=True, shadow=True )     
        ENDSTOPS  = (3*PI/4, 5*PI/4)  #Position of endstop if not the edge of the frame
        PIVOT     = -0.5
        ANNOTATE  = { 'Valign':'middle', 'text':'dB', 'colour':'mid' }
        FONTH     = 0.06
        PIVOT     = -0.5
        NEEDLELEN = 0.8
        TICKLEN   = 0.75
        SCALESLEN = 0.80
        ARCLEN    = TICKLEN
        TICK_PC   = 0.1
        TICK_W    = 3
        MARKS     = {   0.12: {'text':'-20', 'width': TICK_W, 'colour': 'light'},
                        0.3: {'text':'-10', 'width': TICK_W, 'colour': 'light'},
                        0.5: {'text':'-3', 'width': TICK_W, 'colour': 'light'},
                        0.6: {'text':'-1', 'width': TICK_W, 'colour': 'light'},
                        0.7: {'text':'+0', 'width': TICK_W, 'colour': 'light'},
                        0.8: {'text':'+1', 'width': TICK_W, 'colour': 'alert'},
                        0.9: {'text':'+3', 'width': TICK_W, 'colour': 'alert'}}

        ARCS      = { ARCLEN*0.9: {'width': TICK_W-1, 'colour': 'light'} }

        VUGlow          = AmbientGlowStyle(colour='foreground', radius=0.2, softness=0.4, opacity=0.7)
        VUOutline       = OutlineStyle(colour='mid', width=4, opacity=1.0, radius=25, glow_intensity=0.1, softness=0.05)  
        VUBackground    = BackgroundStyle(colour='background', texture_path='particles.jpg', texture_opacity=0.2, ambient_glow=VUGlow)
        VUscale         = VUMeterScale(marks=MARKS, arcs=ARCS, annotate=ANNOTATE, tick_width=TICK_W, scale_radius=SCALESLEN, font_height=FONTH, tick_length=TICKLEN, tick_radius_pc=TICK_PC)

        meter=VUMeterStyle(pivot=PIVOT, endstops=ENDSTOPS, needle=NEEDLE, scale=VUscale )
  
        SPECTRUM_STYLE = SpectrumStyle( bar_space = 0.1, barw_min = 12, decay = 0.2)
        BAR_STYLE      = BarStyle(led_gap=2, peak_h=2, radius=0, led_h=15)
        SPECTRUM_BACKGROUND    = BackgroundStyle(colour='background', texture_opacity=0.3, ambient_glow=None)


        # 2 Rows
        # Row 1 = VU left, Spectrum, VU right
        #                  Play Bar
        # Row 2 = MetaData (Track, Artist),  Volume + Source

        rows = RowFramer(self, row_ratios=(4,1))
        # Row 1 
        cols_r1  = ColFramer(rows, col_ratios=(1,2,1), padpc=0.05,padding=0)

        vu_l  = RowFramer(cols_r1,row_ratios=(1,4,1))
        vu_l += Frame(vu_l)
        vu_l += VUMeter(vu_l, 'left', square=False, style=meter, background=VUBackground, outline=SimpleOutline,padding=METERPAD)
        vu_l += Frame(vu_l)

        centre  = RowFramer(cols_r1, row_ratios=(8,1),outline=SimpleOutline,padding=5)
        centre += SpectrumFrame(centre, 'mono', spectrum_style=SPECTRUM_STYLE, bar_style=BAR_STYLE, background=SPECTRUM_BACKGROUND) 
        centre += PlayProgressFrame(centre)

        vu_r  = RowFramer(cols_r1,row_ratios=(1,4,1),padpc=0.0)
        vu_r += Frame(vu_r)
        vu_r += VUMeter(vu_r,'right', square=False, style=meter, background=VUBackground, outline=SimpleOutline,padding=METERPAD)
        vu_r += Frame(vu_r)

        # Row 2
        cols_r2   = ColFramer(rows, col_ratios=(10,1,2),padpc=0.05,padding=5, outline=None)
        metadata  = RowFramer(cols_r2,padpc=0.0,outline=None)
        metadata  += MetaData(metadata, metadata_type='track',justify=('left'), colour='light')
        metadata  += MetaData(metadata, metadata_type='artist',justify=('left'), colour='mid')

        source    = RowFramer(cols_r2, row_ratios=(2,1,1),padpc=0.0)
        source    += MetaData(source, metadata_type='source', colour='mid')
        source    += MetaData(source, metadata_type='format', colour='mid')
        source    += MetaData(source, metadata_type='sample_rate', colour='mid')

        cols_r2 += MetaData(cols_r2, metadata_type='volume', colour='light')

class H2(Frame):   # comprises volume on the left, spectrum on the right
    @property
    def title(self): return 'Spectrum, Metadata and progress bar'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        # SpectrumGlow          = AmbientGlowStyle(colour='foreground', radius=0.2, softness=0.7, opacity=0.5)
        # SpectrumReact          = ReactiveGlowStyle(colour='foreground', attack=0.5, decay=0.1, threshold=0.2)
        SpectrumGlow          = None
        SpectrumReact         = None
        SpectrumBackground    = BackgroundStyle(colour='background', ambient_glow=SpectrumGlow, \
                                                texture_path='particles.jpg', texture_opacity=0.1, \
                                                reactive_glow=SpectrumReact   )
        SimpleOutline         = OutlineStyle(colour='mid', width=1, radius=10, opacity=1.0, glow_intensity=0.0, softness=0.0)
        Frame.__init__(self, platform, theme= 'hifi', background=SpectrumBackground)

        cols = ColFramer(self,col_ratios=(1,2.2,0.3), padding=0, padpc=0.1)

        artoutline       = OutlineStyle(colour='mid', width=5, radius=10, opacity=1.0, glow_intensity=0.3, softness=0.1)
        cols            += MetaImages(cols, padding=10, art_type='album', background=None, outline=artoutline)
 
        right            = RowFramer(cols, row_ratios=(1,3,1), padding=0, padpc=0.0)

        metadata         = RowFramer(right,padpc=0.0)
        metadata        += MetaData(metadata, metadata_type='track',justify=('left'), colour='light')
        metadata        += MetaData(metadata, metadata_type='artist',justify=('left'), colour='mid')

        bar_style        = BarStyle(led_gap=0, peak_h=2, radius=3, tip=True,flip=False)
        spectrum_style   = SpectrumStyle(barw_min=3, bar_space=2, barw_max=10, decay=0.2)
        reflection_style = ReflectionStyle(size=0.5, opacity=0.05)
        effects_style    = Effects(reflection=reflection_style, threshold=0.6, scale=2.0, alpha=200, blur=1.5)

        right           += SpectrumFrame(right, 'mono', padding=0,bar_style=bar_style, spectrum_style=spectrum_style, effects=effects_style) 
        # empty Frame to ensure space for the reflection
        right           += Frame(right)

        # Add the source and Volume
        volsource        = RowFramer(cols, row_ratios=(1,2), padding=0,padpc=0.0)
        volsource += MetaData(volsource, metadata_type='source', colour='mid')
        volsource += MetaData(volsource, metadata_type='volume', colour='light')


class H3(Frame):   # comprises volume on the left, spectrum on the right    
    @property
    def title(self): return 'Art, Visualiser, Metadata and progress bar'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):

        SpectrumGlow          = AmbientGlowStyle(colour='light', radius=0.2, softness=0.2, opacity=0.5)
        back = BackgroundStyle(texture_path='blue.jpg', texture_opacity=0.2, reactive_glow=None, ambient_glow=SpectrumGlow, cloud=True )
        Frame.__init__(self, platform, theme= 'hifi', padding=0, background=back)


        colframe = ColFramer(self, padpc=0.05, col_ratios=(2,3,1.8), outline={'width':0,'colour':'light'}, padding=10,background=None)
        artoutline  = OutlineStyle(colour='mid', width=5, radius=10, opacity=1.0, glow_intensity=0.3, softness=0.1)
        colframe += MetaImages(colframe, art_type='album', background=None, outline=artoutline)
        colframe += MetaDataFrame(colframe, background=None )
        colframe += Diamondiser(colframe,  'mono', background=None)