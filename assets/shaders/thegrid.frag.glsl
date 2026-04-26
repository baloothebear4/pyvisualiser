// sun & grid functions
// Shader License: CC BY 3.0
// Author: Jan Mróz (jaszunio15)
// Thanks

#version 330

uniform float iTime;
uniform vec2 iResolution;
in  vec2 v_uv;    // Volume level (0.0 to 1.0)
out vec4 f_colour; // Output color

// Audio Uniforms
uniform float u_volume;      
uniform float u_centroid;    
uniform float u_flux;        
uniform bool  u_beat;        
uniform float u_kurtosis; 
uniform float u_bpm;    

float grid(vec2 uv, float battery)
{
    vec2 size = vec2(uv.y, uv.y * uv.y * 0.2) * 0.01;
    uv += vec2(0.0, iTime * 4.0 * u_bpm * (battery + 0.05));
    uv = abs(fract(uv) - 0.5);
 	vec2 lines = smoothstep(size, vec2(0.0), uv);
 	lines += smoothstep(size * 5.0, vec2(0.0), uv) * 0.4 * battery;
    return clamp(lines.x + lines.y, 0.0, 3.0);
}


void main()
{
    vec2 uv = (v_uv * 2.0 - 1.0);
    uv.x *= iResolution.x / iResolution.y;

    float battery = 1.0;
    vec3  background = vec3(0.0, 0.02, 0.1);
    vec3  GridCol = vec3(0.0, 0.2, 1.0);

    // Grid
    // float fog = smoothstep(0.1, -0.02, abs(uv.y + 0.2));
    vec3 col = background;

    if (uv.y < 1.0)
    {
        uv.y = 3.0 / (abs(uv.y + 0.0) + 0.00);
        uv.x *= uv.y * 1.0;
        float gridVal = grid(uv, battery);
        col = mix(col, GridCol, gridVal);
    }
    else
    {

    }

    // col += fog * fog * fog;
    col = mix(vec3(col.r, col.r, col.r) * 0.5, col, battery * 0.7);

    f_colour = vec4(col,1.0);
    
}
// #version 330

// uniform float iTime;
// uniform vec2  iResolution;

// uniform float u_bpm;
// uniform float u_volume;
// uniform float u_flux;
// uniform bool  u_beat;
// uniform float u_centroid;
// uniform float u_kurtosis;

// in vec2 v_uv;
// out vec4 f_colour;


// // --- Simple grid function ---
// float grid(vec2 uv, float thickness)
// {
//     vec2 g = abs(fract(uv) - 0.5);
//     float line = min(g.x, g.y);
//     return 1.0 - smoothstep(thickness, thickness + 0.01, line);
// }


// void main()
// {
//     // Normalized coords
//     vec2 uv = (v_uv * 2.0 - 1.0);
//     uv.x *= iResolution.x / iResolution.y;

//     vec3 background = vec3(0.0, 0.02, 0.1);
//     vec3 col = background;

//     // --- BPM timing ---
//     float bps = u_bpm / 60.0;
//     float beatTime = iTime * bps;
//     float beatPhase = fract(beatTime);

//     // --- Beat shaping (kick envelope) ---
//     float kick = exp(-beatPhase * 10.0);

//     // Optional: extra punch if CPU beat detected
//     float beatBoost = u_beat ? 1.0 : 0.0;
//     kick += beatBoost;

//     if (uv.y < 1.0)
//     {
//         // Perspective warp
//         uv.y = 3.0 / (abs(uv.y) + 0.001);

//         // --- BPM synced forward motion ---
//         uv.y += beatTime * 0.5;

//         // --- Volume → stretch ---
//         uv.x *= uv.y * (1.0 + u_volume * 2.0);

//         // --- Beat pulse → big distortion ---
//         uv.x *= (1.0 + kick * 2.0);

//         // --- Flux → jitter ---
//         uv.x += sin(uv.y * 10.0 + iTime * 5.0) * u_flux * 0.2;

//         // Grid
//         float thickness = 0.02 + u_volume * 0.05 + kick * 0.05;
//         float gridVal = grid(uv, thickness);

//         // --- Kurtosis → sharpness ---
//         gridVal = pow(gridVal, 1.0 + u_kurtosis * 2.0);

//         // --- Color from audio ---
//         vec3 gridColor = mix(
//             vec3(0.0, 0.2, 1.0),   // base blue
//             vec3(0.3, 0.8, 1.0),   // brighter cyan
//             u_centroid
//         );

//         // --- Apply intensity ---
//         float intensity = (0.5 + u_volume * 1.5 + kick * 2.0);
//         col = mix(col, gridColor, gridVal * 1.0);
//     }

//     // --- Global glow ---
//     col += u_volume * 0.2 + kick * 0.3;

//     f_colour = vec4(col, 1.0);
// }