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

# 



# Bar Presets
#



# Spectrum Presets
#


# Image Presets
#


# VU Meter presets (analogue)
#


# VU Meter presets (bar based)


# Profiles are a collection of presets that have ano overall style eg desktop, hifi, jukebox
HiFiProfile = {
    'palette':      'hifi',                 # dark blue colour palette
    'background':   BackgroundDefault,      # soft ambient glow
    'bar':          BarStyle                # tbd
}