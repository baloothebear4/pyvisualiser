"""
GLSL Wrapper Class for PyVisualiser
Allows running fragment shaders within a Frame context.
"""
from pyvisualiser.core.framecore import Frame, get_asset_path
from pyvisualiser.core.render import RenderPass
import moderngl
import numpy as np
import time, os

class GLSLRenderPass(RenderPass):
    """
    Standardised GLSL Render Pass for Visualiser Frames.
    """
    def __init__(self, context, frame):
        super().__init__(context)
        self.frame = frame
        self.viewport = None
        self.start_time = time.time()

    def render(self, **kwargs):
        if not self.frame.initialized:
            return

        # 1. Viewport setup
        original_viewport = self.ctx.viewport
        if self.viewport:
            self.ctx.viewport = self.viewport
            
        prog = self.frame.prog
        
        # 2. Standard Uniforms
        prog['iTime'].value = time.time() - self.start_time
        if 'iResolution' in prog:
            prog['iResolution'].value = (float(self.viewport[2]), float(self.viewport[3]))
        
        # Audio Reactor
        platform = self.frame.platform
        ap = getattr(platform, 'audio_processor', None)
        if ap:
            # Basic VU/Bass/Treble
            if 'u_vu' in prog: prog['u_vu'].value = float(getattr(ap, 'vu_mono', 0.5))
            if 'u_bass' in prog: prog['u_bass'].value = float(getattr(ap, 'bass', 0.0))
            if 'u_treble' in prog: prog['u_treble'].value = float(getattr(ap, 'treble', 0.0))
            
            # Full Spectral Analysis
            analysis = ap.get_analysis() if hasattr(ap, 'get_analysis') else {}
            for key, val in analysis.items():
                u_key = f"u_{key}"
                if u_key in prog:
                    prog[u_key].value = float(val) if not isinstance(val, bool) else int(val)

        # Coordinate Mapping
        if 'u_frame_offset' in prog:
            prog['u_frame_offset'].value = (float(self.viewport[0]), float(self.viewport[1]))
        if 'u_frame_size' in prog:
            prog['u_frame_size'].value = (float(self.viewport[2]), float(self.viewport[3]))
        if 'u_screen_size' in prog:
            prog['u_screen_size'].value = (float(self.frame.platform.W), float(self.frame.platform.H))

        # Allow frame to push custom uniforms
        self.frame.update_uniforms()

        # 3. Draw
        self.ctx.enable(moderngl.BLEND)
        self.ctx.blend_func_separate = (
            moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA, 
            moderngl.ONE, moderngl.ONE_MINUS_SRC_ALPHA
        )
        self.frame.vao.render(self.frame.render_mode)
        # The compositor manages the high-level state; we stay enabled for subsequent passes.
        
        # Restore viewport
        self.ctx.viewport = original_viewport

