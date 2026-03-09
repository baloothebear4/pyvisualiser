#!/usr/bin/env python
"""
 All top level screens.  Screens are comprised of Frames

 v1.0 Baloothebear4 Mar 2026

A comprehensive set of Test screens for each of the componenents

"""

from pyvisualiser.visualisers.vumeters import *
from pyvisualiser.styles.presets import *
from pyvisualiser.styles.styles  import *
from pyvisualiser.core.framecore  import Frame, RowFramer, ColFramer
from pyvisualiser.visualisers.frames import MetaDataFrame, PlayProgressFrame, TextFrame


class VUTungstenScreen(Frame):
    @property
    def title(self): return 'Analogue VU Meter - Tungsten Style'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        # Use the new 'meter2' theme which has the cream background
        super().__init__(platform, theme='meter2', padding=0)
  
        # Define the style for the meter using the theme's colors
        
        # Custom marks for the cream/black meter
        MARKS_METER2 = {
            0.1: {'text':'-40', 'width': 2, 'colour': 'dark'},
            0.3: {'text':'-20', 'width': 2, 'colour': 'dark'},
            0.5: {'text':'-5',  'width': 2, 'colour': 'dark'},
            0.65:{'text':'-3',  'width': 2, 'colour': 'dark'},
            0.72:{'text':'+0',  'width': 3, 'colour': 'alert'},
            0.8: {'text':'+3',  'width': 4, 'colour': 'alert'},
            0.9: {'text':'+6',  'width': 4, 'colour': 'alert'}
        }

        # Custom arcs - just simple black lines
        ARCS_METER2 = {
            0.8: {'width': 1, 'colour': 'background'},
            0.9: {'width': 1, 'colour': 'light'}
        }


        # The needle should be black ('foreground' in meter2 theme)
        NEEDLE_METER2 = VUNeedleStyle(colour='foreground', width=3, length=0.8, radius_pc=1.0)

        # The background for the meter itself will be transparent to show the screen's cream background
        # The ambient glow will simulate the tungsten light
        METER_BACKGROUND = BackgroundStyle(
            colour='dark', # This will be the cream from the theme
            ambient_glow=AmbientGlowStyle(colour='light', opacity=0.6, radius=1.5, softness=0.7)
        )

        METER_OUTLINE = OutlineStyle(width=15, radius=25, colour='dark', glow_intensity=0.05)

        cols = ColFramer(self, padpc=0.05, padding=30)
        for channel in  ('left', 'right'):
            meter_style = VUMeterStyle(pivot=-0.5, endstops=(3*PI/4, 5*PI/4), needle=NEEDLE_METER2, show_peak=True,
                                       scale=VUMeterScale(marks=MARKS, arcs=None, annotate={'text':channel}))
            cols += VUMeter(cols, channel, square=False, style=meter_style, outline=METER_OUTLINE, background=METER_BACKGROUND)
        
        cols += MetaDataFrame(cols, padding=0, background=None, z_order=10)


class VUTestScreen1(Frame):   # comprises volume on the left, spectrum on the right
    @property
    def title(self): return 'Analogue VU Meters, Roon Album Art, Metadata and progress bar'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        back = BackgroundStyle(texture_path='carbonfibre.jpg',texture_opacity=1.0)
        Frame.__init__(self, platform, background=back, theme= 'meter1', padding=0)
  
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

class VUTestScreen2(Frame):   # comprises volume on the left, spectrum on the right
    @property
    def title(self): return 'Analogue VU Meters, Roon Album Art, Metadata and progress bar'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        back = BackgroundStyle(texture_path='carbonfibre.jpg',texture_opacity=1.0)
        Frame.__init__(self, platform, background=back, theme= 'meter2', padding=0)

        glow          = AmbientGlowStyle(colour='mid', radius=0.2, softness=0.3, opacity=0.95)
        outline       = OutlineStyle(colour='mid', width=10, opacity=1.0, radius=25, glow_intensity=0.3, softness=0.1)  
        background    = BackgroundStyle(colour='background', ambient_glow=glow, texture_path='carbonfibre.jpg',texture_opacity=0.3)
        self += VUMeterFrame4(self, theme='meter2', background=background, outline=outline)


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
            noise=NoiseStyle(strength=0.4)
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

