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
import pygame

# from .test_api_coverage import BarTest
# from framecore import Frame, ColFramer, RowFramer
# from frames import TextFrame
# from advanced_frames import EchoWaveFrame, PulseOrbFrame, SpectrumWaveFrame, FreqWaveFrame



class BarTest(Frame):
    """
    Creates a set of static bars with varying levels of effects so we can see whats going on
    """
    def __init__(self, parent, channel, scalers=None, align=None, theme=None, background=None, \
                 outline=None,square=False, update_fn=None, style=None, barsize_pc=0.7):

        # 1. Capture all configuration parameters into self.config
        self.config = {
            'channel': channel, \
            'style': style, \
            'update_fn':update_fn
        }
        self.barsize_pc = barsize_pc
        Frame.__init__(self, parent, scalers=scalers, align=align,theme=theme,background=background, outline=outline,square=square)
        self.configure()

    def configure(self):
        style = self.config['style']
        self.barw   = self.abs_w * self.barsize_pc if style.orient == 'vert' else self.abs_h * self.barsize_pc   # width of the bar
        box         = (self.barw, self.h) if style.orient == 'vert' else (self.w, self.barw)
        self.bar    = Bar(self, align=('centre', 'middle'), box_size=box, style=style)

        self.level     = self.config['channel']
        self.update_fn = self.config['update_fn']
        # print("VUFrame._configure> box=%s, flip=%d, orient %s, frame> %s" % (box, self.config['flip'], self.config['orient'], self.geostr()))

    def update_screen(self):

        if self.update_fn is not None:
            height = self.update_fn()
            peaks  = height
        else:
            height, peaks = self.level, self.level
        # self.draw_background(True)
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
        #                 colour='light', background=BackgroundStyle(colour='dark'))
        # # Test parameters: history depth and perspective scaling
        # c1 += EchoWaveFrame(c1, channel='mono', history_size=30, decay=0.92, 
        #                     perspective_scale=0.96, y_step=8,
        #                     background={'colour':'background', 'opacity':200},
        #                     outline={'colour':'mid', 'width':1})
        
        # --- Freq Wave (Scrolling) ---
        c2 = RowFramer(self, row_ratios=(1, 8), padding=10)
        c2 += TextFrame(c2, text="Freq Wave\n(Scrolling)", align=('centre', 'middle'), 
                        colour='light', background=BackgroundStyle(colour='dark'))
        c2 += FreqWaveFrame(c2, channel='mono', mode='spectrum', num_bands=5, speed=5,
                            y_step=2, perspective_scale=0.98,
                            background={'colour':'background', 'opacity':200},
                            outline={'colour':'mid', 'width':1})

        # --- BOTTOM ROW ---
        bottom_cols = ColFramer(rows, col_ratios=(1, 1), padding=10, padpc=0.02)

        # --- Pulse Orb (Particle System) ---
        # c3 = RowFramer(bottom_cols, row_ratios=(1, 8), padding=10)
        # c3 += TextFrame(c3, text="Pulse Orb\n(Particles)", align=('centre', 'middle'), 
        #                 colour='foreground', background=BackgroundStyle(colour='dark'))
        # # Test parameters: particle limits and spin speed
        # # c3 += PulseOrbFrame(c3, channel='right', particle_limit=150, spin_speed=0.05,
        # #                     pulse_scale=1.8,
        # #                     background={'colour':'mid', 'opacity':50})

        # --- Spectrum Wave (New) ---
        # c4 = RowFramer(bottom_cols, row_ratios=(1, 8), padding=10)
        # c4 += TextFrame(c4, text="Spectrum Wave\n(FFT History)", align=('centre', 'middle'), 
        #                 colour='light', background=BackgroundStyle(colour='dark'))
        # c4 += SpectrumWaveFrame(c4, channel='mono', history_size=20, decay=0.90,
        #                         perspective_scale=0.95, y_step=10,
        #                         background={'colour':'background', 'opacity':200},
        #                         outline={'colour':'mid', 'width':1})



