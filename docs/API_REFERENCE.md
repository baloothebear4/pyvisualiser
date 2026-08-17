# PyVisualiser API Reference

This document provides a comprehensive guide to the core classes, layout managers, components, and style configurations used for creating custom screens and user interfaces in `pyvisualiser`.

---

## 1. Core Architecture

The architecture of `pyvisualiser` is hierarchical: **Screens** are composed of **Frames**, which in turn contain other layout frames or specific visual elements. 

### `ScreenController`
The main orchestrator that manages screens, processes live audio feedback, captures metadata, routes keystroke events, and runs the main loop.

**Constructor:**
```python
ScreenController(screens: list[type[Frame]], hw_platform: dict)
```

**Parameters:**
*   **`screens`**: A list of custom `Frame` subclasses representing the screens the user can cycle through.
*   **`hw_platform`**: A dictionary specifying hardware/driver parameters:
    *   `"gfx"`: `"gl"` (OpenGL rendering) or `"pi_kms"` (Raspberry Pi native KMS framebuffer).
    *   `"loopback"`: String name of the audio loopback device (e.g., `"BlackHole 2ch"`).
    *   `"roon_zone"`: String name of the target Roon zone (e.g., `"MacViz"`).

---

### `Frame` (Base Class)
The fundamental layout block representing a relative rectangular space inside a parent container.

**Constructor:**
```python
Frame(parent, scalers=(1.0, 1.0), align=('centre', 'middle'), square=False, 
      theme=None, background=None, outline=None, padding=0, z_order=0)
```

**Parameters:**
*   **`parent`**: The containing `Frame` (or `platform` for the top-level screen).
*   **`scalers`**: `(width_pc, height_pc)` tuple representing percentages of the parent's size (e.g., `(1.0, 0.5)` is full width, half height).
*   **`align`**: `(horizontal, vertical)` anchoring tuple:
    *   *Horizontal:* `'left'`, `'centre'`, `'right'`
    *   *Vertical:* `'top'`, `'middle'`, `'bottom'`
*   **`square`**: If `True`, forces a 1:1 aspect ratio based on the smallest dimension.
*   **`theme`**: String key of the colour palette (e.g., `'hifi'`, `'ocean'`, `'retro'`). Inherits parent's theme if `None`.
*   **`background`**: Background style definition:
    *   `BackgroundStyle` object for GPU-accelerated backgrounds (stars, clouds, edge lights, shaders).
    *   String theme colour key (e.g., `'background'`, `'dark'`).
    *   Dict for static image backgrounds: `{'image': 'file.png', 'opacity': 120}`.
*   **`outline`**: Outline border styling:
    *   `OutlineStyle` object.
    *   Dict: `{'colour': 'light', 'width': 2, 'radius': 10, 'opacity': 255}`.
*   **`padding`**: Inner padding in pixels.
*   **`z_order`**: Integer defining the paint hierarchy (higher values draw on top).

---

## 2. Layout Managers

Layout managers are subclasses of `Frame` that dynamically distribute and resize child frames. Children are added using the `+=` operator.

### `ColFramer`
Arranges children horizontally in columns.

**Constructor:**
```python
ColFramer(parent, col_ratios=None, padpc=0, **kwargs)
```

**Parameters:**
*   **`col_ratios`**: A tuple of numbers defining the width ratios (e.g., `(1, 2, 1)` makes the middle column twice as wide as the sides). If `None`, infers widths equally.
*   **`padpc`**: Percentage of width (0.0 to 1.0) reserved for gaps between columns.

---

### `RowFramer`
Arranges children vertically in rows.

**Constructor:**
```python
RowFramer(parent, row_ratios=None, padpc=0, **kwargs)
```

**Parameters:**
*   **`row_ratios`**: A tuple defining the height ratios (e.g., `(1, 1)` split into two equal rows).
*   **`padpc`**: Percentage of height (0.0 to 1.0) reserved for gaps between rows.

---

## 3. Core UI Components

These components are designed to present media information, lyrics, volume, or playback status.

### `TextFrame`
Displays a single or wrapped line of text, automatically scaled to fit within the frame.

**Constructor:**
```python
TextFrame(parent, text='Default Text', wrap=False, justify='centre', 
          colour='foreground', font_size=None, update_fn=None, **kwargs)
```

