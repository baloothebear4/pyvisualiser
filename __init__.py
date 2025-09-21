"""
PyVisualiser - Audio Visualization Library
==========================================

A Python library for real-time audio visualization with support for:
- Spectrum analysis
- Waveform display  
- Multiple display backends
- Audio processing pipelines
"""

__version__ = "0.1.0"
__author__ = "Your Name"

# Import main classes so they can be used as: from pyvisualiser import SpectrumAnalyzer
from .visualiser import *
from .processaudio import *
from .displaydriver import *
from .screens import *
from .frames import *

# Optional: Define what gets imported with "from pyvisualiser import *"
__all__ = [
    # Add your main class names here, for example:
    # 'SpectrumAnalyzer',
    # 'WaveformDisplay', 
    # 'AudioProcessor',
    # 'Visualiser'
]

# Optional: Package-level convenience functions
def get_version():
    """Return the current version of pyvisualiser"""
    return __version__

def list_available_visualizers():
    """List all available visualization classes"""
    # This would return info about your available visualizers
    pass