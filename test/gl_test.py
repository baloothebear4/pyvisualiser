import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import numpy as np

from OpenGL import contextdata
contextdata.setValue = lambda *args, **kwargs: None


def main():
    pygame.init()

    # --- request a proper GL context ---
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 1)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)

    # --- create the window before any GL calls ---
    screen = pygame.display.set_mode((1280, 400), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("GL Test - RPi5")

    # --- confirm context ---
    version = glGetString(GL_VERSION)
    print("OpenGL version:", version.decode() if version else "None (no context)")

    # --- shader sources ---
    vertex_src = """
    #version 130
    in vec2 position;
    void main() {
        gl_Position = vec4(position, 0.0, 1.0);
    }
    """

    frag_src = """
    #version 130
    out vec4 outColor;
    void main() {
        outColor = vec4(0.1, 0.3, 0.6, 1.0);
    }
    """

    # --- compile/link shader program ---
    prog = compileProgram(
        compileShader(vertex_src, GL_VERTEX_SHADER),
        compileShader(frag_src, GL_FRAGMENT_SHADER)
    )
    glUseProgram(prog)

    # --- geometry data ---
    vertices = np.array([
        -0.5, -0.5,
         0.5, -0.5,
         0.0,  0.5
    ], dtype=np.float32)

    # --- create VAO (modern GL needs this) ---
    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)

    # --- create VBO and feed vertex data ---
    vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

    # --- bind attribute ---
    pos_loc = glGetAttribLocation(prog, "position")
    if pos_loc == -1:
        raise RuntimeError("Shader attribute 'position' not found.")

    glEnableVertexAttribArray(pos_loc)
    glVertexAttribPointer(pos_loc, 2, GL_FLOAT, GL_FALSE, 0, None)

    # --- draw loop ---
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

        glClearColor(0.02, 0.02, 0.02, 1)
        glClear(GL_COLOR_BUFFER_BIT)
        glDrawArrays(GL_TRIANGLES, 0, 3)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
