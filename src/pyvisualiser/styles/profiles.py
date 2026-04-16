"""
Core Profile definitions for pyvisualiser.
A Profile is the top-level configuration hierarchy that defines the target environment
(e.g. Embedded HiFi Preamp, Desktop) and its default aesthetic styling.
"""

from dataclasses import dataclass, field
from typing import Optional, Any

from .styles import BarEffects, BackgroundStyle, BarStyle, SpectrumStyle, VUMeterStyle, TextStyle


@dataclass
class ProfileControls:
    """Master perceptual controls that drive rendering parameters dynamically."""
    intensity: float = 0.8
    softness: float = 0.5
    threshold: float = 1.0
    energy: float = 0.5
    smoothness: float = 0.7
    warmth: float = 0.5
    saturation: float = 0.8
    depth: float = 0.3
    vignette: float = 0.2
    sharpness: float = 0.6


class ProfileController:
    """Live-mutable controller that applies ProfileControls to the static styles and Compositor."""
    def __init__(self, controls: Optional[ProfileControls] = None):
        if controls is None:
            controls = ProfileControls()
        self.controls = controls
        self.selected_index = 0
        self.parameters = [
            'intensity', 'softness', 'threshold', 'energy', 
            'warmth', 'saturation', 'vignette', 'sharpness'
        ]

    def select_next(self):
        self.selected_index = (self.selected_index + 1) % len(self.parameters)
        print(f"ProfileController.select_next> {self.parameters[self.selected_index]}")

    def select_prev(self):
        self.selected_index = (self.selected_index - 1) % len(self.parameters)
        print(f"ProfileController.select_prev> {self.parameters[self.selected_index]}")

    @property
    def selected_parameter(self) -> str:
        return self.parameters[self.selected_index]

    def adjust(self, key: Optional[str], delta: float):
        """Safely adjust a control parameter by delta, clamping bounds."""
        target = key if key is not None else self.selected_parameter
        
        if hasattr(self.controls, target):
            current = getattr(self.controls, target)
            new_val = max(0.0, min(2.0, current + delta))
            setattr(self.controls, target, new_val)
            # print(f"ProfileController.adjust> {target} = {new_val:.2f} (delta={delta:+.1f}) id(self)={id(self)}")
        else:
            # print(f"ProfileController.adjust> Unknown key: {target} id(self)={id(self)}")
            pass

    def apply_profile(self, compositor, style=None):
        """Map the high-level perceptual controls down to technical rendering parameters."""
        if not compositor:
            return
            
        # 1. Provide the controls object to the compositor for direct lookup
        # This is the primary 'wiring' that drives the render loop in render.py
        compositor.active_controls = self.controls
            
        # 2. High-level feature toggles
        compositor.fxaa_enabled = self.controls.sharpness > 0.3


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
    effects: BarEffects = field(default_factory=BarEffects)
    
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
    """Singleton manager for the active application profile and live controller."""
    _active_profile: Optional[VisualiserProfile] = None
    _controller: Optional[ProfileController] = None
    
    @classmethod
    def set_profile(cls, profile: VisualiserProfile):
        cls._active_profile = profile
        
    @classmethod
    def get_profile(cls) -> VisualiserProfile:
        if cls._active_profile is None:
            raise RuntimeError("No active profile set! Call ProfileManager.set_profile() before initialising visualisers.")
        return cls._active_profile

    @classmethod
    def get_controller(cls) -> ProfileController:
        if cls._controller is None:
            cls._controller = ProfileController()
        # print(f"ProfileManager.get_controller> id={id(cls._controller)}")
        return cls._controller
