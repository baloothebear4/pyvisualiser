// Clouds
//
// Copyright Inigo Quilez, 2013 - https://iquilezles.org/
// I am the sole copyright owner of this Work. You cannot
// host, display, distribute or share this Work neither as
// is or altered, in any form including physical and
// digital. You cannot use this Work in any commercial or
// non-commercial product, website or project. You cannot
// sell this Work and you cannot mint an NFTs of it. You
// cannot use this Work to train AI models. I share this
// Work for educational purposes, you can link to it as
// an URL, proper attribution and unmodified screenshot,
// as part of your educational material. If these
// conditions are too restrictive please contact me.


// Volumetric clouds. Not physically correct in any way - 
// it does the wrong extintion computations and also
// works in sRGB instead of linear RGB color space. No
// shadows are computed, no scattering is computed. It is
// a volumetric raymarcher than samples an fBM and tweaks
// the colors to make it look good.
//
// Lighting is done with only one extra sample per raymarch
// step instead of using 3 to compute a density gradient,
// by using this directional derivative technique:
//
// https://iquilezles.org/articles/derivative


#version 330

uniform float iTime;
uniform vec2 iResolution;
uniform float u_vu;    // Volume level (0.0 to 1.0)
uniform float u_bass;  // Bass energy (0.0 to ~1.0)


// 0: sunset look
// 1: bright look
#define LOOK 1

// 0: one 3d texture lookup
// 1: two 2d texture lookups with hardware interpolation
// 2: two 2d texture lookups with software interpolation
#define NOISE_METHOD 1

// 0: no LOD
// 1: yes LOD
#define USE_LOD 1


mat3 setCamera( in vec3 ro, in vec3 ta, float cr )
{
	vec3 cw = normalize(ta-ro);
	vec3 cp = vec3(sin(cr), cos(cr),0.0);
	vec3 cu = normalize( cross(cw,cp) );
	vec3 cv = normalize( cross(cu,cw) );
    return mat3( cu, cv, cw );
}

// Procedural noise from https://www.shadertoy.com/view/4sfGDB
// This replaces the original texture-based noise.
vec3 hash3( vec3 p )
{
    p = vec3( dot(p,vec3(127.1,311.7, 74.7)),
			  dot(p,vec3(269.5,183.3,246.1)),
			  dot(p,vec3(113.5,271.9,124.6)));

	return -1.0 + 2.0*fract(sin(p)*43758.5453123);
}

float noise( in vec3 p )
{
    vec3 i = floor( p );
    vec3 f = fract( p );
	
	vec3 u = f*f*(3.0-2.0*f);

    return mix( mix( mix( dot( hash3( i + vec3(0.0,0.0,0.0) ), f - vec3(0.0,0.0,0.0) ), 
                          dot( hash3( i + vec3(1.0,0.0,0.0) ), f - vec3(1.0,0.0,0.0) ), u.x),
                     mix( dot( hash3( i + vec3(0.0,1.0,0.0) ), f - vec3(0.0,1.0,0.0) ), 
                          dot( hash3( i + vec3(1.0,1.0,0.0) ), f - vec3(1.0,1.0,0.0) ), u.x), u.y),
                mix( mix( dot( hash3( i + vec3(0.0,0.0,1.0) ), f - vec3(0.0,0.0,1.0) ), 
                          dot( hash3( i + vec3(1.0,0.0,1.0) ), f - vec3(1.0,0.0,1.0) ), u.x),
                     mix( dot( hash3( i + vec3(0.0,1.0,1.0) ), f - vec3(0.0,1.0,1.0) ), 
                          dot( hash3( i + vec3(1.0,1.0,1.0) ), f - vec3(1.0,1.0,1.0) ), u.x), u.y), u.z );
}

#if LOOK==0
float map( in vec3 p, int oct )
{
	vec3 q = p - vec3(0.0,0.1,1.0)*iTime;
    float g = 0.5+0.5*noise( q*0.3 );
    
	float f;
    f  = 0.50000*noise( q ); q = q*2.02;
    #if USE_LOD==1
    if( oct>=2 ) 
    #endif
    f += 0.25000*noise( q ); q = q*2.23;
    #if USE_LOD==1
    if( oct>=3 )
    #endif
    f += 0.12500*noise( q ); q = q*2.41;
    #if USE_LOD==1
    if( oct>=4 )
    #endif
    f += 0.06250*noise( q ); q = q*2.62;
    #if USE_LOD==1
    if( oct>=5 )
    #endif
    f += 0.03125*noise( q ); 
    
    f = mix( f*0.1-0.5, f, g*g );
        
    return 1.5*f - 0.5 - p.y;
}

