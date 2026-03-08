#!/usr/bin/env python
"""
Test Harness for Compositor and Render Pipeline
Verifies that the Compositor correctly handles Pre-Passes (Backgrounds),
Geometry Passes, and Post-Processing.
"""
import sys
import os
import time
import pygame
import moderngl
import numpy as np

# Adjust path to find pyvisualiser package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from pyvisualiser.core.render import RenderContext, Compositor, RenderPass
from pyvisualiser.core.backgrounds import BackgroundBase
from pyvisualiser.styles.styles import (
    BackgroundStyle, AmbientGlowStyle, VignetteStyle, NoiseStyle, 
    ReactiveGlowStyle, PeakAccentStyle, StarfieldStyle
)

# --- Mock Classes to satisfy dependencies ---
class MockPlatform:
    W = 1280
    H = 400
    def __init__(self):
        self.gfx_driver = None
        # Add audio simulation support for Reactive Glow
        self.audio_available = True
        self.vu = {'mono': 0.0}

class MockFrame:
    def __init__(self, platform):
        self.platform = platform
        self.colours = MockColours()
        self.w = platform.W
        self.h = platform.H
        self.x0 = 0
        self.y0 = 0
        self.outline_w = 0
        self.padding = 0

    def abs_rect(self):
        return (0, 0, self.w, self.h)

class MockColours:
    def get(self, name):
        # Return a visible color for testing
        if name == 'background': return (20, 20, 40)
        if name == 'red': return (255, 0, 0)
        if name == 'green': return (0, 255, 0)
        if name == 'blue': return (0, 0, 255)
        if name == 'light': return (200, 200, 255)
        if name == 'alert': return (255, 50, 50)
        if name == 'mid': return (100, 100, 150)
        if name == 'dark': return (50, 50, 80)
        return (100, 100, 100)

# --- Test Render Pass ---
class SimpleTestPass(RenderPass):
    """A simple pass that draws a red triangle (HDR) to verify geometry rendering."""
    def __init__(self, context):
        super().__init__(context)
        self.prog = self.ctx.program(
            vertex_shader="""
                #version 330
                in vec2 in_vert;
                void main() {
                    gl_Position = vec4(in_vert, 0.0, 1.0);
                }
            """,
            fragment_shader="""
                #version 330
                out vec4 f_color;
                void main() {
                    f_color = vec4(4.0, 0.0, 0.0, 1.0); // HDR RED (Should Glow)
                }
            """
        )
        # Triangle vertices
        vertices = np.array([
            0.0, 0.5,
            -0.5, -0.5,
            0.5, -0.5,
        ], dtype='f4')
        self.vbo = self.ctx.buffer(vertices)
        self.vao = self.ctx.simple_vertex_array(self.prog, self.vbo, 'in_vert')

    def render(self, **kwargs):
        self.vao.render(moderngl.TRIANGLES)

