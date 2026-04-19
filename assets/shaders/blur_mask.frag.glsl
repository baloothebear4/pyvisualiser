#version 330

in vec2 v_texcoord;
out vec4 f_color;

uniform vec2 u_resolution;
uniform float u_blur_radius;
uniform vec4 u_mask_rect; // [x, y, width, height]
uniform vec4 u_glow_color;

// Function to calculate distance to a rectangle
float sdBox(vec2 p, vec2 b) {
    vec2 d = abs(p) - b;
    return length(max(d, 0.0)) + min(max(d.x, d.y), 0.0);
}

void main() {
    // Convert normalized coordinates to pixel space
    vec2 pixel_pos = v_texcoord * u_resolution;
    
    // Calculate the center and half-extents of the frame
    vec2 frame_center = u_mask_rect.xy + (u_mask_rect.zw * 0.5);
    vec2 half_extents = u_mask_rect.zw * 0.5;
    
    // Distance from current pixel to frame edge
    float d = sdBox(pixel_pos - frame_center, half_extents);

    // 1. PUNCH OUT: If we are inside the frame (d < 0), don't draw anything
    // This prevents the glow from bleeding through the content
    if (d < 0.0) discard;

    // 2. GLOW: Calculate alpha based on distance from edge
    // d = 0 is edge of frame (alpha 1.0), d = blur_radius is edge of glow (alpha 0.0)
    float alpha = smoothstep(u_blur_radius, 0.0, d);
    
    // Final output with additive/alpha blending
    f_color = vec4(u_glow_color.rgb, u_glow_color.a * alpha);
}