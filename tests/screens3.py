#!/usr/bin/env python
"""
 All top level screens.  Screens are comprised of Frames

 v1.0 Baloothebear4 Mar 2026


"""


# from pyvisualiser import *
from pyvisualiser.visualisers.vumeters import *
from pyvisualiser.visualisers.metadata import *
from pyvisualiser.visualisers.spectrum import *
from pyvisualiser.visualisers.glvisualisers import *
from pyvisualiser.visualisers.oscillogramme import *

from pyvisualiser.styles.presets import *
from pyvisualiser.styles.styles  import *
from pyvisualiser.core.framecore  import Frame, RowFramer, ColFramer


class H1(Frame):   # comprises volume on the left, spectrum on the right
    @property
    def title(self): return 'Hero 1: Analogue VU Meters, Roon Album Art, Metadata and progress bar'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):


        edge = EdgeLightStyle(enabled=True, intensity=0.7, width=0.2, softness=1.2,audio_reactivity=0.0)
        BACKGROUND    = BackgroundStyle(colour='background', ambient_glow=None, \
                                        texture_path='particles.jpg', texture_opacity=0.6, \
                                        reactive_glow=None, starfield=False, edge_light=edge   )
        
        SimpleOutline         = OutlineStyle(colour='mid', width=1, radius=10, opacity=1.0, glow_intensity=0.0, softness=0.1)
        Frame.__init__(self, platform, background=BACKGROUND, theme= 'hifi', padding=0, outline=None)

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

        ARCS      = { ARCLEN*0.9: {'width': TICK_W-1, 'colour': 'foreground'} }

        VIS_OPACITY     = 0.5
        VUGlow          = AmbientGlowStyle(colour='foreground', radius=0.2, softness=0.4, opacity=0.7)
        VUOutline       = OutlineStyle(colour='mid', width=4, opacity=1.0, radius=25, glow_intensity=0.1, softness=0.05)  
        VUBackground    = BackgroundStyle(colour='background', colour_opacity=VIS_OPACITY, ambient_glow=VUGlow)
        VUscale         = VUMeterScale(marks=MARKS, arcs=ARCS, annotate=ANNOTATE, tick_width=TICK_W, scale_radius=SCALESLEN, font_height=FONTH, tick_length=TICKLEN, tick_radius_pc=TICK_PC)

        meter=VUMeterStyle(pivot=PIVOT, endstops=ENDSTOPS, needle=NEEDLE, scale=VUscale )
  
        SPECTRUM_STYLE = SpectrumStyle( barsize_pc = 0.2, barw_min = 12, decay = 0.2)
        BAR_STYLE      = BarStyle(led_gap=2, peak_h=2, radius=0, led_h=6)
        SPECTRUM_BACKGROUND    = BackgroundStyle(colour='background', colour_opacity=VIS_OPACITY, ambient_glow=None)

        METERPAD  = 0
        METAPAD = 0

        # 3 Columns Rows
        # Col 1 = VU left, Source/Quality
        # Col 2 = Spectrum, Playprogress, Track, Artist
        # Col 3 = VU right, Volume

        cols = ColFramer(self, col_ratios=(1,2,1),padpc=0.1)

        # Row 1 
        # cols_r1  = ColFramer(rows, col_ratios=(1,3.5,1), padpc=0.1,padding=10)
        # vu_l  = RowFramer(cols_r1,row_ratios=(1,50,1))
        # vu_l += Frame(vu_l)
        # vu_l += VUMeter(vu_l, 'left', square=False, style=meter, background=VUBackground, outline=SimpleOutline,padding=METERPAD)
        # vu_l += Frame(vu_l)
        row_l = RowFramer(cols, row_ratios=(2,1),padpc=0.15)
        row_l += VUMeter(row_l, 'left', square=False, style=meter, background=VUBackground, outline=SimpleOutline,padding=METERPAD)

        source    = RowFramer(row_l, row_ratios=(2,1,1),padding=METAPAD)
        source    += MetaData(source, metadata_type='source', colour='light')
        source    += MetaData(source, metadata_type='format', colour='light')
        source    += MetaData(source, metadata_type='sample_rate', colour='light')
        # row_l += Frame(row_l)  #padding after meter
 
        centre  = RowFramer(cols, row_ratios=(3,1,0.4),outline=None,padding=0,padpc=0.1)
        centre += SpectrumFrame(centre, 'mono', spectrum_style=SPECTRUM_STYLE, bar_style=BAR_STYLE, background=SPECTRUM_BACKGROUND, outline=SimpleOutline) 

        metadata  = RowFramer(centre,padpc=0.0,outline=SimpleOutline, background=BackgroundStyle(reactive_glow=ReactiveGlowStyle(colour='mid')))
        metadata  += MetaData(metadata, metadata_type='track',justify=('left'), colour='foreground')
        metadata  += MetaData(metadata, metadata_type='artist',justify=('left'), colour='light')
        centre += PlayProgressFrame(centre)

        rows_r   = RowFramer(cols, row_ratios=(2,1),padpc=0.15)
        rows_r += VUMeter(rows_r,'right', square=False, style=meter, background=VUBackground, outline=SimpleOutline,padding=METERPAD)

        # rows_r += Frame(rows_r)
        rows_r += MetaData(rows_r, metadata_type='volume', colour='foreground',padding=METAPAD)
        # rows_r += Frame(rows_r)
        # vu_r  = RowFramer(cols_r1,row_ratios=(1,50,1),padpc=0.0)
        # vu_r += Frame(vu_r)
        # vu_r += VUMeter(vu_r,'right', square=False, style=meter, background=VUBackground, outline=SimpleOutline,padding=METERPAD)
        # vu_r += Frame(vu_r)

        # Row 2
        # cols_r2   = ColFramer(rows, col_ratios=(10,1,2),padpc=0.05,padding=5)





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
        edge = EdgeLightStyle(enabled=True, intensity=0.7, width=0.2, softness=1.2,audio_reactivity=0.0)
        SpectrumBackground    = BackgroundStyle(colour='background', ambient_glow=SpectrumGlow, edge_light=edge,\
                                                texture_path='particles.jpg', texture_opacity=0.6 )
        SimpleOutline         = OutlineStyle(colour='mid', width=1, radius=10, opacity=1.0, glow_intensity=0.0, softness=0.0)
        Frame.__init__(self, platform, theme= 'hifi', background=SpectrumBackground)

        cols = ColFramer(self,col_ratios=(1,2.2,0.3), padding=0, padpc=0.05)

        artoutline       = OutlineStyle(colour='mid', width=5, radius=10, opacity=1.0, glow_intensity=0.7, softness=0.3)
        cols            += MetaImages(cols, padding=10, art_type='album', background=None, outline=artoutline, opacity=1.0)
 
        centre            = RowFramer(cols, row_ratios=(1.5,3,1), padding=0, padpc=0.0)

        metadata         = RowFramer(centre,padpc=0.0)
        metadata        += MetaData(metadata, metadata_type='track',justify=('left'), colour='foreground')
        metadata        += MetaData(metadata, metadata_type='artist',justify=('left'), colour='light')

        reflection_style = ReflectionStyle(size=0.5, opacity=0.05)
        effects_style    = BarEffects(reflection=reflection_style, threshold=0.6, scale=2.0, alpha=200, blur=1.5)
        bar_style        = BarStyle(led_gap=0, peak_h=2, radius=3, tip=True,flip=False,effects=effects_style)
        spectrum_style   = SpectrumStyle(barw_min=3, barsize_pc=1, barw_max=10, decay=0.2)



        centre           += SpectrumFrame(centre, 'mono', padding=0,bar_style=bar_style, spectrum_style=spectrum_style) 
        # empty Frame to ensure space for the reflection
        centre           += Frame(centre)

        # Add the source and Volume
        volsource        = RowFramer(cols, row_ratios=(1,2), padding=0,padpc=0.0)
        volsource += MetaData(volsource, metadata_type='source', colour='light')
        volsource += MetaData(volsource, metadata_type='volume', colour='foreground')


