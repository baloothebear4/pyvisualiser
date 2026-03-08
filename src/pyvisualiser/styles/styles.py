'''
Mar 26. Baloothebear4 v1

Collating all the classes that hold the styles of how visualisers work enables:
- standardisation & consistency
- use of presets
- the ability to careful curate themes or overall profiles for finished visualisers

'''


class Effects:
    def __init__(self, threshold=0.75, scale=2.5, blur=1.0, alpha=150, attack=0.4, decay=0.1, power=2.0,
                 inner_glow_scale=0.2, outer_glow_scale_min=0.5, outer_glow_scale_max=0.5,
                 outer_glow_alpha_mult=0.6, outer_glow_blur_mult=2.5):
        self.threshold = threshold
        self.scale     = scale
        self.blur      = blur
        self.alpha     = alpha
        self.attack    = attack
        self.decay     = decay
        self.power     = power
        # New parameters for multi-layer bloom, with defaults matching the old hardcoded values
        self.inner_glow_scale = inner_glow_scale
        self.outer_glow_scale_min = outer_glow_scale_min
        self.outer_glow_scale_max = outer_glow_scale_max
        self.outer_glow_alpha_mult = outer_glow_alpha_mult
        self.outer_glow_blur_mult = outer_glow_blur_mult


class TextStyle:
    def __init__(self, typeface='Inter/Inter-VariableFont_opsz,wght.ttf', min_size=18, max_lines=1):
        self.typeface = typeface
        self.min_size = min_size
        self.max_lines = max_lines

class VignetteStyle:
    def __init__(self, strength=0.0, radius=0.8, softness=0.5):
        self.strength = strength
        self.radius = radius
        self.softness = softness

class NoiseStyle:
    def __init__(self, strength=0.0, speed=1.0):
        self.strength = strength
        self.speed = speed

class AmbientGlowStyle:
    def __init__(self, colour='light', opacity=0.5, radius=1.6, softness=0.8):
        self.colour = colour
        self.opacity = opacity
        self.radius = radius
        self.softness = softness

class ReactiveGlowStyle:
    def __init__(self, colour='alert', attack=0.5, decay=0.1, threshold=0.5):
        self.colour = colour
        self.attack = attack
        self.decay = decay
        self.threshold = threshold

class PeakAccentStyle:
    def __init__(self, colour='alert', attack=0.1, decay=0.5, threshold=0.9):
        self.colour = colour
        self.attack = attack
        self.decay = decay
        self.threshold = threshold

class StarfieldStyle:
    def __init__(self, density=0.0, speed=0.5):
        self.density = density
        self.speed = speed

class BackgroundStyle:
    def __init__(self, colour='background', texture_path=None, texture_opacity=0.5, theme='std',
                 vignette: VignetteStyle = None, noise: NoiseStyle = None, ambient_glow: AmbientGlowStyle = None,
                 reactive_glow: ReactiveGlowStyle = None, peak_accent: PeakAccentStyle = None,
                 starfield: StarfieldStyle = None):
        self.colour = colour
        self.texture_path = texture_path
        self.texture_opacity = texture_opacity
        self.theme = theme
        # self.vignette = vignette if vignette is not None else VignetteStyle()
        # self.noise = noise if noise is not None else NoiseStyle()
        # self.ambient_glow = ambient_glow if ambient_glow is not None else AmbientGlowStyle()
        # self.reactive_glow = reactive_glow if reactive_glow is not None else ReactiveGlowStyle()
        # self.peak_accent = peak_accent if peak_accent is not None else PeakAccentStyle()
        # self.starfield = starfield if starfield is not None else StarfieldStyle()
        self.vignette = vignette if vignette is not None else False
        self.noise = noise if noise is not None else False
        self.ambient_glow = ambient_glow if ambient_glow is not None else False
        self.reactive_glow = reactive_glow if reactive_glow is not None else False
        self.peak_accent = peak_accent if peak_accent is not None else False
        self.starfield = starfield if starfield is not None else False

class BarStyle:
    def __init__(self, led_h=10, led_gap=4, peak_h=1, right_offset=0, flip=False, radius=0, tip=False, orient='vert', col_mode=None, segment_size=None, segment_gap=None, corner_radius=None, edge_softness=0.0):
        self.segment_size = segment_size if segment_size is not None else led_h
        self.segment_gap  = segment_gap  if segment_gap  is not None else led_gap
        self.corner_radius = corner_radius if corner_radius is not None else radius
        self.peak_h     = peak_h
        self.right_offset = right_offset
        self.flip       = flip
        self.orient     = orient
        self.col_mode   = col_mode if col_mode is not None else orient
        self.tip        = tip
        self.edge_softness = edge_softness