const int kDiv = 1; // make bigger for higher quality
const vec3 sundir = normalize( vec3(1.0,0.0,-1.0) );

vec4 raymarch( in vec3 ro, in vec3 rd, in vec3 bgcol, in ivec2 px )
{
    // bounding planes	
    const float yb = -3.0;
    const float yt =  0.6;
    float tb = (yb-ro.y)/rd.y;
    float tt = (yt-ro.y)/rd.t;

    // find tigthest possible raymarching segment
    float tmin, tmax;
    if( ro.y>yt )
    {
        // above top plane
        if( tt<0.0 ) return vec4(0.0); // early exit
        tmin = tt;
        tmax = tb;
    }
    else
    {
        // inside clouds slabs
        tmin = 0.0;
        tmax = 60.0;
        if( tt>0.0 ) tmax = min( tmax, tt );
        if( tb>0.0 ) tmax = min( tmax, tb );
    }
    
    // Simple hash for procedural dithering, replaces texture lookup
    float hash( ivec2 p ) { return fract(sin(float(p.x*12345+p.y*54321))*12345.6789); }

    // dithered near distance
    float t = tmin + 0.1*hash(px);
    
    // raymarch loop
	vec4 sum = vec4(0.0);
    for( int i=0; i<190*kDiv; i++ )
    {
       // step size
       float dt = max(0.05,0.02*t/float(kDiv));

       // lod
       #if USE_LOD==0
       const int oct = 5;
       #else
       int oct = 5 - int( log2(1.0+t*0.5) );
       #endif
       
       // sample cloud
       vec3 pos = ro + t*rd;
       float den = map( pos,oct );
       if( den>0.01 ) // if inside
       {
           // do lighting
           float dif = clamp((den - map(pos+0.3*sundir,oct))/0.25, 0.0, 1.0 );
           vec3  lin = vec3(0.65,0.65,0.75)*1.1 + 0.8*vec3(1.0,0.6,0.3)*dif;
           vec4  col = vec4( mix( vec3(1.0,0.93,0.84), vec3(0.25,0.3,0.4), den ), den );
           col.xyz *= lin;
           // fog
           col.xyz = mix(col.xyz,bgcol, 1.0-exp2(-0.1*t));
           // composite front to back
           col.w    = min(col.w*8.0*dt,1.0);
           col.rgb *= col.a;
           sum += col*(1.0-sum.a);
       }
       // advance ray
       t += dt;
       // until far clip or full opacity
       if( t>tmax || sum.a>0.99 ) break;
    }

    return clamp( sum, 0.0, 1.0 );
}

vec4 render( in vec3 ro, in vec3 rd, in ivec2 px )
{
	float sun = clamp( dot(sundir,rd), 0.0, 1.0 );

    // background sky
    vec3 col = vec3(0.76,0.75,0.95);
    col -= 0.6*vec3(0.90,0.75,0.95)*rd.y;
	col += 0.2*vec3(1.00,0.60,0.10)*pow( sun, 8.0 );

    // clouds    
    vec4 res = raymarch( ro, rd, col, px );
    col = col*(1.0-res.w) + res.xyz;
    
    // sun glare    
	col += 0.2*vec3(1.0,0.4,0.2)*pow( sun, 3.0 );

    // tonemap
    col = smoothstep(0.15,1.1,col);
 
    return vec4( col, 1.0 );
}

#else


