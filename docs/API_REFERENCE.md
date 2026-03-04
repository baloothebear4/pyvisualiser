# PyVisualiser API Reference

This document provides a comprehensive guide to the core classes used for creating screens in `pyvisualiser`. The architecture is hierarchical: Screens are composed of Frames, which contain other Frames or specific visual components.

## 1. Layout & Geometry

The layout system is relative. Every component is a `Frame` (or subclass) that exists within a `parent` Frame. Its size and position are defined relative to that parent.

### `Frame` (Base Class)
The fundamental building block. It defines a rectangular area within its parent.

**Constructor:**
```python
Frame(parent, scalers=(1.0, 1.0), align=('centre', 'middle'), square=False, 
      theme=None, background=None, outline=None, padding=0, z_order=0)
```

**Parameters:**
*   **`parent`**: The container Frame (or `platform` for the top-level screen).
*   **`scalers`**: `(width_pc, height_pc)` tuple. Scaling factors relative to the parent. `(1.0, 0.5)` means full width, half height.
*   **`align`**: `(horizontal, vertical)` tuple. Anchors the frame within the parent.
    *   Horizontal: `'left'`, `'centre'`, `'right'`
    *   Vertical: `'top'`, `'middle'`, `'bottom'`
*   **`square`**: `True`/`False`. If True, forces the aspect ratio to 1:1 based on the smallest dimension.
*   **`theme`**: String key for the colour palette (e.g., `'hifi'`, `'ocean'`, `'retro'`). Inherited by children if not specified.
*   **`background`**: Configuration for the background.
    *   String: Colour name (e.g., `'dark'`).
    *   Dict: `{'image': 'filename.jpg', 'opacity': 100, 'per_frame_update': False}`.
    *   Dict (Shadow): `{'colour': 'dark', 'shadow': {'color': (0,0,0), 'offset': (10,10), 'softness': 0.5}}`.
*   **`outline`**: Dict defining the border. `{'colour': 'alert', 'width': 2, 'radius': 10, 'opacity': 255}`.
*   **`padding`**: Integer pixels. Inner padding for content.
*   **`z_order`**: Integer. Drawing order. Higher numbers draw on top of lower numbers.

---

### `ColFramer` & `RowFramer`
Layout managers that automatically arrange child frames in a grid.

#### `ColFramer`
Arranges children horizontally (columns).

**Constructor:**
```python
ColFramer(parent, col_ratios=None, padpc=0, **kwargs)
```

**Parameters:**
*   **`col_ratios`**: Tuple of numbers defining relative widths. `(1, 2, 1)` creates three columns where the middle is 2x wider. If `None`, infers from child scalers.
*   **`padpc`**: Float (0.0 - 1.0). Percentage of space to reserve for gaps between columns.
*   **`**kwargs`**: Standard `Frame` arguments (`align`, `background`, etc.).

**Example:**
```python
# Create 3 columns: Left (1 part), Middle (2 parts), Right (1 part)
cols = ColFramer(self, col_ratios=(1, 2, 1), padding=10)
cols += MetaImages(cols, ...) # Goes in col 1
cols += SpectrumFrame(cols, ...) # Goes in col 2
cols += TextFrame(cols, ...) # Goes in col 3
```

#### `RowFramer`
Arranges children vertically (rows).

**Constructor:**
```python
RowFramer(parent, row_ratios=None, padpc=0, **kwargs)
```

**Parameters:**
*   **`row_ratios`**: Tuple defining relative heights. `(1, 1)` creates two equal rows.
*   **`padpc`**: Float. Percentage gap between rows.

---

## 2. Core Visual Components

These frames display specific content like text, images, or metadata.

### `TextFrame`
Displays a single line of text, automatically scaled to fit the frame.

**Constructor:**
```python
TextFrame(parent, text='Default', justify='centre', wrap=False, colour='foreground', **kwargs)
```

**Parameters:**
*   **`text`**: String to display.
*   **`justify`**: Alignment of text within the frame. `('left'|'centre'|'right', 'top'|'middle'|'bottom')`.
*   **`wrap`**: `True`/`False`. Wraps text to a second line if it doesn't fit.
*   **`colour`**: Theme colour key (e.g., `'light'`, `'alert'`).

### `MetaImages`
Displays Album or Artist artwork from the metadata source.

**Constructor:**
```python
MetaImages(parent, art_type='album', reflection=None, opacity=255, **kwargs)
```

**Parameters:**
*   **`art_type`**: `'album'` (Square) or `'artist'` (Landscape/Portrait).
*   **`reflection`**: Adds a reflection effect below the image.
    *   `True`: Default reflection.
    *   Dict: `{'size': 0.3, 'opacity': 0.5}` (Size is % of image height).
