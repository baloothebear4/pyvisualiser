# pyvisualiser — UI & Effects Implementation Plan

## Implementation Checklist

- [x] Phase 1 — Formalise the Rendering Core
- [x] Phase 2 — Background System
- [x] Phase 3 — Unified Glow & Bloom System
- [x] Phase 4 — Visualiser Effect Upgrades
- [ ] Phase 5 — Album Art Integration
- [ ] Phase 6 — Overlay Framework
- [x] Phase 7 — Style System Completion
- [ ] Phase 8 — Visualiser Profiles (Embedded HiFi Preamp & Desktop)
- [ ] Phase 9 — Hardware Porting & Performance Validation (Mac to Pi 5)
- [ ] Phase 10 — Packaging & API Hardening
- [ ] Phase 11 — Comprehensive Test Suite
- [ ] Phase 12 — Hero Screens
- [ ] Phase 13 — Integration & Aesthetic Honing

## Objective

Complete `pyvisualiser` as a:

- Hardware-grade OpenGL visualisation engine
- Style-driven UI system
- GPU-accelerated effects framework
- Platform-agnostic core (Mac prototype → Raspberry Pi 5 deployment)
- Clean foundation for `pypreamp` hardware integration

Primary development target: **Mac prototype**  
Secondary deployment target: **Pi 5 (1280×400 landscape)**

---

# Phase 1 — Formalise the Rendering Core

## 1.1 Document the Rendering Pipeline

Create:

    docs/render_pipeline.md

Define:

- Frame lifecycle
- Render pass order
- FBO structure
- Glow/bloom architecture
- Blur strategy
- Composition order
- Where styles inject parameters
- Hardware vs desktop mode differences

Purpose:
- Make architecture explicit
- Improve AI-assisted development quality
- Prevent drift and effect duplication

---

## 1.2 Render Pass Abstractions

Create core abstractions:

    render classes
        pass_base
        fbo
        context
        compositor

Define:

    class RenderPass:
        def render(self, context): ...

Required passes:

- Base geometry pass
- Glow extraction pass
- Blur pass (ping-pong)
- Composite pass
- Optional post-processing pass

Goal:
- Centralised effect management
- No visualiser-specific blur implementations

---

# Phase 2 — Background System

## 2.1 Background Engine

Create:

    background.py with classes
        BackgroundBase
        BackgroundSurface
        BackgroundLighting

Background must support:

- Base surface colour or texture
- Ambient panel glow
- Optional album-art derived wash
- Subtle noise layer
- Vignette layer

Goal:
- Treat background as a virtual hardware surface
- Reusable across all visualisers

---

## 2.2 Lighting Model

Define lighting zones:

- Ambient panel light (always present)
- Reactive glow source (audio-driven)
- Peak accent highlight

Expose all parameters via style configuration.

Goal:
- No hardcoded glow values inside visualisers
- Unified lighting behaviour

---

# Phase 3 — Unified Glow & Bloom System

## 3.1 Glow Manager

Create:

    effects/glow.py

Responsibilities:

- Downsample extraction
- Horizontal + vertical blur
- Composite (additive/screen)
- Radius scaling
- Intensity mapping

All visualisers must route glow through this system.

---

## 3.2 Style-Driven Glow Configuration

Expose through style:

- Glow intensity
- Glow radius
- Glow colour bias
- Reactive mapping curve
- Blur resolution scale

Goal:
- Central control
- Easy hardware tuning
- No duplicated glow logic

---

# Phase 4 — Visualiser Effect Upgrades

Visualisers:

- Spectrum
- Stereo spectrum
- Vertical VU bars
- Horizontal VU bars
- Analogue VU needle

For each visualiser:

1. Clean geometry rendering
2. Integrate unified glow system
3. Integrate lighting model
4. Add audio smoothing / inertia
5. Validate at 1280×400
6. Validate scaled desktop mode

Work sequentially. Do not refactor all simultaneously.

---

# Phase 5 — Album Art Integration

## 5.1 Album Art Loader

