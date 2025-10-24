import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import numpy as np
import time

# PyOpenGL workaround for embedded systems (prevents context data errors)
from OpenGL import contextdata
contextdata.setValue = lambda *args, **kwargs: None

# --- GLSL SHADER SOURCES ---
# The vertex shader handles the 90-degree rotation of the content
# to match your physical screen orientation (1280x400 output on a 400x1280 physical display).
vertex_src = """
#version 130
in vec2 position;
out vec2 v_uv;

void main() {
    // 1. Apply 90-degree Clockwise rotation: (x, y) -> (y, -x).
    // This transforms the viewport, rotating the rendered image correctly.
    vec2 rotated_pos = vec2(position.y, -position.x);

    // Set the final screen position (Normalized Device Coordinates)
    gl_Position = vec4(rotated_pos, 0.0, 1.0);

    // 2. Pass the UV coordinate (0 to 1) for the fragment shader
    v_uv = position * 0.5 + 0.5;
}
"""

# The fragment shader is a corrected version of the ShaderToy code,
# now declaring the necessary uniforms and using standard outputs.
frag_src = """
#version 130
in vec2 v_uv; // Input from vertex shader (0.0 to 1.0)
out vec4 outColor;

// Uniforms must be declared when porting from ShaderToy
uniform float iTime;
uniform vec2 iResolution;

void main()
{
    // Define the fragment coordinate 'I' (like gl_FragCoord in ShaderToy)
    // Here, we convert v_uv (0-1) to pixel coordinates, then scale by the short dimension (y)
    vec2 fragCoord = v_uv * iResolution.xy;
    vec2 I = (fragCoord * 2.0 - iResolution.xy) / iResolution.y;

    float i,d,s,t = iTime/2.;
    vec3 p;
    // Set 'r' for resolution scaling (similar to iResolution in original)
    vec3 r = vec3(iResolution, 0.0);

    // Initialize output color (O is now outColor)
    vec4 O = vec4(0.0);

    // Rotation matrix 'R'
    mat2 R = mat2(cos(t + vec4(0, 33, 11, 0)));
    
    // Main raymarching loop
    for(i=0.; i++<1e2; O+=max(1.3*sin(vec4(3,2,1,1)+i*.3)/s,-length(p*p*p)))
    {
        p = vec3(I * d * R, d - 4.0); // Simplified coordinate calculation
        p.xz *= R;
        
        // Distance function calculation
        d+=s=.012+.07*abs(max(sin(length(p*p)/.4),clamp(length(p*p)-4.,0.,2.))-i/1e2);  
    }

    // Final color adjustment and output
    O=tanh(O*O/2e6);
    outColor = O;
}
"""

def make_fullscreen_quad_vertices():
    """Defines a full-screen quad that covers Normalized Device Coordinates (-1 to 1)."""
    return np.array([
        -1.0, -1.0,  # Bottom-left (UV: 0, 0)
         1.0, -1.0,  # Bottom-right (UV: 1, 0)
         1.0,  1.0,  # Top-right (UV: 1, 1)

        -1.0, -1.0,  # Bottom-left (UV: 0, 0)
         1.0,  1.0,  # Top-right (UV: 1, 1)
        -1.0,  1.0   # Top-left (UV: 0, 1)
    ], dtype=np.float32)

def main():
    # Configuration
    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 400
    START_TIME = time.time()
    
    pygame.init()

    # --- GL context setup ---
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 1)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)

    # --- Window setup ---
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("GLSL Visualizer - RPi5 Rotated")

    # --- Context Check ---
    version = glGetString(GL_VERSION)
    print("OpenGL version:", version.decode() if version else "None (no context)")

    # --- Shader compilation ---
    try:
        prog = compileProgram(
            compileShader(vertex_src, GL_VERTEX_SHADER),
            compileShader(frag_src, GL_FRAGMENT_SHADER)
        )
    except Exception as e:
        print("Shader Compilation Error:")
        print(e)
        pygame.quit()
        return

    glUseProgram(prog)

    # --- Uniform Locations (CRITICAL for ShaderToy porting) ---
    time_loc = glGetUniformLocation(prog, "iTime")
    res_loc = glGetUniformLocation(prog, "iResolution")
    
    if time_loc == -1 or res_loc == -1:
         print("Warning: One or more uniform locations not found (iTime/iResolution).")

    # --- Geometry setup (Fullscreen Quad) ---
    vertices = make_fullscreen_quad_vertices()

    # Create VAO
    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)

    # Create VBO
    vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

    # Bind attribute 'position'
    pos_loc = glGetAttribLocation(prog, "position")
    if pos_loc == -1:
        raise RuntimeError("Shader attribute 'position' not found.")

    glEnableVertexAttribArray(pos_loc)
    glVertexAttribPointer(pos_loc, 2, GL_FLOAT, GL_FALSE, 0, None)

    # --- Draw loop ---
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
        
        # 1. Update Uniforms
        elapsed_time = time.time() - START_TIME
        glUniform1f(time_loc, elapsed_time)
        glUniform2f(res_loc, float(SCREEN_WIDTH), float(SCREEN_HEIGHT))

        # 2. Draw
        glClearColor(0.02, 0.02, 0.02, 1)
        glClear(GL_COLOR_BUFFER_BIT)
        
        # Draw the fullscreen quad (6 vertices)
        glDrawArrays(GL_TRIANGLES, 0, 6)
        
        # 3. Swap buffers
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
