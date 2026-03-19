// SpiralClouds
//
/*
    490->473 by @jolle (and easier to read now :)
    
    ty!! :D
*/
#version 330

uniform float iTime;
uniform vec2 iResolution;
uniform float u_vu;    // Volume level (0.0 to 1.0)
uniform float u_bass;  // Bass energy (0.0 to ~1.0)

void mainImage(out vec4 o, vec2 u) {
    float a,e,i,s,d,t = iTime;
    vec3  p = iResolution;    
    
    // scale coords, camera movement
    u = (u+u-p.xy)/p.y;
    
    u +=  cos(t*vec2(.4, .3))*.3;
    
    vec3 D = normalize(vec3(u, 1));
    for(o*=i; i++<1e2 && d < 1.5e2;
        
        // accumulate distance
        d += s = min(.15+.12*abs(s), e=max(.8*e,.001)),

        // accumulate color
        o += 1e1*vec4(6,2,1,0)/e + 1./s
    )
        
        // noise loop start, march
        for (
            // raymarch position
            p = D*d,
            
            // move forward
            p.z += t*4.,

            // squiggly line along z
            e = length(p.xy -  sin(p.z / 12. + vec2(0, 1.57))*12.) - .4,

            // spin by t, twist by p.z
            p.xy *= mat2(cos(p.z/7e1+vec4(0,33,11,0))),
            
            // 2 planes 32 units apart
            s = 32. - abs(p.y),
            
            // noise loop params
            a = .01; a < 4.; a *= 3.
        )
            p *= .8,
            // apply noise
            s -= abs(dot(sin(.3*p.z+.2*t+p / a ), vec3(a+a)));
    
    // tanh tonemap, brightness
    o = tanh(o*o/length(u)/4e5+.1*dot(u,u));
}