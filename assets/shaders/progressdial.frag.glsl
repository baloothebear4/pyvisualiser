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


float ring(vec2 uv, float radius, float width) {
    // Calculate distance from center and create a ring effect
    float dist    = (length(uv) - radius); // Modulate with progressDial for dynamic effect

    return 1.0-smoothstep(width, width + 0.01, abs(dist));
}


float progressDial(vec2 uv, float radius, float thickness, float progress) {
    
    // 1. Get the angle (-PI to PI)
    float ang = atan(uv.x, uv.y);
    
    // 2. Map progress to radians, but centered around 0.0
    // This makes the start and end of the bar symmetrical
    float halfAngle = progress * PI;
    
    // 3. Rotate the UVs so the center of the progress bar is at angle 0
    // This simplifies the math: we just check if we are within 'halfAngle' of 0
    float currentAng = ang - halfAngle;
    
    // 4. Wrap the angle to stay within -PI to PI
    // This handles the 12 o'clock "jump" perfectly
    if (currentAng < -PI) currentAng += 2.0 * PI;
    if (currentAng >  PI) currentAng -= 2.0 * PI;

    // 5. Clamp the angle to the arc's range
    float clampedAngle = clamp(currentAng, -halfAngle, halfAngle);

    // 6. Calculate the nearest point using the adjusted angle
    // We add the halfAngle back to restore the 12 o'clock orientation
    float renderAngle = clampedAngle + halfAngle;
    vec2 nearestPoint = vec2(sin(renderAngle), cos(renderAngle)) * radius;

    // 7. Distance check for rounded caps
    float dist = distance(uv, nearestPoint);
    float capRadius = thickness * 0.5;

    return smoothstep(capRadius + 0.01, capRadius, dist);
}

void main()
{
    vec2 uv = (v_uv * 2.0 - 1.0);
    uv.x *= iResolution.x / iResolution.y;
    float t = iTime;
    float progress  = fract(u_progress);

    float radius    = 0.90;    // Outer radius of the dial
    float ringWidth = radius * 0.1;
    vec3  shadowColour   = u_colour*0.2;  
    vec3  backingColour  = u_colour*0.4; 
    vec3  progressColour = u_colour;
 
    float dialPattern = progressDial(uv, radius, ringWidth, progress);
    float backPattern = progressDial(uv, radius, ringWidth, 1.0);

    float shadow  = (circle(uv, radius-ringWidth, ringWidth) * backPattern) * 0.2; // 3D effect

    // Mixing
    // 0. Start with a transparent base
    vec4 finalColor = vec4(0.0);
    
    // Correct Mixing
    // We start with the backing color, then mix in the progress color 
    // based on the progress mask.
    vec3 finalRGB = mix(backingColour+shadow, progressColour+shadow*0.9, dialPattern);

    // Use backPattern for the alpha so the center remains transparent
    f_color = vec4(finalRGB, backPattern);

}