class GLSLFrame(Frame):
    """
    A robust GLSL Visualiser Frame that standardises shader loading and audio reactivity.
    """
    FRAGMENT_TEMPLATE = """
        #version 330
        in vec2 v_uv;
        out vec4 f_colour;

        uniform float iTime;
        uniform vec2 iResolution;
        uniform float u_vu;
        uniform float u_bass;
        uniform float u_treble;
        uniform float u_volume; 
        uniform float u_centroid;    
        uniform float u_flux;        
        uniform bool  u_beat;        
        uniform float u_kurtosis;    

        uniform vec2 u_frame_offset;
        uniform vec2 u_frame_size;
        uniform vec2 u_screen_size;

        // --- INJECTED SHADER CODE START ---
        %s
        // --- INJECTED SHADER CODE END ---

        void main() {
            vec2 screen_coords = u_frame_offset + v_uv * u_frame_size;
            f_colour = run_pattern(u_screen_size, screen_coords);
        }
    """

    def __init__(self, parent, shader_name, **kwargs):
        super().__init__(parent, **kwargs)
        self.shader_name = shader_name
        self.ctx = None
        self.prog = None
        self.vao = None
        self.render_pass = None
        self.initialized = False
        self.render_mode = moderngl.TRIANGLE_STRIP 

    def init_gl(self):
        if self.initialized: return
        
        import re
        
        # 1. Get Context
        try:
            gfx = getattr(self.platform, 'gfx_driver', None)
            if gfx and hasattr(gfx, 'render_context'):
                self.ctx = gfx.render_context.ctx
                self.render_pass = GLSLRenderPass(gfx.render_context, self)
            else:
                self.ctx = moderngl.get_context()
        except Exception as e:
            print(f"GLSLFrame> Context error: {e}")
            return

        # 2. Source Loading & Transformation
        try:
            path = None
            for ext in ['.glsl', '.frag.glsl']:
                try:
                    p = get_asset_path('shaders', f"{self.shader_name}{ext}")
                    if os.path.exists(p):
                        path = p
                        break
                except: pass
            
            if not path:
                raise FileNotFoundError(f"Shader {self.shader_name} not found")

            with open(path, 'r') as f:
                src = f.read()

            # Transformation logic
            src = re.sub(r'#version\s+\d+', '', src)
            common_to_strip = [
                'v_uv', 'iTime', 'iResolution', 
                'u_volume', 'u_centroid', 'u_flux', 'u_beat', 'u_kurtosis',
                'u_vu', 'u_bass', 'u_treble',
                'u_frame_offset', 'u_frame_size', 'u_screen_size'
            ]
            for u in common_to_strip:
                src = re.sub(rf'uniform\s+\w+\s+{u}\s*;', '', src)
                src = re.sub(rf'in\s+vec2\s+{u}\s*;', '', src)

            # Redirect output
            src = "vec4 pattern_out = vec4(0.0);\n" + src
            for out_name in ['f_colour', 'f_color', 'fragColor']:
                if out_name in src:
                    src = re.sub(rf'out\s+vec4\s+{out_name}\s*;', '', src)
                    src = re.sub(rf'\b{out_name}\b', 'pattern_out', src)

            # Rename main
            if 'void main()' in src:
                src = re.sub(r'\bvoid\s+main\s*\(\s*\)', 'void pattern_main()', src)

            # Injected Wrapper
            pattern_code = f"""
{src}
vec4 run_pattern(vec2 screenSize, vec2 screen_coords) {{
    pattern_out = vec4(0.0, 0.0, 0.0, 1.0);
    vec2 iResolution = screenSize;
    #ifdef PATTERN_USES_EFFECT
        pattern_out = effect(screenSize, screen_coords);
    #else
        pattern_main();
    #endif
    return pattern_out;
}}
"""
            if 'vec4 effect(' in src:
                pattern_code = "#define PATTERN_USES_EFFECT\n" + pattern_code
            elif 'pattern_main()' not in pattern_code:
                pattern_code += "\nvoid pattern_main() { pattern_out = vec4(1.0, 0.0, 1.0, 1.0); }\n"

            # 3. Final Compilation
            vert_src = """
                #version 330
                in vec2 in_vert;
                out vec2 v_uv;
                void main() {
                    gl_Position = vec4(in_vert, 0.0, 1.0);
                    v_uv = in_vert * 0.5 + 0.5;
                }
            """
            self.prog = self.ctx.program(
                vertex_shader=vert_src,
                fragment_shader=self.FRAGMENT_TEMPLATE % pattern_code
            )
            
            # Mesh geometry
            vertices = np.array([-1,-1, 1,-1, -1,1, 1,1], dtype='f4')
            self.vbo = self.ctx.buffer(vertices)
            self.vao = self.ctx.simple_vertex_array(self.prog, self.vbo, 'in_vert')
            self.initialized = True

        except Exception as e:
            print(f"GLSLFrame> Error on {self.shader_name}: {e}")

    def update_uniforms(self):
        """Hook for subclasses to push custom uniforms"""
        pass

    def update_screen(self, full=False):
        """Standard pyvisualiser draw hook"""
        if not self.initialized:
            self.init_gl()
            if not self.initialized: return False

        if self.render_pass and hasattr(self.platform.gfx_driver, 'compositor'):
            x, y, w, h = self.abs_rect()
            gl_y = self.platform.H - (y + h)
            self.render_pass.viewport = (int(x), int(gl_y), int(w), int(h))
            
            # Register with compositor (using pre-pass so it draws behind UI)
            self.platform.gfx_driver.compositor.add_pre_pass(self.render_pass)
            
            # Continue traversal to allowed nested UI elements to draw over the shader
            super().update_screen(full=full)
            return True
        return False
