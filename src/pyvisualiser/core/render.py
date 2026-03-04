'''
Mar 2026 Baloothebeare4 v1

These are the base classes for rendering on OpenGL shared by the graphics driver and background


'''
import moderngl
from   abc import ABC, abstractmethod
import numpy as np

# --- Phase 1: New Rendering Core Abstractions ---



BACKGROUND_COLOR = (10, 10, 20)  # Dark Blue/Grey, a nice HiFi screen background
class RenderContext:
    """
    Wraps the ModernGL context and manages shared resources.
    It is created by the GraphicsDriver and passed to other render components.
    """
    def __init__(self, ctx: moderngl.Context, size: tuple[int, int], platform):
        self.ctx = ctx
        self.size = size
        self.platform = platform # Reference to the GraphicsDriverGL instance
        
        # Shared Full-screen Quad for post-processing passes.
        # Using a TRIANGLE_STRIP-compatible order: BL, BR, TL, TR
        self.quad_data = np.array([
            # x,    y,   u,   v
            -1.0, -1.0, 0.0, 0.0,  # Bottom-Left
             1.0, -1.0, 1.0, 0.0,  # Bottom-Right
            -1.0,  1.0, 0.0, 1.0,  # Top-Left
             1.0,  1.0, 1.0, 1.0,  # Top-Right
        ], dtype='f4')
        
        self.quad_buffer = self.ctx.buffer(self.quad_data)

    def resize(self, size: tuple[int, int]):
        self.size = size
        self.ctx.viewport = (0, 0, size[0], size[1])

    def clear(self, color=(0.0, 0.0, 0.0, 1.0)):
        self.ctx.clear(*color)

    def get_quad_buffer(self):
        return self.quad_buffer

    @property
    def width(self):
        return self.size[0]

    @property
    def height(self):
        return self.size[1]

class RenderTarget:
    """
    Manages a Texture and a Framebuffer Object (FBO).
    Supports resolution scaling and different data types (e.g., float for HDR).
    """
    def __init__(self, ctx: moderngl.Context, size: tuple[int, int], scale: float = 1.0, components: int = 4, dtype='f1'):
        self.ctx = ctx
        self.base_size = size
        self.scale = scale
        self.components = components
        self.dtype = dtype
        self.texture = None
        self.fbo = None
        self._build()

    def _build(self):
        if self.texture: self.texture.release()
        if self.fbo: self.fbo.release()

        w = max(1, int(self.base_size[0] * self.scale))
        h = max(1, int(self.base_size[1] * self.scale))

        self.texture = self.ctx.texture((w, h), self.components, dtype=self.dtype)
        self.texture.repeat_x = False
        self.texture.repeat_y = False
        
        self.fbo = self.ctx.framebuffer(color_attachments=[self.texture])

    def resize(self, size: tuple[int, int]):
        if size != self.base_size:
            self.base_size = size
            self._build()

    def use(self):
        self.fbo.use()

    def clear(self, color=(0,0,0,0)):
        self.fbo.clear(*color)

class PingPongBuffer:
    """
    Helper for multi-pass effects like Blur that require reading from one buffer
    and writing to another iteratively.
    """
    def __init__(self, ctx: moderngl.Context, size: tuple[int, int], scale: float = 1.0, dtype='f2'):
        self.read = RenderTarget(ctx, size, scale, dtype=dtype)
        self.write = RenderTarget(ctx, size, scale, dtype=dtype)

    def swap(self):
        self.read, self.write = self.write, self.read

    def resize(self, size: tuple[int, int]):
        self.read.resize(size)
        self.write.resize(size)

class RenderPass(ABC):
    """Abstract base class for a rendering pass."""
    def __init__(self, context: RenderContext):
        self.context = context
        self.ctx = context.ctx

    @abstractmethod
    def render(self, **kwargs):
        pass

    def resize(self, size: tuple[int, int]):
        pass

class TextureBlitPass(RenderPass):
    """A simple pass to draw a texture to a target (usually the screen)."""
    def __init__(self, context: RenderContext):
        super().__init__(context)
        self.prog = self.ctx.program(
            vertex_shader="""
                #version 330
                in vec2 in_vert;
                in vec2 in_uv;
                out vec2 v_uv;
                void main() {
                    gl_Position = vec4(in_vert, 0.0, 1.0);
                    v_uv = in_uv;
                }
            """,
            fragment_shader="""
                #version 330
                uniform sampler2D source_texture;
                in vec2 v_uv;
                out vec4 f_color;
                void main() {
                    f_color = texture(source_texture, v_uv);
                }
            """
        )
        self.quad_buffer = self.context.get_quad_buffer()
        self.vao = self.ctx.simple_vertex_array(self.prog, self.quad_buffer, 'in_vert', 'in_uv')

    def render(self, input_target: RenderTarget, output_target: RenderTarget = None, **kwargs):
        if output_target:
            output_target.use()
        else:
            self.ctx.screen.use()
        
        self.ctx.disable(moderngl.BLEND) # Blitting should be a direct copy
        input_target.texture.use(location=0)
        self.prog['source_texture'].value = 0
        self.vao.render(moderngl.TRIANGLE_STRIP)
        self.ctx.enable(moderngl.BLEND) # Re-enable for subsequent passes/frames

