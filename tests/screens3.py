#!/usr/bin/env python
"""
 All top level screens.  Screens are comprised of Frames

 v1.0 Baloothebear4 Mar 2026


"""


from pyvisualiser import *
from pyvisualiser.visualisers.vumeters import *
from pyvisualiser.styles.presets import *
from pyvisualiser.styles.styles  import *
from pyvisualiser.core.framecore  import Frame, RowFramer, ColFramer
from pyvisualiser.visualisers.frames import MetaDataFrame, PlayProgressFrame, TextFrame
PI = 3.14159265358979323846


class H1(Frame):   # comprises volume on the left, spectrum on the right
    @property
    def title(self): return 'Hero 1: Analogue VU Meters, Roon Album Art, Metadata and progress bar'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        Frame.__init__(self, platform, background=VUBackground, theme= 'hifi', padding=30)
  
        NEEDLE    = VUNeedleStyle( colour='foreground', width=2, length=0.8, radius_pc=1.0, 
                                  glow_intensity=0.5, glow_colour='dark', tip_glow=True, shadow=True )     
        ENDSTOPS  = (3*PI/4, 5*PI/4)  #Position of endstop if not the edge of the frame
        PIVOT     = -0.5

        meter=VUMeterStyle(pivot=PIVOT, endstops=ENDSTOPS, needle=NEEDLE)
        # OUTLINE   = {'colour':'foreground', 'width':5, 'opacity': 255, 'radius': 10}

        cols = ColFramer(self, padpc=0.05,padding=30)
        cols += VUMeter(cols  ,  'left', square=False, style=meter, outline=VUOutline, background=VUBackground)
        cols += MetaDataFrame(cols,padding=0, background=None, z_order=10)#,outline=OUTLINE)
        cols += VUMeter(cols  ,  'right', square=False, style=meter, outline=VUOutline, background=VUBackground)


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

        cols = ColFramer(self,col_ratios=(1,2.2), padding=10, padpc=0.1)

        artoutline       = OutlineStyle(colour='mid', width=5, radius=10, opacity=1.0, glow_intensity=0.3, softness=0.1)
        cols            += MetaImages(cols, padding=10, art_type='album', background=None, outline=artoutline)
 
        right            = RowFramer(cols, row_ratios=(1,3,1), padding=0, padpc=0.0)

        metadata         = RowFramer(right,padpc=0.0)
        metadata        += MetaData(metadata, metadata_type='track',justify=('left'), colour='light')
        metadata        += MetaData(metadata, metadata_type='artist',justify=('left'), colour='mid')

        bar_style        = BarStyle(led_gap=0, peak_h=2, radius=3, tip=True,flip=False)
        spectrum_style   = SpectrumStyle(barw_min=3, bar_space=2, barw_max=10, decay=0.2)
        reflection_style = ReflectionStyle(size=0.5, opacity=0.1)
        effects_style    = Effects(reflection=reflection_style, threshold=0.6, scale=2.0, alpha=200, blur=1.5)

        right           += SpectrumFrame(right, 'mono', padding=0,bar_style=bar_style, spectrum_style=spectrum_style, effects=effects_style) 
        # empty Frame to ensure space for the reflection
        right           += Frame(right)

        # spectrum += SpectrumFrame(spectrum, 'right', bar_style=BarStyle(led_gap=0, peak_h=1, radius=0, tip=True,flip=True), spectrum_style=spectrum_style)
 


class H3(Frame):   # comprises volume on the left, spectrum on the right    
    @property
    def title(self): return 'Art, Visualiser, Metadata and progress bar'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):

        SpectrumGlow          = AmbientGlowStyle(colour='light', radius=0.2, softness=0.7, opacity=0.5)
        back = BackgroundStyle(texture_path='blue.jpg', texture_opacity=0.2, reactive_glow=ReactiveGlowStyle(threshold=0.3), ambient_glow=SpectrumGlow)
        Frame.__init__(self, platform, theme= 'hifi', padding=0, background=back)


        colframe = ColFramer(self, padpc=0.05, col_ratios=(2,3,1.8), outline={'width':0,'colour':'light'}, padding=10,background=None)
        artoutline       = OutlineStyle(colour='mid', width=5, radius=10, opacity=1.0, glow_intensity=0.3, softness=0.1)
        colframe += MetaImages(colframe, art_type='album', background=None, outline=artoutline)
        colframe += MetaDataFrame(colframe, background=None )
        colframe += Diamondiser(colframe,  'mono', background=None)