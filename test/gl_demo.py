# visual_bg_gl.py
# GPU-powered background + panel + subtle 3D light
# Requires: pygame, PyOpenGL, numpy

import sys, time
import pygame
from pygame.locals import *
from OpenGL.GL import *
import numpy as np

# PyOpenGL context fix for certain environments (keeping as provided)
from OpenGL import contextdata
contextdata.setValue = lambda *args, **kwargs: None


# -------- Configuration --------
# Physical Screen/Viewport Resolution (Portrait)
WIDTH, HEIGHT = 400, 1280
# Content Resolution (Desired render target for the visualizer content - Landscape)
CONTENT_WIDTH, CONTENT_HEIGHT = 1280, 400
FPS = 60
# --------------------------------

# --- VERTEX SHADER: Handles 90-degree Rotation ---
VERTEX_SHADER = """#version 130
in vec2 a_pos;
out vec2 v_uv;

void main() {
    // 1. Rotation: Apply 90-degree Clockwise rotation: (x, y) -> (y, -x).
    // This rotates the 1280x400 content so it appears correctly on the 400x1280 screen.
    vec2 rotated_pos = vec2(a_pos.y, -a_pos.x);

    // Set the final screen position
    gl_Position = vec4(rotated_pos, 0.0, 1.0);

    // 2. UV Calculation: Pass the *original* unrotated UVs (0-1) to the fragment shader.
    // v_uv.x is the long dimension (1280), v_uv.y is the short dimension (400).
    v_uv = a_pos * 0.5 + 0.5;
}
"""

# --- FRAGMENT SHADER: Renders the dynamic, aspect-corrected visuals ---
FRAGMENT_SHADER = """#version 130
out vec4 outColor;
uniform float time;
uniform vec2 resolution; // Set to (1280, 400) - the content size
in vec2 v_uv;

void main() {
    // uv now represents the normalized coordinate of the 1280x400 content space.
    vec2 uv = v_uv;

    // Center the coordinates around (0, 0)
    vec2 center = uv - 0.5;

    // Aspect Correction: Stretch the x-coordinate to match the content's 3.2:1 aspect ratio.
    // This ensures circular/radial effects look correct on the wide content.
    center.x *= resolution.x / resolution.y; // 1280 / 400 = 3.2

    // Distance from center (for radial gradient)
    float dist = length(center);
    // Vignette: smooth transition from bright (inside) to dark (outside)
    float vignette = smoothstep(0.8, 0.1, dist);

    // Rotating light direction
    float angle = time * 0.5; // slower rotation
    vec2 lightDir = vec2(cos(angle), sin(angle));

    // Compute simple shading (how aligned the pixel is to the light direction)
    float light = dot(normalize(center), lightDir);
    light = 0.5 + 0.5 * light; // normalize to 0–1
    light = pow(light, 1.2);   // soft contrast

    // Base colours
    vec3 baseColor = vec3(0.07, 0.09, 0.19);   // dark navy base
    vec3 glowColor = vec3(0.25, 0.35, 0.55);   // soft blue light

    // Blend background with moving light, modulated by the vignette
    vec3 color = mix(baseColor, glowColor, light * vignette);

    // Add subtle 3D frame edge (based on content UV)
    float edge = smoothstep(0.02, 0.0, min(min(uv.x, uv.y), min(1.0 - uv.x, 1.0 - uv.y)));
    color += vec3(edge) * 0.1;

    outColor = vec4(color, 1.0);
}
"""


# --------- GL helper functions ----------
def compile_shader(src, shader_type):
    sh = glCreateShader(shader_type)
    glShaderSource(sh, src)
    glCompileShader(sh)
    # check compile status
    ok = glGetShaderiv(sh, GL_COMPILE_STATUS)
    if not ok:
        err = glGetShaderInfoLog(sh).decode()
        raise RuntimeError("Shader compile error: " + err)
    return sh

def link_program(vs_src, fs_src):
    vs = compile_shader(vs_src, GL_VERTEX_SHADER)
    fs = compile_shader(fs_src, GL_FRAGMENT_SHADER)
    prog = glCreateProgram()
    glAttachShader(prog, vs)
    glAttachShader(prog, fs)
    glLinkProgram(prog)
    ok = glGetProgramiv(prog, GL_LINK_STATUS)
    if not ok:
        err = glGetProgramInfoLog(prog).decode()
        raise RuntimeError("Program link error: " + err)
    # cleanup shaders (they are linked now)
    glDeleteShader(vs)
    glDeleteShader(fs)
    return prog

# ---------- Setup pygame + GL ----------
def make_fullscreen_quad_vao():
    # Fullscreen quad positions (NDC)
    data = np.array([
        -1.0, -1.0, # bottom-left
         1.0, -1.0, # bottom-right
        -1.0,  1.0, # top-left
         1.0,  1.0  # top-right
    ], dtype=np.float32)
    # vbo
    vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, data.nbytes, data, GL_STATIC_DRAW)
    glBindBuffer(GL_ARRAY_BUFFER, 0)
    return vbo

def main():
    pygame.init()
    # Request an OpenGL context and set window size to physical screen resolution (400x1280)
    pygame.display.gl_set_attribute(pygame.GL_DOUBLEBUFFER, 1)
    surface = pygame.display.set_mode((WIDTH, HEIGHT), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("GPU Background Shader Demo")

    prog = link_program(VERTEX_SHADER, FRAGMENT_SHADER)
    glUseProgram(prog)

    # Get uniform locations
    time_loc = glGetUniformLocation(prog, "time")
    res_loc = glGetUniformLocation(prog, "resolution")
    # Added back the pointer uniform location, though it's not currently used in the active shader
    pointer_loc = glGetUniformLocation(prog, "pointer")


    # prepare VBO
    vbo = make_fullscreen_quad_vao()
    a_pos = glGetAttribLocation(prog, "a_pos")
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glEnableVertexAttribArray(a_pos)
    glVertexAttribPointer(a_pos, 2, GL_FLOAT, GL_FALSE, 0, None)


    # GL states
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_CULL_FACE)

    clock = pygame.time.Clock()
    running = True
    start_time = time.time()
    # Pointer is normalized (0-1) for touch/mouse
    pointer = (0.5, 0.5)

    while running:
        # Time in seconds since last frame
        dt = clock.tick(FPS) / 1000.0
        for evt in pygame.event.get():
            if evt.type == QUIT:
                running = False
            elif evt.type == KEYDOWN and evt.key == K_ESCAPE:
                running = False
            elif evt.type == MOUSEMOTION:
                # Normalize mouse position based on current window size (400x1280)
                mx, my = evt.pos
                pointer = (mx / WIDTH, my / HEIGHT)
            elif evt.type == FINGERMOTION or evt.type == FINGERDOWN:
                # pygame gives normalized positions for touch (0-1)
                pointer = (evt.x, evt.y)
            elif evt.type == FINGERUP:
                pointer = (0.5, 0.5) # Reset pointer on release


        now = time.time() - start_time
        glUseProgram(prog)

        # Set content resolution (1280x400) for the fragment shader calculations
        glUniform2f(res_loc, float(CONTENT_WIDTH), float(CONTENT_HEIGHT))
        # Set time uniform
        glUniform1f(time_loc, now)
        # Set pointer uniform (currently unused in active shader)
        # glUniform2f(pointer_loc, float(pointer[0]), float(pointer[1]))


        # draw fullscreen quad
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)
        glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)

        pygame.display.flip()

    # cleanup
    glDeleteBuffers(1, [vbo])
    glDeleteProgram(prog)
    pygame.quit()
    sys.exit(0)

if __name__ == "__main__":
    main()