class H3(Frame):   # comprises volume on the left, spectrum on the right    
    @property
    def title(self): return 'Art, Visualiser, Metadata and progress bar'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):

        edge = EdgeLightStyle(enabled=True, intensity=0.7, width=0.2, softness=1.2,audio_reactivity=0.0)
        SpectrumGlow          = AmbientGlowStyle(colour='light', radius=0.2, softness=0.2, opacity=0.5)
        back = BackgroundStyle(edge_light=edge,texture_path='blue.jpg', texture_opacity=0.1, reactive_glow=None, ambient_glow=False, cloud=CloudStyle(opacity=0.5) )
        Frame.__init__(self, platform, theme= 'hifi', padding=0, background=back)


        colframe = ColFramer(self, padpc=0.05, col_ratios=(2,3,1.8), padding=10,background=None)
        artoutline  = OutlineStyle(colour='mid', width=5, radius=10, opacity=1.0, glow_intensity=0.3, softness=0.1)

        # Album art on Left
        colframe += MetaImages(colframe, padding=10, art_type='album', background=None, outline=artoutline)

        # Metadata and progress in centre
        metadata_col  = RowFramer(colframe, row_ratios=(3,1,1,0.5,2), padding=0,padpc=0.0)
        metadata_col += MetaData(metadata_col, metadata_type='track', colour='foreground',justify=('left'))
        metadata_col += MetaData(metadata_col, metadata_type='album', colour='light',justify=('left'))
        metadata_col += MetaData(metadata_col, metadata_type='artist', colour='light',justify=('left'))
        metadata_col += PlayProgressFrame(metadata_col)

        # Add the source and Volume
        volsource     = ColFramer(metadata_col, col_ratios=(2,1), padding=0,padpc=0.0)
        volsource    += MetaData(volsource, metadata_type='source', colour='light')
        volsource    += MetaData(volsource, metadata_type='volume', colour='foreground')
        
        # Complex visualiser on Right
        # colframe += Diamondiser(colframe,  'mono', background=None)
        colframe += GLshader(colframe, shader='starvis')

        


