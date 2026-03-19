// pinkball
//

#version 330
in vec2 v_uv;
out vec4 f_color;

uniform float iTime;
uniform vec2 iResolution;
uniform float u_fold_offset;
uniform float u_speed_mult;

// vec3 palette(float d){
//     return mix(vec3(0.2,0.7,0.9),vec3(1.,0.,1.),d);
// }

// vec2 rotate(vec2 p,float a){
//     float c = cos(a);
//     float s = sin(a);
//     return p*mat2(c,s,-s,c);
// }

// float map(vec3 p){
//     for( int i = 0; i<8; ++i){ 
//         float t = iTime * u_speed_mult;
//         p.xz =rotate(p.xz,t);
//         p.xy =rotate(p.xy,t*1.89);
//         p.xz = abs(p.xz);
//         p.xz -= u_fold_offset;
//     }
//     return dot(sign(p),p)/5.0;
// }

// vec4 rm (vec3 ro, vec3 rd){
//     float t = 0.;
//     vec3 col = vec3(0.);
//     float d;
//     for(float i =0.; i<64.; i++){ 
//         vec3 p = ro + rd*t;
//         d = map(p)*.5;
//         if(d<0.02){
//             break;
//         }
//         if(d>100.){
//             break;
//         }
//         col+=palette(length(p)*.1)/(400.*(d));
//         t+=d;
//     }
//     return vec4(col,1./(d*100.));
// }

// Original Pinkball

vec3 palette(float d){
	return mix(vec3(0.2,0.7,0.9),vec3(1.,0.,1.),d);
}

vec2 rotate(vec2 p,float a){
	float c = cos(a);
    float s = sin(a);
    return p*mat2(c,s,-s,c);
}

float map(vec3 p){
    for( int i = 0; i<8; ++i){
        float t = iTime*0.2;
        p.xz =rotate(p.xz,t);
        p.xy =rotate(p.xy,t*1.89);
        p.xz = abs(p.xz);
        p.xz-=.5;
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
        //col+=vec3(0.6,0.8,0.8)/(400.*(d));
        col+=palette(length(p)*.1)/(400.*(d));
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




// void mainImage( out vec4 fragColor, in vec2 fragCoord )
// {
//     vec2 uv = (fragCoord-(iResolution.xy/2.))/iResolution.x;
// 	vec3 ro = vec3(0.,0.,-50.);
//     ro.xz = rotate(ro.xz,iTime);
//     vec3 cf = normalize(-ro);
//     vec3 cs = normalize(cross(cf,vec3(0.,1.,0.)));
//     vec3 cu = normalize(cross(cf,cs));
    
//     vec3 uuv = ro+cf*3. + uv.x*cs + uv.y*cu;
    
//     vec3 rd = normalize(uuv-ro);
    
//     vec4 col = rm(ro,rd);
    
    
//     fragColor = col;
// }