Create:

    media/
        album_loader.py

Responsibilities:

- Image loading
- Resize & scaling
- GPU upload
- Texture caching

---

## 5.2 Album Art Background Processor

Create:

    effects/album_background.py

Capabilities:

- Heavy blur pass
- Desaturation
- Brightness clamp
- Dominant colour extraction
- Ambient profile generation

Returns:

    AmbientColorProfile

Used by background and lighting systems.

---

# Phase 6 — Overlay Framework

Although hardware logic lives in `pypreamp`, rendering support belongs here.

## 6.1 Overlay Renderer

Create:

    ui/
        overlay.py
        transitions.py

Must support:

- Volume overlay
- Source overlay
- Mute overlay
- Menu overlay

Features:

- Fade in/out
- Slide transitions
- Z-layer control
- Non-blocking display

Goal:
- Reusable for hardware + desktop

---

# Phase 7 — Style System Completion

## 7.1 Style Data Classes

Create:

    styles/
        spectrum.py
        vu.py
        background.py
        effects.py

Use immutable dataclasses.

Include:

- Colour palette
- Glow config
- Blur config
- Lighting intensity
- Typography scale
- Motion timing

---

## 7.2 Preset Definitions

Define preset profiles:

- Studio Black
- Warm Sunset
- Cool Precision
- Dark Void

Each preset returns a fully defined style object.

Goal:
- Clean public API
- Consistent product identity

---

# Phase 8 — Visualiser Profiles & Layout design hierarchy

## 8.1 Priority Profile: Embedded HiFi Preamp