class H4(Frame):   # comprises volume on the left, spectrum on the right    
    @property
    def title(self): return 'Artist, Visualiser, Metadata, Bar VU and progress bar, spectrum along bottom'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):

        SpectrumGlow          = AmbientGlowStyle(colour='light', radius=0.2, softness=0.2, opacity=0.5)
        back = BackgroundStyle(colour='background', colour_opacity=0.7, reactive_glow=None, ambient_glow=False, cloud=CloudStyle(opacity=0.8),\
                               edge_light=EdgeLightStyle(enabled=True, intensity=0.7, width=0.2, softness=1.2,audio_reactivity=0.0) )
        Frame.__init__(self, platform, theme= 'hifi', padding=0, background=back)


        colframe    = ColFramer(self, padpc=0.05, col_ratios=(3,4,0.5), padding=10,background=None)
        artoutline  = OutlineStyle(colour='mid', width=5, radius=10, opacity=0.4, glow_intensity=0.1, softness=0.1)


        image = RowFramer(colframe, row_ratios=(4,1),outline=artoutline,)
        image += MetaImages(image, padding=10, art_type='artist', background=None,  reflection=True)  
        # image += Frame(image) # blank padding space for the reflection
        image += MetaData(image, metadata_type='artist', colour='mid',justify=('centre'))

        #  Artist art, meta data progress in centre
        metadata_col  = RowFramer(colframe, row_ratios=(1,3,3), padding=0,padpc=0.0)
        metadata_col += MetaData(metadata_col, metadata_type='track', colour='foreground')
        metadata_col += OscilogrammeBar(metadata_col, 'left', oscillograme=OscillogrammeStyle(barsize_pc=0.5, barw_min=2), bar=BarStyle(led_gap=0))
        metadata_col += OscilogrammeBar(metadata_col, 'right', oscillograme=OscillogrammeStyle(barsize_pc=0.5, barw_min=2), bar=BarStyle(led_gap=0,flip=True))

        # VU Bars
        # colframe += VUFrame(colframe, 'left', barsize_pc=1.0, style=BarStyle(orient='vert', led_h=5, led_gap=2, tip=False))
        # colframe += VUFrame(colframe, 'right', barsize_pc=1.0, style=BarStyle(orient='vert', led_h=5, led_gap=2, tip=False))

        # Add the source and Volume
        volsource     = RowFramer(colframe, row_ratios=(1,2), padding=0,padpc=0.0)
        volsource    += MetaData(volsource, metadata_type='source', colour='light')
        volsource    += MetaData(volsource, metadata_type='volume', colour='foreground')
        
