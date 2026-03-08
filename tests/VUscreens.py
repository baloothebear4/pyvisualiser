#!/usr/bin/env python
"""
 All top level screens.  Screens are comprised of Frames

 v1.0 Baloothebear4 Mar 2026

A comprehensive set of Test screens for each of the componenents

"""


from pyvisualiser import *
from pyvisualiser.styles.presets import *

PI = 3.14159265358979323846


class VUTestScreen1(Frame):   # comprises volume on the left, spectrum on the right
    @property
    def title(self): return 'Analogue VU Meters, Roon Album Art, Metadata and progress bar'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        back = BackgroundStyle(texture_path='carbonfibre.jpg',texture_opacity=1.0)
        Frame.__init__(self, platform, background=back, theme= 'meter1', padding=0)
  
        NEEDLE    = VUNeedleStyle( colour='foreground', width=2, length=0.8, radius_pc=1.0, 
                                  glow_intensity=0.0, glow_colour='dark', tip_glow=True, shadow=True )     
        ENDSTOPS  = (3*PI/4, 5*PI/4)  #Position of endstop if not the edge of the frame
        PIVOT     = -0.5

        meter=VUMeterStyle(pivot=PIVOT, endstops=ENDSTOPS, needle=NEEDLE)
        # OUTLINE   = {'colour':'foreground', 'width':5, 'opacity': 255, 'radius': 10}
        glow      = AmbientGlowStyle(colour='foreground', radius=0.2, softness=0.4, opacity=0.7)
        OUTLINE   = OutlineStyle(colour='foreground', width=5, opacity=1.0, radius=25, glow_intensity=0.1, softness=0.05)  
        BACK      = BackgroundStyle(colour='background', ambient_glow=glow)

        cols = ColFramer(self, padpc=0.05,padding=30)
        cols += VUMeter(cols  ,  'left', square=False, style=meter, outline=OUTLINE, background=BACK)
        cols += MetaDataFrame(cols,padding=0, background=None, z_order=10)#,outline=OUTLINE)
        cols += VUMeter(cols  ,  'right', square=False, style=meter, outline=OUTLINE, background=BACK)

class VUNeedleEffectsScreen(Frame):
    @property
    def title(self): return 'VU Needle Effects Test'
    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        back = BackgroundStyle(texture_path='particles.jpg',texture_opacity=0.5)
        super().__init__(platform, theme='hifi', background=back)
        
        cols = ColFramer(self, padding=30, padpc=0.05)
        
        # Realistic Meter Background: Warm backlight + Vignette + Grain
        meter_bg = BackgroundStyle(
            colour='background', 
            ambient_glow=AmbientGlowStyle(colour='light', opacity=0.3, radius=2.0, softness=0.8),
            vignette=VignetteStyle(strength=0.6, radius=0.4, softness=0.6),
            noise=NoiseStyle(strength=0.04)
        )

        # 1. Standard Needle
        needle_style = VUNeedleStyle(colour='alert', width=4, shadow=True, glow_colour='alert')
        cols += VUMeter(cols, 'mono', style=VUMeterStyle(needle=needle_style), background=meter_bg, outline=OutlineStyle(width=4, radius=10, colour='mid', glow_intensity=0.1, softness=0.2))
        
        # 2. Glowing Needle
        glow_style = VUNeedleStyle(colour='alert', width=4, glow_intensity=0.3, glow_colour='alert')
        cols += VUMeter(cols, 'mono', style=VUMeterStyle(needle=glow_style), background=meter_bg, outline=OutlineStyle(width=4, radius=10, colour='mid', glow_intensity=0.1, softness=0.2))
        
        # 3. Tip Glow (High Level)
        tip_style = VUNeedleStyle(colour='light', width=4, tip_glow=True, glow_colour='alert')
        cols += VUMeter(cols, 'mono', style=VUMeterStyle(needle=tip_style), background=meter_bg, outline=OutlineStyle(width=4, radius=10, colour='mid', glow_intensity=0.1, softness=0.2))

class VUNeedleStylesScreen(Frame):
    @property
    def title(self): return 'VU Needle Styles Gallery'
    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        super().__init__(platform, theme='std', background={'image': 'particles.jpg', 'opacity': 50})
        
        cols = ColFramer(self, padding=30, padpc=0.05)
        
        # 1. Standard Hi-Fi Needle
        needle1 = VUNeedleStyle(colour='foreground', width=3, length=0.85, radius_pc=1.0, glow_intensity=0.0)
        style1 = VUMeterStyle(needle=needle1)
        c1 = RowFramer(cols, row_ratios=(5, 1))
        c1 += VUMeter(c1, 'mono', style=style1, background='dark', outline={'colour':'mid', 'width':2})
        c1 += TextFrame(c1, text="Standard Hi-Fi", align=('centre', 'top'))

        # 2. Glowing "Laser" Needle
        needle2 = VUNeedleStyle(colour='alert', width=4, length=1.0, radius_pc=0.9, glow_intensity=0.2, glow_colour='alert', tip_glow=True)
        style2 = VUMeterStyle(needle=needle2)
        c2 = RowFramer(cols, row_ratios=(5, 1))
        c2 += VUMeter(c2, 'mono', style=style2, background='dark', outline={'colour':'mid', 'width':2})
        c2 += TextFrame(c2, text="Laser Glow", align=('centre', 'top'))

        # 3. Floating Tick
        needle3 = VUNeedleStyle(colour='light', width=5, length=0.95, radius_pc=0.15)
        style3 = VUMeterStyle(needle=needle3)
        c3 = RowFramer(cols, row_ratios=(5, 1))
        c3 += VUMeter(c3, 'mono', style=style3, background='dark', outline={'colour':'mid', 'width':2})
        c3 += TextFrame(c3, text="Floating Tick", align=('centre', 'top'))

""" VU Meters """

class VUImageScreen(Frame):
    """ VU meters left and right - based on an image background"""
    @property
    def title(self): return 'VU meters with image background'

    @property
    def type(self): return 'VU Image'

    def __init__(self, platform, type='blueVU'):

        glow =AmbientGlowStyle(colour='foreground',radius=0.5, softness=0.1, opacity=0.6)
        back = BackgroundStyle(texture_path='particles.jpg',texture_opacity=0.8 )
        
        Frame.__init__(self, platform, theme='hifi',background=back,padding=0)

        rows = RowFramer(self, row_ratios=(15,1), padding=0, padpc=0.05)
        rows += VUMeterImageFrame(rows  , type=type, outline=None )
        rows += PlayProgressFrame(rows,background=None)


class TestVUImageScreen1(Frame):
    """ VU meters left and right - based on an image background"""
    @property
    def title(self): return 'Test multiple VU meters with image backgrounds'

    @property
    def type(self): return 'Test'

    def __init__(self, platform, type=None):

        back = {'colour':'background', 'per_frame_update':True}
        Frame.__init__(self, platform, background=back)

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
        back = {'colour':'background', 'per_frame_update':True}
        Frame.__init__(self, platform, background=back)

        self += VUMeterFrame1(self  , scalers=(0.5,0.5), align=('left','top'))
        self += VUMeterFrame2(self  , scalers=(0.5,0.5), align=('left','bottom'))
        self += VUMeterFrame3(self  ,  scalers=(0.5,0.5), align=('right','top'))
        self += VUMeterFrame4(self  ,  scalers=(0.5,0.5), align=('right','bottom'))

        # self += VolumeSourceFrame(self  , 0.2, 'centre'