class VUVintageScreen(Frame):
    """ VU meters left and right - based on an image background"""
    @property
    def title(self): return 'Vintage VU meters with image background'

    @property
    def type(self): return 'VU Image'

    def __init__(self, platform, type='Vintage-VU.png'):

        glow =AmbientGlowStyle(colour='foreground',radius=0.5, softness=0.1, opacity=0.6)
        back = BackgroundStyle(texture_path='particles.jpg',texture_opacity=0.8, ambient_glow=glow )
        
        Frame.__init__(self, platform, theme='hifi',background=back,padding=0)

        self += VUMeterImageFrame(self  , type='OldVU', outline=OutlineDefault )


class VUModernScreen(Frame):
    """ VU meters left and right - based on an image background"""
    @property
    def title(self): return 'Modern VU meters with image background'

    @property
    def type(self): return 'VU Image'

    def __init__(self, platform, type='blueVU'):       
        glow =AmbientGlowStyle(colour='foreground',radius=0.5, softness=0.1, opacity=0.6)
        back = BackgroundStyle(texture_path='metal.jpg',texture_opacity=0.8 )
        
        Frame.__init__(self, platform, theme='hifi',background=back,padding=0)

        self += VUMeterImageFrame(self  , type='ModVU', outline=None )


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

class VUMeterFrame1(Frame):
    """ Simple Meter with marks and scales  - based on frame width"""
    def __init__(self, parent, scalers=None, align=('centre', 'middle')):

        Frame.__init__(self, parent, scalers=scalers, align=align)
        style = VUMeterStyle(endstops=(3*PI/4-0.2, 5*PI/4+0.2), 
                             needle=VUNeedleStyle(width=4, colour='foreground', length=0.8, radius_pc=1.0),
                             scale=VUMeterScale(arcs={}))
        self += VUMeter(self, 'left', scalers=(0.5, 1.0), align=('left', 'bottom'), style=style)
        self += VUMeter(self, 'right', scalers=(0.5, 1.0), align=('right', 'bottom'), style=style)

