// Star like visualiser designed to interpret the mood and shifting enery of music
//
//Version 2
#version 330
in vec2 v_uv;
out vec4 f_color;

uniform float iTime;
uniform vec2  iResolution;

// Audio Uniforms
uniform float u_volume;      // Overall loudness
uniform float u_centroid;    // Brightness/Color (0-1)
uniform float u_flux;        // Spectral change (energy spikes)
uniform bool  u_beat;        // Pulse trigger
uniform float u_kurtosis;    // Tonal vs Noise (Sharpness)

// Helper to create a rotating star ray layer
float get_petals(vec2 uv, float count, float speed, float sharpness) {
    float angle = atan(uv.y, uv.x);
    float d = length(uv);
    // Create rays using a power function for sharpness
    float r = abs(cos(angle * count + iTime * speed));
    return pow(r, sharpness);
}

void main() {
    // Normalize coordinates
    vec2 uv = (v_uv * 2.0 - 1.0);
    uv.x *= iResolution.x / iResolution.y;
    
    float dist = length(uv);
    
    // 1. Dynamic Parameters from Audio
    float vol = u_volume * 1.5;
    float flux_jitter = u_flux * 0.15;
    // Map Kurtosis to "pointiness" (3.0 for noisy, 15.0 for sharp tonal notes)
    float sharpness = 2.0 + (u_kurtosis * 20.0); 
    
    // 2. Complex Petal Layering
    // We mix three different frequencies to create organic complexity
    float layer1 = get_petals(uv, 5.0,  0.5, sharpness);   // Large slow base
    float layer2 = get_petals(uv, 8.0, -0.8, sharpness * 0.5); // Counter-rotating
    float layer3 = get_petals(uv, 13.0, 1.2, 2.0);        // Fast thin "hairs"
    
    float petal_shape = (layer1 * 0.5 + layer2 * 0.3 + layer3 * 0.2);
    
    // 3. The "Bloom" and Pulse
    float pulse = vol + (u_beat ? 0.2 : 0.0);
    float core_size = 0.05 + pulse * 0.1;
    
    // 4. Multi-stage Glow (The "Beauty" secret)
    // Core glow: tight and hot
    float glow1 = 0.01 / (dist - core_size);
    // Petal glow: follows the ray shapes
    float glow2 = (petal_shape * 0.05) / (dist - core_size);
    // Outer haze: soft volumetric feel
    float haze = exp(-dist * (3.0 - vol));
    
    // 5. Color Palette (Using Centroid)
    // Low (Bass) = Deep Red/Purple | High (Treble) = Electric Cyan/White
    // vec3 color_low = vec3(0.5, 0.0, 0.7);  // Nebula Purple
    // vec3 color_mid = vec3(1.0, 0.2, 0.3);  // Starfire Orange
    // vec3 color_high = vec3(0.2, 0.8, 1.0); // Pulsar Blue
    vec3 color_deep   = vec3(0.0, 0.02, 0.1);   // Deep Midnight (Background)
    vec3 color_low    = vec3(0.0, 0.1, 0.4);    // Royal Blue (Bass)
    vec3 color_mid    = vec3(0.0, 0.5, 0.8);    // Hi-Fi Blue (Mid)
    vec3 color_high   = vec3(0.4, 0.9, 1.0);    // Electric Cyan (Treble)


    vec3 star_color;
    if(u_centroid < 0.5) {
        star_color = mix(color_low, color_mid, u_centroid * 2.0);
    } else {
        star_color = mix(color_mid, color_high, (u_centroid - 0.5) * 2.0);
    }
    
    // Add white core for high volume/beats
    star_color = mix(star_color, vec3(1.0), u_volume * 0.5);

    // 6. Final Composition
    vec3 final_rgb = star_color * (glow1 + glow2 + (haze * 0.4));
    
    // Subtle additive contrast
    final_rgb = pow(final_rgb, vec3(0.8)); // Gamma correction for pop
    
    f_color = vec4(final_rgb, 1.0);
}