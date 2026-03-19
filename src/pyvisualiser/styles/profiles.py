"""
Core Profile definitions for pyvisualiser.
A Profile is the top-level configuration hierarchy that defines the target environment
(e.g. Embedded HiFi Preamp, Desktop) and its default aesthetic styling.
"""

from dataclasses import dataclass, field
from typing import Optional, Any

from .styles import Effects, BackgroundStyle, BarStyle, SpectrumStyle, VUMeterStyle, TextStyle


@dataclass
class VisualiserProfile:
    """
    Base class for a complete Visualiser Profile.
    Defines the absolute root context for the application.
    """
    name: str = "Base Profile"
    target_resolution: tuple[int, int] = (1920, 1080)
    fullscreen: bool = False
    framerate: int = 60
    
    # Global default palette name
    default_palette: str = 'std'
    
    # Global effects configuration (bloom intensity, blur scaling)
    effects: Effects = field(default_factory=Effects)
    
    # Default styles for core components
    background_style: Optional[BackgroundStyle] = None
    bar_style: Optional[BarStyle] = None
    spectrum_style: Optional[SpectrumStyle] = None
    vu_meter_style: Optional[VUMeterStyle] = None
    text_style: Optional[TextStyle] = None

    def get_style(self, component_type: str) -> Any:
        """Fetch the default style for a given component type (e.g., 'vu_meter')."""
        return getattr(self, f"{component_type}_style", None)


class ProfileManager:
    """Singleton manager for the active application profile."""
    _active_profile: Optional[VisualiserProfile] = None
    
    @classmethod
    def set_profile(cls, profile: VisualiserProfile):
        cls._active_profile = profile
        
    @classmethod
    def get_profile(cls) -> VisualiserProfile:
        if cls._active_profile is None:
            raise RuntimeError("No active profile set! Call ProfileManager.set_profile() before initialising visualisers.")
        return cls._active_profile