class VUMeterFrame2(Frame):
    """ 180 degrees meter, centre rotate """

    def __init__(self, parent, scalers=None, align=('centre', 'middle')):
        Frame.__init__(self, parent, scalers=scalers, align=align)
        TICK_W    = 3

        TICKLEN   = 0.8         # length marks
        TICK_PC   = 0.1         # lenth of the ticks as PC of the needle
        SCALESLEN = 0.9
        DECAY     = 0.3         # decay factor
        SMOOTH    = 10          # samples to smooth
        ARCLEN    = TICKLEN * (1-TICK_PC)

        MARKS     = {0.0: {'text':'0', 'width': TICK_W, 'colour': 'mid'},
                     0.14: {'text':'1', 'width': TICK_W, 'colour': 'mid'},
                     0.28: {'text':'2', 'width': TICK_W, 'colour': 'mid'},
                     0.42: {'text':'3', 'width': TICK_W, 'colour': 'mid'},
                     0.56: {'text':'4', 'width': TICK_W, 'colour': 'light'},
                     0.70: {'text':'5', 'width': TICK_W, 'colour': 'light'},
                     0.84: {'text':'6', 'width': TICK_W, 'colour': 'alert'},
                     1.0: {'text':'7', 'width': TICK_W, 'colour': 'alert'} }
        ARCS      = {ARCLEN    : {'width': TICK_W//2, 'colour': 'mid'} }
        ANNOTATE  = { 'Valign':'middle', 'text':'PPM', 'colour':'mid' }
        
        style = VUMeterStyle(endstops=(PI/2, 3*PI/2), pivot=-0.4, 
                             needle=VUNeedleStyle(width=4, colour='foreground', length=0.8, radius_pc=1.0),
                             scale=VUMeterScale(marks=MARKS, arcs=ARCS, annotate=ANNOTATE, 
                                                tick_width=TICK_W, tick_length=TICKLEN, tick_radius_pc=TICK_PC, scale_radius=SCALESLEN), 
                             show_peak=True)

        self += VUMeter(self, 'left', scalers=(0.5, 1.0), align=('left', 'bottom'), \
                        style=style)
        self += VUMeter(self, 'right', scalers=(0.5, 1.0), align=('right', 'bottom'), \
                        style=style)

class VUMeterFrame3(Frame):
    """ 270 speedo dial type VU - colourful """
    def __init__(self, parent, scalers=None, align=('left', 'bottom')):
        Frame.__init__(self, parent, scalers=scalers, align=align)
        TICK_W    = 3
        ARCLEN    = 0.70
        MARKS     = {0.0: {'text':'0', 'width': TICK_W, 'colour': 'mid'},
                     0.14: {'text':'1', 'width': TICK_W, 'colour': 'mid'},
                     0.28: {'text':'2', 'width': TICK_W, 'colour': 'mid'},
                     0.42: {'text':'3', 'width': TICK_W, 'colour': 'mid'},
                     0.56: {'text':'4', 'width': TICK_W, 'colour': 'light'},
                     0.70: {'text':'5', 'width': TICK_W, 'colour': 'light'},
                     0.84: {'text':'6', 'width': TICK_W, 'colour': 'alert'},
                     1.0: {'text':'7', 'width': TICK_W, 'colour': 'alert'} }
        ARCS      = {ARCLEN    : {'width': TICK_W//2, 'colour': 'mid'} }
        ANNOTATE  = { 'Valign':'bottom', 'text':'Peak RMS', 'colour':'mid' }
        
        style = VUMeterStyle(pivot=0, endstops=(PI/4, 7*PI/4),
                             scale=VUMeterScale(marks=MARKS, arcs=ARCS, annotate=ANNOTATE, 
                                                tick_width=TICK_W))

        self += VUMeter(self, 'left', scalers=(0.5, 1.0), align=('left', 'bottom'), \
                        style=style)
        self += VUMeter(self, 'right', scalers=(0.5, 1.0), align=('right', 'bottom'), \
                        style=style)

class VUMeterFrame4(Frame):
    """120 degrees meter, low pivot """
    def __init__(self, parent,theme='meter1',background=VUBackground, outline=VUOutline,scalers=None, align=('left', 'bottom'   )):


        Frame.__init__(self, parent, theme=theme, scalers=scalers, align=align)
        TICK_W    = 3
        TICK_PC   = 0.1
        ARCLEN    = 0.8
        MARKS     = {0.0: {'text':'-20', 'width': TICK_W, 'colour': 'mid'},
                     0.1: {'text':'-15', 'width': TICK_W, 'colour': 'mid'},
                     0.2: {'text':'-10', 'width': TICK_W, 'colour': 'mid'},
                     0.3: {'text':'-7', 'width': TICK_W, 'colour': 'mid'},
                     0.4: {'text':'-5', 'width': TICK_W, 'colour': 'mid'},
                     0.5: {'text':'-3', 'width': TICK_W, 'colour': 'mid'},
                     0.6: {'text':'-1', 'width': TICK_W, 'colour': 'mid'},
                     0.7: {'text':'0', 'width': TICK_W*2, 'colour': 'alert'},
                     0.8: {'text':'+1', 'width': TICK_W*2, 'colour': 'alert'},
                     0.9: {'text':'+2', 'width': TICK_W*2, 'colour': 'alert'},
                     1.0: {'text':'+3', 'width': TICK_W*2, 'colour': 'alert'}
                     }
        # ARCS      = {ARCLEN    : {'width': TICK_W//2, 'colour': 'mid'},
        #              ARCLEN*(1-TICK_PC): {'width': TICK_W//2, 'colour': 'mid'} }
        ARCS      = {ARCLEN*(1-TICK_PC): {'width': TICK_W-1, 'colour': 'mid'} }
        ANNOTATE  = { 'Valign':'middle', 'text':'dB', 'colour':'mid' }
        
        laserneedle2 = VUNeedleStyle(colour='alert', width=4, length=1.0, radius_pc=0.9, glow_intensity=0.2, glow_colour='alert', tip_glow=True)
        style = VUMeterStyle(pivot=-0.7, endstops=(3*PI/4, 5*PI/4), theme=theme,
                             needle=VUNeedleStyle(width=2, colour='foreground', length=0.8, radius_pc=0.6, glow_intensity=0.3, glow_colour='foreground',tip_glow=True, shadow=False),
                             scale=VUMeterScale(marks=MARKS, arcs=ARCS, annotate=ANNOTATE, 
                                                tick_width=TICK_W, tick_radius_pc=TICK_PC))

        cols = ColFramer(self, padpc=0.05,padding=30)
        cols += VUMeter(cols, 'left', style=style, background=background, outline=outline)
        cols += VUMeter(cols, 'right', style=style, background=background, outline=outline)
