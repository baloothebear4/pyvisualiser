#!/usr/bin/env python
"""
Advanced Visualiser Test Script
Tests the instantiation and layout of advanced 3D and particle-based frames.
"""

from framecore import Frame, ColFramer, RowFramer
from frames import TextFrame
from advanced_frames import EchoWaveFrame, PulseOrbFrame, SpectrumWaveFrame, FreqWaveFrame

class AdvancedVisualsScreen(Frame):
    @property
    def title(self): return 'Advanced Visuals Test'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        # Setup main screen with a space-themed background
        super().__init__(platform, theme='hifi', background={'image': 'metal.jpg', 'opacity': 90})
        
        # Layout: 2x2 Grid for 4 visualisers
        rows = RowFramer(self, padding=10, padpc=0.02)
        
        # --- TOP ROW ---
        top_cols = ColFramer(rows, padding=10, padpc=0.02)
        
        # --- Echo Wave (3D Effect) ---
        # c1 = RowFramer(top_cols, row_ratios=(1, 8), padding=10)
        # c1 += TextFrame(c1, text="Echo Wave\n(3D History)", align=('centre', 'middle'), 
        #                 colour='light', background='dark')
        # # Test parameters: history depth and perspective scaling
        # c1 += EchoWaveFrame(c1, channel='mono', history_size=30, decay=0.92, 
        #                     perspective_scale=0.96, y_step=8,
        #                     background={'colour':'background', 'opacity':200},
        #                     outline={'colour':'mid', 'width':1})
        
        # --- Freq Wave (Scrolling) ---
        c2 = RowFramer(self, row_ratios=(1, 8), padding=10)
        c2 += TextFrame(c2, text="Freq Wave\n(Scrolling)", align=('centre', 'middle'), 
                        colour='light', background='dark')
        c2 += FreqWaveFrame(c2, channel='mono', mode='spectrum', num_bands=5, speed=5,
                            y_step=2, perspective_scale=0.98,
                            background={'colour':'background', 'opacity':200},
                            outline={'colour':'mid', 'width':1})

        # --- BOTTOM ROW ---
        bottom_cols = ColFramer(rows, col_ratios=(1, 1), padding=10, padpc=0.02)

        # --- Pulse Orb (Particle System) ---
        # c3 = RowFramer(bottom_cols, row_ratios=(1, 8), padding=10)
        # c3 += TextFrame(c3, text="Pulse Orb\n(Particles)", align=('centre', 'middle'), 
        #                 colour='foreground', background='dark')
        # # Test parameters: particle limits and spin speed
        # # c3 += PulseOrbFrame(c3, channel='right', particle_limit=150, spin_speed=0.05,
        # #                     pulse_scale=1.8,
        # #                     background={'colour':'mid', 'opacity':50})

        # --- Spectrum Wave (New) ---
        # c4 = RowFramer(bottom_cols, row_ratios=(1, 8), padding=10)
        # c4 += TextFrame(c4, text="Spectrum Wave\n(FFT History)", align=('centre', 'middle'), 
        #                 colour='light', background='dark')
        # c4 += SpectrumWaveFrame(c4, channel='mono', history_size=20, decay=0.90,
        #                         perspective_scale=0.95, y_step=10,
        #                         background={'colour':'background', 'opacity':200},
        #                         outline={'colour':'mid', 'width':1})