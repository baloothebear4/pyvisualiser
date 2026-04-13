'''
Mar 2026 Baloothebear4 v1

Backgrounds and fundemental and core to the whole look and feel. They deserve their own shaders and focus


'''

from  pyvisualiser.core.framecore import Frame, Cache, Colour, get_asset_path
from  pyvisualiser.core.components import Image
from  pyvisualiser.core.render import RenderPass, RenderContext
from  pyvisualiser.styles.styles import *

import random
import moderngl, time
import pygame
import numpy as np


class Background:

    # background is a Str with a colour index eg 'background' or a Dict with the {path, opacity} for an image
    def __init__(self, frame, background=None):
        self.frame            = frame
        self.background_image = None
        self.background_base  = None
        self.background       = background

        # print("Background.__init__>", background, self.frame.colours.is_colour(self.background))

        if background is None:
            self.background       = None #Do nothing there is no background

        # --- OpenGL Background Style Support ---
        elif isinstance(background, BackgroundStyle):
            self.background_base = BackgroundBase(frame, background)

        # its a old API so default to new
        else:
            self.background_base = BackgroundBase(frame, BackgroundStyle())

        # print("Background.__init__> background is", self.background, self.frame.framestr())


    def make_image(self):
        if 'opacity'           not in self.background:   self.background.update({'opacity': Background.BACKGROUND_DEFAULT['opacity']})    

        # use artist or album art as the background
        if self.background['image'] in ('artist', 'album'):
            self.background_image = Image(self.frame, opacity=self.background['opacity'], target_wh=self.frame.abs_background()[-2:])  
            self.update_fn = self.BACKGROUND_ART[self.background['image']]['update_fn']  
        else:
            path = get_asset_path('backgrounds', self.background['image'])
            self.background_image = Image(self.frame, path=path, opacity=self.background['opacity'], target_wh=self.frame.abs_background()[-2:])
        # print("Background.__init__> background image created", self.background)    


    def per_frame_update(self, condition=True):
        pass


    def is_per_frame_update(self):
        return True

    def is_opaque(self):
        return

    def draw(self):
        if self.background is None: return
        
        # --- OpenGL Background Drawing ---
        self.background_base.update()
        self.background_base.draw()

  
    def __str__(self):
        return str(self.background)

#---- End Background -------     


class BackgroundLighting:
    """
    Manages the state of dynamic lighting elements based on audio input.
    """
    def __init__(self, style: BackgroundStyle):
        self.style = style
        self.reactive_intensity = 0.0
        self.peak_intensity = 0.0
        self.cloud_intensity = 0.0
        self.last_update = time.time()

    def update(self, audio_processor):
        if not audio_processor:
            return

        now = time.time()
        dt = now - self.last_update
        self.last_update = now

        # 1. Reactive Glow (General Volume)
        rg = self.style.reactive_glow
        if rg:
            if not isinstance(rg, ReactiveGlowStyle): rg = ReactiveGlowStyle()
            target = 0.0
            if hasattr(audio_processor, 'vu'):
                vu = audio_processor.vu['mono']
                if vu > rg.threshold:
                    # Normalize target based on threshold
                    target = (vu - rg.threshold) / max(0.001, (1.0 - rg.threshold))
            
            # Smooth transition
            rate = rg.attack if target > self.reactive_intensity else rg.decay
            self.reactive_intensity += (target - self.reactive_intensity) * rate

        # 2. Peak Accent (Beat Detection / High Energy)
        pa = self.style.peak_accent
        if pa:
            if not isinstance(pa, PeakAccentStyle): pa = PeakAccentStyle()
            # Simple beat detection logic: if VU is very high
            target_peak = 0.0
            if hasattr(audio_processor, 'vu') and audio_processor.vu['mono'] > pa.threshold:
                target_peak = 1.0
            
            rate = pa.attack if target_peak > self.peak_intensity else pa.decay
            self.peak_intensity += (target_peak - self.peak_intensity) * rate

        # 3. Clouds & Edge (Slow changing linked to overall volume)
        au = self.style.cloud or self.style.edge_light
        if au:
            # if not isinstance(cl, CloudStyle): cl = CloudStyle()
            # Simple beat detection logic: if VU is very high
            self.audio_vu = audio_processor.vu['mono'] * 1.0


