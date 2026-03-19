#version 330
in vec2 v_uv;
out vec4 f_color;

uniform float iTime;
uniform vec2  iResolution;

// Audio Uniforms
uniform float u_volume;      
uniform float u_centroid;    
uniform float u_flux;        
uniform bool  u_beat;        
uniform float u_kurtosis;    

// Internal Plasma for the "Boiling" Sun effect
float plasma(vec2 uv, float speed) {
    float v = 0.0;
    vec2 c = uv * 4.0 - vec2(2.0);
    v += sin(c.x + iTime * speed);
    v += sin((c.y + iTime * speed) * 0.5);
    v += sin((c.x + c.y + iTime * speed) * 0.5);
    c += vec2(0.6 * sin(iTime * speed), 0.4 * cos(iTime * speed));
    v += sin(sqrt(c.x*c.x + c.y*c.y + 1.0) + iTime * speed);
    return v;
}

void main() {
    vec2 uv = (v_uv * 2.0 - 1.0);
    uv.x *= iResolution.x / iResolution.y;
    float dist = length(uv);
    float angle = atan(uv.y, uv.x);
    
    // 1. DYNAMIC SCALING
    float vol = u_volume * 1.6;
    float pulse_size = 0.25 + (vol * 0.2) + (u_beat ? 0.1 : 0.0);
    
    // 2. HI-FI BLUE PALETTE DEFINITION
    // We strictly use cold colors now.
    vec3 color_deep   = vec3(0.0, 0.02, 0.1);   // Deep Midnight (Background)
    vec3 color_low    = vec3(0.0, 0.1, 0.4);    // Royal Blue (Bass)
    vec3 color_mid    = vec3(0.0, 0.5, 0.8);    // Hi-Fi Blue (Mid)
    vec3 color_high   = vec3(0.4, 0.9, 1.0);    // Electric Cyan (Treble)
    
    // Determine the "Theme" based on the musical style (Centroid)
    vec3 theme_color = mix(color_low, color_high, u_centroid);
    
    // 3. THE ACTIVE SUPERNOVA CORE
    // The plasma noise creates the "boiling" activity inside the star
    float activity = plasma(uv * 1.2, 0.4 + u_flux * 0.8);
    float sun_body = smoothstep(pulse_size + 0.05, pulse_size - 0.1, dist);
    
    // Internal glow that doesn't go pitch black
    vec3 core_render = mix(color_deep, theme_color, (activity * 0.5 + 0.5) * sun_body);

    // 4. DETACHED RIPPLE RAYS
    float petal_count = 6.0;
    // Radial movement: Rays appear to fly outward from the core
    float ripple = dist - (iTime * 0.6) - (vol * 0.3);
    float ray_shape = pow(abs(cos(angle * petal_count + ripple * 3.5)), 4.0);
    
    // Gap logic: Start rays outside the sun and fade them at the edges
    float ray_mask = smoothstep(pulse_size, pulse_size + 0.3, dist);
    ray_mask *= smoothstep(1.3, 0.6, dist); // Edge softening
    
    vec3 ray_render = ray_shape * ray_mask * theme_color * (vol + 0.6);

    // 5. VOLUMETRIC GLOW (The Nebula Fill)
    // This removes the "Ominous Black" and fills it with dark blue haze
    float nebula_haze = exp(-dist * 1.1) * 0.4;
    vec3 nebula_render = nebula_haze * color_low;

    // 6. THE SINGULARITY (Hot Center)
    // Always keep a bright point to guide the eye
    float sparkle = 0.015 / (dist + 0.005);
    vec3 center_light = sparkle * vec3(0.8, 0.9, 1.0) * (vol + 1.0);

    // 7. FINAL COMPOSITION (Additive)
    vec3 final_rgb = nebula_render;   // Start with background haze
    final_rgb += core_render;         // Add the boiling sun
    final_rgb += ray_render;          // Add the rippling rays
    final_rgb += center_light;        // Add the white-hot core

    // Beat interaction: a quick boost to saturation/brightness
    if(u_beat) {
        final_rgb *= 1.15;
        final_rgb += (1.0 - smoothstep(0.0, 0.5, dist)) * 0.2 * color_high;
    }

    // Post-processing for a clean Hi-Fi look
    final_rgb = clamp(final_rgb, 0.0, 1.0);
    final_rgb = pow(final_rgb, vec3(0.95)); // Slight gamma adjustment
    
    f_color = vec4(final_rgb, 1.0);
}