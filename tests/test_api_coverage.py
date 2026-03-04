#!/usr/bin/env python
"""
Comprehensive API Coverage Test Script
Systematically instantiates core classes with various parameters to verify API compliance.
"""

from framecore import Frame, ColFramer, RowFramer
from frames import (
    TextFrame, MetaImages, MetaData, PlayProgressFrame,
    VUFrame, VUMeter, SpectrumFrame, Oscilogramme, Diamondiser
)
import math
from components import Bar, Effects, BarStyle, SpectrumStyle, NeonGlow
import numpy as np

PI = 3.14159

class APICoverageScreen(Frame):
    @property
    def title(self): return 'API Coverage Test Screen'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        # Test Frame parameters: theme, background (dict with image/opacity)
        super().__init__(platform, theme='hifi', background={'image': 'particles.jpg', 'opacity': 50})
        
        # Test RowFramer with ratios and padding
        rows = RowFramer(self, row_ratios=(1, 1, 1), padding=20, padpc=0.05)
        
        # --- ROW 1: Core Visual Components ---
        r1 = ColFramer(rows, col_ratios=(1, 1, 1, 1), padding=10)
        
        # 1. TextFrame: Test wrap, justify, colour, outline
        r1 += TextFrame(r1, text="TextFrame\nWrapped & Centred", wrap=True, justify=('centre', 'middle'), 
                        colour='alert', background='mid', 
                        outline={'colour':'light', 'width':1, 'radius':5})
        
        # 2. MetaImages: Test art_type, reflection, opacity
        r1 += MetaImages(r1, art_type='album', reflection={'size':0.4, 'opacity':0.6}, 
                         opacity=220, outline={'colour':'foreground', 'width':2})
        
        # 3. MetaData: Test metadata_type, alignment
        r1 += MetaData(r1, metadata_type='artist', justify=('left', 'top'), 
                       background={'colour':'dark', 'opacity':150}, colour='light')
        
        # 4. PlayProgressFrame: Test orientation, barsize
        r1 += PlayProgressFrame(r1, barsize_pc=0.4, orient='horz', led_h=4, led_gap=1, 
                                background={'colour':'mid', 'opacity':100})

        # --- ROW 2: Audio Visualisers (Bars & Spectrums) ---
        r2 = ColFramer(rows, col_ratios=(1, 1, 1), padding=10)
        
        # 1. VUFrame: Test new API (segments, glow, corner_radius)
        r2 += VUFrame(r2, channel='left', orient='vert', 
                      segment_size=8, segment_gap=2, corner_radius=3, edge_softness=0.1, 
                      intensity_threshold=0.6, intensity_scale=2.5, intensity_blur=0.8, intensity_alpha=100,
                      background='background', outline={'colour':'mid', 'width':1})
        
        # 2. SpectrumFrame: Test bar settings, peak_h
        r2 += SpectrumFrame(r2, channel='mono', led_h=3, led_gap=1, 
                            peak_h=2, decay=0.3, background={'colour':'dark', 'opacity':200},
                            spectrum_style=SpectrumStyle(bar_space=0.2, barw_min=5),
                            effects=Effects(threshold=0.5, scale=3.0, blur=2.0, alpha=150))
        
        # 3. Diamondiser: Test circular spectrum
        r2 += Diamondiser(r2, channel='mono', bar_space=1, background='mid')

        # --- ROW 3: Audio Visualisers (Meters & Waveforms) & Z-Order ---
        r3 = ColFramer(rows, col_ratios=(1, 1, 1), padding=10)
        
        # 1. VUMeter: Test dial parameters
        r3 += VUMeter(r3, channel='mono', pivot=-0.2, endstops=(-PI/4, 3*PI/4), 
                      background={'colour':'light', 'opacity':50}, outline={'colour':'alert', 'width':1})
        
        # 2. Oscilogramme: Test waveform
        r3 += Oscilogramme(r3, channel='left', background='background')
        
        # 3. Z-Order Test: Overlapping frames
        z_test = Frame(r3, background='dark', outline={'colour':'foreground', 'width':1})
        # Background text (z=0)
        z_test += TextFrame(z_test, text="Background\n(z=0)", z_order=0, 
                            scalers=(1.0, 1.0), align=('centre', 'middle'), colour='mid')
        # Foreground overlay (z=1) - Should draw on top
        z_test += TextFrame(z_test, text="Foreground\n(z=1)", z_order=1, 
                            scalers=(0.6, 0.4), align=('right', 'bottom'), 
                            background='alert', colour='background', outline={'colour':'foreground', 'width':2})
        r3 += z_test

