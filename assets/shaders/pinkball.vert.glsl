//
// Pinkball vertex shader
//
#version 330
in vec2 in_vert;
out vec2 v_uv;
void main() {
    // Scale (0.4) and translate to top-right (0.5, 0.5)
    // The line below was shrinking the visualizer. The fix is to use the input vertices directly.
    gl_Position = vec4(in_vert, 0.0, 1.0);
    v_uv = in_vert * 0.5 + 0.5;
}

            // vertex_shader="""
            //     #version 330
            //     in vec2 in_vert;
            //     out vec2 v_uv;
            //     void main() {
            //         // Scale (0.4) and translate to top-right (0.5, 0.5)
            //         gl_Position = vec4(in_vert * 0.4 + vec2(0.5, 0.5), 0.0, 1.0);
            //         v_uv = in_vert * 0.5 + 0.5;
            //     }
            // """,