class RaymarchingPass(RenderPass):
    """Draws a raymarching shader example in the top-right corner."""
    def __init__(self, context):
        super().__init__(context)
        self.start_time = time.time()
        self.prog = self.ctx.program(
            vertex_shader="""
                #version 330
                in vec2 in_vert;
                out vec2 v_uv;
                void main() {
                    // Scale (0.4) and translate to top-right (0.5, 0.5)
                    gl_Position = vec4(in_vert * 0.4 + vec2(0.5, 0.5), 0.0, 1.0);
                    v_uv = in_vert * 0.5 + 0.5;
                }
            """,
            fragment_shader="""
                #version 330
                in vec2 v_uv;
                out vec4 f_color;

                uniform float iTime;
                uniform vec2 iResolution;
                uniform float u_fold_offset;
                uniform float u_speed_mult;

                vec3 palette(float d){
                    return mix(vec3(0.2,0.7,0.9),vec3(1.,0.,1.),d);
                }

                vec2 rotate(vec2 p,float a){
                    float c = cos(a);
                    float s = sin(a);
                    return p*mat2(c,s,-s,c);
                }

                float map(vec3 p){
                    for( int i = 0; i<8; ++i){ 
                        float t = iTime * u_speed_mult;
                        p.xz =rotate(p.xz,t);
                        p.xy =rotate(p.xy,t*1.89);
                        p.xz = abs(p.xz);
                        p.xz -= u_fold_offset;
                    }
                    return dot(sign(p),p)/5.;
                }

                vec4 rm (vec3 ro, vec3 rd){
                    float t = 0.;
                    vec3 col = vec3(0.);
                    float d;
                    for(float i =0.; i<64.; i++){ 
                        vec3 p = ro + rd*t;
                        d = map(p)*.5;
                        if(d<0.02){
                            break;
                        }
                        if(d>100.){
                            break;
                        }
                        col+=palette(length(p)*.1)/(400.*(d));
                        t+=d;
                    }
                    return vec4(col,1./(d*100.));
                }

                void main() {
                    vec2 uv = (v_uv * iResolution.xy - iResolution.xy * 0.5) / iResolution.y;
                    
                    vec3 ro = vec3(0.,0.,-50.);
                    ro.xz = rotate(ro.xz,iTime/2.0);
                    vec3 cf = normalize(-ro);
                    vec3 cs = normalize(cross(cf,vec3(0.,1.,0.)));
                    vec3 cu = normalize(cross(cf,cs));
                    
                    vec3 uuv = ro+cf*3. + uv.x*cs + uv.y*cu;
                    
                    vec3 rd = normalize(uuv-ro);
                    
                    vec4 col = rm(ro,rd);
                    
                    f_color = col;
                }
            """
        )
        vertices = np.array([
            -1.0, -1.0,
             1.0, -1.0,
            -1.0,  1.0,
             1.0,  1.0,
        ], dtype='f4')
        self.vbo = self.ctx.buffer(vertices)
        self.vao = self.ctx.simple_vertex_array(self.prog, self.vbo, 'in_vert')

    def render(self, **kwargs):
        self.prog['iTime'].value = time.time() - self.start_time
        self.prog['iResolution'].value = (512.0, 160.0)
        self.prog['u_fold_offset'].value = 0.5 + 0.1 * np.sin((time.time() - self.start_time) * 0.5)
        self.prog['u_speed_mult'].value = 0.5
        self.vao.render(moderngl.TRIANGLE_STRIP)

class BlueBarPass(RenderPass):
    """Draws a blue bar across the bottom."""
    def __init__(self, context):
        super().__init__(context)
        self.prog = self.ctx.program(
            vertex_shader="""
                #version 330
                in vec2 in_vert;
                void main() {
                    // Bottom strip
                    gl_Position = vec4(in_vert.x, in_vert.y * 0.1 - 0.9, 0.0, 1.0);
                }
            """,
            fragment_shader="""
                #version 330
                out vec4 f_color;
                void main() {
                    f_color = vec4(0.0, 0.5, 5.0, 1.0); // HDR Blue/Cyan
                }
            """
        )
        vertices = np.array([
            -1.0, -1.0,
             1.0, -1.0,
            -1.0,  1.0,
             1.0,  1.0,
        ], dtype='f4')
        self.vbo = self.ctx.buffer(vertices)
        self.vao = self.ctx.simple_vertex_array(self.prog, self.vbo, 'in_vert')

    def render(self, **kwargs):
        self.vao.render(moderngl.TRIANGLE_STRIP)

class YellowCrossPass(RenderPass):
    """Draws a yellow cross in the center."""
    def __init__(self, context):
        super().__init__(context)
        self.prog = self.ctx.program(
            vertex_shader="""
                #version 330
                in vec2 in_vert;
                void main() {
                    gl_Position = vec4(in_vert, 0.0, 1.0);
                }
            """,
            fragment_shader="""
                #version 330
                out vec4 f_color;
                void main() {
                    f_color = vec4(3.0, 3.0, 0.0, 1.0); // HDR Yellow
                }
            """
        )
        # Two rectangles forming a cross (using triangles)
        vertices = np.array([
             # Vertical rect (2 triangles)
             -0.05, -0.5,  0.05, -0.5, -0.05, 0.5,
              0.05, -0.5,  0.05,  0.5, -0.05, 0.5,
             # Horizontal rect
             -0.5, -0.05,  0.5, -0.05, -0.5, 0.05,
              0.5, -0.05,  0.5,  0.05, -0.5, 0.05,
        ], dtype='f4')
        self.vbo = self.ctx.buffer(vertices)
        self.vao = self.ctx.simple_vertex_array(self.prog, self.vbo, 'in_vert')

    def render(self, **kwargs):
        self.vao.render(moderngl.TRIANGLES)

