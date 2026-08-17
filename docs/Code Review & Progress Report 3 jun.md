# Code Review & Progress Report: `pyvisualiser`

This report provides a comprehensive code review of the `pyvisualiser` package, detailing current progress against the implementation plan, performance bottlenecks, weak/inconsistent coding practices, and latent defects.

---

## 1. Project Progress Against Implementation Plan

Below is an assessment of the project's current state relative to the 13 phases defined in [implementation plan.md](file:///Volumes/Media/dev/pyvisualiser/docs/implementation%20plan.md):

| Phase | Description | Status | Verification & Findings |
| :--- | :--- | :--- | :--- |
| **Phase 1** | Formalise the Rendering Core | **Completed** | [render.py](file:///Volumes/Media/dev/pyvisualiser/src/pyvisualiser/core/render.py) contains `Compositor`, `RenderTarget`, and standard shader passes (`GlowExtractionPass`, `BlurPass`, `CompositePass`, `ToneMappingPass`, `FXAAPass`). Pipeline docs exist. |
| **Phase 2** | Background System | **Completed** | [backgrounds.py](file:///Volumes/Media/dev/pyvisualiser/src/pyvisualiser/core/backgrounds.py) contains `BackgroundBase`, `BackgroundSurface`, and `BackgroundLighting` classes with custom uniforms. |
| **Phase 3** | Unified Glow & Bloom System | **Completed** | Integrated via `CompositePass` and `GlowExtractionPass` in [render.py](file:///Volumes/Media/dev/pyvisualiser/src/pyvisualiser/core/render.py) and configured via `BarEffects`. |
| **Phase 4** | Visualiser Effect Upgrades | **Completed** | Bars, Spectrums, and VU needle meters have been updated to support GPU shaders and bloom logic. |
| **Phase 5** | Album Art Integration | **In Progress** | `MetaImages` and `ArtFrame` are present in [metadata.py](file:///Volumes/Media/dev/pyvisualiser/src/pyvisualiser/visualisers/metadata.py). However, `media/album_loader.py` and the dedicated background processor are **missing**. Texture caching is also absent, causing performance concerns. |
| **Phase 6** | Overlay Framework | **Missing** | The `ui/` directory and overlay renderer (`ui/overlay.py` and `ui/transitions.py`) do not exist. |
| **Phase 7** | Style System Completion | **Completed** | Dataclasses exist in [styles.py](file:///Volumes/Media/dev/pyvisualiser/src/pyvisualiser/styles/styles.py) and presets in [presets.py](file:///Volumes/Media/dev/pyvisualiser/src/pyvisualiser/styles/presets.py). |
| **Phase 8** | Visualiser Profiles | **In Progress** | `VisualiserProfile` and `ProfileController` are in [profiles.py](file:///Volumes/Media/dev/pyvisualiser/src/pyvisualiser/styles/profiles.py). Parameter constraints and layout adjustments have minor defects. |
| **Phase 9** | Hardware Porting & Perf | **Missing** | Pi-specific optimizations are not fully integrated, and requirements configuration is currently Mac-only. |
| **Phase 10** | Packaging & API Hardening | **Missing** | Public API is undocumented. [examples/](file:///Volumes/Media/dev/pyvisualiser/examples) directory is currently empty. |
| **Phase 11** | Comprehensive Test Suite | **In Progress** | Some visual test scripts exist in `tests/`, but structured/automated test coverage is limited. |
| **Phase 12** | Hero Screens | **Missing** | No flagship / composite screens are implemented yet. |
| **Phase 13** | Integration & Aesthetic Honing | **Missing** | Overall layout integration and consistency pass remain. |

---

## 2. Performance Bottlenecks & Optimization Suggestions

### A. Critical: Expensive Font Instantiation on Every Frame
* **Location:** [components.py:L826-841](file:///Volumes/Media/dev/pyvisualiser/src/pyvisualiser/core/components.py#L826-L841) (`Text.shrink_fontsize`)
* **Issue:** 
  In `TextFrame`, the `reset` flag is `True` by default. When the text is drawn, it calls `self.update(text)`, which triggers `self.scalefont` and `self.shrink_fontsize` **every single frame**. 
  Inside `shrink_fontsize`, a new `pygame.font.Font` object is instantiated up to **three times** per call:
  ```python
  font = pygame.font.Font(self.fontfile, int(fontsize))
  ```
  Creating a `pygame.font.Font` involves opening the TTF file, parsing vector paths, and rasterizing glyphs. Doing this 60 times a second for every text element (e.g. elapsed time, track title) causes severe CPU spikes and frame rate drops, rendering the app unusable on a Raspberry Pi.
* **Suggestion:** 
  Implement a static / class-level font cache in the `Text` class or a centralized font registry that stores instantiated `pygame.font.Font` objects keyed by `(fontfile, size)`. Re-use existing instances rather than recreating them.
  Additionally, add a dirty flag so font scaling only recalculates if the text content or the bounding box dimensions actually change.

### B. Severe GPU VRAM / Memory Leak
* **Location:** [displaydriver.py:L944-971](file:///Volumes/Media/dev/pyvisualiser/src/pyvisualiser/core/displaydriver.py#L944-L971) (`GeometryPass.blit`)
* **Issue:** 
  Whenever text changes (e.g., elapsed playback seconds) or images update, a new OpenGL texture is uploaded via `self.ctx.texture()`. 
  To clear the cache on track changes or text updates, the old reference is simply set to `None` (e.g., `self._gl_texture = None` in `Text.draw` and `Image.draw`). 
  However, in ModernGL, orphan textures are not automatically released from GPU memory, resulting in a continuous VRAM memory leak that will eventually crash the application or exhaust device memory.
* **Suggestion:** 
  Explicitly call the `.release()` method on the old `moderngl.Texture` before setting it to `None`:
  ```python
  if self._gl_texture is not None:
      self._gl_texture.release()
      self._gl_texture = None
  ```

### C. Inefficient Text Size Calculations
* **Location:** [components.py:L961-967](file:///Volumes/Media/dev/pyvisualiser/src/pyvisualiser/core/components.py#L961-L967) (`Text.textsize`)
* **Issue:** 
  To calculate text width and height, the code calls `font.render` to generate a temporary Pygame surface, and then queries its bounding rect:
  ```python
  def textsize(self, text=None, font=None):
      ...
      text_surface = font.render(text, True, (0, 128, 255))
      text_abcd = text_surface.get_rect()
      return (text_abcd[2], text_abcd[3])
  ```
  This incurs unnecessary memory allocation and CPU rasterization overhead.
* **Suggestion:** 
  Replace this with Pygame's built-in `font.size(text)` method, which directly queries the font metrics without allocating a surface or rendering glyphs:
  ```python
  def textsize(self, text=None, font=None):
      if text is None: text = self.text
      if font is None: font = self.font
      return font.size(text)
  ```

---

## 3. Weak & Inconsistent Coding Practices

### A. Wildcard Imports (`from ... import *`)
* **Location:** [__init__.py](file:///Volumes/Media/dev/pyvisualiser/src/pyvisualiser/__init__.py), [displaydriver.py](file:///Volumes/Media/dev/pyvisualiser/src/pyvisualiser/core/displaydriver.py), [components.py](file:///Volumes/Media/dev/pyvisualiser/src/pyvisualiser/core/components.py), [backgrounds.py](file:///Volumes/Media/dev/pyvisualiser/src/pyvisualiser/core/backgrounds.py)
* **Issue:** 
  Wildcard imports are used extensively (e.g., `from .core.processaudio import *`, `from pyvisualiser.styles.styles import *`). 
  This pollutes the namespace, creates potential naming collisions, makes dependencies difficult to track, and hides where imported classes/variables originate.
* **Suggestion:** 
  Refactor wildcard imports to use explicit imports (e.g., `from .core.processaudio import AudioProcessor`).

### B. Tight Coupling of UI with Backend platform
* **Location:** [metadata.py](file:///Volumes/Media/dev/pyvisualiser/src/pyvisualiser/visualisers/metadata.py)
* **Issue:** 
  UI frames directly fetch state variables from the backend platform using `self.platform.elapsed`, `parent.platform.track`, etc. 
  This makes UI components impossible to unit-test in isolation without spinning up the entire backend/audio capture pipeline.
* **Suggestion:** 
  Define a clean data-binding interface or state container (e.g., `TrackState` or `UIContext`) that exposes only the necessary properties. Pass this state object to the update/draw methods instead of allowing UI elements to directly read from backend engines.

### C. Multiple Inheritance Mixins with Missing Class Declarations
* **Location:** [spectrum.py](file:///Volumes/Media/dev/pyvisualiser/src/pyvisualiser/visualisers/spectrum.py) (`SpectrumFrame(Frame, Spectrum)`)
* **Issue:** 
  The `Spectrum` base class is used as a mixin. Inside `Spectrum.__init__`, it calls `self.platform.createBands(...)`. 
  However, `Spectrum` does not inherit from `Frame`, nor does it declare `self.platform` in its signature, which causes static typing and linting issues. It assumes that whichever class mixes it in will happen to have a `self.platform` attribute.
* **Suggestion:** 
  Declare typing protocols or use standard single-inheritance. If `Spectrum` requires platform properties, pass it explicitly into `Spectrum.__init__(self, platform, ...)` or use type hints (`self.platform: Platform`).

### D. requirements.txt Configuration is macOS-Specific
* **Location:** [requirements.txt](file:///Volumes/Media/dev/pyvisualiser/requirements.txt)
* **Issue:** 
  The file includes macOS-specific packages like `pyobjc-core` and other Quartz/Cocoa libraries. Running `pip install -r requirements.txt` on the target Raspberry Pi 5 will fail immediately during installation.
* **Suggestion:** 
  Separate dependencies using environment markers in `pyproject.toml` or split into `requirements.txt` and `requirements-mac.txt`.

---

## 4. Latent Defects & Bugs

### A. Critical: `VUHorzFrame` Will Crash Due to Undefined Variable
* **Location:** [vumeters.py:L497](file:///Volumes/Media/dev/pyvisualiser/src/pyvisualiser/visualisers/vumeters.py#L497)
* **Code:**
  ```python
  cols += VUFrame(cols, channel=channel, barsize_pc=0.8, bar_style=BarStyle(orient='horz', tip=tip))
  ```
* **Issue:** 
  `tip` is passed to the `BarStyle` constructor, but it is never defined inside `VUHorzFrame.__init__` parameters or local scope. This will raise a `NameError` and crash the application if `VUHorzFrame` is ever instantiated (which is the case when running `VU2chHorzFrame`).
* **Suggestion:** 
  Add `tip=False` as a parameter to `VUHorzFrame.__init__` and pass it down.

### B. Division by Zero / TypeError in `CircularProgress`
* **Location:** [metadata.py:L143-L144](file:///Volumes/Media/dev/pyvisualiser/src/pyvisualiser/visualisers/metadata.py#L143-L144) (`CircularProgress.update_text`)
* **Code:**
  ```python
  minutes = self.platform.duration//60
  seconds = self.platform.duration%60
  ```
* **Issue:** 
  On startup, before metadata has loaded from Roon or MPD, `self.platform.duration` is `None` or `0`.
  * If it is `None`, it will crash with `TypeError: unsupported operand type(s) for //: 'NoneType' and 'int'`.
  * If it is `0` (or `None` handled unsafely), it could cause division by zero errors elsewhere.
* **Suggestion:** 
  Add a defensive check:
  ```python
  duration = self.platform.duration or 0.0
  minutes = int(duration // 60)
  seconds = int(duration % 60)
  ```

### C. Hardcoded Parameter Bounds in `ProfileController`
* **Location:** [profiles.py:L58](file:///Volumes/Media/dev/pyvisualiser/src/pyvisualiser/styles/profiles.py#L58) (`ProfileController.adjust`)
* **Code:**
  ```python
  new_val = max(0.0, min(2.0, current + delta))
  ```
* **Issue:** 
  Clamping every perceptual value strictly to `[0.0, 2.0]` is a silent limitation. Certain parameters, like `vignette` or `sharpness`, should only be adjusted between `[0.0, 1.0]`, while others might need larger bounds (like blur iterations or particle counts).
* **Suggestion:** 
  Define a parameter specification dictionary mapping each controller attribute to its min and max bounds:
  ```python
  PARAMETER_BOUNDS = {
      'intensity': (0.0, 3.0),
      'softness': (0.0, 1.0),
      'vignette': (0.0, 1.0),
      'sharpness': (0.0, 1.0),
      ...
  }
  ```
  Lookup constraints dynamically in `adjust` instead of hardcoding `[0.0, 2.0]`.