class BackgroundEffectsScreen0(Frame):
    @property
    def title(self): return 'Background Effects 0: Caustic, background ambient'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        cloud_style = CloudStyle(opacity=0.5)
        vignette=VignetteStyle(strength=1.0, radius=0.2, softness=0.8)

        edge = EdgeLightStyle(enabled=True, intensity=0.5, width=0.5, softness=2.0,audio_reactivity=0.0)

        s1 = BackgroundStyle(colour='mid', vignette=vignette)
        s0 = BackgroundStyle(colour='background', ambient_glow=AmbientGlowStyle(colour='foreground', opacity=0.7, radius=0.5, softness=0.5))
        s2 = BackgroundStyle(colour='background', cloud=cloud_style, edge_light=edge)
        super().__init__(platform, theme='hifi', background=s2)
        
        outline=OutlineStyle(colour='mid', width=3, radius=10)
        # Layout
        # rows = RowFramer(self, padding=20, padpc=0.02, outline=outline)
        # top = ColFramer(rows, padding=10, padpc=0.02)
        # bot = ColFramer(rows, padding=10, padpc=0.02   )
        
        # Define a safe peak accent style to prevent colour errors


        # 1. Cloud (TL)
 
        # f1 = Frame(top, background=s2)
        # top += f1
        # self += TextFrame(top, background=s1, outline=outline ,text="Vignette (Strong)")
        
        # # 2. Noise (TR)
        # s2 = BackgroundStyle(colour='mid',  noise=NoiseStyle(strength=0.2, speed=0.5), peak_accent=peak_style)
        # # f2 = Frame(top, background=s2)
        # top += TextFrame(top, background=s2, outline=outline ,text="Noise (Heavy)", colour='light')
        
        # # 3. Ambient Glow (BL)
        # s3 = BackgroundStyle(colour='dark',  ambient_glow=AmbientGlowStyle(colour='foreground', opacity=0.8, radius=0.5, softness=0.2))
        # # f3 = Frame(bot, background=s3)
        # bot += TextFrame(bot, background=s3, outline=outline ,text="Ambient Glow (Pulse)", colour='foreground')
        
        # # 4. Reactive Glow (BR)
        # s4 = BackgroundStyle(colour='dark',  reactive_glow=ReactiveGlowStyle(colour='light', attack=0.1, decay=0.1, threshold=0.0))
        # # f4 = Frame(bot, background=s4)
        # bot += TextFrame(bot, background=s4, outline=outline, text="Reactive Glow (Audio)", colour='light')

class BackgroundEffectsScreen1(Frame):
    @property
    def title(self): return 'Background Effects 1: No Texture'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        peak_style = PeakAccentStyle(colour='alert')
        vignette=VignetteStyle(strength=1.0, radius=0.2, softness=0.8)
        s1 = BackgroundStyle(colour='mid', vignette=vignette)
        s0 = BackgroundStyle(colour='background', ambient_glow=AmbientGlowStyle(colour='foreground', opacity=0.7, radius=0.5, softness=0.5))
        super().__init__(platform, theme='std', background=s0)
        
        outline={'colour':'mid', 'width':3, 'radius':5}
        # Layout
        rows = RowFramer(self, padding=20, padpc=0.02, outline=outline)
        top = ColFramer(rows, padding=10, padpc=0.02)
        bot = ColFramer(rows, padding=10, padpc=0.02   )
        
        # Define a safe peak accent style to prevent colour errors


        # 1. Vignette (TL)
 
        # f1 = Frame(top, background=s1)
        top += TextFrame(top, background=s1, outline=outline ,text="Vignette (Strong)")
        
        # 2. Noise (TR)
        s2 = BackgroundStyle(colour='mid',noise=NoiseStyle(strength=0.2, speed=0.5), peak_accent=peak_style)
        # f2 = Frame(top, background=s2)
        top += TextFrame(top, background=s2, outline=outline ,text="Noise (Heavy)", colour='light')
        
        # 3. Ambient Glow (BL)
        s3 = BackgroundStyle(colour='dark', ambient_glow=AmbientGlowStyle(colour='foreground', opacity=0.8, radius=0.5, softness=0.2))
        # f3 = Frame(bot, background=s3)
        bot += TextFrame(bot, background=s3, outline=outline ,text="Ambient Glow (Pulse)", colour='foreground')
        
        # 4. Reactive Glow (BR)
        s4 = BackgroundStyle(colour='dark', reactive_glow=ReactiveGlowStyle(colour='light', attack=0.1, decay=0.1, threshold=0.0))
        # f4 = Frame(bot, background=s4)
        bot += TextFrame(bot, background=s4, outline=outline, text="Reactive Glow (Audio)", colour='light')

    # def update_screen(self, full=True, **kwargs):
    #     # if hasattr(self.platform, 'compositor'):
    #     #     self.platform.compositor.debug_view = 'pre_pass_output'
    #     super().update_screen(full, **kwargs)