class BackgroundSurface:
    """
    Manages static surface properties, like loading textures.
    """
    def __init__(self, style: BackgroundStyle, context: RenderContext):
        self.style = style
        self.context = context
        self.texture = None
        self._load_texture()

    def _load_texture(self):
        if not self.style.texture_path:
            return

        try:
            path = get_asset_path('backgrounds', self.style.texture_path)
            surface = pygame.image.load(path).convert_alpha()
            
            # Convert to ModernGL texture
            rgba_data = pygame.image.tostring(surface, "RGBA", False)
            self.texture = self.context.ctx.texture(surface.get_size(), 4, rgba_data)
            # self.texture.build_mipmaps()
            # self.texture.filter = (moderngl.LINEAR_MIPMAP_LINEAR, moderngl.LINEAR)
        except Exception as e:
            print(f"BackgroundSurface> Failed to load texture {self.style.texture_path}: {e}")


class BackgroundRenderPass(RenderPass):
    """
    A dedicated render pass that draws all background layers in a single, efficient shader.
    """
    def __init__(self, context: RenderContext, style: BackgroundStyle, surface: BackgroundSurface, lighting: BackgroundLighting):
        super().__init__(context)
        self.style = style
        self.surface = surface
        self.lighting = lighting
        self.start_time = time.time()
        self.viewport = None # (x, y, w, h) set by BackgroundBase before render

        self.prog = self.ctx.program(
            vertex_shader="""
                #version 330
                in vec2 in_vert;
                in vec2 in_uv;
                out vec2 v_uv;
                void main() {
                    gl_Position = vec4(in_vert, 0.0, 1.0);
                    v_uv = in_uv;
                }
            """,
            fragment_shader="""
                #version 330
                in vec2 v_uv;
                out vec4 f_colour;

                uniform vec3 u_colour;
                uniform float u_colour_opacity;
                uniform float u_time;
                // Texture
                uniform bool u_has_texture;
                uniform sampler2D u_texture;
                uniform float u_texture_opacity;

                // Vignette
                uniform float u_vignette_strength;
                uniform float u_vignette_radius;
                uniform float u_vignette_softness;

                // Noise
                uniform float u_noise_strength;

                // Ambient Glow
                uniform vec3 u_ambient_colour;
                uniform float u_ambient_opacity;
                uniform float u_ambient_radius;
                uniform float u_ambient_softness;

                // Reactive Glow
                uniform vec3 u_reactive_colour;
                uniform float u_reactive_intensity;

                // Peak Accent
                uniform vec3 u_peak_accent_colour;
                uniform float u_peak_intensity;

                // Starfield
                uniform float u_starfield_density;
                uniform float u_starfield_speed;

                // Cloud
                uniform float u_cloud_intensity;
                uniform float u_cloud_opacity;
                uniform bool u_cloud_enabled;

                // Panel Edge Lighting
                uniform vec3  u_edge_colour;
                uniform float u_edge_intensity;
                uniform float u_edge_width;
                uniform float u_edge_softness;
                uniform float u_edge_audio_reactivity;
                uniform float u_aspect_ratio;
                uniform float u_audio_vu;

                float random(vec2 st) {
                    return fract(sin(dot(st.xy, vec2(12.9898,78.233))) * 43758.5453123);
                }

                // simple smooth noise
                float hash(vec2 p) {
                    return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
                }

                float noise(vec2 p){
                    vec2 i = floor(p);
                    vec2 f = fract(p);

                    float a = hash(i);
                    float b = hash(i + vec2(1.0, 0.0));
                    float c = hash(i + vec2(0.0, 1.0));
                    float d = hash(i + vec2(1.0, 1.0));

                    vec2 u = f * f * (3.0 - 2.0 * f);

                    return mix(a, b, u.x) +
                        (c - a)* u.y * (1.0 - u.x) +
                        (d - b) * u.x * u.y;
                }

                //Edge lighting
                float edge_mask(vec2 uv) {

                    vec2 d = min(uv, 1.0 - uv);
                    d.x *= u_aspect_ratio;
                    
                    float edge_dist = min(d.x, d.y);

                    float edge = smoothstep(u_edge_width*0.1, 0.0, edge_dist);

                    edge = pow(edge, u_edge_softness);

                    return edge;
                }

                void main() {

                    // 0. Base colour
                    vec4 colour = vec4(u_colour, u_colour_opacity);
                    
                    // 1. Texture Layer
                    if (u_has_texture) {
                        vec4 texcolour = texture(u_texture, v_uv);
                        colour = mix(colour, texcolour, u_texture_opacity);
                    }
                    
                    // 2. Noise Layer (Film Grain)
                    if (u_noise_strength > 0.0) {
                        float noise = random(v_uv + u_time * 0.1);
                        // Overlay noise (centered around 0)
                        colour.rgb += (noise - 0.5) * u_noise_strength;
                    }
                    
                    // 3. Ambient Glow (Radial wash from bottom-center)
                    if (u_ambient_opacity > 0.0) {
                        float dist = distance(v_uv, vec2(0.5, 0.0)); // Bottom center
                        // Smoothstep for soft falloff
                        float glow = 1.0 - smoothstep(u_ambient_radius - u_ambient_softness, u_ambient_radius + u_ambient_softness, dist);
                        colour.rgb = mix(colour.rgb, u_ambient_colour, glow * u_ambient_opacity);
                        colour = mix(colour, vec4(u_ambient_colour, 1.0), glow * u_ambient_opacity);
                    }

                    // 4. Reactive Glow (Pulsing from center)
                    if (u_reactive_intensity > 0.0) {
                        float dist = distance(v_uv, vec2(0.5, 0.5));
                        float glow = 1.0 - smoothstep(0.0, 0.6, dist); // Fixed radius for now
                        colour.rgb += u_reactive_colour * glow * u_reactive_intensity;
                        float layer_a = glow * u_reactive_intensity;
                        colour.a = max(colour.a, layer_a);
                    }

                    // 5. Peak Accent (Flash)
                    if (u_peak_intensity > 0.0) {
                        // Subtle screen flash or edge highlight
                        float peak_dist = distance(v_uv, vec2(0.5, 0.5));
                        float peak_glow = (1.0 - smoothstep(0.05, 0.2, peak_dist)) * u_peak_intensity;
                        colour.rgb += u_peak_accent_colour * peak_glow;
                        colour.a = max(colour.a, peak_glow);
                    }

                    // 6. Vignette (Darken edges)
                    if (u_vignette_strength > 0.0) {
                        float d = distance(v_uv, vec2(0.5));
                        float v = smoothstep(u_vignette_radius, u_vignette_radius + u_vignette_softness, d);
                        colour.rgb = mix(colour.rgb, vec3(0.0), v * u_vignette_strength);
                    }

                    // 7. Starfield
                    if (u_starfield_density > 0.0) {
                        for (float i = 1.0; i <= 3.0; i++) {
                            float speed = u_starfield_speed * 0.05 * i;
                            vec2 shift = vec2(u_time * speed, 0.0);
                            vec2 uv_scaled = v_uv * 10.0 * i + shift;
                            vec2 id = floor(uv_scaled);
                            vec2 pos = fract(uv_scaled) - 0.5;
                            
                            float n = random(id);
                            
                            if (n > (1.0 - u_starfield_density * 0.002)) {
                                float size = 0.1 * n; 
                                float star = 1.0 - smoothstep(0.0, size, length(pos));
                                colour.rgb += vec3(star * n);
                            }
                        }
                    }
                    // 8. Cloud moving shape in centre of screen
                    if (u_cloud_opacity > 0.0) {

                        vec2 uv = v_uv;
                        vec2 center = uv - 0.5;
                        float dist = length(center);
                        float vignette = 1.0 - smoothstep(0.3, 0.9, dist);

                        float t = u_time * 0.05;

                        float n = noise(uv * 4.0 + vec2(t, t*0.3));
                        float n2 = noise(uv * 2.0 - vec2(t*0.2, t*0.5));

                        float blend = mix(n, n2, 0.5);

                        // contrast shaping and base intensity for debug visibility
                        float brightness = pow(blend, 1.5);
                        brightness = brightness * 0.6 + 0.15;
                        
                        // audio boost
                        float audio = pow(u_audio_vu, 0.5);
                        brightness += audio * 0.05;

                        // colour

                        // static colours used for test
                        //vec3 col1 = vec3(0.2, 0.4, 0.8);
                        //vec3 col2 = vec3(0.25, 0.70, 0.9);
                        // dynamic colours based off the base colour
                        vec3 col1 = max(u_colour * 4, vec3(0.01));
                        vec3 col2 = u_colour * 25 + 0.05;
                        float shaped = pow(blend, 1.4);
                        vec3 cloud_rgb = mix(col1, col2, shaped);
                        cloud_rgb *= brightness * vignette;

                        // Layer the cloud over the base colour
                        colour.rgb = mix(colour.rgb, cloud_rgb, u_cloud_opacity);

                    }

                    // 9. Panel Edge Lighting
                    if (u_edge_intensity > 0.0) {

                        float edge = edge_mask(v_uv);
                        
                        // subtle audio influence
                        float audio = pow(u_audio_vu, 0.5);
                        float audio_boost = 1.0 + audio * u_edge_audio_reactivity;

                        // match your "overdriven" pipeline
                        // vec3 edge_col = u_edge_colour * 20.0 + 0.05;
                        vec3 edge_col = mix(u_colour, vec3(1.0), 0.7);  // push toward white
                        edge_col = edge_col * 1.0 + 0.05;

                        colour.rgb += edge_col * edge * u_edge_intensity * audio_boost;
                    }


                    f_colour = colour;

                }
            """
        )
        self.quad_vao = self.ctx.simple_vertex_array(self.prog, context.get_quad_buffer(), 'in_vert', 'in_uv')
        
        # Initialize aspect ratio to 1.0 as a safe default
        if 'u_aspect_ratio' in self.prog:
            self.prog['u_aspect_ratio'].value = 1.0

    def render(self, **kwargs):
        # Ensure standard blending is used for background, preventing additive bleed from previous frames
        self.ctx.disable(moderngl.DEPTH_TEST)
        self.ctx.disable(moderngl.CULL_FACE)
        self.ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA
        
        # Handle Viewport for split-screen testing
        original_viewport = None
        if self.viewport:
            original_viewport = self.ctx.viewport
            self.ctx.viewport = self.viewport

            vw, vh = self.viewport[2], self.viewport[3]
            if 'u_aspect_ratio' in self.prog:
                self.prog['u_aspect_ratio'].value = float(vw / vh)
            # self.ctx.scissor = self.viewport # DEBUG: Disable Scissor to test FBO write access

        self.prog['u_time'].value = time.time() - self.start_time

        # We need a way to resolve theme colours to RGB floats (0-1).
        # We will inject a `colour_resolver` function into this pass from BackgroundBase.
        resolver = getattr(self, 'colour_resolver', lambda x: (0,0,0))

        # Base colour
        base_rgb = resolver(self.style.colour)
        self.prog['u_colour'].value = base_rgb
        if 'u_colour_opacity' in self.prog:
            op = float(self.style.colour_opacity) if self.style.colour is not None else 0.0
            self.prog['u_colour_opacity'].value = op

        # Texture
        if self.surface.texture:
            self.surface.texture.use(location=0)
            self.prog['u_texture'].value = 0
            self.prog['u_texture_opacity'].value = float(self.style.texture_opacity)
            self.prog['u_has_texture'].value = True
        else:
            # Bind dummy texture to avoid feedback loop (reading from FBO target)
            self.context.empty_texture.use(location=0)
            self.prog['u_texture'].value = 0
            self.prog['u_has_texture'].value = False

        # Vignette
        v = self.style.vignette
        if v:
            if not isinstance(v, VignetteStyle): v = VignetteStyle()
            self.prog['u_vignette_strength'].value = float(v.strength)
            self.prog['u_vignette_radius'].value = float(v.radius)
            self.prog['u_vignette_softness'].value = float(v.softness)
        else:
            self.prog['u_vignette_strength'].value = 0.0

        # Noise
        n = self.style.noise
        if n:
            if not isinstance(n, NoiseStyle): n = NoiseStyle()
            self.prog['u_noise_strength'].value = float(n.strength)
        else:
            self.prog['u_noise_strength'].value = 0.0

        # Ambient Glow
        ag = self.style.ambient_glow
        if ag:
            if not isinstance(ag, AmbientGlowStyle): ag = AmbientGlowStyle()
            self.prog['u_ambient_colour'].value = resolver(ag.colour)
            self.prog['u_ambient_opacity'].value = float(ag.opacity)
            self.prog['u_ambient_radius'].value = float(ag.radius)
            self.prog['u_ambient_softness'].value = float(ag.softness)
        else:
            self.prog['u_ambient_opacity'].value = 0.0

        # Reactive Glow
        rg = self.style.reactive_glow
        if rg:
            if not isinstance(rg, ReactiveGlowStyle): rg = ReactiveGlowStyle()
            self.prog['u_reactive_colour'].value = resolver(rg.colour)
            self.prog['u_reactive_intensity'].value = self.lighting.reactive_intensity
        else:
            self.prog['u_reactive_intensity'].value = 0.0

        # Peak Accent
        pa = self.style.peak_accent
        if pa:
            if not isinstance(pa, PeakAccentStyle): pa = PeakAccentStyle()
            self.prog['u_peak_accent_colour'].value = resolver(pa.colour)
            self.prog['u_peak_intensity'].value = self.lighting.peak_intensity
        else:
            self.prog['u_peak_intensity'].value = 0.0

        # Starfield
        sf = self.style.starfield
        if sf:
            if not isinstance(sf, StarfieldStyle): sf = StarfieldStyle()
            self.prog['u_starfield_density'].value = float(sf.density)
            self.prog['u_starfield_speed'].value = float(sf.speed)
        else:
            self.prog['u_starfield_density'].value = 0.0

        # Cloud
        cloud = self.style.cloud
        if cloud:
            if not isinstance(cloud, CloudStyle): cloud = CloudStyle()
            if 'u_cloud_intensity' in self.prog:
                self.prog['u_audio_vu'].value = self.lighting.audio_vu
            if 'u_cloud_opacity' in self.prog:
                self.prog['u_cloud_opacity'].value = cloud.opacity

        else:
            if 'u_cloud_intensity' in self.prog:
                self.prog['u_cloud_intensity'].value = 0.0
            if 'u_cloud_opacity' in self.prog:
                self.prog['u_cloud_opacity'].value = 0.0

        # Panel Edge lighting
        edge_style = self.style.edge_light

        if edge_style:

            self.prog['u_edge_intensity'].value = edge_style.intensity
            self.prog['u_edge_width'].value = edge_style.width
            self.prog['u_edge_softness'].value = edge_style.softness
            self.prog['u_edge_audio_reactivity'].value = edge_style.audio_reactivity
            self.prog['u_audio_vu'].value = self.lighting.audio_vu
        else:
            self.prog['u_edge_intensity'].value = 0.0


        # print(f"  BackgroundRenderPass> Drawing Quad... Program: {self.prog.glo}")
        self.quad_vao.render(moderngl.TRIANGLE_STRIP)
        # print("  BackgroundRenderPass> Draw complete.")

        # Restore viewport
        if original_viewport:
            self.ctx.viewport = original_viewport

