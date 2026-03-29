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
        back = {'image':'carbonfibre.jpg', 'per_frame_update':False, 'opacity': 255}
        Frame.__init__(self, platform, background=back, theme= 'hifi', padding=30)
  
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
        Frame.__init__(self, platform, theme= 'hifi')

        rows = RowFramer(self)
        # spectrum = Frame(cols)
        spectrum = RowFramer(self, padding=10, outline={'width':4,'colour':'light'})
        bar_style     = BarStyle(led_gap=0, peak_h=1, radius=0, tip=True,flip=False)
        spectrum_style=SpectrumStyle(barw_min=3, bar_space=2, barw_max=10)
        spectrum += SpectrumFrame(spectrum, 'left',  bar_style=bar_style, spectrum_style=spectrum_style) 
        spectrum += SpectrumFrame(spectrum, 'right', bar_style=BarStyle(led_gap=0, peak_h=1, radius=0, tip=True,flip=True), spectrum_style=spectrum_style)
        # artoutline = {'colour':'background', 'width':5}
        # # cols += MetaImages(cols  , scalers=(0.8,1.0),align=('left','middle'), opacity=100, outline=artoutline)
        # cols += MetaDataFrame(cols  ,  scalers=(1.0, 1.0),align=('right','middle'))

class H3(Frame):   # comprises volume on the left, spectrum on the right    
    @property
    def title(self): return 'Art, Visualiser, Metadata and progress bar'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        Frame.__init__(self, platform, theme= 'hifi', padding=0)

        BACK = {'image':'particles.jpg', 'opacity':50, 'glow':True}
        colframe = ColFramer(self, padpc=0.05, col_ratios=(2,3,1.8), outline={'width':0,'colour':'light'}, padding=10,background=None)
        out = outline={'colour':'light', 'width':2, 'opacity': 255, 'radius': 20}
        colframe += MetaImages(colframe, art_type='album', background=None)
        colframe += MetaDataFrame(colframe, background=None )
        colframe += Diamondiser(colframe,  'mono', background=None)