class BackgroundEffectsScreen2(Frame):
    @property
    def title(self): return 'Background Effects 2: With Texture'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        super().__init__(platform, theme='zomp')
        
        rows = RowFramer(self, padding=30)
        top = ColFramer(rows, padding=10, padpc=0.02); bot = ColFramer(rows, padding=10, padpc=0.02)
        tex = 'metal.jpg'
        
        # 1. Texture + Vignette
        s1 = BackgroundStyle(colour='foreground', texture_path=tex, texture_opacity=0.1, vignette=VignetteStyle(strength=1.8, radius=0.2))
        # f1 = Frame(top, background=s1)
        top += TextFrame(top, background=s1, text="Tex + Vignette", colour='light')
        
        # 2. Texture + Noise
        s2 = BackgroundStyle(colour='background',  texture_path=tex, texture_opacity=0.1, noise=NoiseStyle(strength=0.15))
        # f2 = Frame(top, background=s2)
        top += TextFrame(top, background=s2, text="Tex + Noise", colour='light')
        
        # 3. Texture + Ambient
        s3 = BackgroundStyle(colour='foreground',  texture_path=tex, texture_opacity=0.9, ambient_glow=AmbientGlowStyle(colour='mid', opacity=0.8))
        # f3 = Frame(bot, background=s3)
        bot += TextFrame(bot, background=s3, text="Tex + Ambient", colour='light')
        
        # 4. Texture + Reactive
        s4 = BackgroundStyle(colour='dark',  texture_path=tex, texture_opacity=0.1, starfield=StarfieldStyle(density=50, speed=0.5))
        # f4 = Frame(bot, background=s4)
        bot += TextFrame(bot, background=s4, text="Tex + Stars", colour='light')