class BlurPass(RenderPass):
    """
    Gaussian blur using a separable kernel (Horizontal then Vertical).
    """
    def __init__(self, context: 'RenderContext', iterations: int = 2):
        super().__init__(context)
        self.iterations = iterations
        self.prog = self.ctx.program(
            vertex_shader="""
                #version 330
                in vec2 in_vert;
                in vec2 in_uv;
                out vec2 v_uv;
                void main() {
                    gl_Position = vec4(in_vert, 0.0, 1.0);
                    v_uv = in_uv;
                }
            """,
            fragment_shader="""
                #version 330
                uniform sampler2D image;
                uniform bool horizontal;
                in vec2 v_uv;
                out vec4 f_color;
                
                // 5-tap Gaussian weights
                uniform float weight[5] = float[] (0.227027, 0.1945946, 0.1216216, 0.054054, 0.016216);

                void main() {
                    vec2 tex_offset = 1.0 / textureSize(image, 0); 
                    float spread = 3.0; // Increase spread for wider, softer glow
                    vec3 result = texture(image, v_uv).rgb * weight[0]; 
                    
                    if(horizontal) {
                        for(int i = 1; i < 5; ++i) {
                            result += texture(image, v_uv + vec2(tex_offset.x * i * spread, 0.0)).rgb * weight[i];
                            result += texture(image, v_uv - vec2(tex_offset.x * i * spread, 0.0)).rgb * weight[i];
                        }
                    } else {
                        for(int i = 1; i < 5; ++i) {
                            result += texture(image, v_uv + vec2(0.0, tex_offset.y * i * spread)).rgb * weight[i];
                            result += texture(image, v_uv - vec2(0.0, tex_offset.y * i * spread)).rgb * weight[i];
                        }
                    }
                    f_color = vec4(result, 1.0);
                }
            """
        )
        self.quad_vao = self.ctx.simple_vertex_array(self.prog, context.get_quad_buffer(), 'in_vert', 'in_uv')

    def render(self, ping_pong: PingPongBuffer, **kwargs):
        self.ctx.disable(moderngl.BLEND)
        
        for _ in range(self.iterations):
            # Horizontal
            ping_pong.write.use()
            ping_pong.read.texture.use(location=0)
            self.prog['image'].value = 0
            self.prog['horizontal'].value = True
            self.quad_vao.render(moderngl.TRIANGLE_STRIP)
            ping_pong.swap()
            
            # Vertical
            ping_pong.write.use()
            ping_pong.read.texture.use(location=0)
            self.prog['image'].value = 0
            self.prog['horizontal'].value = False
            self.quad_vao.render(moderngl.TRIANGLE_STRIP)
            ping_pong.swap()

class CompositePass(RenderPass):
    """
    Combines the main scene with the blurred bloom texture.
    """
    def __init__(self, context: 'RenderContext'):
        super().__init__(context)
        self.prog = self.ctx.program(
            vertex_shader="""
                #version 330
                in vec2 in_vert;
                in vec2 in_uv;
                out vec2 v_uv;
                void main() {
                    gl_Position = vec4(in_vert, 0.0, 1.0);
                    v_uv = in_uv;
                }
            """,
            fragment_shader="""
                #version 330
                uniform sampler2D scene;
                uniform sampler2D bloom;
                uniform float bloom_intensity;
                in vec2 v_uv;
                out vec4 f_color;
                void main() {
                    vec4 hdrColor = texture(scene, v_uv);
                    vec3 bloomColor = texture(bloom, v_uv).rgb;
                    
                    // Additive blending
                    vec3 result = hdrColor.rgb + bloomColor * bloom_intensity;

                    // Removed Tone mapping and Gamma correction to prevent "fog" / washout.
                    // The input scene is assumed to be sRGB-ish already, so we just add the bloom.

                    f_color = vec4(result, hdrColor.a);
                }
            """
        )
        self.quad_vao = self.ctx.simple_vertex_array(self.prog, context.get_quad_buffer(), 'in_vert', 'in_uv')

    def render(self, scene_target: RenderTarget, bloom_target: RenderTarget, output_target: RenderTarget = None, intensity=1.0, **kwargs):
        if output_target:
            output_target.use()
        else:
            self.ctx.screen.use()
            
        # CRITICAL FIX: The final composite to the screen MUST use standard alpha blending
        # to correctly handle the transparency of the rendered scene.
        self.ctx.enable(moderngl.BLEND)
        self.ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA
        
        scene_target.texture.use(location=0)
        bloom_target.texture.use(location=1)
        
        self.prog['scene'].value = 0
        self.prog['bloom'].value = 1
        self.prog['bloom_intensity'].value = intensity
        
        self.quad_vao.render(moderngl.TRIANGLE_STRIP)

