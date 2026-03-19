#version 330
in vec2 v_uv;
out vec4 f_color;

uniform float iTime;
uniform vec2  iResolution;

// Audio Uniforms
uniform float u_volume;      
uniform float u_centroid;    
uniform float u_flux;        
uniform bool  u_beat;        
uniform float u_kurtosis;    

mat2 rot(float a) {
    float s = sin(a), c = cos(a);
    return mat2(c, -s, s, c);
}

// 1. THE GEOMETRY ENGINE (SDF)
float map(vec3 p) {
    // Spin the entire scene
    p.xz *= rot(iTime * 0.2);
    
    // Calculate Fracturing/Spiking based on Kurtosis
    // High Kurtosis = Tonal/Sharp. Low Kurtosis = Noisy/Rough.
    float noise_mode = smoothstep(0.1, 0.8, u_kurtosis);
    
    // Multi-frequency displacement
    float freq = 3.0 + (u_centroid * 4.0);
    float amp = 0.05 + (u_flux * 0.5);
    
    // Wave displacement (The "Liquid" part)
    float waves = sin(p.x * freq + iTime) * cos(p.y * freq + iTime) * sin(p.z * freq + iTime);
    
    // Spiky displacement (The "Fracture" part)
    // We use an absolute sin function to create sharp ridges
    float spikes = abs(sin(p.x * 10.0) * sin(p.y * 10.0) * sin(p.z * 10.0));
    
    // Mix between liquid and shattered based on Kurtosis
    float displacement = mix(waves, spikes, noise_mode) * amp;
    
    float sphere = length(p) - (0.6 + u_volume * 0.3);
    if(u_beat) sphere -= 0.05;

    // Floor at y = -1.5
    float floorDist = p.y + 1.5;
    
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

    vec3 background = vec3(0.0, 0.01, 0.03) * (1.0 - length(uv));
    vec3 color = background;

    if(t < 20.0) {
        vec3 p = ro + rd * t;
        vec3 n = getNormal(p);
        
        // Dynamic Hi-Fi Palette
        vec3 col_a = vec3(0.0, 0.1, 0.4); // Midnight Blue
        vec3 col_b = vec3(0.2, 0.8, 1.0); // Electric Cyan
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
            
            // Beat flash core
            if(u_beat) color += vec3(0.2, 0.4, 0.5);
        }
    }

    // Gamma and Bloom
    color = smoothstep(-0.1, 1.1, color);
    f_color = vec4(pow(color, vec3(0.8)), 1.0);
}