class GlowTestScreen(Frame):
    @property
    def title(self): return 'Glow Extraction Test'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        super().__init__(platform, theme='hifi', background='background') # No background to interfere
        
        # A row of bars with different brightness levels
        cols = ColFramer(self, col_ratios=(1, 1, 1, 1), padding=50, padpc=0.1)

        # This bar should NOT glow. It's bright, but not using additive blending.
        cols += BarTest(cols, 0.9,  style=BarStyle(colour_mode='solid', orient='vert', effects=None))

        # This bar SHOULD glow. It uses additive blending for values > threshold.
        # The NeonGlow preset has a low threshold, so it should be bright.
        cols += BarTest(cols, 0.9,  style=BarStyle(colour_mode='solid', orient='vert', effects=NeonGlow))

        # A dimmer bar that should also glow, but less intensely.
        cols += BarTest(cols, 0.7, style=BarStyle(orient='vert', effects=NeonGlow))
        
        # A very dim bar that should not glow.
        cols += BarTest(cols, 0.3, style=BarStyle(orient='vert', effects=NeonGlow))

        # Add text to explain
        self.text_frame = TextFrame(self, text="Viewing Glow Buffer. Left bar is normal, others are additive.",
                                    scalers=(1.0, 0.1), align=('centre', 'top'), colour='light')
        self += self.text_frame

    def update_screen(self, **kwargs):
        # Tell the compositor to render the glow buffer for debugging
        if hasattr(self.platform, 'compositor'):
            # self.platform.compositor.debug_view = 'glow'
            # Lower threshold so standard bright colours (max 1.0) trigger the glow for testing
            self.platform.compositor.glow_extraction_pass.threshold = 0.5
        
        super().update_screen(**kwargs)


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
                                                                            255 (Solid colour)	    50 to 150   Keep it semi-transparent so it looks like light, not a solid block.
        intensity_blur	        **The Softness.**Multiplier for the edge 
                                blur. Relates to the bar size. 0.0 is 
                                sharp, 1.0 is a standard soft glow.	        0.0 (Sharp)to
                                                                            3.0 (Very diffuse)	    0.5 to 1.5  Warning: Values > 3.0 can create massive screen-filling fogs. 
        '''

        for level in np.arange(0.1, 1.1, 0.1):
            eff_h = BarEffects(threshold=0.8, scale=1.0*level, alpha=200, blur=1.5)
            horzbars += BarTest(horzbars, level, style=BarStyle(orient='horz', effects=eff_h))
            eff_v = BarEffects(threshold=0.8, scale=1.0*level, alpha=200, blur=0.5)
            vertbars += BarTest(vertbars, level, theme='std', style=BarStyle(orient='vert', effects=eff_v))


class AudioTest(Frame):
    """
    Checking out how all the audio metadata works:  bass, treble, bpm
    """
    def __init__(self, parent, metadata):
        Frame.__init__(self, parent)
        self.metadata = metadata
        r1 = RowFramer(self, padding=0, padpc=0.05)

        r1 += TextFrame(r1, update_fn=self.get_audio_metadata_str)
        r1 += BarTest(r1, 0, style=BarStyle(orient='vert'), update_fn=self.get_audio_metadata)

    def get_audio_metadata_str(self):
         return "%s\n%.2f" % (self.metadata,self.get_audio_metadata())

    def get_audio_metadata(self):
        return self.platform.audioanalysis[self.metadata]
 

ANALYSIS_METADATA = ["beat", "bpm","centroid", "kurtosis","flux","volume"]

class AudioTestScreen(Frame):
    @property
    def title(self): return 'Audio Parameters Test Screen'    
    @property
    def type(self): return 'Test'

    def __init__(self, platform):   
        super().__init__(platform, theme='hifi', background='background')


        cols = ColFramer(self, padding=0, padpc=0.05)
        # cols += TextFrame(cols, text="Audio Parameters")

        for metadata in ANALYSIS_METADATA:
            cols += AudioTest(cols, metadata)


class AudioTestScreen1(Frame):
    @property
    def title(self): return 'Audio Parameters Test Screen'    
    @property
    def type(self): return 'Test'

    def __init__(self, platform):   
        super().__init__(platform, theme='hifi', background='background')


        cols = ColFramer(self, padding=0, padpc=0.05)
        r1 = RowFramer(cols, padding=0, padpc=0.05)
        r2 = RowFramer(cols, padding=0, padpc=0.05)
        r3 = RowFramer(cols, padding=0, padpc=0.05)
        # eff_h = Effects(threshold=0.8, scale=1.0*level, alpha=200, blur=1.5)

        r1 += TextFrame(r1, update_fn=self.get_bass_str)
        r1 += BarTest(r1, 0, style=BarStyle(orient='vert'), update_fn=self.get_bass)

        r2 += TextFrame(r2,  update_fn=self.get_treble_str)
        r2 += BarTest(r2, 0, style=BarStyle(orient='vert'), update_fn=self.get_treble)

        r3 += TextFrame(r3, update_fn=self.get_bpm_str)
        r3 += BarTest(r3, 0, orient='vert', update_fn=self.get_bpm)

    def get_bass_str(self):
        return "Bass\n%.2f" % self.get_bass()

    def get_treble_str(self):
        return "Treble\n%.2f" % self.get_treble()

    def get_bpm_str(self):
        return "BPM\n%.2f" % (self.get_bpm()*160)

    def get_bass(self):
        return self.platform.bass*15

    def get_treble(self):
        return  self.platform.treble*400

    def get_bpm(self):
        return  self.platform.bpm/160


class OutlineGlowTestScreen(Frame):
    @property
    def title(self): return 'Outline Glow Effects Test'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        super().__init__(platform, theme='hifi', background={'image': 'particles.jpg', 'opacity': 50})
        
        rows = RowFramer(self, padding=30, padpc=0.05)
        
        # Row 1: Intensity Variations
        r1 = ColFramer(rows, col_ratios=(1, 1, 1), padding=20,padpc=0.3)
        
        # 1. Subtle (Default-ish)
        style1 = {'colour': 'light', 'width': 2, 'radius': 10, 'glow_intensity': 0.2, 'softness': 0.5}
        r1 += TextFrame(r1, text="Subtle Glow\nInt: 0.2, Soft: 0.5", align=('centre', 'middle'), 
                        outline=style1, background=BackgroundStyle(colour='dark'))

        # 2. Medium
        style2 = {'colour': 'alert', 'width': 3, 'radius': 10, 'glow_intensity': 1.0, 'softness': 0.5}
        r1 += TextFrame(r1, text="Medium Glow\nInt: 1.0, Soft: 0.5", align=('centre', 'middle'), 
                        outline=style2, background=BackgroundStyle(colour='dark'))

        # 3. Intense
        style3 = {'colour': 'foreground', 'width': 2, 'radius': 10, 'glow_intensity': 2.0, 'softness': 0.5}
        r1 += TextFrame(r1, text="Intense Glow\nInt: 2.0, Soft: 0.5", align=('centre', 'middle'), 
                        outline=style3, background=BackgroundStyle(colour='dark'))

        # Row 2: Softness Variations
        r2 = ColFramer(rows, col_ratios=(1, 1, 1), padding=20,padpc=0.3)

        # 1. Sharp
        style4 = {'colour': 'mid', 'width': 2, 'radius': 5, 'glow_intensity': 1.0, 'softness': 0.1}
        r2 += TextFrame(r2, text="Sharp Glow\nSoft: 0.1", align=('centre', 'middle'), 
                        outline=style4, background=BackgroundStyle(colour='dark'))

        # 2. Soft
        style5 = {'colour': 'mid', 'width': 2, 'radius': 5, 'glow_intensity': 1.0, 'softness': 1.0}
        r2 += TextFrame(r2, text="Soft Glow\nSoft: 1.0", align=('centre', 'middle'), 
                        outline=style5, background=BackgroundStyle(colour='dark'))

        # 3. Very Diffuse
        style6 = {'colour': 'mid', 'width': 2, 'radius': 5, 'glow_intensity': 1.0, 'softness': 2.0}
        r2 += TextFrame(r2, text="Diffuse Glow\nSoft: 2.0", align=('centre', 'middle'), 
                        outline=style6, background=BackgroundStyle(colour='dark'))

class ParameterTuner:
    def __init__(self, target_object, parameters):
        """
        target_object: The object instance to modify (e.g. an AmbientGlowStyle instance)
        parameters: List of dicts defining the params:
                    [{'name': 'Radius', 'attr': 'radius', 'min': 0.0, 'max': 5.0, 'step': 0.1}, ...]
        """
        self.target = target_object
        self.params = parameters
        self.selected_index = 0

    def handle_key(self, key):
        # Number keys 1-9 to select parameter
        if key >= pygame.K_1 and key <= pygame.K_9:
            idx = key - pygame.K_1
            if idx < len(self.params):
                self.selected_index = idx
                print(f"Selected: {self.params[idx]['name']}")
        
        # Up/Down to adjust value
        elif key == pygame.K_UP:
            self._adjust(1)
        elif key == pygame.K_DOWN:
            self._adjust(-1)
            
    def _adjust(self, direction):
        p = self.params[self.selected_index]
        attr = p['attr']
        current_val = getattr(self.target, attr)
        new_val = current_val + (p['step'] * direction)
        
        # Clamp
        new_val = max(p['min'], min(p['max'], new_val))
        
        # Set
        setattr(self.target, attr, new_val)
        # print(f"Adjusted {p['name']} to {new_val:.2f}")

    def get_display_text(self):
        lines = ["Parameter Tuner (Keys 1-{}, Up/Down)".format(len(self.params))]
        for i, p in enumerate(self.params):
            val = getattr(self.target, p['attr'])
            prefix = ">> " if i == self.selected_index else "   "
            lines.append(f"{prefix}{i+1}. {p['name']}: {val:.2f}")
        lines.append("\nPress 'S' to print Preset code")
        return "\n".join(lines)

class AmbientGlowTunerScreen(Frame):
    @property
    def title(self): return 'Ambient Glow Tuner'
    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        # 1. Create the style object we want to tune
        self.glow_style = AmbientGlowStyle(colour='light', opacity=0.5, radius=1.0, softness=0.5)
        
        # 2. Create background using this style object
        bg_style = BackgroundStyle(colour='background', ambient_glow=self.glow_style)
        
        super().__init__(platform, theme='hifi', background=bg_style)
        
        # 3. Setup Tuner
        params = [
            {'name': 'Radius',   'attr': 'radius',   'min': 0.0, 'max': 3.0, 'step': 0.1},
            {'name': 'Softness', 'attr': 'softness', 'min': 0.0, 'max': 2.0, 'step': 0.05},
            {'name': 'Opacity',  'attr': 'opacity',  'min': 0.0, 'max': 1.0, 'step': 0.05},
        ]
        self.tuner = ParameterTuner(self.glow_style, params)
        
        # 4. Display Frame
        self.info_display = TextFrame(self, text="", align=('centre', 'middle'), 
                                      background={'colour':'dark', 'opacity': 150}, 
                                      outline={'colour':'mid', 'width':1})
        self += self.info_display

    def handle_key(self, key):
        if key == pygame.K_s:
            self.print_preset()
        else:
            self.tuner.handle_key(key)
            # Force update of text
            self.info_display.textcomp.text = self.tuner.get_display_text()

    def update_screen(self, **kwargs):
        # Update text content
        self.info_display.textcomp.text = self.tuner.get_display_text()
        super().update_screen(**kwargs)

    def print_preset(self):
        g = self.glow_style
        print("\n--- PRESET CODE ---")
        print(f"AmbientGlowStyle(colour='{g.colour}', radius={g.radius:.2f}, softness={g.softness:.2f}, opacity={g.opacity:.2f})")
        print("-------------------\n")