class BackgroundBase:
    """
    The main public-facing class for the background system.
    It holds the style, manages state, and provides the render pass to the compositor.
    """
    def __init__(self, frame, style: BackgroundStyle):
        self.frame = frame
        self.style = style
        self.engine = frame.platform.gfx_driver # Access to GL context via GraphicsDriverGL
        
        # Ensure we are on an OpenGL platform
        if not hasattr(self.engine, 'render_context'):
            print("BackgroundBase> Error: OpenGL Backgrounds require GraphicsDriverGL.")
            return

        self.lighting    = BackgroundLighting(style)
        self.surface     = BackgroundSurface(style, self.engine.render_context)
        self.render_pass = BackgroundRenderPass(self.engine.render_context, style, self.surface, self.lighting)
        
        # Inject colour resolver into render pass
        self.render_pass.colour_resolver = self._resolve_colour

    def _resolve_colour(self, colour_name):
        """Helper to convert theme colour names to (r,g,b) floats"""
        if not colour_name: return (0.0, 0.0, 0.0)
        # Use Frame's Colour object to lookup
        # Colour.get returns (r,g,b) or (r,g,b,a) 0-255 integers
        col = self.frame.colours.get(colour_name)
        return tuple(c / 255.0 for c in col[:3])

    def update(self):
        # Update lighting state based on audio
        self.lighting.update(self.frame.platform)

    def draw(self):
        # Register the render pass with the compositor for this frame
        if hasattr(self.engine, 'compositor'):
            # Calculate viewport for this frame
            # abs_rect returns (x, y, w, h) in Pygame coords (Top-Left origin)
            # BUT Frame.abs_rect() is designed to return GL-compatible coordinates (x, y_bottom, w, h)
            # because it does: screen_h - (y0 + h)
            x, y, w, h = self.frame.abs_rect()
            
            viewport = (int(x), int(y), int(w), int(h))
            # Convert Pygame Y (Top-Left) to OpenGL Y (Bottom-Left)
            # GL_Y = ScreenHeight - (Pygame_Y + Height)
            screen_h = self.frame.platform.H
            gl_y = screen_h - (y + h)
            
            viewport = (int(x), int(gl_y), int(w), int(h))
            
            # DEBUG: Trace coordinate calculation
            # print(f"Background.draw> Frame: {type(self.frame).__name__} Abs: ({x}, {y}, {w}, {h}) -> GL Viewport: {viewport} (Screen H: {self.frame.platform.H})")
            # print(f"Background.draw> Frame: {type(self.frame).__name__} Abs: ({x}, {y}, {w}, {h}) -> GL Viewport: {viewport} (Screen H: {screen_h})")
            
            self.render_pass.viewport = viewport
            self.engine.compositor.add_pre_pass(self.render_pass)


