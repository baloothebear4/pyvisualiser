PyVisualiser: OpenGL Rendering Pipeline & Integration

1. The High-Level Flow
The engine has moved from "Immediate Rendering" (drawing directly to the screen) to a "Deferred Multi-Pass" architecture. Instead of components drawing pixels to a window, they now submit data to a pipeline that processes it in stages.

Code snippet
graph TD
    A[App Loop: vis.py] --> B[ScreenController]
    B --> C[GraphicsDriverGL]
    C --> D[Compositor: render_frame]
    
    subgraph Pipeline Stages
    D --> E[Pre-Pass: BackgroundRenderPass]
    E --> F[Main-Pass: GeometryPass / UI Components]
    F --> G[Post-Pass 1: GlowExtractionPass]
    G --> H[Post-Pass 2: BlurPass / Ping-Pong]
    H --> I[Final-Pass: CompositePass / Tone Mapping]
    end
    
    I --> J[Display Flip]
2. Core Architectural Components
A. The Compositor (render.py)

The Compositor is the "Director" of the pipeline. It manages the off-screen buffers (FBOs) where the drawing actually happens before being shown to the user.

Main Target: An HDR-capable (16-bit float) buffer that stores the sharp image.

Glow Buffer: A half-resolution buffer used specifically for blurring effects to save GPU performance.

B. The GeometryPass (displaydriver.py)

This is the "Worker" that components like Bar, Text, and Image talk to.

Batching: To maximize speed, it doesn't draw one rect at a time. It collects all rectangles, lines, and textures into a large vertex buffer (VBO) and sends them to the GPU in a single "Batch".

SDF Shaders: It uses "Signed Distance Fields" to render rounded corners, soft edges, and segmented LED effects directly on the GPU, keeping your CPU usage low.

3. The Rendering Pipeline Stages
Phase 1: The Geometry Pass (The Sharp Layer)

Clear: The MainTarget is cleared to your HiFi background color.

Backgrounds: The BackgroundRenderPass runs first. It executes a specialized shader that handles vignetting, grain/noise, and ambient lighting zones.

Components: Every UI component (VU bars, Spectrum, Text) adds its geometry to the GeometryPass queue.

Phase 2: Post-Processing (The Glow/Bloom Layer)

Extraction: The GlowExtractionPass looks at the sharp MainTarget. Anything brighter than the threshold (e.g., the "hot" tips of a VU bar) is copied to the GlowBuffer.

Blur (Ping-Pong): The BlurPass runs a Gaussian blur horizontally, then vertically. It does this "Ping-Pong" style, bouncing the image between two textures until it is soft and spread out.

Phase 3: Composition & Tone Mapping

Additive Blend: The CompositePass takes the sharp image and adds the blurred glow on top.

Reinhard Tone Mapping: Because "Glow + Color" can result in values brighter than a monitor can show (pure white blowout), this math maps infinite brightness down to a visible 1.0 range, preserving color detail in bright areas.

Gamma Correction: The image is adjusted for standard sRGB displays (Gamma 2.2) so colors look "natural" rather than washed out.

4. How to Integrate and Configure
Configuration via Styles

You should not change the shaders to change the look. Instead, use the Style objects which inject values into the uniforms of these passes.

Glow Intensity: Managed in the CompositePass via bloom_intensity.

Background Dynamics: Managed in BackgroundRenderPass via uniforms for u_vignette_strength, u_noise_strength, and u_reactive_intensity.

Adding Assets

The system now uses a standardized get_asset_path helper.

Place your textures in assets/backgrounds/ or assets/textures/.

The BackgroundSurface will automatically load these and convert them to OpenGL textures only when needed, preventing memory leaks.

Performance Tuning for Pi 5

If the frame rate drops:

Downsample: Increase the scale factor in the GlowBuffer (e.g., from 0.5 to 0.25).

Blur Iterations: Reduce the iterations count in the BlurPass.

Threshold: Raise the extraction threshold so fewer pixels need to be blurred.