*   **`opacity`**: 0-255. Transparency of the main image.

### `MetaData`
Displays track information (Artist, Title, Album).

**Constructor:**
```python
MetaData(parent, metadata_type='artist', justify='centre', **kwargs)
```

**Parameters:**
*   **`metadata_type`**: `'track'`, `'album'`, or `'artist'`.
*   **`justify`**: Text alignment.

### `PlayProgressFrame`
A progress bar showing elapsed/remaining time and a visual bar.

**Constructor:**
```python
PlayProgressFrame(parent, barsize_pc=0.5, orient='horz', led_h=1, led_gap=0, **kwargs)
```

**Parameters:**
*   **`barsize_pc`**: Thickness of the bar relative to the frame.
*   **`orient`**: `'horz'` or `'vert'`.

---

## 3. Audio Visualisers

Frames that react to audio data (VU levels or FFT spectrums).

### `VUFrame` (Bar Meter)
A highly configurable LED-style or solid bar meter.

**Constructor:**
```python
VUFrame(parent, channel, orient='vert', flip=False, 
        segment_size=5, segment_gap=1, corner_radius=0, edge_softness=0.05,
        intensity_threshold=0.8, intensity_scale=2.0, intensity_blur=0.7, intensity_alpha=20,
        **kwargs)
```

**Parameters:**
*   **`channel`**: `'left'`, `'right'`, or `'mono'`.
*   **`orient`**: `'vert'` (Vertical) or `'horz'` (Horizontal).
*   **`flip`**: Direction.
    *   Vert: `False` = Up, `True` = Down.
    *   Horz: `False` = Right, `True` = Left.
*   **Structure:**
    *   **`segment_size`**: Height/Width of each LED block.
    *   **`segment_gap`**: Space between blocks. Set to 0 for a solid bar.
    *   **`corner_radius`**: Rounding of LED corners (0 = square).
*   **Style:**
    *   **`edge_softness`**: Blur on the edges of the bar (0.0 = sharp, 0.1+ = neon/soft).
*   **Reaction (Glow/Bloom):**
    *   **`intensity_threshold`**: Volume level (0.0-1.0) where the glow starts.
    *   **`intensity_scale`**: How much the glow expands (multiplier of bar width).
    *   **`intensity_blur`**: Softness of the glow halo.
    *   **`intensity_alpha`**: Opacity of the glow (0-255).

### `VUMeter` (Dial/Needle Meter)
A skeuomorphic dial meter with needle, arcs, and ticks.

**Constructor:**
```python
VUMeter(parent, channel, pivot=-0.5, endstops=(3*PI/4, 5*PI/4), 
        needle=..., marks=..., arcs=..., bgdimage=None, **kwargs)
```

**Parameters:**
*   **`pivot`**: Vertical position of the needle pivot relative to frame height (-0.5 is below screen).
*   **`endstops`**: Start and End angles in radians.
*   **`bgdimage`**: Filename of a background image (e.g., `'blue-bgr.png'`).
*   **`needle`**: Dict config `{ 'width':4, 'colour': 'foreground', 'length': 0.8 }`.
*   **`marks`**: Dict of scale markings.
*   **`arcs`**: Dict of colored arcs drawn on the dial.

### `SpectrumFrame`
An FFT-based spectrum analyser.

**Constructor:**
```python
SpectrumFrame(parent, channel, bar_space=0.5, barw_min=1, barw_max=20, 
              led_h=5, led_gap=1, peak_h=1, decay=0.4, **kwargs)
```

**Parameters:**
*   **`channel`**: `'left'`, `'right'`, `'mono'`.
*   **`bar_space`**: Gap between frequency bars (relative to bar width).
*   **`barw_min` / `barw_max`**: Constraints for dynamic bar sizing.
*   **`led_h` / `led_gap`**: Segmentation of the frequency bars.
*   **`peak_h`**: Height of the "peak hold" indicator (0 to disable).
*   **`decay`**: Speed at which bars fall (lower is slower).

### `Oscilogramme`
Displays the raw audio waveform.

**Constructor:**
```python
Oscilogramme(parent, channel, **kwargs)
```

**Parameters:**
*   **`channel`**: `'left'`, `'right'`, `'mono'`.
*   **`resolution`**: (Internal) Number of points to draw (default 256 for performance).

### `Diamondiser`
A circular spectrum analyser where bars radiate from the center.

**Constructor:**
```python
Diamondiser(parent, channel, bar_space=1, **kwargs)
```

**Parameters:**
*   **`bar_space`**: Width of the radiating lines.