Define the configuration and scaling logic for the primary hardware target:
- **Target Resolution**: 1280x400 (7.9" ultrawide screen).
- **Aesthetic**: Premium, hardware-accurate rendering with cinematic lighting.
- **Testing Flow**: Develop and test comprehensively on the Mac Mini, then migrate to the Raspberry Pi 5.

## 8.2 Future Profile: Desktop Visualiser

Define the configuration for a desktop widget mode:
- **Aesthetic**: Floating widget, optional transparency, simplified background so it doesn't distract from desktop work.
- **Adjustments**: Reduced glow radius, lower texture detail to save background GPU overhead.
- **Workflow**: Runs independently alongside the user's daily desktop tasks.

Add runtime configuration support: `profile = "embedded" | "desktop"`

## 8.3 Profile Controls

The complexity of styles and presets is daunting. I need real time interaction to be able to tune the effects and
create the subtle layered type displays that make the visualisers professional and natural looking.  So each Profile 
has a set of controls.  

Each profile has a Look class that massively simplfied the parameter tuning and makes the artistic design much more intuitive:  foe example

@dataclass
class ProfileLook:
    name: str
    brightness: float = 1.0
    contrast: float = 1.0
    energy: float = 0.5
    warmth: float = 0.5

Which maps to :
    energy → bloom + reactivity
    warmth → colour palette
    contrast → threshold

And in the design mode where the visualiser is running on a Mac, with a keyboard to dynamically change parameters to achieve the
real-time design I am after.  This needs a wrapper for the base @dataclasses:  eg

class StyleController:
    def __init__(self, style):
        self.style = style
        self.runtime = asdict(style)

    def adjust(self, key, delta):
        self.runtime[key] += delta

This needs a control surface to make this work:
class StyleController:
    def __init__(self, style):
        self.style = style
        self.runtime = asdict(style)

    def adjust(self, key, delta):
        self.runtime[key] += delta        

## 8.4 Lighting hierarchy

The controls enable the effects to be balances across frames and also have a consistant visual look that is shared across
one or more Screens through the Profile.  This is the target lighting hierarchy for rendering to ensure Text remains sharp:
1 background gradient
2 ambient particle layer
3 main visualiser (spectrum / VU)
4 highlight edges
5 bloom pass
6 light fog
7 metadata UI

This also introduces a LightingStyle class that is the vehicle for this sharing.   

Refactor Effects into:
class LightingResponse:
    attack: float
    decay: float
    power: float

class BloomStyle:
    threshold: float
    intensity: float
    blur: float

Replace boolean with optional styles so that blending is easier:
Eg vignette: Union[VignetteStyle, bool] = False goes to
vignette: Optional[VignetteStyle] = None

---

# Phase 9 — Hardware Porting & Performance Validation

## 9.1 The Mac Mini to Pi 5 Pipeline

Establish a clear staging strategy:
1. **Mac Mini Development**: Build features, formalize aesthetics, and complete rigorous unit/visual testing on macOS.
2. **Profiling Harness**: Profile the Mac implementation (Frame time per pass, FBO costs, Blur overhead) to establish a baseline.
3. **Pi 5 Porting**: Deploy to the Raspberry Pi 5 and validate against the 60fps requirement for the 1280x400 form factor.

## 9.2 Pi-Specific Optimisations

Ensure the framework can seamlessly downgrade intensity for the Pi 5 if necessary:
- Downsample bloom pass to ½ or ¼ resolution.
- Enforce low-resolution for background album art blur.
- Simplify noise layer and particle calculations.

---

# Phase 10 — Packaging & API Hardening

## 10.1 Public API Definition

Document:

- Entry point classes
- Required dependencies
- Style API
- Visualiser instantiation pattern
- Desktop vs hardware configuration

---

## 10.2 Demo Applications

Create:

    examples/
        desktop_demo.py
        hardware_demo.py

Purpose:

- Prototypes
- Regression validation
- Documentation reference
- AI-assisted iteration playground

---

# Phase 11 — Comprehensive Test Suite

## 11.1 Visualiser Test Harnesses

Create dedicated test files for each major component family:

    test/
        VUscreens.py
        spectrum_screens.py
        metadata_screens.py
        barvu_screens.py
        gl_visualiser_screens.py

Responsibilities:
- Isolate each visualiser type for rapid iteration
- Showcase all configuration options and edge cases
- Serve as visual regression tests during refactoring

---

# Phase 12 — Hero Screens

## 12.1 Flagship Visualisations

Create:

    examples/
        hero_screens.py

Design stunning "Hero" screens that exemplify the power of the `pyvisualiser` API (implementing a selection of the following concepts):
- **Radial**: Circular spectrum surrounding central album art, flanked by dual glowing analogue VU meters.
- **Horizon Line**: Expansive horizontal reflecting spectrum analyzer set against a deep starry background.
- **Orbital**: Immersive planetary/orbital rings with glowing particles and a lower horizontal spectrum.
- **Grid / Component Dashboard**: Structured layout featuring album art, dual VU meters, tracklist, and mini spectrum.
- **Central Totem**: A vertical, mirrored cascading spectrum analyzer forming a dramatic central pyramid against a starfield.

Goal:
- Wow the user instantly.
- Demonstrate premium, state-of-the-art aesthetics out-of-the-box.
- Serve as the primary reference for defining beautiful Style profiles.

---

# Phase 13 — Integration & Aesthetic Honing

## 13.1 Holistic Tuning

Focus on the overall feel across all modules:
- Ensure lighting effects (ambient glow, reactive peaks) behave consistently across all visualisers.
- Hone bloom combinations and additive blending so screens look homogenous and deeply integrated.
- Profile complex multi-pass composites to ensure smooth performance without dropping frames.
- Standardize the `Style` dataclasses so that moving from a VU meter to a Spectrum feels like the same unified app.

Goal:
- Transform individual components into a cohesive, highly polished visual engine.

---

# Final Outcome

At completion, `pyvisualiser` will be:

- Fully style-driven
- GPU-optimised
- Hardware-ready
- Desktop-compatible
- Modular and maintainable
- Cleanly separable from `pypreamp`

---

# Development Strategy (AI-Assisted)

For each phase:

1. Define deliverable clearly in Markdown.
2. Ask AI to propose structure only.
3. Implement incrementally.
4. Run visually.
5. Refactor before moving to next phase.
6. Commit per deliverable.

Never allow effects to grow organically without being formalised into the architecture.