# --- Main Test Function ---
def run_test():
    # 1. Setup Pygame & OpenGL Context
    pygame.init()
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)
    
    screen_size = (1280, 400)
    pygame.display.set_mode(screen_size, pygame.OPENGL | pygame.DOUBLEBUF)
    ctx = moderngl.create_context()
    
    # 2. Setup Render Pipeline
    platform = MockPlatform()
    render_context = RenderContext(ctx, screen_size, platform)
    compositor = Compositor(render_context)
    
    # 3. Setup Test Components
    
    # A. Persistent Geometry Passes
    compositor.add_pass(SimpleTestPass(render_context)) # Red Triangle
    compositor.add_pass(RaymarchingPass(render_context)) # Raymarching Shader (Top Right)
    compositor.add_pass(BlueBarPass(render_context))    # Blue Bar (Bottom)
    compositor.add_pass(YellowCrossPass(render_context))# Yellow Cross (Center)
    
    # B. Background Pass (Blue-ish via BackgroundBase)
    # Setup Mock Driver structure for BackgroundBase
    class MockDriver:
        def __init__(self, rc, comp):
            self.render_context = rc
            self.compositor = comp
    
    platform.gfx_driver = MockDriver(render_context, compositor)
    frame = MockFrame(platform)

    # --- Define Background Styles for Testing ---
    styles = [
        ("Ambient Glow", BackgroundStyle(base_color='background', ambient_glow=AmbientGlowStyle(opacity=1.0, color='light'))),
        ("Vignette", BackgroundStyle(base_color='background', vignette=VignetteStyle(strength=1.0))),
        ("Noise", BackgroundStyle(base_color='background', noise=NoiseStyle(strength=0.5))),
        ("Reactive Glow", BackgroundStyle(base_color='background', reactive_glow=ReactiveGlowStyle(color='alert', threshold=0.0))),
        ("Combined", BackgroundStyle(base_color='background', 
                                     ambient_glow=AmbientGlowStyle(opacity=0.5, color='blue'),
                                     vignette=VignetteStyle(strength=0.8),
                                     noise=NoiseStyle(strength=0.2),
                                     reactive_glow=ReactiveGlowStyle(color='red', threshold=0.2))),
        ("Starfield", BackgroundStyle(base_color='background', starfield=StarfieldStyle(density=50.0, speed=0.2)))
    ]
    
    current_style_idx = 0
    bg_base = BackgroundBase(frame, styles[current_style_idx][1])

    print("=== Compositor Test Harness ===")
    print("Expected Output:")
    print("1. Background: Dark Blue (BackgroundRenderPass)")
    print("2. Center: HDR Red Triangle (SimpleTestPass)")
    print("3. Top-Right: Raymarching Shader (RaymarchingPass)")
    print("4. Bottom: HDR Blue Bar (BlueBarPass)")
    print("5. Center: HDR Yellow Cross (YellowCrossPass)")
    print("6. All shapes should have a visible GLOW effect.")
    print("Controls: UP/DOWN to adjust bloom intensity.")
    print("Controls: 'F' to toggle FXAA.")
    print("Controls: 1-5 to switch Background Styles.")
    print(f"Current Style: {styles[current_style_idx][0]}")
    print("Press ESC to exit.")

    clock = pygame.time.Clock()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_UP:
                    compositor.bloom_intensity += 0.1
                    print(f"Bloom Intensity: {compositor.bloom_intensity:.1f}")
                elif event.key == pygame.K_DOWN:
                    compositor.bloom_intensity = max(0.0, compositor.bloom_intensity - 0.1)
                    print(f"Bloom Intensity: {compositor.bloom_intensity:.1f}")
                elif event.key == pygame.K_f:
                    compositor.fxaa_enabled = not compositor.fxaa_enabled
                    print(f"FXAA Enabled: {compositor.fxaa_enabled}")
                elif event.key >= pygame.K_1 and event.key <= pygame.K_6:
                    idx = event.key - pygame.K_1
                    if idx < len(styles):
                        current_style_idx = idx
                        bg_base = BackgroundBase(frame, styles[current_style_idx][1])
                        print(f"Switched to Style: {styles[current_style_idx][0]}")

        # Simulate Audio for Reactive Glow
        platform.vu['mono'] = 0.5 + 0.4 * np.sin(time.time() * 5.0)

        # Simulate Frame Loop
        
        # 1. Add Pre-Passes (Backgrounds must be added every frame as they are transient)
        # BackgroundBase handles adding itself to the compositor
        bg_base.update()
        bg_base.draw()
        
        # 2. Render
        compositor.render_frame()
        
        # 3. Swap Buffers
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    run_test()