float map5( in vec3 p )
{    
    vec3 q = p - vec3(0.0,0.1,1.0)*iTime;    
    float f;
    f  = 0.50000*noise( q ); q = q*2.02;    
    f += 0.25000*noise( q ); q = q*2.03;    
    f += 0.12500*noise( q ); q = q*2.01;    
    f += 0.06250*noise( q ); q = q*2.02;    
    f += 0.03125*noise( q );    
    return clamp( 1.5 - p.y - 2.0 + 1.75*f, 0.0, 1.0 );
}
float map4( in vec3 p )
{    
    vec3 q = p - vec3(0.0,0.1,1.0)*iTime;    
    float f;
    f  = 0.50000*noise( q ); q = q*2.02;    
    f += 0.25000*noise( q ); q = q*2.03;    
    f += 0.12500*noise( q ); q = q*2.01;   
    f += 0.06250*noise( q );    
    return clamp( 1.5 - p.y - 2.0 + 1.75*f, 0.0, 1.0 );
}
float map3( in vec3 p )
{
    vec3 q = p - vec3(0.0,0.1,1.0)*iTime;    
    float f;
    f  = 0.50000*noise( q ); q = q*2.02;    
    f += 0.25000*noise( q ); q = q*2.03;    f += 0.12500*noise( q );    
    return clamp( 1.5 - p.y - 2.0 + 1.75*f, 0.0, 1.0 );
}
float map2( in vec3 p )
{    
    vec3 q = p - vec3(0.0,0.1,1.0)*iTime;    
    float f;
    f  = 0.50000*noise( q ); 
    q = q*2.02;    f += 0.25000*noise( q );;    
    return clamp( 1.5 - p.y - 2.0 + 1.75*f, 0.0, 1.0 );
}

const vec3 sundir = vec3(-0.7071,0.0,-0.7071);

// Simple hash for procedural dithering, replaces texture lookup
float hash( ivec2 p ) { return fract(sin(float(p.x*12345+p.y*54321))*12345.6789); }

#define MARCH(STEPS,MAPLOD) for(int i=0; i<STEPS; i++) { vec3 pos = ro + t*rd; if( pos.y<-3.0 || pos.y>2.0 || sum.a>0.99 ) break; float den = MAPLOD( pos ); if( den>0.01 ) { float dif = clamp((den - MAPLOD(pos+0.3*sundir))/0.6, 0.0, 1.0 ); vec3  lin = vec3(1.0,0.6,0.3)*dif+vec3(0.91,0.98,1.05); vec4  col = vec4( mix( vec3(1.0,0.95,0.8), vec3(0.25,0.3,0.35), den ), den ); col.xyz *= lin; col.xyz = mix( col.xyz, bgcol, 1.0-exp(-0.003*t*t) ); col.w *= 0.4; col.rgb *= col.a; sum += col*(1.0-sum.a); } t += max(0.06,0.05*t); }

vec4 raymarch( in vec3 ro, in vec3 rd, in vec3 bgcol, in ivec2 px )
{    
    vec4 sum = vec4(0.0);    
    float t = 0.05*hash(px);
    MARCH(40,map5);    
    MARCH(40,map4);    
    MARCH(30,map3);    
    MARCH(30,map2);    
    return clamp( sum, 0.0, 1.0 );
}

vec4 render( in vec3 ro, in vec3 rd, in ivec2 px )
{
    // background sky         
    float sun = clamp( dot(sundir,rd), 0.0, 1.0 );    
    vec3 col = vec3(0.6,0.71,0.75) - rd.y*0.2*vec3(1.0,0.5,1.0) + 0.15*0.5;    
    col += 0.2*vec3(1.0,.6,0.1)*pow( sun, 8.0 );    
    // clouds        
    vec4 res = raymarch( ro, rd, col, px );    
    col = col*(1.0-res.w) + res.xyz;        
    // sun glare        
    col += vec3(0.2,0.08,0.04)*pow( sun, 3.0 );    
    return vec4( col, 1.0 );
}

#endif
out vec4 f_color;
in vec2 v_uv;

void main(  )
{
    // Standard aspect-corrected coordinates from v_uv
    vec2 p = (v_uv * 2.0 - 1.0);
    p.x *= iResolution.x / iResolution.y;

    // Animate camera automatically since there is no mouse input
    vec2 m = vec2(iTime * 0.05, 0.4);

    // camera
    vec3 ro = 4.0*normalize(vec3(sin(3.0*m.x), 0.8*m.y, cos(3.0*m.x))) - vec3(0.0,0.1,0.0);
	vec3 ta = vec3(0.0, -1.0, 0.0);
    mat3 ca = setCamera( ro, ta, 0.07*cos(0.25*iTime) );
    // ray
    vec3 rd = ca * normalize( vec3(p.xy,1.5));

    f_color = render( ro, rd, ivec2(v_uv * iResolution.xy - 0.5) );
}
