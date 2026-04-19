#version 330

in vec2 v_texcoord;
out vec4 f_color;

uniform sampler2D u_texture;
uniform vec2 u_resolution;
uniform float u_blur_radius;
uniform vec4 u_mask_rect; // [x, y, width, height]
uniform vec4 u_glow_color;

void main() {
    vec2 pixel_pos = v_texcoord * u_resolution;

    // Use .x, .y, .z, .w for [x, y, width, height]
    if (pixel_pos.x >= u_mask_rect.x && 
        pixel_pos.x <= u_mask_rect.x + u_mask_rect.z && // z = width
        pixel_pos.y >= u_mask_rect.y && 
        pixel_pos.y <= u_mask_rect.y + u_mask_rect.w)    // w = height
    {
        discard; 
    }

    // ... rest of your blur logic ...
    vec4 sum = vec4(0.0);
    float samples = 0.0;
    for (float x = -u_blur_radius; x <= u_blur_radius; x += 1.0) {
        for (float y = -u_blur_radius; y <= u_blur_radius; y += 1.0) {
            sum += texture(u_texture, v_texcoord + vec2(x, y) / u_resolution);
            samples += 1.0;
        }
    }
    f_color = (sum / samples) * u_glow_color;
}