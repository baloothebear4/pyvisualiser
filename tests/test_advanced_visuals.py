#!/usr/bin/env python
"""
Advanced Visualiser Test Script
Tests the instantiation and layout of advanced 3D and particle-based frames.
Also includes test screens for new rendering pipeline features like Backgrounds and Glow.
"""

from pyvisualiser import *
from pyvisualiser.core.backgrounds import BackgroundBase
from pyvisualiser.styles.presets import NeonGlow
import numpy as np
import math, time

# from .test_api_coverage import BarTest
# from framecore import Frame, ColFramer, RowFramer
# from frames import TextFrame
# from advanced_frames import EchoWaveFrame, PulseOrbFrame, SpectrumWaveFrame, FreqWaveFrame


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


class BackgroundEffectsScreen1(Frame):
    @property
    def title(self): return 'Background Effects 1: No Texture'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        super().__init__(platform, theme='hifi', background=None)
        
        # Create 4 distinct background engines for the 4 quadrants
        self.engines = []
        
        # 1. Vignette (TL)
        s1 = BackgroundStyle(base_color='mid', vignette=VignetteStyle(strength=1.0, radius=0.5, softness=0.4))
        self.engines.append(BackgroundBase(platform, s1))
        
        # 2. Noise (TR)
        s2 = BackgroundStyle(base_color='dark', noise=NoiseStyle(strength=0.2, speed=0.5))
        self.engines.append(BackgroundBase(platform, s2))
        
        # 3. Ambient Glow (BL)
        s3 = BackgroundStyle(base_color='black', ambient_glow=AmbientGlowStyle(color='alert', opacity=1.0, radius=0.5, softness=0.5))
        self.engines.append(BackgroundBase(platform, s3))
        
        # 4. Reactive Glow (BR)
        s4 = BackgroundStyle(base_color='black', reactive_glow=ReactiveGlowStyle(color='light', attack=0.1, decay=0.1, threshold=0.0))
        self.engines.append(BackgroundBase(platform, s4))

        # Add Labels
        rows = RowFramer(self)
        top = ColFramer(rows)
        bot = ColFramer(rows)
        top += TextFrame(top, text="Vignette (Strong)", colour='light')
        top += TextFrame(top, text="Noise (Heavy)", colour='light')
        bot += TextFrame(bot, text="Ambient Glow (Pulse)", colour='light')
        bot += TextFrame(bot, text="Reactive Glow (Audio)", colour='light')

    def update_screen(self, full=False, **kwargs):
        # Calculate Viewports for 4 Quadrants (Bottom-Left Origin for GL)
        w, h = self.platform.W, self.platform.H
        hw, hh = int(w/2), int(h/2)
        viewports = [
            (0, hh, hw, hh),  # TL
            (hw, hh, hw, hh), # TR
            (0, 0, hw, hh),   # BL
            (hw, 0, hw, hh)   # BR
        ]

        # Fake pulse for testing if no audio
        sim_pulse = (math.sin(time.time() * 3) + 1) / 2.0
        
        audio_data = {'mono': sim_pulse, 'peak_mono': sim_pulse}
        if hasattr(self.platform, 'vu') and self.platform.vu['mono'] > 0.01:
             audio_data = {'mono': self.platform.vu['mono'], 'peak_mono': self.platform.peak['mono']}

        for i, engine in enumerate(self.engines):
            engine.set_viewport(viewports[i])
            engine.update(audio_data)
            if hasattr(self.platform, 'compositor'):
                self.platform.compositor.add_pre_pass(engine.get_render_pass())
        
        super().update_screen(full, **kwargs)


