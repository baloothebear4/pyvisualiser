#version 330

in vec2 v_uv;
out vec4 f_color;

uniform float iTime;
uniform vec2  iResolution;



uniform float time; // Uniform variable to animate the lines

void main()
{
    float centerX = 0.5;
    float centerY = 0.5;
    float lineWidth = 0.01;
    
    // Calculate distance from center
    float dist = length(v_uv - vec2(centerX, centerY));
    
    // Create a shifting effect using time
    float shiftFactor = cos(v_uv.x * 30.0 + iTime) + sin(v_uv.y * 30.0 + iTime);
    
    // Adjust the distance to create lines at specific intervals
    dist += shiftFactor * lineWidth;
    
    // Set color based on the distance from the center
    if (dist < 1.0)
    {
        vec3 blueColor = vec3(0.0, 0.2, 0.8);
        f_colour = vec4(blueColor, 1.0);
    }
    else
    {
        f_colour = vec4(0.0, 0.0, 0.0, 0.0); // Black for the background
    }
}