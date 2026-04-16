"""
PyVisualiser - Audio Visualization Library
==========================================

A Python library for real-time audio visualization with support for:
- Spectrum analysis
- Waveform display  
- Multiple display backends
- Audio processing pipelines
"""

__version__ = "2.0.0" # GPU accelerated version
__author__ = "Baloothebear4"

# Import main classes so they can be used as: from pyvisualiser import SpectrumAnalyzer
# Core imports (lifting them from the sub-packages)
from .core.processaudio import *
from .core.displaydriver import *

# Visualiser imports
# Note: Since you're moving frames.py and screens.py, update these paths:

from .visualisers.advanced_frames import *

# From the core subdirectory
from .core.components import *
from .core.framecore import Frame, ColFramer, RowFramer
from .core.screenhandler import ScreenController, Platform

# From the visualisers subdirectory
from pyvisualiser.visualisers.vumeters import *
from pyvisualiser.visualisers.metadata import *
from pyvisualiser.visualisers.spectrum import *

from .styles.styles import *
from .styles.presets import *

# Optional: Define what gets imported with "from pyvisualiser import *"
# __all__ = [
#     'ScreenController',
#     'Platform', 
#     'Frame',
#     'ColFramer',
#     'RowFramer','Bar', 'Effects', 'BarStyle', 'SpectrumStyle', 'NeonGlow',
#     'SpectrumFrame', 'NeonGlow'

#     # Add your main class names here, for example:
#     # 'SpectrumAnalyzer',
#     # 'WaveformDisplay', 
#     # 'AudioProcessor',
#     # 'Visualiser'
# ]

# Optional: Package-level convenience functions
def get_version():
    """Return the current version of pyvisualiser"""
    return __version__

def list_available_visualizers():
    """List all available visualization classes"""
    # This would return info about your available visualizers
    pass

# Dynamically setup all classes and presets to make writing the app code straightforward
# We want Classes, Functions, AND our Preset Instances
import inspect

__all__ = [
    name for name, obj in locals().items() 
    if not name.startswith("_") and (
        inspect.isclass(obj) or 
        inspect.isfunction(obj) or 
        isinstance(obj, (BarEffects, BarStyle, SpectrumStyle)) # Add this!
    )
]