**Parameters:**
*   **`text`**: Initial text content.
*   **`wrap`**: Wraps text onto a second line if it exceeds frame bounds.
*   **`justify`**: Text positioning. Can be a string key or a `(horizontal, vertical)` tuple.
*   **`colour`**: Theme colour key (e.g., `'foreground'`, `'light'`, `'alert'`).
*   **`font_size`**: Explicit cap on the font size. If `None`, scales up to the frame height.
*   **`update_fn`**: An optional callback function returning a string, evaluated on each update tick.

---

### `MetaImages`
Loads and displays album artwork or artist pictures from the active media metadata.

**Constructor:**
```python
MetaImages(parent, art_type='album', opacity=1.0, reflection=None, **kwargs)
```

**Parameters:**
*   **`art_type`**: `'album'` (enforces square constraints) or `'artist'`.
*   **`opacity`**: Float (`0.0` to `1.0`) setting texture opacity.
*   **`reflection`**: Adds a mirrored reflection below the image:
    *   `True` / `False` toggle.
    *   `ReflectionStyle` / Dict mapping: `{'size': 0.3, 'opacity': 0.5}`.

---

### `MetaData`
Displays specific textual track information (Title, Artist, Album, Format, etc.) bound to the active platform.

**Constructor:**
```python
MetaData(parent, metadata_type='artist', justify=('centre', 'middle'), **kwargs)
```

**Parameters:**
*   **`metadata_type`**: one of `'track'`, `'album'`, `'artist'`, `'volume'`, `'source'`, `'sample_rate'`, `'format'`.
*   **`justify`**: Bounding alignment.

---

### `PlayProgressFrame`
A playback progression bar flanked by elapsed and remaining track timers.

**Constructor:**
```python
PlayProgressFrame(parent, barsize_pc=0.5, orient='horz', led_h=1, led_gap=0, **kwargs)
```

**Parameters:**
*   **`barsize_pc`**: Percentage thickness of the progress bar relative to the frame.
*   **`orient`**: `'horz'` or `'vert'`.
*   **`led_h` / `led_gap`**: Segments the bar into individual LED blocks for a hardware appearance.

---

## 4. Audio Visualisers

GPU-accelerated components that react dynamically to real-time audio.

### `VUFrame` (LED Bar)
A responsive segmented or solid channel level meter.

**Constructor:**
```python
VUFrame(parent, channel, orient='vert', flip=False, barsize_pc=0.7, bar_style=None, **kwargs)
```

**Parameters:**
*   **`channel`**: `'left'`, `'right'`, or `'mono'`.
*   **`orient`**: `'vert'` (grows vertically) or `'horz'` (grows horizontally).
*   **`flip`**: Direction. If `True`, vertical bars grow downwards, horizontal grow left.
*   **`barsize_pc`**: Width/height of the active bar relative to the frame.
*   **`bar_style`**: `BarStyle` configuration object.

---

### `VUMeter` (Needle Dial)
A classic skeuomorphic analogue needle meter with custom markings, glowing needles, and specular pivots.

**Constructor:**
```python
VUMeter(parent, channel, style=None, **kwargs)
```

**Parameters:**
*   **`channel`**: `'left'`, `'right'`, or `'mono'`.
*   **`style`**: `VUMeterStyle` configuration object.

---

### `SpectrumFrame` (FFT Analyzer)
A multi-band audio spectrum analyzer.

**Constructor:**
```python
SpectrumFrame(parent, channel, bar_style=None, spectrum_style=None, **kwargs)
```

**Parameters:**
*   **`channel`**: `'left'`, `'right'`, or `'mono'`.
*   **`bar_style`**: `BarStyle` configuration.
*   **`spectrum_style`**: `SpectrumStyle` configuration.

---

### `Oscilogramme` (Waveform)
Displays the live modulated audio waveform.

**Constructor:**
```python
Oscilogramme(parent, channel, **kwargs)
```

---

### `Diamondiser` (Concentric Radial)
Renders a circular spectrum analyzer where neon lines project outwards from the center.

**Constructor:**
```python
Diamondiser(parent, channel, barsize_pc=1, **kwargs)
```

---

## 5. Style Configurations

Styles are defined using immutable dataclasses to enforce standardized aesthetics across profiles.

