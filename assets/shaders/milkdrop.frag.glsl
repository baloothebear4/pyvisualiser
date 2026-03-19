#version 330
in vec2 v_uv;
out vec4 f_color;

uniform float iTime;
uniform vec2  iResolution;

// Audio Uniforms from your system
uniform float u_volume;      
uniform float u_centroid;    
uniform float u_flux;        
uniform bool  u_beat;        
uniform float u_kurtosis;    

// 1. COORDINATE WARPING (The MilkDrop "Motion" Engine)
vec2 warp(vec2 uv, float amplitude) {
    // MilkDrop uses polar coordinates for its zoom and rotation effects
    float r = length(uv);
    float a = atan(uv.y, uv.x);

    // Zoom effect: pulls pixels inward/outward based on volume
    // u_beat adds a sudden 'kick' to the zoom
    float zoom = 0.95 - (u_volume * 0.1) - (u_beat ? 0.05 : 0.0);
    r *= zoom;

    // Rotation effect: swirls the screen slightly over time
    float swirl = iTime * 0.2 + (u_flux * 0.5);
    a += swirl * (1.0 - r); // More rotation in the center

    // Convert back to Cartesian
    return vec2(r * cos(a), r * sin(a));
}

// 2. PROCEDURAL WAVEFORM (The "Milk" Layer)
float get_wave(vec2 uv) {
    float v = 0.0;
    // Layered sine waves mimic the 'liquid' feedback look
    v += sin(uv.x * 10.0 + iTime) * 0.5;
    v += sin(uv.y * 8.0 - iTime * 1.2) * 0.5;
    v += sin((uv.x + uv.y) * 5.0 + u_flux * 2.0);
    return abs(v) * (u_volume + 0.2);
}

void main() {
    // Normalize UVs to center (0,0)
    vec2 uv = (v_uv * 2.0 - 1.0);
    uv.x *= iResolution.x / iResolution.y;

    // A. Apply Warp
    // This creates the 'tunnel' feedback loop effect
    vec2 warped_uv = warp(uv, u_volume);

    // B. Color Palette (Using your Hi-Fi Blue theme)
    vec3 color_low    = vec3(0.0, 0.1, 0.4);  // Deep Blue
    vec3 color_high   = vec3(0.4, 0.9, 1.0);  // Electric Cyan
    vec3 theme_color  = mix(color_low, color_high, u_centroid);

    // C. Generate Pattern
    float pattern = get_wave(warped_uv);
    
    // D. Edge Glow / Feedback Fade
    // In MilkDrop, the edges usually fade or "wrap"
    float edge_fade = smoothstep(1.5, 0.2, length(uv));
    
    // E. Composition
    // Additive blending of waves and a central 'spark'
    vec3 final_rgb = pattern * theme_color * edge_fade;
    
    // Central "Star" or "Singularity" influenced by the beat
    float glow = 0.02 / (length(uv) + 0.01);
    final_rgb += glow * color_high * (u_volume + 0.5);

    // Beat Flash: Briefly saturate the whole scene
    if(u_beat) {
        final_rgb *= 1.2;
        final_rgb += theme_color * 0.15;
    }

    // Post-processing
    final_rgb = clamp(final_rgb, 0.0, 1.0);
    final_rgb = pow(final_rgb, vec3(0.8)); // High contrast for CRT feel
    
    f_color = vec4(final_rgb, 1.0);
}