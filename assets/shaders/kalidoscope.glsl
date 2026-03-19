//kalidoscope
//
/* This animation is the material of my first youtube tutorial about creative 
   coding, which is a video in which I try to introduce programmers to GLSL 
   and to the wonderful world of shaders, while also trying to share my recent 
   passion for this community.
                                       Video URL: https://youtu.be/f4s1h2YETNY
*/

// //https://iquilezles.org/articles/palettes/
// vec3 palette( float t ) {
//     vec3 a = vec3(0.5, 0.5, 0.5);
//     vec3 b = vec3(0.5, 0.5, 0.5);
//     vec3 c = vec3(1.0, 1.0, 1.0);
//     vec3 d = vec3(0.263,0.416,0.557);

//     return a + b*cos( 6.28318*(c*t+d) );
// }

// //https://www.shadertoy.com/view/mtyGWy
// void mainImage( out vec4 fragColor, in vec2 fragCoord ) {
//     vec2 uv = (fragCoord * 2.0 - iResolution.xy) / iResolution.y;
//     vec2 uv0 = uv;
//     vec3 finalColor = vec3(0.0);
    
//     for (float i = 0.0; i < 4.0; i++) {
//         uv = fract(uv * 1.5) - 0.5;

//         float d = length(uv) * exp(-length(uv0));

//         vec3 col = palette(length(uv0) + i*.4 + iTime*.4);

//         d = sin(d*8. + iTime)/8.;
//         d = abs(d);

//         d = pow(0.01 / d, 1.2);

//         finalColor += col * d;
//     }
        
//     fragColor = vec4(finalColor, 1.0);
// }

#version 330

uniform float iTime;
uniform vec2 iResolution;
uniform float u_vu;    // Volume level (0.0 to 1.0)
uniform float u_bass;  // Bass energy (0.0 to ~1.0)


// Audio Uniforms
uniform float u_volume;      // Overall loudness
uniform float u_centroid;    // Brightness/Color (0-1)
uniform float u_flux;        // Spectral change (energy spikes)
uniform bool  u_beat;        // Pulse trigger
uniform float u_kurtosis;    // Tonal vs Noise (Sharpness)

in vec2 v_uv; // Passed from vertex shader, ranges from 0.0 to 1.0
out vec4 f_color;

// Palette function for coloring
vec3 palette(float t) {
    vec3 a = vec3(0.5, 0.5, 0.5);
    vec3 b = vec3(0.5, 0.5, 0.5);
    // Slow down the color cycling for a more subtle effect
    vec3 c = vec3(0.8, 0.8, 0.8); 
    vec3 d = vec3(0.263, 0.416, 0.557);
    return a + b * cos(6.28318 * (c * t + d));
}

void main() {
    // Convert from 0-1 v_uv to centered, aspect-corrected coordinates
    vec2 uv = (v_uv * 2.0 - 1.0);
    uv.x *= iResolution.x / iResolution.y;
    vec2 uv0 = uv;
    
    vec3 finalColor = vec3(0.0);
    
    // Dynamic parameters based on audio
    // Reduce the base speed from 0.2 to 0.05 to slow down the geometric animation
    float speed = 0.05 + (u_flux * 0.1); 
    float scale_audio = 1.0 + (u_vu * 0.1);
    
    for (float i = 0.0; i < 4.0; i++) {
        // Fractal space folding
        uv = fract(uv * 1.5) - 0.5;
        
        float d = length(uv) * exp(-length(uv0));
        
        // Color mapping
        // Reduce the time multiplier from 0.4 to 0.1 to slow down the color cycling
        vec3 col = palette(length(uv0) + i*.4 + iTime*0.01);
        
        d = sin(d * (8.0 + u_centroid*10.0) + iTime * speed) / 8.0;
        d = abs(d);
        
        // Neon glow effect
        d = pow(0.01 / d, 1.2);
        
        finalColor += col * d;
    }
    
    // Pulse brightness with volume
    finalColor *= scale_audio/2;
    
    // Reduce overall brightness to prevent excessive bloom, while keeping the glow effect
    finalColor /= 2.0;
    
    f_color = vec4(finalColor, 1.0);
}