### `BackgroundStyle`
Drives the GPU background shader pass.
*   **`colour`**: str. Theme colour index (default: `'background'`).
*   **`colour_opacity`**: float. Default: `1.0`.
*   **`texture_path`**: Optional[str]. File name of background overlay.
*   **`texture_opacity`**: float. Default: `0.5`.
*   **`vignette`**: `VignetteStyle` or `bool`. Renders soft outer shadows.
*   **`noise`**: `NoiseStyle` or `bool`. Adds organic analog film grain.
*   **`ambient_glow`**: `AmbientGlowStyle` or `bool`. Radial background lighting.
*   **`reactive_glow`**: `ReactiveGlowStyle` or `bool`. Audio-driven pulsing lights.
*   **`peak_accent`**: `PeakAccentStyle` or `bool`. Flash effect on high audio peaks.
*   **`starfield`**: `StarfieldStyle` or `bool`. Moving particulate stars.
*   **`cloud`**: `CloudStyle` or `bool`. Flowing vapor clouds.
*   **`edge_light`**: `EdgeLightStyle` or `bool`. Adds glowing ambient borders.
*   **`shader`**: Union[str, bool]. Standard GLSL pattern name (e.g. `'balatro'`).

### `BarStyle`
Defines VU levels and spectrum columns.
*   **`led_h`**: int. Height of LED blocks (default: `10`).
*   **`led_gap`**: int. Gap spacing. Set to `0` for solid bars.
*   **`peak_h`**: int. Height of floating peak points.
*   **`flip`**: bool. Inverts growth directions.
*   **`orient`**: str. `'vert'` or `'horz'`.
*   **`edge_softness`**: float. Softness halo on bar shapes.
*   **`colour_mode`**: str. `'vert'` (frequency height gradient) or `'horz'` (horizontal spread gradient).

---

## 6. Complete API Integration Example

The following code illustrates how to build a custom multi-panel Hifi screen and launch it.

```python
import platform
from pyvisualiser import (
    Frame, ColFramer, RowFramer, SpectrumFrame, VUMeter, 
    MetaDataFrame, MetaImages, PlayProgressFrame, ScreenController
)
from pyvisualiser.styles.presets import EmbeddedHiFiProfile
from pyvisualiser.styles.styles import BarStyle, SpectrumStyle, BackgroundStyle
from pyvisualiser.styles.profiles import ProfileManager

# 1. Define the Custom Screen Layout
class CustomStudioDashboard(Frame):
    @property
    def title(self):
        return "Custom Studio Dashboard"

    @property
    def type(self):
        return "Base"

    def __init__(self, parent):
        # Initialize screen Frame with a dark hifi theme
        super().__init__(
            parent, 
            theme='hifi', 
            background=BackgroundStyle(colour='dark', noise=True, vignette=True)
        )
        
        # Grid: Split horizontally into 3 columns (left dial, middle meta/progress, right spectrum)
        cols = ColFramer(self, col_ratios=(1, 2, 1), padpc=0.04)
        
        # Col 1: Analogue needle VU meter for Left channel
        cols += VUMeter(cols, channel='left', outline={'colour': 'light', 'width': 1, 'radius': 12})
        
        # Col 2: Stack of album artwork, metadata text fields, and play progress bar
        center_stack = RowFramer(cols, row_ratios=(4, 2, 1), padpc=0.03)
        center_stack += MetaImages(center_stack, art_type='album', reflection={'size': 0.3, 'opacity': 0.4})
        center_stack += MetaDataFrame(center_stack)
        center_stack += PlayProgressFrame(center_stack, barsize_pc=0.3)
        
        # Col 3: Segmented neon FFT Spectrum for Right channel
        cols += SpectrumFrame(
            cols, 
            channel='right', 
            bar_style=BarStyle(led_h=6, led_gap=2, peak_h=2, tip=True),
            spectrum_style=SpectrumStyle(barw_min=6, barsize_pc=0.5)
        )

# 2. Platform Selector Helper
def get_hardware_platform():
    # Detect platform dynamically
    if platform.system() == "Darwin":
        return {
            "gfx": "gl",                # Use OpenGL compositor
            "loopback": "BlackHole 2ch", # Local loopback audio
            "roon_zone": "MacViz"       # Roon audio source
        }
    else:
        return {
            "gfx": "pi_kms",            # Pi framebuffer
            "loopback": "loopin",
            "roon_zone": "pre3"
        }

# 3. Main Launch Loop
if __name__ == "__main__":
    # Apply global profile controls
    ProfileManager.set_profile(EmbeddedHiFiProfile)
    
    # Initialize and run visualiser ScreenController
    visualiser = ScreenController(
        screens=[CustomStudioDashboard], 
        hw_platform=get_hardware_platform()
    )

    try:
        visualiser.run()
    except KeyboardInterrupt:
        visualiser.stop()
```