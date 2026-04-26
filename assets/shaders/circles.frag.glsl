#version 330

in vec2 v_uv;
out vec4 f_color;

uniform float iTime;
uniform vec2  iResolution;

// Helpers
float random(vec2 st) {
    return fract(sin(dot(st.xy, vec2(12.9898,78.233))) * 43758.5453123);
}

void main()
{
    vec2 uv = (v_uv * 2.0 - 1.0);
    uv.x *= iResolution.x / iResolution.y;

    float lineWidth = 0.01;
    vec3 blueColor = vec3(0.0, 0.2, 0.8);    
    // Calculate distance from center
    float dist = length(0.0 - uv);
    
    // Create a shifting effect using time
    float shiftFactor = cos(v_uv.x * 30.0 + iTime) + sin(v_uv.y * 30.0 + iTime);
    
    // Adjust the distance to create lines at specific intervals
    dist += shiftFactor * lineWidth;
    
    float line = smoothstep(lineWidth, lineWidth + 0.01, abs(dist - 0.5)); // Create a line at distance 0.5 from the center
    // Set color based on the distance from the center
    // if (dist < 0.5 && dist > 0.48)
    if (line < 0.5)
    {

        f_colour = vec4(blueColor, 1.0);
    }
    else    
    {
        f_colour = vec4(0.0, 0.0, 0.0, 0.0); // Black for the background
    }


}