class Compositor:
    """Orchestrates the rendering pipeline."""
    def __init__(self, context: RenderContext):
        self.context = context
        # Use a 16-bit float buffer ('f2') to allow for HDR values from additive blending (for bloom/glow)
        self.main_target = RenderTarget(context.ctx, context.size, scale=1.0, dtype='f2')
        # Ping-Pong buffer for glow/blur (Half resolution)
        self.glow_buffer = PingPongBuffer(context.ctx, context.size, scale=0.5, dtype='f2')
        
        self.passes: list[RenderPass] = []
        self.pre_passes: list[RenderPass] = [] # Transient passes cleared every frame
        self.post_passes: list[RenderPass] = []

        self.final_blit_pass = TextureBlitPass(context)

        # Add post-processing passes
        self.glow_extraction_pass = GlowExtractionPass(context, threshold=1.0)
        self.post_passes.append(self.glow_extraction_pass)
        self.blur_pass = BlurPass(context, iterations=2)
        self.composite_pass = CompositePass(context)
        
        self.bloom_intensity = 0.8 # Slightly reduce default intensity
        self.debug_view = None # Can be 'glow'
    def add_pass(self, render_pass: RenderPass, at_start=False):
        if at_start:
            self.passes.insert(0, render_pass)
        else:
            self.passes.append(render_pass)

    def add_pre_pass(self, render_pass: RenderPass):
        self.pre_passes.append(render_pass)

    def resize(self, size: tuple[int, int]):
        self.context.resize(size)
        self.main_target.resize(size)
        self.glow_buffer.resize(size)
        for p in self.passes:
            p.resize(size)
        for p in self.post_passes:
            p.resize(size)

    def render_frame(self):
        """
        Executes the pipeline.
        1. Runs geometry passes into an off-screen HDR FBO.
        2. (Future) Runs post-processing passes like blur and glow composite.
        3. Blits the final FBO to the screen (backbuffer).
        """
        # --- Pass 1: Geometry ---
        # All standard drawing goes into our main off-screen buffer.
        self.main_target.use()
        bg = [c/255.0 for c in BACKGROUND_COLOR]
        self.main_target.clear(color=(bg[0], bg[1], bg[2], 1.0))
        
        # Ensure standard blending for pre-passes
        self.context.ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA
        
        # Execute transient pre-passes (e.g. Backgrounds)
        for p in self.pre_passes:
            p.render(output_target=self.main_target)
        
        # Execute all registered passes (just GeometryPass for now)
        for p in self.passes:
            p.render(output_target=self.main_target)

        # --- Pass 2: Post-Processing (Glow Extraction) ---
        self.glow_extraction_pass.render(input_target=self.main_target, output_target=self.glow_buffer.read)

        # --- Pass 3: Blur ---
        self.blur_pass.render(ping_pong=self.glow_buffer)

        # --- Final Pass: Composite to Screen ---
        if self.debug_view == 'glow':
            # For testing, just show the glow map
            self.final_blit_pass.render(input_target=self.glow_buffer.read)
        else:
            # Composite Glow back onto Main
            self.composite_pass.render(scene_target=self.main_target, bloom_target=self.glow_buffer.read, intensity=self.bloom_intensity)

        # Reset transient state for the next frame
        self.pre_passes = []
        self.debug_view = None
        
        # Reset threshold to default to prevent test settings leaking
        self.glow_extraction_pass.threshold = 1.0


class GlowExtractionPass(RenderPass):
    """
    Extracts bright parts of an image based on a threshold.
    This is the first step in a bloom/glow pipeline.
    """
    def __init__(self, context: 'RenderContext', threshold: float = 1.0):
        super().__init__(context)
        self.threshold = threshold
        self.prog = self.ctx.program(
            vertex_shader="""
                #version 330
                in vec2 in_vert;
                in vec2 in_uv;
                out vec2 v_uv;
                void main() {
                    gl_Position = vec4(in_vert, 0.0, 1.0);
                    v_uv = in_uv;
                }
            """,
            fragment_shader="""
                #version 330
                uniform sampler2D source_texture;
                uniform float threshold;
                in vec2 v_uv;
                out vec4 f_color;
                void main() {
                    vec3 color = texture(source_texture, v_uv).rgb;
                    vec3 bright_color = max(vec3(0.0), color - threshold);
                    f_color = vec4(bright_color, 1.0);
                }
            """
        )
        self.quad_vao = self.ctx.simple_vertex_array(self.prog, context.get_quad_buffer(), 'in_vert', 'in_uv')

    def render(self, input_target: 'RenderTarget', output_target: 'RenderTarget', **kwargs):
        output_target.use()
        output_target.clear()
        self.ctx.disable(moderngl.BLEND)
        input_target.texture.use(location=0)
        self.prog['source_texture'].value = 0
        self.prog['threshold'].value = self.threshold
        self.quad_vao.render(moderngl.TRIANGLE_STRIP)