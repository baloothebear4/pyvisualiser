// pinkball
//

#version 330
in vec2 v_uv;
out vec4 f_color;

uniform float iTime;
uniform vec2 iResolution;
uniform vec3  u_colour; // To align the colours for dynamic theming
uniform float u_vu;    // Volume level (0.0 to 1.0)
uniform float u_bass;  // Bass energy (0.0 to ~1.0)
uniform float u_bpm;   // Beats Per Minute

// Audio Uniforms
uniform float u_volume;      // Overall loudness
uniform float u_centroid;    // Brightness/Color (0-1)
uniform float u_flux;        // Spectral change (energy spikes)
uniform bool  u_beat;        // Pulse trigger
uniform float u_kurtosis;    // Tonal vs Noise (Sharpness)


// approximating hifi theme colours
vec3 palette(float d){
    // Define a palette that approximates the hifi theme
	// vec3 color1 = vec3(1.0, 0.78, 0.55); // Light Cream
	// vec3 color2 = vec3(0.55, 0.78, 1.00); // Light Blue
    vec3 color1 = u_colour*0.7;
    vec3 color2 = u_colour*1.0;
    
    return mix(color1, color2, d);
}

vec2 rotate(vec2 p,float a){
	float c = cos(a);
    float s = sin(a);
    return p*mat2(c,s,-s,c);
}

float map(vec3 p){
    // STABILIZATION: Use a constant low base speed for iTime. 
    // We use audio to shift the 'phase' (position) rather than the speed.
    // This prevents the "jumping" effect when u_bpm or u_volume jitters.
    float rotation_phase = (u_bpm * 0.1) + (u_volume * 0.05);
    
    // DAMPENING: Reduce the beat pulse impact significantly.
    float beat_pulse = u_beat ? 0.01 : 0.0;

    for( int i = 0; i<8; ++i){
        // Constant slow rotation + a subtle audio-reactive phase nudge
        float t = iTime * 0.15 + rotation_phase;
        p.xz = rotate(p.xz, t);
        p.xy = rotate(p.xy, t * 1.89);
        
        // Use a very small fraction of kurtosis. 
        // We also use u_volume to ensure it only "flips" when there is actual sound.
        p.xz = abs(p.xz) - (u_kurtosis * u_volume * 0.02);
        
        // Damping the flux to prevent high-frequency jitter.
        p.xz -= (0.5 - (u_flux * 0.01) - beat_pulse);
    }
	return dot(sign(p),p)/5.;
}

vec4 rm (vec3 ro, vec3 rd){
    float t = 0.;
    vec3 col = vec3(0.);
    float d;
    for(float i =0.; i<64.; i++){
		vec3 p = ro + rd*t;
        d = map(p)*.5;
        if(d<0.02){
            break;
        }
        if(d>100.){
        	break;
        }
        // Pulse brightness with overall volume. A smaller divisor = brighter glow.
        float brightness = 900.0 - clamp(u_volume, 0.0, 1.0) * 400.0;
        col+=palette(length(p)*.1)/(brightness*(d));
        t+=d;
    }
    return vec4(col,1./(d*100.));
}

void main() {    
    
    // Convert from 0-1 v_uv to centered, aspect-corrected coordinates
    
    vec2 uv = (v_uv * 2.0 - 1.0);
    uv.x *= iResolution.x / iResolution.y;
    
    vec3 ro = vec3(0.,0.,-15.);
    // Slow down camera rotation to match the luxury preamp aesthetic.
    ro.xz = rotate(ro.xz, iTime * 0.1);
    vec3 cf = normalize(-ro);
    vec3 cs = normalize(cross(cf,vec3(0.,1.,0.)));
    vec3 cu = normalize(cross(cf,cs));
    
    vec3 uuv = ro+cf*3. + uv.x*cs + uv.y*cu;
    
    vec3 rd = normalize(uuv-ro);
    
    vec4 col = rm(ro,rd);
    
    // f_color = vec4(col.rgb, 1.0);
    // IMPROVED BACKGROUND: Replace the "black void" with a subtle atmosphere.
    // A radial vignette centered on the ball creates depth and focus.
    float dist = length(uv);
    float vignette = smoothstep(1.6, 0.0, dist);
    
    // Base atmosphere using the theme colour, subtly pulsing with the music volume
    vec3 bg = u_colour * (0.02 + u_volume * 0.01) * vignette;
    
    // Add a subtle "horizon" lift at the bottom to ground the object
    bg += u_colour * 0.015 * smoothstep(0.2, -1.2, uv.y) * vignette;

    f_color = vec4(col.rgb + bg, 1.0);
}
