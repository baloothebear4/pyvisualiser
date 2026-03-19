// Disco Sun Vortex
// SPDX-License-Identifier: CC-BY-NC-SA-4.0
// Copyright (c) 2026 @WorkingClassHacker
//[LICENSE] https://creativecommons.org/licenses/by-nc-sa/4.0/

// SPDX-License-Identifier: CC-BY-NC-SA-4.0
// Based on Abstract Shine by @Frosbyte
// Copyright (c) 2026 @Frostbyte

// Rotation matrix using cosine phase offsets.
// cos(a+33) ≈ -sin(a)
// cos(a+11) ≈  sin(a)
// compact 2D rotation without sin(). 
// Approximates sin within an invisible margin for animated graphics

#version 330

uniform float iTime;
uniform vec2 iResolution;
uniform float u_vu;    // Volume level (0.0 to 1.0)
in vec2 v_uv; // Passed from vertex shader, ranges from 0.0 to 1.0
uniform float u_bass;  // Bass energy (0.0 to ~1.0)

#define R(a) mat2(cos(a+vec4(0, 33, 11, 0)))
precision mediump float;
out vec4 fragColor;

// IQ`s continuous cosine palette (MIT)
// produces smooth, periodic color gradients
// https://www.shadertoy.com/view/ll2GD3


vec3 palette(float i){
    const vec3 a = vec3(0.50, 0.38, 0.26);  // base tone (warm midtone)
    const vec3 b = vec3(0.50, 0.35, 0.25);  // amplitude (vibrance)
    const vec3 c = vec3(1.00);              // frequency (cyclic complexity)
    const vec3 d = vec3(0.00, 0.12, 0.25);  // phase offsets (hue shift)
    return a + b * cos(6.2831853 * (c * i + d));
}

vec3 palette2(float i){

    const vec3 a = vec3(0.742702f, 0.908877f, 0.959831f);
    const vec3 b = vec3(-0.711000f, 0.275000f, -0.052000f);
    const vec3 c = vec3(1.000000f, 1.855000f, 1.000000f);
    const vec3 d = vec3(0.180000f, 0.091000f, 0.380000f);
    return a + b * cos(6.2831853f * (c * i + d));

}

out vec4 f_color;

void main(void)
{
    // pixel coordinate
    vec2 u = gl_FragCoord.xy;

    // normalized screen space centered at origin

	// (useful for screen-space modulation later)
    vec2 uv = (u - 0.5*iResolution.xy + 0.5) / iResolution.y;

    float i, s;
    float t = mod(iTime, 6.283185);

    vec3 p;

	// ray direction through pixel (camera ray)
    vec3 d = normalize(vec3(
        2.0 * u - iResolution.xy,
        iResolution.y
    ));

    // starting depth → creates forward motion
    p.z = t;

	vec4 f_color = vec4(0.0);
    for (fragColor *= i; i < 20.0; i++)
    {
        // depth-dependent rotation
        // produces corkscrew tunnel motion
        p.xy *= R(-p.z * 0.01 - t * 0.05);

        // base step size
        s = 0.6;

        // cylindrical confinement
        // creates tunnel boundary at radius ≈ 10
        s = max(s, 4.0 * (-length(p.xy) + 10.0));

        // organic deformation field
        // adds flow & energy patterns
        s += abs(
            p.y * 0.004 +                // slight tilt
            sin(t - p.x * 0.5) * 0.9 +  // traveling wave
            1.0                          // baseline thickness
        );

        // march ray forward
        p += d * s;

        // volumetric glow accumulation
        f_color += 1.0 / (s * 0.2);
    }

    // apply palette based on final ray distance
    // length(p) approximates depth travelled
    // gives depth-dependent coloration
    // divisor controls the palette scaling - try messing with it!
	// vec4 f_color = vec4(0.0);
    // try swapping to palette2 here!
    f_color *= vec4(palette(length(p)/(abs(sin(iTime*0.02)*50.)+6.0)), 1.0);

    // time-gated screen-space shimmer / interference layer
    f_color -= 20.0 *
        smoothstep(
            .001,
            abs(sin(iTime*5.0)), // pulsating dots, in a demo I would sync this to beat
            .7 - length(sin(uv*200.0)/1.5)-abs(uv.y)+.2   // high-frequency pattern
        );

	// brightness normalization
    f_color /= 0.5e2;

    // radial gradient
    float l = length(uv);

    // vignette
    f_color *= 1.2-l;

    // center glow

    f_color = mix(f_color, vec4(palette(l-.23).rgb, 1.0), 1.0-smoothstep(.01,.95,l));

    // soft highlight compression
    f_color = tanh(f_color+f_color);

	fragColor = f_color;
}