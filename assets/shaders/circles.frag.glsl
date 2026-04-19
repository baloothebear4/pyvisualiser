#version 330 core

out vec4 FragColor;

in vec2 TexCoords; // Interpolated texture coordinates from vertex shader

uniform float time; // Uniform variable to animate the lines

void main()
{
    float centerX = 0.5;
    float centerY = 0.5;
    float lineWidth = 0.01;
    
    // Calculate distance from center
    float dist = length(TexCoords - vec2(centerX, centerY));
    
    // Create a shifting effect using time
    float shiftFactor = cos(TexCoords.x * 30.0 + time) + sin(TexCoords.y * 
30.0 + time);
    
    // Adjust the distance to create lines at specific intervals
    dist += shiftFactor * lineWidth;
    
    // Set color based on the distance from the center
    if (dist < 1.0)
    {
        vec3 blueColor = vec3(0.0, 0.2, 0.8);
        FragColor = vec4(blueColor, 1.0);
    }
    else
    {
        FragColor = vec4(0.0, 0.0, 0.0, 0.0); // Black for the background
    }
}