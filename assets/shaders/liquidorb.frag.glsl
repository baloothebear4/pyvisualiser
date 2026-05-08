#version 330
in vec2 v_uv;
out vec4 f_color;

uniform float iTime;
uniform vec2  iResolution;
uniform vec3  u_colour; // To align the colours for dynamic theming

// Audio Uniforms
uniform float u_volume;      
uniform float u_centroid;    
uniform float u_flux;        
uniform bool  u_beat;        
uniform float u_kurtosis;    
uniform float u_bpm;         

mat2 rot(float a) {
    float s = sin(a), c = cos(a);
    return mat2(c, -s, s, c);
}

// 1. THE GEOMETRY ENGINE (SDF)
float map(vec3 p) {
    // Calculate floor distance using original world-space coordinates
    float floorDist = p.y + 1.5;

    // Create a local coordinate copy for the orb to isolate its rotation
    vec3 q = p;

    // Synchronize rotation to BPM. 
    float beat_step = u_bpm * 60.0;
    
    // Rotate based on tempo + dynamic volume-based "kick"
    float rot_speed = iTime * beat_step * 0.4 + (u_volume * 0.5);
    q.xz *= rot(rot_speed);
    q.xy *= rot(rot_speed * 0.3); // Add a subtle vertical tumble for a 3D liquid feel
    
    // Calculate Fracturing/Spiking based on Kurtosis
    // High Kurtosis = Tonal/Sharp. Low Kurtosis = Noisy/Rough.
    float noise_mode = smoothstep(0.1, 0.8, u_kurtosis);
    
    // Multi-frequency displacement
    float freq = 3.0 + (u_centroid * 4.0);
    float amp = 0.05 + (u_flux * 0.7);
    
    // Wave displacement (The "Liquid" part) - modulated by volume for responsiveness
    float displacement_time = iTime * (1.0 + u_volume * 2.0);
    float waves = sin(q.x * freq + displacement_time) * 
                  cos(q.y * freq + displacement_time) * 
                  sin(q.z * freq + displacement_time);
    
    // Spiky displacement (The "Fracture" part)
    // We use an absolute sin function to create sharp ridges
    float spikes = abs(sin(q.x * 10.0) * sin(q.y * 10.0) * sin(q.z * 10.0));
    
    // Mix between liquid and shattered based on Kurtosis
    float displacement = mix(waves, spikes, noise_mode) * amp;
    
    float sphere = length(q) - (0.6 + u_volume * 0.3);
    if(u_beat) sphere -= 0.05;
    
    return min(sphere + displacement, floorDist);
}

// 2. CALCULATE NORMALS (For lighting and reflections)
vec3 getNormal(vec3 p) {
    vec2 e = vec2(0.001, 0.0);
    return normalize(vec3(
        map(p + e.xyy) - map(p - e.xyy),
        map(p + e.yxy) - map(p - e.yxy),
        map(p + e.yyx) - map(p - e.yyx)
    ));
}

void main() {
    vec2 uv = (v_uv * 2.0 - 1.0);
    uv.x *= iResolution.x / iResolution.y;
    
    vec3 ro = vec3(0, 0, -4.0); // Camera position
    vec3 rd = normalize(vec3(uv, 2.0)); // Ray direction
    
    float t = 0.0;
    for(int i = 0; i < 80; i++) {
        float d = map(ro + rd * t);
        if(d < 0.001 || t > 20.0) break;
        t += d;
    }

    vec3 background = vec3(0.0, 0.00, 0.0) * (1.0 - length(uv));
    vec3 color = background;

    if(t < 20.0) {
        vec3 p = ro + rd * t;
        vec3 n = getNormal(p);
        
        // Dynamic Hi-Fi Palette
        vec3 col_a = u_colour*0.5;
        vec3 col_b = u_colour*1.3;
        vec3 theme = mix(col_a, col_b, u_centroid);

        if(p.y < -1.49) {
            // FLOOR RENDERING
            // Calculate reflection ray
            vec3 refDir = reflect(rd, vec3(0, 1, 0));
            float rt = 0.1;
            float rd_dist = 0.0;
            // Short raymarch for reflection
            for(int j=0; j<30; j++) {
                rd_dist = map(p + refDir * rt);
                if(rd_dist < 0.01 || rt > 5.0) break;
                rt += rd_dist;
            }
            
            // Floor color + faint reflection of the orb
            color = col_a * 0.5; 
            if(rt < 5.0) color += theme * 0.3 * exp(-rt);
            
            // Add some "gloss" to the floor
            color *= smoothstep(4.0, 0.0, length(p.xz)); 
        } else {
            // ORB RENDERING
            float diffuse = max(dot(n, vec3(0.577)), 0.0);
            float spec = pow(max(dot(reflect(rd, n), vec3(0, 0, -1)), 0.0), 32.0);
            float rim = pow(1.0 - max(dot(n, -rd), 0.0), 3.0);
            
            color = theme * diffuse + spec * 0.5 + col_b * rim * (u_flux + 0.5);
            
            //Beat flash core
            if(u_beat) color += u_colour * 0.2;
        }
    }

    // Gamma and Bloom
    color = smoothstep(-0.1, 1.1, color);
    f_color = vec4(pow(color, vec3(0.8)), 1.0);
}