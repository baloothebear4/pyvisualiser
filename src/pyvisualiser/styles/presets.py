'''

Mar 26 Baloothebear4 v1

Package of presets that are used to dynamically configure the 

'''

from .styles import *

# Define your instances
# NeonGlow = BarStyle(colour='neon_blue', glow=True, opacity=180)
# ClassicHiFi = BarStyle(colour='amber', spacing=2)
# RetroSpectrum = SpectrumStyle(mode='bars', decay=0.8)


# Effects Presets
#
StrongEffect    = Effects(threshold=0.75, scale=2.5, blur=1.0, alpha=150, attack=0.4, decay=0.1)
DreamEffect     = Effects(threshold=0.75, scale=3.0, blur=3.0, alpha=150, attack=0.4, decay=0.1)
NeonGlow        = Effects(threshold=0.1, scale=2.0, blur=0.5, alpha=220, attack=0.8, decay=0.1, power=1.0)

# Bar Presets
#



# Spectrum Presets
#


# Image Presets
#


# VU Meter presets (analogue)
#


# VU Meter presets (bar based)