class H5(Frame):   # comprises volume on the left, spectrum on the right
    @property
    def title(self): return 'Analogue VU Meters, Roon Album Art, Metadata and progress bar'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        # back = BackgroundStyle(texture_path='blue.jpg',texture_opacity=1.0)
        back = BackgroundStyle(cloud=CloudStyle(opacity=0.5), edge_light=EdgeLightStyle(enabled=True, intensity=0.7, width=0.2, softness=1.2,audio_reactivity=0.0))
        Frame.__init__(self, platform, background=back, theme= 'hifi', padding=0)


        TICK_W    = 3
        TICK_PC   = 0.1
        ARCLEN    = 0.8
        MARKS     = {0.0: {'text':'-20', 'width': TICK_W, 'colour': 'light'},
                     0.1: {'text':'-15', 'width': TICK_W, 'colour': 'light'},
                     0.2: {'text':'-10', 'width': TICK_W, 'colour': 'light'},
                     0.3: {'text':'-7', 'width': TICK_W, 'colour': 'light'},
                     0.4: {'text':'-5', 'width': TICK_W, 'colour': 'light'},
                     0.5: {'text':'-3', 'width': TICK_W, 'colour': 'light'},
                     0.6: {'text':'-1', 'width': TICK_W, 'colour': 'light'},
                     0.7: {'text':'0', 'width': TICK_W*2, 'colour': 'alert'},
                     0.8: {'text':'+1', 'width': TICK_W*2, 'colour': 'alert'},
                     0.9: {'text':'+2', 'width': TICK_W*2, 'colour': 'alert'},
                     1.0: {'text':'+3', 'width': TICK_W*2, 'colour': 'alert'}
                     }
        # ARCS      = {ARCLEN    : {'width': TICK_W//2, 'colour': 'mid'},
        #              ARCLEN*(1-TICK_PC): {'width': TICK_W//2, 'colour': 'mid'} }
        ARCS      = {ARCLEN*(1-TICK_PC): {'width': TICK_W-1, 'colour': 'foreground'} }
        ANNOTATE  = { 'Valign':'middle', 'text':'dB', 'colour':'mid' }
        
        # laserneedle2 = VUNeedleStyle(colour='alert', width=4, length=1.0, radius_pc=0.9, glow_intensity=0.2, glow_colour='alert', tip_glow=True)

        glow          = AmbientGlowStyle(colour='foreground', radius=0.2, softness=0.3, opacity=0.3)
        outline       = OutlineStyle(colour='foreground', width=5, opacity=1.0, radius=25, glow_intensity=0.8, softness=0.2)  
        background    = BackgroundStyle(colour='background', colour_opacity=1.0, ambient_glow=None, texture_opacity=0.0, texture_path='particles.jpg') #), texture_path='particles.jpg',texture_opacity=0.8)

        style = VUMeterStyle(pivot=-0.7, endstops=(3*PI/4, 5*PI/4),
                             needle=VUNeedleStyle(width=2, colour='foreground', length=0.8, radius_pc=0.75, glow_intensity=0.0, glow_colour='foreground',tip_glow=True, shadow=True),
                             scale=VUMeterScale(marks=MARKS, arcs=ARCS, annotate=ANNOTATE, 
                                                tick_width=TICK_W, tick_radius_pc=TICK_PC))

        # 2 Row
        # VU Meters
        # Meta Data
        rows = RowFramer(self, row_ratios=(4,1),padding=20, padpc=0.0)

        cols = ColFramer(rows, padpc=0.2,padding=0)
        cols += VUMeter(cols, 'left', style=style, background=background, outline=outline)
        cols += VUMeter(cols, 'right', style=style, background=background, outline=outline)

                # Add the source and Volume
        cols_r2   = ColFramer(rows, col_ratios=(2,10,2),padpc=0.15,padding=5, outline=None)
        cols_r2 += MetaData(cols_r2, metadata_type='source', colour='light')

        metadata  = RowFramer(cols_r2,padpc=0.0,outline=None)
        metadata  += MetaData(metadata, metadata_type='track',justify=('left'), colour='foreground')
        metadata  += MetaData(metadata, metadata_type='artist',justify=('left'), colour='light')

        # volsource  = RowFramer(cols_r2, row_ratios=(1,2), padding=0,padpc=0.0)

        cols_r2 += MetaData(cols_r2, metadata_type='volume', colour='foreground')

class H6(Frame):

    def __init__(self, parent):
        particles = {'count': 80, 'colour': 'light', 'speed': 0.2, 'size': 1, 'softness': 0.1}
        Frame.__init__(self, parent, theme='hifi', background=BackgroundStyle(colour='background', starfield=True, colour_opacity=1.0))

        ARTIST = {'artist': {'colour':'foreground', 'align': ('right', 'middle'), 'scalers': (1.0, 1.0)}}
        TRACK  = {'track' : {'colour':'light', 'align': ('right', 'middle'), 'scalers': (1.0, 1.0)}}
        ALBUM  = {'album' : {'colour':'mid',   'align': ('right','middle'), 'scalers': (1.0, 1.0)} }

        back  = BackgroundStyle(colour='background', colour_opacity=0.5 )
        cols  = ColFramer(self, col_ratios=(1,2), padding=5)

        image = RowFramer(cols,row_ratios=(5,1), outline=OutlineStyle(colour='mid',width=3, radius=10))
        image += MetaImages(image,  'album',padding=10,background=back, reflection=True)
        image += Frame(image) # blank padding space for the reflection

        rows  = RowFramer(cols, row_ratios=(3,1), padpc=0)
        rows += MetaDataFrame(rows, justify='left', background=back)

        rows_b = ColFramer(rows, col_ratios=(8,1))
        rows_b  += SpectrumFrame(rows_b,channel='mono', bar_style=BarStyle(led_gap=0), spectrum_style=SpectrumStyle(barsize_pc=4), background=back)
        rows_b  += MetaData(rows_b, metadata_type='volume', colour='foreground')