class SpectrumStyle:
    def __init__(self, bar_space=0.5, barw_min=1, barw_max=20):
        self.bar_space = bar_space
        self.barw_min  = barw_min
        self.barw_max  = barw_max

class OutlineStyle:
    def __init__(self, width=1, radius=0, colour='foreground', opacity=1.0, glow_intensity=0.0, softness=0.1):
        self.width = width
        self.radius = radius
        self.colour = colour
        self.opacity = opacity
        self.glow_intensity = glow_intensity
        self.softness = softness

#
# Analogue VU meter styles and configuration
#
class VUNeedleStyle:
    def __init__(self, colour='foreground', width=4, length=0.8, radius_pc=1.0, 
                 glow_intensity=0.0, glow_colour='alert', tip_glow=False, shadow=False):
        self.colour = colour
        self.width = width
        self.length = length
        self.radius_pc = radius_pc
        self.glow_intensity = glow_intensity
        self.glow_colour = glow_colour
        self.tip_glow = tip_glow
        self.shadow = shadow

ANNOTATE  = { 'Valign':'middle', 'text':'dB', 'colour':'mid' }
FONTH     = 0.05        # as a percentage of the overall frame height
PIVOT     = -0.5        # % of the frame height the pivot is below
NEEDLELEN = 0.8         # length of the needle as pc of height
TICKLEN   = 0.8         # length marks
SCALESLEN = 0.9
ARCLEN    = TICKLEN
TICK_PC   = 0.1         # lenth of the ticks as PC of the needle
TICK_W    = 3           # width of the ticks in pixels
MARKS     = {0.1: {'text':'-40', 'width': TICK_W, 'colour': 'light'},
                0.3: {'text':'-20', 'width': TICK_W, 'colour': 'light'},
            #  0.4: {'text':'-10', 'width': TICK_W, 'colour': 'light'},
                0.5: {'text':'-5', 'width': TICK_W, 'colour': 'light'},
                0.6: {'text':'-3', 'width': TICK_W, 'colour': 'light'},
                0.7: {'text':'+0', 'width': TICK_W, 'colour': 'alert'},
                0.8: {'text':'+3', 'width': TICK_W*2, 'colour': 'alert'},
                0.9: {'text':'+6', 'width': TICK_W*3, 'colour': 'alert'} }
# Key is the radius, attributes width & colour
ARCS      = {ARCLEN    : {'width': TICK_W//2, 'colour': 'mid'},
                ARCLEN*0.9: {'width': TICK_W//2, 'colour': 'mid'} }
class VUMeterScale:
    def __init__(self, marks=MARKS, arcs=ARCS, annotate=ANNOTATE, 
                 tick_width=TICK_W, tick_length=TICKLEN, tick_radius_pc=TICK_PC, 
                 scale_radius=0.9, font_height=FONTH):
        self.marks          = marks
        self.arcs           = arcs
        self.annotate       = annotate
        self.tick_width     = tick_width
        self.tick_length    = tick_length
        self.tick_radius_pc = tick_radius_pc
        self.scale_radius   = scale_radius
        self.font_height    = font_height

DECAY     = 0.3         # decay factor
SMOOTH    = 15          # samples to smooth
PI = 3.14152
class VUMeterStyle:
    def __init__(self, endstops = (3*PI/4, 5*PI/4), pivot=-0.5, needle: VUNeedleStyle = VUNeedleStyle(),
                 scale: VUMeterScale = None, 
                 texture_path=None, texture_opacity=1.0, theme='meter1', show_peak=False,
                 decay=DECAY, smooth=SMOOTH):
        
        self.endstops = endstops
        self.pivot = pivot
        self.needle = needle
        self.scale = scale
        self.texture_opacity = texture_opacity
        self.texture_path = texture_path
        self.theme = theme
        self.show_peak = show_peak
        self.decay = decay
        self.smooth = smooth


                        # endstops=None, pivot=None, bgdimage=None, needle=None, theme=None, \
                # tick_w=TICK_W, tick_pc=TICK_PC, fonth=FONTH, decay=DECAY, smooth=SMOOTH, \
                # ticklen=TICKLEN, scaleslen=SCALESLEN, marks=MARKS, annotate=ANNOTATE, arcs=ARCS, \
                # background=None, , **kwargs):