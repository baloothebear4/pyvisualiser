'''
Mar 26. Baloothebear4 v1

Collating all the classes that hold the styles of how visualisers work enables:
- standardisation & consistency
- use of presets
- the ability to carefully curate themes or overall profiles for finished visualisers

'''

from dataclasses import dataclass, field
from typing import Optional, Union, Any



@dataclass(frozen=True)
class ReflectionStyle:
    size: float = 0.5
    opacity: float = 0.2    

@dataclass(frozen=True)
class TextStyle:
    typeface: str = 'Inter/Inter-VariableFont_opsz,wght.ttf'
    min_size: int = 18
    max_lines: int = 1

@dataclass(frozen=True)
class TextStyle:
    typeface: str = 'Inter/Inter-VariableFont_opsz,wght.ttf'
    min_size: int = 18
    max_lines: int = 1

@dataclass(frozen=True)
class VignetteStyle:
    strength: float = 0.0
    radius: float = 0.8
    softness: float = 0.5

@dataclass(frozen=True)
class NoiseStyle:
    strength: float = 0.0
    speed: float = 1.0

@dataclass(frozen=True)
class AmbientGlowStyle:
    colour: str = 'light'
    opacity: float = 0.5
    radius: float = 1.6
    softness: float = 0.8

@dataclass(frozen=True)
class ReactiveGlowStyle:
    colour: str = 'foreground'
    attack: float = 0.5
    decay: float = 0.1
    threshold: float = 0.2

@dataclass(frozen=True)
class PeakAccentStyle:
    colour: str = 'alert'
    attack: float = 0.1
    decay: float = 0.5
    threshold: float = 0.9

@dataclass(frozen=True)
class StarfieldStyle:
    density: float = 50.0
    speed: float = 0.5

@dataclass(frozen=True)
class CloudStyle:
    radius: float = 0.0 #percent of the screen this covers, approx 

@dataclass(frozen=True)
class BackgroundStyle:
    colour: str = 'background'
    texture_path: Optional[str] = None
    texture_opacity: float = 0.5
    theme: str = 'std'
    vignette: Union[VignetteStyle, bool] = False
    noise: Union[NoiseStyle, bool] = False
    ambient_glow: Union[AmbientGlowStyle, bool] = False
    reactive_glow: Union[ReactiveGlowStyle, bool] = False
    peak_accent: Union[PeakAccentStyle, bool] = False
    starfield: Union[StarfieldStyle, bool] = False
    cloud: Union[CloudStyle, bool] = False

@dataclass(frozen=True)
class Effects:
    threshold: float = 0.75
    scale: float = 2.5
    blur: float = 1.0
    alpha: int = 150
    attack: float = 0.4
    decay: float = 0.1
    power: float = 2.0
    inner_glow_scale: float = 0.2
    outer_glow_scale_min: float = 0.5
    outer_glow_scale_max: float = 0.5
    outer_glow_alpha_mult: float = 0.6
    outer_glow_blur_mult: float = 2.5
    reflection: Union[ReflectionStyle, bool] = False


@dataclass(frozen=True)
class BarStyle:
    led_h: int = 10
    led_gap: int = 4
    peak_h: int = 1
    right_offset: int = 0
    flip: bool = False
    radius: int = 0
    orient: str = 'vert'
    tip: bool = False
    edge_softness: float = 0.0
    colour_mode: Optional[str] = 'horz'
    segment_size: Optional[int] = None
    segment_gap: Optional[int] = None
    corner_radius: Optional[int] = None

    def __post_init__(self):
        # Workaround for mutable fallback logic in a frozen dataclass
        if self.segment_size is None: object.__setattr__(self, 'segment_size', self.led_h)
        if self.segment_gap is None: object.__setattr__(self, 'segment_gap', self.led_gap)
        if self.corner_radius is None: object.__setattr__(self, 'corner_radius', self.radius)
        if self.colour_mode is None: object.__setattr__(self, 'colour_mode', self.orient)

@dataclass(frozen=True)
class SpectrumStyle:
    bar_space: float = 2
    barw_min: int = 2
    barw_max: int = 50
    decay: int = 0.4
    flip: bool = False #plots highs on left, lows on right


@dataclass(frozen=True)
class OutlineStyle:
    width: int = 1
    radius: int = 0
    colour: str = 'foreground'
    opacity: float = 1.0
    glow_intensity: float = 0.0
    softness: float = 0.1

@dataclass(frozen=True)
class VUNeedleStyle:
    colour: str = 'foreground'
    width: int = 4
    length: float = 0.8
    radius_pc: float = 1.0
    glow_intensity: float = 0.0
    glow_colour: str = 'alert'
    tip_glow: bool = False
    shadow: bool = False

ANNOTATE  = { 'Valign':'middle', 'text':'dB', 'colour':'mid' }
FONTH     = 0.05
PIVOT     = -0.5
NEEDLELEN = 0.8
TICKLEN   = 0.8
SCALESLEN = 0.9
ARCLEN    = TICKLEN
TICK_PC   = 0.1
TICK_W    = 3
MARKS     = {   0.12: {'text':'-20', 'width': TICK_W, 'colour': 'light'},
                0.3: {'text':'-10', 'width': TICK_W, 'colour': 'light'},
                0.5: {'text':'-3', 'width': TICK_W, 'colour': 'light'},
                0.6: {'text':'-1', 'width': TICK_W, 'colour': 'light'},
                0.7: {'text':'+0', 'width': TICK_W, 'colour': 'light'},
                0.8: {'text':'+1', 'width': TICK_W*2, 'colour': 'alert'},
                0.9: {'text':'+3', 'width': TICK_W*2, 'colour': 'alert'}}

ARCS      = { ARCLEN*0.9: {'width': TICK_W-1, 'colour': 'mid'} }

@dataclass(frozen=True)
class VUMeterScale:
    marks: dict = field(default_factory=lambda: MARKS.copy())
    arcs: Optional[dict] = field(default_factory=lambda: ARCS.copy())
    annotate: dict = field(default_factory=lambda: ANNOTATE.copy())
    tick_width: int = TICK_W
    tick_length: float = TICKLEN
    tick_radius_pc: float = TICK_PC
    scale_radius: float = SCALESLEN
    font_height: float = FONTH

DECAY     = 0.4
SMOOTH    = 15
PI = 3.14152

@dataclass(frozen=True)
class VUMeterStyle:
    endstops: tuple = (3*PI/4, 5*PI/4)
    pivot: float = PIVOT
    needle: VUNeedleStyle = field(default_factory=VUNeedleStyle)
    scale: VUMeterScale = field(default_factory=VUMeterScale)
    texture_path: Optional[str] = None
    texture_opacity: float = 1.0
    theme: str = None
    show_peak: bool = False
    decay: float = DECAY
    smooth: int = SMOOTH