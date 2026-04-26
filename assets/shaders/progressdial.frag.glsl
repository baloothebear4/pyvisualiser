#version 330

in vec2 v_uv;
out vec4 f_color;

uniform float u_progress;
uniform vec3  u_colour;   //Foreground colour
uniform vec2  iResolution;

#define PI 3.14159265

// Helpers
float random(vec2 st) {
    return fract(sin(dot(st.xy, vec2(12.9898,78.233))) * 43758.5453123);
}

float circle(vec2 uv, float radius, float width) {
    return smoothstep(radius, radius + width, length(uv));
}

// radius is the outer radius of the dial, width is the thickness of the ring, progress is a value from 0 to 1 indicating how much of the dial is filled
float progressDial(vec2 uv, float radius, float width, float progress) {

    float angle = atan(uv.x, uv.y) / (2.0 * PI) + 0.5; // Normalize angle to [0,1]
    float spread = 0.01; // Adjust this for a thicker or thinner dial
    float t = iTime;

    // Calculate distance from center and create a ring effect
    float dist     = length(uv);
    float dial     = step(angle, progress); // +0.25 to start from the top (12 o'clock position)
    float ringMask = smoothstep(spread, 0.0, abs(dist - (radius - width/2.0)) - width/2.0);

    return ringMask * dial;

}

float ring(vec2 uv, float radius, float width) {
    // Calculate distance from center and create a ring effect
    float dist    = (length(uv) - radius); // Modulate with progressDial for dynamic effect

    return 1.0-smoothstep(width, width + 0.01, abs(dist));
}

void main()
{
    vec2 uv = (v_uv * 2.0 - 1.0);
    uv.x *= iResolution.x / iResolution.y;

    float progress  = fract(u_progress);

    float radius    = 1.0;    // Outer radius of the dial
    float ringWidth = radius * 0.1;
    vec3  shadowColour = u_colour*0.4;  
 
    float dialPattern = progressDial(uv, radius, ringWidth, progress);

    vec3 shadow  = circle(uv, radius-ringWidth, ringWidth) * shadowColour; // 3D effect
    f_colour = vec4(u_colour+shadow, dialPattern);
}

// #version 330

// in vec2 v_uv;
// out vec4 f_colour;

// uniform float iTime;
// uniform vec2  iResolution;

// #define PI 3.14159265

// void main() {
//     // 1. Center and Aspect Ratio
//     vec2 uv = (v_uv * 2.0 - 1.0);
//     uv.x *= iResolution.x / iResolution.y;

//     // 2. Parameters
//     float progress = fract(iTime * 0.2);
//     float radius = 0.6;
//     float thickness = 0.1;
//     vec3 baseColor = vec3(0.0, 0.2, 0.8);

//     // 3. Polar Coordinates (rotated 90 deg to start at top)
//     // We swap x and y in atan to rotate the coordinate system
//     float angle = atan(uv.x, uv.y) / (PI * 2.0) + 0.5; 
    
//     // 4. Distance Field for the Ring
//     float d = length(uv);
//     float ringMask = smoothstep(0.01, 0.0, abs(d - radius) - thickness);
    
//     // 5. Progress Mask
//     // We use a small smoothstep here to anti-alias the tip of the progress bar
//     float progressMask = smoothstep(progress + 0.001, progress, angle);
    
//     // 6. The 3D "Bevel" Effect
//     // Calculate how far we are from the center of the ring's "pipe"
//     float pipeDepth = 1.0 - (abs(d - radius) / thickness);
//     pipeDepth = clamp(pipeDepth, 0.0, 1.0);
//     float bevel = sin(pipeDepth * PI * 0.5); // Curved profile
    
//     // 7. Lighting
//     float highlight = pow(bevel, 3.0) * 0.3; // Inner glow
//     float shadow = bevel * 0.5;              // Soft base color
    
//     // 8. Combine
//     vec3 backgroundRing = vec3(0.1); // Faint gray track
//     vec3 activeColor = (baseColor * shadow) + highlight;
    
//     // Layering: Background Track + Active Progress
//     vec3 finalRGB = backgroundRing * ringMask;
//     finalRGB = mix(finalRGB, activeColor, ringMask * progressMask);

//     f_colour = vec4(finalRGB, 1.0);
// }