# pyvisualiser — UI & Effects Implementation Plan

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

# Phase 8 — Desktop Mode

## 8.1 Mode Configuration Layer

Add configuration flag:

    mode = "desktop" | "hardware"

Desktop mode adjustments:

- Reduced texture detail
- Reduced glow radius
- Simplified background
- Optional transparency
- Adjusted scaling logic

Validate on Mac before hardware deployment.

---

# Phase 9 — Performance & Pi Readiness

## 9.1 Profiling Harness

Add profiling for:

- Frame time per pass
- FBO cost
- Blur cost
- Texture upload spikes
- Album art processing

---

## 9.2 Downsampling Strategy

Ensure:

- Bloom pass at ½ or ¼ resolution
- Album art blur low resolution
- Noise layer lightweight
- No redundant state changes

Goal:
- Stable 60fps on Pi 5
- Controlled GPU cost

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