class BackgroundEffectsScreen2(Frame):
    @property
    def title(self): return 'Background Effects 2: With Texture'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        super().__init__(platform, theme='hifi', background=None)
        
        self.engines = []
        tex = 'metal.jpg'
        
        # 1. Texture + Vignette
        s1 = BackgroundStyle(base_color='mid', texture_path=tex, texture_opacity=0.5, vignette=VignetteStyle(strength=0.8, radius=0.6))
        self.engines.append(BackgroundBase(platform, s1))
        
        # 2. Texture + Noise
        s2 = BackgroundStyle(base_color='dark', texture_path=tex, texture_opacity=0.5, noise=NoiseStyle(strength=0.15))
        self.engines.append(BackgroundBase(platform, s2))
        
        # 3. Texture + Ambient
        s3 = BackgroundStyle(base_color='dark', texture_path=tex, texture_opacity=0.3, ambient_glow=AmbientGlowStyle(color='mid', opacity=0.8))
        self.engines.append(BackgroundBase(platform, s3))
        
        # 4. Texture + Reactive
        s4 = BackgroundStyle(base_color='dark', texture_path=tex, texture_opacity=0.3, reactive_glow=ReactiveGlowStyle(color='alert', threshold=0.0))
        self.engines.append(BackgroundBase(platform, s4))

        rows = RowFramer(self)
        top = ColFramer(rows); bot = ColFramer(rows)
        top += TextFrame(top, text="Tex + Vignette", align=('centre', 'middle'), colour='light')
        top += TextFrame(top, text="Tex + Noise", align=('centre', 'middle'), colour='light')
        bot += TextFrame(bot, text="Tex + Ambient", align=('centre', 'middle'), colour='light')
        bot += TextFrame(bot, text="Tex + Reactive", align=('centre', 'middle'), colour='light')

    def update_screen(self, full=False, **kwargs):
        w, h = self.platform.W, self.platform.H
        hw, hh = int(w/2), int(h/2)
        viewports = [(0, hh, hw, hh), (hw, hh, hw, hh), (0, 0, hw, hh), (hw, 0, hw, hh)]

        sim_pulse = (math.sin(time.time() * 3) + 1) / 2.0
        audio_data = {'mono': sim_pulse, 'peak_mono': sim_pulse}
        if hasattr(self.platform, 'vu') and self.platform.vu['mono'] > 0.01:
             audio_data = {'mono': self.platform.vu['mono'], 'peak_mono': self.platform.peak['mono']}

        for i, engine in enumerate(self.engines):
            engine.set_viewport(viewports[i])
            engine.update(audio_data)
            if hasattr(self.platform, 'compositor'):
                self.platform.compositor.add_pre_pass(engine.get_render_pass())
        
        super().update_screen(full, **kwargs)


class GlowTestScreen(Frame):
    @property
    def title(self): return 'Glow Extraction Test'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        super().__init__(platform, theme='hifi', background=None) # No background to interfere
        
        # A row of bars with different brightness levels
        cols = ColFramer(self, col_ratios=(1, 1, 1, 1), padding=50, padpc=0.1)

        # This bar should NOT glow. It's bright, but not using additive blending.
        cols += BarTest(cols, 0.9, orient='vert', effects=None, style=BarStyle(col_mode='solid'))

        # This bar SHOULD glow. It uses additive blending for values > threshold.
        # The NeonGlow preset has a low threshold, so it should be bright.
        cols += BarTest(cols, 0.9, orient='vert', effects=NeonGlow)

        # A dimmer bar that should also glow, but less intensely.
        cols += BarTest(cols, 0.7, orient='vert', effects=NeonGlow)
        
        # A very dim bar that should not glow.
        cols += BarTest(cols, 0.3, orient='vert', effects=NeonGlow)

        # Add text to explain
        self.text_frame = TextFrame(self, text="Viewing Glow Buffer. Left bar is normal, others are additive.",
                                    scalers=(1.0, 0.1), align=('centre', 'top'), colour='light')
        self += self.text_frame

    def update_screen(self, full=False, **kwargs):
        # Tell the compositor to render the glow buffer for debugging
        if hasattr(self.platform, 'compositor'):
            # self.platform.compositor.debug_view = 'glow'
            # Lower threshold so standard bright colors (max 1.0) trigger the glow for testing
            self.platform.compositor.glow_extraction_pass.threshold = 0.5
        
        super().update_screen(full, **kwargs)


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