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


# Image Presets
#


# VU Meter presets (analogue)
#
VUGlow          = AmbientGlowStyle(colour='foreground', radius=0.2, softness=0.4, opacity=0.7)
VUOutline       = OutlineStyle(colour='foreground', width=4, opacity=1.0, radius=25, glow_intensity=0.1, softness=0.05)  
VUBackground    = BackgroundStyle(colour='background', ambient_glow=VUGlow)
# VU Meter presets (bar based)


from .profiles import VisualiserProfile

# Primary Hardware Profile
EmbeddedHiFiProfile = VisualiserProfile(
    name="Embedded HiFi Preamp",
    target_resolution=(1280, 400),
    fullscreen=True,
    framerate=60,
    default_palette='hifi',
    effects=StrongEffect,
    background_style=VUBackground,
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