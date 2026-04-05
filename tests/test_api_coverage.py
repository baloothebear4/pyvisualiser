#!/usr/bin/env python
"""
Comprehensive API Coverage Test Script
Systematically instantiates core classes with various parameters to verify API compliance.
"""

from pyvisualiser import *
# from frames import (
#     TextFrame, MetaImages, MetaData, PlayProgressFrame,
#     VUFrame, VUMeter, SpectrumFrame, Oscilogramme, Diamondiser
# )
import math
# from components import Bar, Effects, BarStyle, SpectrumStyle, NeonGlow
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
        r1 += PlayProgressFrame(r1, barsize_pc=0.4, orient='horz', bar_style=BarStyle(led_h=4, led_gap=1), 
                                background={'colour':'mid', 'opacity':100})

        # --- ROW 2: Audio Visualisers (Bars & Spectrums) ---
        r2 = ColFramer(rows, col_ratios=(1, 1, 1), padding=10)
        
        # 1. VUFrame: Test new API (segments, glow, corner_radius)
        r2 += VUFrame(r2, channel='left', orient='vert', 
                      style=BarStyle(style=BarStyle(segment_size=8, segment_gap=2, corner_radius=3, edge_softness=0.1)), 
                      intensity_threshold=0.6, intensity_scale=2.5, intensity_blur=0.8, intensity_alpha=100,
                      background='background', outline={'colour':'mid', 'width':1})
        
        # 2. SpectrumFrame: Test bar settings, peak_h
        r2 += SpectrumFrame(r2, channel='mono', bar_style=BarStyle(led_h=3, led_gap=1), 
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

        col = ColFramer(self, padding=0, col_ratios=(10,6), padpc=0.0)

        bars = BarStyle(led_gap=5, peak_h=3,radius=0, tip=False)
        spectrum = SpectrumStyle(barw_min=19, bar_space=0.1, decay=0.2)
        # intensity_threshold=0.3, intensity_scale=1.2, intensity_alpha=200,intensity_blur=1.5
        col += SpectrumFrame(col,  'mono', effects=NeonGlow, bar_style=bars, spectrum_style=spectrum)
        # intensity_threshold=0.8, intensity_scale=1.5, intensity_alpha=200,intensity_blur=1.5)
        col += VUFrame(col, 'mono', barsize_pc=1.0, style=BarStyle(orient='vert', led_h=20, led_gap=2, tip=False),effects=NeonGlow)


