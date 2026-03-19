#version 330

in float v_height;
out vec4 f_color;

// Simple palette function for coloring
vec3 palette(float t) {
    vec3 a = vec3(0.1, 0.5, 0.8);
    vec3 b = vec3(0.5, 0.5, 0.5);
    vec3 c = vec3(1.0, 1.0, 1.0);
    vec3 d = vec3(0.0, 0.33, 0.67);
    return a + b * cos(6.28318 * (c * t + d));
}

void main() {
    // Color based on height, with a minimum brightness
    vec3 color = palette(v_height * 2.0);
    f_color = vec4(color, 1.0);
}