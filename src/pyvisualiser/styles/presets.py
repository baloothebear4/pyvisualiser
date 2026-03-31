'''

Mar 26 Baloothebear4 v1

Package of presets that are used to dynamically configure the 

'''

from .styles import *

# Define your instances
# NeonGlow = BarStyle(colour='neon_blue', glow=True, opacity=180)
# ClassicHiFi = BarStyle(colour='amber', spacing=2)
# RetroSpectrum = SpectrumStyle(mode='bars', decay=0.8)



#Colour Palettes
#
PaletteDefault = 'std'

# Effects Presets
#
StrongEffect    = Effects(threshold=0.75, scale=2.5, blur=1.0, alpha=150, attack=0.4, decay=0.1)
DreamEffect     = Effects(threshold=0.75, scale=3.0, blur=3.0, alpha=150, attack=0.4, decay=0.1)
NeonGlow        = Effects(threshold=0.1, scale=2.0, blur=0.5, alpha=220, attack=0.8, decay=0.1, power=1.0)

# Background Presets
BackgroundDefault  = None #BackgroundStyle(ambient_glow=AmbientGlowStyle(colour='foreground', opacity=1.0, radius=0.5, softness=0.5))
SunriseAmbientGlow = AmbientGlowStyle(colour='light', radius=0.40, softness=0.30, opacity=1.00)

# Default outline
#
OutlineDefault = None #{ 'width' : 1, 'radius' : 5, 'colour' : 'foreground', 'opacity': 255, 'glow_intensity': 0.1, 'softness': 0.1}

# Frame Defaults
FullScale      = (1.0,1.0)
Centred        = ('centre', 'middle')
PI = 3.14159265358979323846

# 



# Bar Presets
#



# Spectrum Presets
#

SpectrumOutline       = OutlineStyle(colour='foreground', width=4, opacity=1.0, radius=25, glow_intensity=0.1, softness=0.05)  



# lass BackgroundStyle:
#     colour: str = 'background'
#     texture_path: Optional[str] = None
#     texture_opacity: float = 0.5
#     theme: str = 'std'
#     vignette: Union[VignetteStyle, bool] = False
#     noise: Union[NoiseStyle, bool] = False
#     ambient_glow: Union[AmbientGlowStyle, bool] = False
#     reactive_glow: Union[ReactiveGlowStyle, bool] = False
#     peak_accent: Union[PeakAccentStyle, bool] = False
#     starfield: Union[StarfieldStyle, bool] = False
# Image Presets
#


# VU Meter presets (analogue)
#
VUGlow          = AmbientGlowStyle(colour='foreground', radius=0.2, softness=0.4, opacity=0.7)
VUOutline       = OutlineStyle(colour='mid', width=4, opacity=1.0, radius=25, glow_intensity=0.1, softness=0.05)  
VUBackground    = BackgroundStyle(colour='background', texture_opacity=0.8, ambient_glow=VUGlow)
# VU Meter presets (bar based)


from .profiles import VisualiserProfile, ProfileControls

# Profile Controls Presets
LUXURY_PROFILE = ProfileControls(
    intensity=0.6, softness=0.8, threshold=1.1, energy=0.3, 
    smoothness=0.8, warmth=0.7, saturation=0.7, depth=0.4, vignette=0.3, sharpness=0.5
)

NEON_PROFILE = ProfileControls(
    intensity=1.2, softness=0.6, threshold=0.6, energy=0.9, 
    smoothness=0.5, warmth=0.2, saturation=1.0, depth=0.2, vignette=0.1, sharpness=0.8
)

MINIMAL_PROFILE = ProfileControls(
    intensity=0.4, softness=0.3, threshold=1.2, energy=0.2, 
    smoothness=0.9, warmth=0.5, saturation=0.3, depth=0.1, vignette=0.1, sharpness=0.9
)

# Primary Hardware Profile
EmbeddedHiFiProfile = VisualiserProfile(
    name="Embedded HiFi Preamp",
    target_resolution=(1280, 400),
    fullscreen=True,
    framerate=60,
    default_palette='hifi',
    effects=StrongEffect,
    background_style=VUBackground,
    spectrum_style=SpectrumStyle(),
    vu_meter_style=VUMeterStyle(show_peak=True)  # Driven by default VU styles
)

# Desktop Widget Profile
DesktopWidgetProfile = VisualiserProfile(
    name="Desktop Visualiser Widget",
    target_resolution=(800, 600),
    fullscreen=False,
    framerate=30,  # Lighter footprint for desktop
    default_palette='std',
    effects=Effects(scale=1.0, blur=0.5, alpha=100),
    background_style=BackgroundStyle(colour='background', texture_opacity=0.0)
)