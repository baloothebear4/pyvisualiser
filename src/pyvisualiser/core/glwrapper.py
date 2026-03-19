"""
GLSL Wrapper Class for PyVisualiser
Allows running fragment shaders within a Frame context.
"""
from pyvisualiser.core.framecore import Frame, get_asset_path
from pyvisualiser.core.render import RenderPass
import moderngl
import numpy as np
import time

class GLSLRenderPass(RenderPass):
    def __init__(self, context, frame):
        super().__init__(context)
        self.frame = frame
        self.viewport = None

    def render(self, **kwargs):
        # Preserve the compositor's viewport (usually full FBO)
        original_viewport = self.ctx.viewport
        if self.viewport:
            self.ctx.viewport = self.viewport
        
        self.frame.render_gl()
        
        # Restore viewport for subsequent passes
        self.ctx.viewport = original_viewport

class GLSLFrame(Frame):
    def __init__(self, parent, shader_name, **kwargs):
        super().__init__(parent, **kwargs)
        self.shader_name = shader_name
        self.ctx = None
        self.prog = None
        self.vao = None
        self.start_time = time.time()
        self.render_pass = None
        self.initialized = False
        self.render_mode = moderngl.TRIANGLE_STRIP # Default render mode

    def create_geometry(self):
        """
        Default geometry is a fullscreen quad.
        Subclasses can override this to create custom geometry.
        Should return a VAO.
        """
        vertices = np.array([
            -1.0, -1.0,
             1.0, -1.0,
            -1.0,  1.0,
             1.0,  1.0,
        ], dtype='f4')
        self.vbo = self.ctx.buffer(vertices)
        # The default vertex shader for the quad uses 'in_vert'
        return self.ctx.simple_vertex_array(self.prog, self.vbo, 'in_vert')
        
    def init_gl(self):
        """Deferred initialization of OpenGL context and resources"""
        if self.initialized: return
        
        # 1. Acquire Context
        try:
            # Try to get existing context from the render pipeline (preferred)
            if hasattr(self.platform, 'gfx_driver') and hasattr(self.platform.gfx_driver, 'render_context'):
                self.ctx = self.platform.gfx_driver.render_context.ctx
                self.render_pass = GLSLRenderPass(self.platform.gfx_driver.render_context, self)
            elif hasattr(self.platform, 'ctx') and self.platform.ctx:
                self.ctx = self.platform.ctx
            else:
                self.ctx = moderngl.get_context()
        except Exception as e:
            print(f"GLSLFrame: Could not get ModernGL context: {e}")
            return

        # 2. Load Shaders
        # Default 2D vertex shader
        vertex_src = """
            #version 330
            in vec2 in_vert;
            out vec2 v_uv;
            void main() {
                gl_Position = vec4(in_vert, 0.0, 1.0);
                v_uv = in_vert * 0.5 + 0.5;
            }
        """
        # Check for a custom vertex shader file
        try:
            vert_path = get_asset_path('shaders', f"{self.shader_name}.vert.glsl")
            with open(vert_path, 'r') as f:
                vertex_src = f.read()
        except FileNotFoundError:
            # This is fine, we'll just use the default
            pass
        except Exception as e:
            print(f"GLSLFrame: Error loading vertex shader file '{self.shader_name}.vert.glsl': {e}")
        
        try:
            # Try to load .glsl first (simple shaders), then .frag.glsl (vert/frag pairs)
            try:
                frag_path = get_asset_path('shaders', f"{self.shader_name}.glsl")
                with open(frag_path, 'r') as f:
                    frag_src = f.read()
            except FileNotFoundError:
                frag_path = get_asset_path('shaders', f"{self.shader_name}.frag.glsl")
                with open(frag_path, 'r') as f:
                    frag_src = f.read()
        except Exception as e:
            print(f"GLSLFrame: Error loading fragment shader for '{self.shader_name}': {e}")
            # Fallback magenta error shader
            frag_src = """
                #version 330
                out vec4 f_color;
                void main() { f_color = vec4(1.0, 0.0, 1.0, 1.0); }
            """

        # 3. Compile Program
        try:
            # Check for geometry shader
            geom_src = None
            try:
                geom_path = get_asset_path('shaders', f"{self.shader_name}.geom.glsl")
                with open(geom_path, 'r') as f:
                    geom_src = f.read()
                self.prog = self.ctx.program(vertex_shader=vertex_src, geometry_shader=geom_src, fragment_shader=frag_src)
            except FileNotFoundError:
                self.prog = self.ctx.program(vertex_shader=vertex_src, fragment_shader=frag_src)
        except Exception as e:
            print(f"GLSLFrame: Shader compilation error in {self.shader_name}: {e}")
            return

        # 4. Setup Geometry (delegated to a method)
        self.vao = self.create_geometry()
        if not self.vao:
            print(f"GLSLFrame: create_geometry() for {self.shader_name} did not return a VAO.")
            return
        
        self.initialized = True

    def update_uniforms(self):
        """Override this method to push custom uniforms to self.prog"""
        if not self.prog: return

        # Standard uniforms
        if 'iTime' in self.prog:
            self.prog['iTime'].value = time.time() - self.start_time
        if 'iResolution' in self.prog:
            self.prog['iResolution'].value = (float(self.w), float(self.h))

    def render_gl(self):
        """The actual draw call, executed by the RenderPass."""
        self.ctx.enable(moderngl.BLEND)
        self.vao.render(self.render_mode)
        self.ctx.disable(moderngl.BLEND)

    def update_screen(self, full=False):
        if not self.initialized:
            self.init_gl()
            if not self.initialized: return False

        self.update_uniforms()

        if self.render_pass and hasattr(self.platform.gfx_driver, 'compositor'):
            # Integrate with Compositor Pipeline
            x, y, w, h = self.abs_rect()
            # Convert Pygame Y (Top-Left) to OpenGL Y (Bottom-Left)
            gl_y = self.platform.H - (y + h)
            
            self.render_pass.viewport = (int(x), int(gl_y), int(w), int(h))
            
            # Add to pre_passes (background layer) or we could add to main passes.
            # Visualisers often act as complex backgrounds, so pre_passes is usually appropriate.
            self.platform.gfx_driver.compositor.add_pre_pass(self.render_pass)
        else:
            # Fallback for non-compositor environments
            x, y, w, h = self.abs_rect()
            gl_y = self.platform.H - (y + h)
            viewport = (int(x), int(gl_y), int(w), int(h))
            
            prev_viewport = self.ctx.viewport
            self.ctx.viewport = viewport
            self.render_gl()
            self.ctx.viewport = prev_viewport
        
        return True