class ParticleSystem:
    def __init__(self, frame, config):
        self.frame = frame
        self.count = config.get('count', 50)
        self.colour = config.get('colour', 'light')
        self.speed = config.get('speed', 1.0)
        self.size  = config.get('size', 2)
        self.softness = config.get('softness', 0.5)
        self.react_to_music = config.get('react_to_music', True)
        self.particles = []
        
        for _ in range(self.count):
            self.particles.append(self._reset_particle(start_random=True))
            
    def _reset_particle(self, start_random=False):
        w, h = self.frame.abs_wh
        x = random.randint(0, int(w))
        y = random.randint(0, int(h)) if start_random else 0 # Start at bottom
        
        # Float up with some drift
        vx = (random.random() - 0.5) * self.speed
        vy = (random.random() * self.speed) + 0.5
        
        life = random.randint(50, 200)
        return [x, y, vx, vy, life, life] # x, y, vx, vy, life, max_life

    def draw(self):
        w, h = self.frame.abs_wh
        origin_x, origin_y = self.frame.abs_origin()
        
        col = self.frame.colours.get(self.colour)
        
        speed_mult = 1.0
        if self.react_to_music and hasattr(self.frame.platform, 'vu'):
            vu = self.frame.platform.vu['mono']
            # Scale speed between 1x and 4x based on volume
            speed_mult = 1.0 + (vu * 3.0)

        for p in self.particles:
            # Update (Frame coords: 0,0 is bottom-left)
            p[0] += p[2] * speed_mult
            p[1] += p[3] * speed_mult
            p[4] -= 1
            
            # Reset if out of bounds or dead
            if p[1] > h or p[4] <= 0 or p[0] < 0 or p[0] > w:
                new_p = self._reset_particle()
                p[:] = new_p[:] # Update in place
            
            # Draw
            alpha = int(255 * (p[4] / p[5]))
            if len(col) == 3:
                draw_col = list(col) + [alpha]
            else:
                draw_col = list(col[:3]) + [alpha]
                
            # Convert Frame (Bottom-Left) to Pygame/GL (Top-Left) for drawing
            draw_x = origin_x + p[0]
            draw_y = origin_y + (h - p[1])
            
            rect = (draw_x, draw_y, self.size, self.size)
            self.frame.platform.renderer.draw_rect(draw_col, rect, softness=self.softness)            