class BarTest(Frame):
    """
    Creates a set of static bars with varying levels of effects so we can see whats going on
    """
    def __init__(self, parent, channel, scalers=None, align=None, theme=None, background=None, \
                 barsize_pc=0.7, flip=False, outline=None,square=False, \
                 peak_h=1, barw_min=10, barw_max=400, tip=False, decay=0.3, orient='vert', \
                 # New API
                 style=None, \
                 segment_size=5, segment_gap=1, corner_radius=0, edge_softness=0.05, \
                 effects=None, \
                 intensity_threshold=0.8, intensity_scale=2.0, intensity_blur=0.7, intensity_alpha=20, \
                 # Legacy args (for compatibility)
                 led_h=None, led_gap=None, radius=None, softness=None, \
                 bloom_threshold=None, bloom_intensity=None, bloom_softness=None, bloom_alpha=None, **kwargs):

        # Map legacy arguments to new API if present
        if led_h is not None: segment_size = led_h
        if led_gap is not None: segment_gap = led_gap
        if radius is not None: corner_radius = radius
        if softness is not None: edge_softness = softness
        if bloom_threshold is not None: intensity_threshold = bloom_threshold
        if bloom_intensity is not None: intensity_scale = bloom_intensity
        if bloom_softness is not None: intensity_blur = bloom_softness
        if bloom_alpha is not None: intensity_alpha = bloom_alpha

        if effects is None:
            effects = Effects(threshold=intensity_threshold, scale=intensity_scale, blur=intensity_blur, alpha=intensity_alpha)

        if style is None:
            style = BarStyle(led_h=led_h, led_gap=led_gap, peak_h=peak_h, flip=flip, orient=orient, 
                             segment_size=segment_size, segment_gap=segment_gap, corner_radius=corner_radius, edge_softness=edge_softness)

        # 1. Capture all configuration parameters into self.config
        self.config = {
            'channel': channel, 'barsize_pc':barsize_pc, 'flip':flip, \
            'peak_h':peak_h, 'barw_min':barw_min, 'barw_max':barw_max, \
            'tip':tip, 'decay':decay, 'orient':orient, \
            'style': style, \
            'effects': effects
        }
        # Add any remaining keyword arguments
        self.config.update(kwargs)

        Frame.__init__(self, parent, scalers=scalers, align=align,theme=theme,background=background, outline=outline,square=square)
        self.configure()

    def configure(self):
        self.barw   = self.abs_w * self.config['barsize_pc'] if self.config['orient'] == 'vert' else self.abs_h * self.config['barsize_pc']   # width of the bar
        box         = (self.barw, self.h) if self.config['orient'] == 'vert' else (self.w, self.barw)
        self.bar    = Bar(self, align=('centre', 'middle'), box_size=box, peak_h=self.config['peak_h'], flip=self.config['flip'], \
                        orient=self.config['orient'], \
                        theme=self.theme, \
                        style=self.config['style'], \
                        effects=self.config['effects'])

        self.level     = self.config['channel']
        # print("VUFrame._configure> box=%s, flip=%d, orient %s, frame> %s" % (box, self.config['flip'], self.config['orient'], self.geostr()))

    def update_screen(self, full):

        height, peaks = self.level, self.level
        self.draw_background(True)
        self.bar.draw( 0, height, self.barw, peaks)
        return True
        

class BarEffectsTestScreen(Frame):
    @property
    def title(self): return 'Bar Parameters Test Screen'    
    @property
    def type(self): return 'Test'

    def __init__(self, platform):   
        super().__init__(platform, theme='hifi', background='background')
  
        # Two cols
        #  Col one is a stack of horz bars
        #  Col two is a stack of vert bars

        cols = ColFramer(self, padding=0, padpc=0.05)

        horzbars = RowFramer(cols, padding=20, padpc=0.5)
        vertbars = ColFramer(cols, padding=20, padpc=0.5)

        '''
        Parameter	            Description	                                Technical               Range	    Recommended Range
        intensity_threshold	    The Trigger Point. The volume level 
                                (0.0 to 1.0) where the glow starts. 
                                Below this, there is no glow. Above this, 
                                the glow fades in linearly.	                0.0 (Always on)
                                                                            to 1.0 (Only at max)	0.5 to 0.9  Set high so it only kicks in on loud beats (like a clip warning).
        intensity_scale	        **The Size.**Multiplier for how much 
                                wider/taller the glow is compared 
                                to the bar itself. 1.0 is the same size, 
                                2.0 is double width.	                    1.0 (No expansion)to
                                                                            5.0 (Huge halo)	        1.5 to 3.0   Needs to be >1.0 to be clearly visible behind the bar.
        intensity_alpha	        **The Brightness.**The maximum opacity 
                                of the glow when the bar hits 100%.	        0 (Invisible)to
                                                                            255 (Solid color)	    50 to 150   Keep it semi-transparent so it looks like light, not a solid block.
        intensity_blur	        **The Softness.**Multiplier for the edge 
                                blur. Relates to the bar size. 0.0 is 
                                sharp, 1.0 is a standard soft glow.	        0.0 (Sharp)to
                                                                            3.0 (Very diffuse)	    0.5 to 1.5  Warning: Values > 3.0 can create massive screen-filling fogs. 
        '''

        for level in np.arange(0.1, 1.1, 0.1):
            eff_h = Effects(threshold=0.8, scale=1.0*level, alpha=200, blur=1.5)
            horzbars += BarTest(horzbars, level, orient='horz', effects=eff_h)
            eff_v = Effects(threshold=0.8, scale=1.0*level, alpha=200, blur=0.5)
            vertbars += BarTest(vertbars, level, orient='vert', theme='std', effects=eff_v)

class LEDtestScreen(Frame):
    @property
    def title(self): return 'LED Test Screen'   

    
    @property
    def type(self): return 'Test'

    def __init__(self, platform):   
        super().__init__(platform, theme='std', background='background')
  
        # Two cols
        #  Col one is a stack of horz bars
        #  Col two is a stack of vert bars

        col = ColFramer(self, padding=0, col_ratios=(10,1), padpc=0.1)

        bars = BarStyle(led_gap=5, peak_h=3,radius=0, tip=False)
        spectrum = SpectrumStyle(barw_min=15, bar_space=0.5)
        # intensity_threshold=0.3, intensity_scale=1.2, intensity_alpha=200,intensity_blur=1.5
        col += SpectrumFrame(col,  'mono', effects=NeonGlow, bar_style=bars, spectrum_style=spectrum)
        # intensity_threshold=0.8, intensity_scale=1.5, intensity_alpha=200,intensity_blur=1.5)
        col += VUFrame(col, 'mono', orient='vert', barsize_pc=1.0, led_h=20,led_gap=2,tip=False,effects=NeonGlow)