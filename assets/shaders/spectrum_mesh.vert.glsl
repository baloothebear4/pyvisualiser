#version 330

uniform mat4 u_mvp;
uniform sampler2D u_spectrum;
uniform float iTime;
uniform float u_strength;

in vec2 in_vert; // Grid coordinates from -1.0 to 1.0

out float v_height;

void main() {
    // in_vert.x is X axis, in_vert.y is Z axis
    vec2 uv = in_vert * 0.5 + 0.5; // Convert to 0.0 - 1.0 for texture sampling

    // Sample the spectrum texture. We'll use the X coordinate of the grid.
    float height = texture(u_spectrum, vec2(uv.x, 0.5)).r;
    
    // Add a secondary wave based on time and Z position for more movement
    // float wave = sin(in_vert.y * 10.0 + iTime * 2.0) * 0.02; // Disabled for tuning
    
    // Combine and apply strength from VU meter
    float final_height = height * u_strength;

    vec3 pos = vec3(in_vert.x, final_height, in_vert.y);

    gl_Position = u_mvp * vec4(pos, 1.0);
    v_height = final_height;
}