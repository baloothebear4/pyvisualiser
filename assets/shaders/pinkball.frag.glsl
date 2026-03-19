// pinkball
//

#version 330
in vec2 v_uv;
out vec4 f_color;

uniform float iTime;
uniform vec2 iResolution;
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
    vec3 color1 = vec3(0.196, 0.255, 0.333); // Mid Blue
    vec3 color2 = vec3(0.706, 0.902, 1.0); // Light Blue
    
    return mix(color1, color2, d);
}
/* original pallette 
	return mix(vec3(0.2,0.7,0.9),vec3(1.,0.,1.),d);
}*/

vec2 rotate(vec2 p,float a){
	float c = cos(a);
    float s = sin(a);
    return p*mat2(c,s,-s,c);
}

float map(vec3 p){
    for( int i = 0; i<8; ++i){

        // change the spin speed with tempo
        float t = iTime*(0.1+0.01*u_kurtosis);
        p.xz =rotate(p.xz,t);
        p.xy =rotate(p.xy,t*1.89);
        p.xz = abs(p.xz);

        // Create a beat-synced pulse (0 to 1) that triggers on each beat
        // float beat = fract(iTime * u_bpm / 60.0);
        // Use a smooth impulse function for the pulse shape (sharp attack, slow decay)
        float pulse = 0.0;
        if(u_beat) {
            pulse = pow(1, 0.5) * exp(-5.0);
        }


        // Make the fractal larger with bass and pulse with the beat
        p.xz -= (0.5 - u_flux * 0.1 - pulse * 1.0);
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
        float brightness = 500.0 - u_volume * 200.0;
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
    ro.xz = rotate(ro.xz,iTime);
    vec3 cf = normalize(-ro);
    vec3 cs = normalize(cross(cf,vec3(0.,1.,0.)));
    vec3 cu = normalize(cross(cf,cs));
    
    vec3 uuv = ro+cf*3. + uv.x*cs + uv.y*cu;
    
    vec3 rd = normalize(uuv-ro);
    
    vec4 col = rm(ro,rd);
    
    f_color = vec4(col.rgb, 1.0);
}
