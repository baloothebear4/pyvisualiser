"""
Mar 2026 Baloothebear4 v1

Backgrounds and fundemental and core to the whole look and feel. They deserve their own shaders and focus


"""

from  pyvisualiser.core.framecore import Frame, Cache, Colour, get_asset_path
from  pyvisualiser.core.components import Image
from  pyvisualiser.core.render import RenderPass, RenderContext
from  pyvisualiser.styles.styles import *

import random
import moderngl, time
import pygame
import numpy as np

class ParticleSystem:
    def __init__(self, frame, config):
        self.frame = frame
        self.count = config.get('count', 50)
        self.color = config.get('colour', 'light')
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
        
        col = self.frame.colours.get(self.color)
        
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

class Background:

    BACKGROUND_DEFAULT    = {'colour':'background', 'image': 'particles.jpg', 'opacity': 255, \
                             'per_frame_update':False, 'glow': False} 
    BACKGROUND_IMAGE_PATH = '../backgrounds'


    # background is a Str with a colour index eg 'background' or a Dict with the {path, opacity} for an image
    def __init__(self, frame, background=None):
        self.frame            = frame
        self.background_image = None
        self.background       = {'colour':None}
        self.BACKGROUND_ART   = {  'album':  { 'update_fn': frame.platform.album_art,  'square' : False},
                                   'artist': { 'update_fn': frame.platform.artist_art, 'square' : False} }
        
        self.background_base = None

        # print("Background.__init__>", background, self.frame.colours.is_colour(self.background))

        if background is None:
            self.background       = None #Background.BACKGROUND_DEFAULT['colour']

        # --- NEW: OpenGL Background Style Support ---
        elif isinstance(background, BackgroundStyle):
            self.background_base = BackgroundBase(frame, background)
            self.background = {'type': 'opengl', 'per_frame_update': True}

        elif isinstance(background, dict) and 'image' in background:
            self.background.update(background)
            self.make_image()
            
        elif isinstance(background, dict) and any(key in background for key in ('colour','opacity','glow','particles')):
            self.background.update(background)
            if 'per_frame_update' not in self.background:   self.background.update({'per_frame_update': Background.BACKGROUND_DEFAULT['per_frame_update']}) 
            if 'opacity'          not in self.background:   self.background.update({'opacity': Background.BACKGROUND_DEFAULT['opacity']})   
            if 'glow'             not in self.background:   self.background.update({'glow': Background.BACKGROUND_DEFAULT['glow']})

            if 'particles' in self.background:
                self.particle_system = ParticleSystem(self.frame, self.background['particles'])
                self.background['per_frame_update'] = True


        # its a filename with no parameters ie a shortcut
        elif background.lower().endswith(('.jpg', '.png')):
            self.background.update({'image': background}) 
            self.make_image()

        # its a colour
        else:
            self.background.update({'colour':background, 'per_frame_update': Background.BACKGROUND_DEFAULT['per_frame_update'], 'opacity': Background.BACKGROUND_DEFAULT['opacity']})

        # print("Background.__init__> background is", self.background, self.frame.framestr())


    def make_image(self):
        if 'opacity'           not in self.background:   self.background.update({'opacity': Background.BACKGROUND_DEFAULT['opacity']})    
        if 'per_frame_update'  not in self.background:   self.background.update({'per_frame_update': Background.BACKGROUND_DEFAULT['per_frame_update']})    

        # use artist or album art as the background
        if self.background['image'] in ('artist', 'album'):
            self.background_image = Image(self.frame, opacity=self.background['opacity'], target_wh=self.frame.abs_background()[-2:])  
            self.update_fn = self.BACKGROUND_ART[self.background['image']]['update_fn']  
        else:
            path = get_asset_path('backgrounds', self.background['image'])
            self.background_image = Image(self.frame, path=path, opacity=self.background['opacity'], target_wh=self.frame.abs_background()[-2:])
        # print("Background.__init__> background image created", self.background)    


    def per_frame_update(self, condition=True):
        if self.background is not None: 
            self.background['per_frame_update']=condition
        else:
            # print("Background.per_frame_update> None background", self.background, self.frame.framestr() )  
            pass


    def is_per_frame_update(self):
        if self.background is None:
            return True
        else:
            return self.background['per_frame_update']

    def is_opaque(self):
        if self.background is None:
            return True  #if there is no background this is opaque!
        else:
            return self.background['opacity']<255

    def draw(self, perform_update=True):
        if self.background is None: return
        
        # --- NEW: OpenGL Background Drawing ---
        if self.background_base:
            self.background_base.update()
            self.background_base.draw()
            return

        BLACK = (0,0,0)

        # print("Background.draw> Test background", self.background, self.frame.framestr())
        if perform_update or self.background['per_frame_update']:


            if self.background.get('glow'):
                # Draw glow using OpenGL renderer
                rect_coords = self.frame.abs_background()
                c_name = self.background.get('colour')
                if c_name is None: c_name = 'background'
                
                colour = self.frame.colours.get(c_name)
                # Increase opacity for visibility and use additive blending
                opacity = self.background.get('opacity', 255) * 0.8
                
                if len(colour) == 3:
                    glow_col = list(colour) + [opacity]
                else:
                    glow_col = list(colour)
                    glow_col[3] = opacity
                
                self.frame.platform.renderer.draw_rect(glow_col, rect_coords, softness=1.5, additive=True)

            if self.background_image is None:
                if self.background['colour'] is None: return

                # 1. Get the coordinates and dimensions of the area to fill
                rect_coords = self.frame.abs_background()  # Should be (x, y, w, h)
                rect_w, rect_h = rect_coords[2:]

                colour = self.frame.colours.get(self.background['colour'])
                
                # Use the renderer to draw the rect directly with opacity
                # We need to append the opacity to the colour tuple if it's not already there
                if len(colour) == 3:
                    colour = list(colour) + [self.background['opacity']]
                elif len(colour) == 4:
                    colour = list(colour)
                    colour[3] = self.background['opacity']
                
                shadow = self.background.get('shadow')
                self.frame.platform.renderer.draw_rect(colour, rect_coords, shadow=shadow)

                if hasattr(self, 'particle_system'):
                    self.particle_system.draw()
 
            else:
                if self.background['image'] in ('artist', 'album'):
                    image_ref = self.update_fn()
                else:
                    image_ref =None

                self.background_image.draw(image_data=image_ref, coords=self.frame.abs_background()[:2]) 

            # print("Background.draw> ", self.background )  

        # print("Background.draw> draw ", perform_update, self.background['per_frame_update'], self.background, self.frame.framestr() )  
  


#---- End Background -------     


class BackgroundLighting:
    """
    Manages the state of dynamic lighting elements based on audio input.
    """
    def __init__(self, style: BackgroundStyle):
        self.style = style
        self.reactive_intensity = 0.0
        self.peak_intensity = 0.0
        self.last_update = time.time()

    def update(self, audio_processor):
        if not audio_processor:
            return

        now = time.time()
        dt = now - self.last_update
        self.last_update = now

        # 1. Reactive Glow (General Volume)
        if self.style.reactive_glow:
            target = 0.0
            if hasattr(audio_processor, 'vu'):
                vu = audio_processor.vu['mono']
                if vu > self.style.reactive_glow.threshold:
                    target = (vu - self.style.reactive_glow.threshold) / (1.0 - self.style.reactive_glow.threshold)
            
            # Smooth transition
            if target > self.reactive_intensity:
                self.reactive_intensity += (target - self.reactive_intensity) * self.style.reactive_glow.attack
            else:
                self.reactive_intensity += (target - self.reactive_intensity) * self.style.reactive_glow.decay

        # 2. Peak Accent (Beat Detection / High Energy)
        if self.style.peak_accent:
            # Simple beat detection logic: if VU is very high
            target_peak = 0.0
            if hasattr(audio_processor, 'vu') and audio_processor.vu['mono'] > 0.8:
                target_peak = 1.0
            
            self.peak_intensity += (target_peak - self.peak_intensity) * 0.2 # Fast attack/decay for beats


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
                out vec4 f_color;

                uniform vec3 u_base_color;
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
                uniform vec3 u_ambient_color;
                uniform float u_ambient_opacity;
                uniform float u_ambient_radius;
                uniform float u_ambient_softness;

                // Reactive Glow
                uniform vec3 u_reactive_color;
                uniform float u_reactive_intensity;

                // Peak Accent
                uniform vec3 u_peak_accent_color;
                uniform float u_peak_intensity;

                float random(vec2 st) {
                    return fract(sin(dot(st.xy, vec2(12.9898,78.233))) * 43758.5453123);
                }

                void main() {
                    vec4 color = vec4(u_base_color, 1.0);
                    
                    // 1. Texture Layer
                    if (u_has_texture) {
                        vec4 texColor = texture(u_texture, v_uv);
                        color = mix(color, texColor, u_texture_opacity);
                    }
                    
                    // 2. Noise Layer (Film Grain)
                    if (u_noise_strength > 0.0) {
                        float noise = random(v_uv + u_time * 0.1);
                        // Overlay noise (centered around 0)
                        color.rgb += (noise - 0.5) * u_noise_strength;
                    }
                    
                    // 3. Ambient Glow (Radial wash from bottom-center)
                    if (u_ambient_opacity > 0.0) {
                        float dist = distance(v_uv, vec2(0.5, 0.0)); // Bottom center
                        // Smoothstep for soft falloff
                        float glow = 1.0 - smoothstep(u_ambient_radius - u_ambient_softness, u_ambient_radius + u_ambient_softness, dist);
                        color.rgb = mix(color.rgb, u_ambient_color, glow * u_ambient_opacity);
                    }

                    // 4. Reactive Glow (Pulsing from center)
                    if (u_reactive_intensity > 0.0) {
                        float dist = distance(v_uv, vec2(0.5, 0.5));
                        float glow = 1.0 - smoothstep(0.0, 0.6, dist); // Fixed radius for now
                        color.rgb += u_reactive_color * glow * u_reactive_intensity;
                    }

                    // 5. Peak Accent (Flash)
                    if (u_peak_intensity > 0.0) {
                        // Subtle screen flash or edge highlight
                        float peak_dist = distance(v_uv, vec2(0.5, 0.5));
                        float peak_glow = (1.0 - smoothstep(0.05, 0.2, peak_dist)) * u_peak_intensity;
                        color.rgb += u_peak_accent_color * peak_glow;
                    }

                    // 6. Vignette (Darken edges)
                    if (u_vignette_strength > 0.0) {
                        float d = distance(v_uv, vec2(0.5));
                        float v = smoothstep(u_vignette_radius, u_vignette_radius + u_vignette_softness, d);
                        color.rgb = mix(color.rgb, vec3(0.0), v * u_vignette_strength);
                    }

                    f_color = color;
                }
            """
        )
        self.quad_vao = self.ctx.simple_vertex_array(self.prog, context.get_quad_buffer(), 'in_vert', 'in_uv')

    def render(self, **kwargs):
        # Ensure standard blending is used for background, preventing additive bleed from previous frames
        self.ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA
        
        # Handle Viewport for split-screen testing
        original_viewport = None
        if self.viewport:
            original_viewport = self.ctx.viewport
            self.ctx.viewport = self.viewport

        self.prog['u_time'].value = time.time() - self.start_time

        # Resolve colors from theme
        def get_rgb(color_name):
            if not color_name: return (0.0, 0.0, 0.0)
            # Assuming Frame.colours logic is available or we use a helper
            # For now, assume style passes color names that need lookup, OR hex/tuples
            # Since we don't have easy access to Frame.colours here, we rely on style resolving it 
            # OR we assume the style object has resolved colors. 
            # Let's assume style colors are strings and we need to look them up in the theme palette
            # BUT RenderPass doesn't have access to Frame.
            # Solution: BackgroundBase should resolve colors before creating/updating style?
            # Or we pass a resolver. For simplicity, let's assume style colors are valid hex/tuples or handled by BackgroundBase.
            # Actually, BackgroundStyle usually holds strings like 'mid', 'dark'.
            # We need the frame's colour palette.
            return (0.0, 0.0, 0.0) # Placeholder, logic moved to BackgroundBase update

        # Uniforms are updated by BackgroundBase before calling render, 
        # or we pull them here if we had access. 
        # Better design: BackgroundBase pushes values to uniforms.
        # But RenderPass.render is called by Compositor.
        # So we must set uniforms here based on self.style and self.lighting state.
        
        # We need a way to resolve theme colors to RGB floats (0-1).
        # We will inject a `color_resolver` function into this pass from BackgroundBase.
        resolver = getattr(self, 'color_resolver', lambda x: (0,0,0))

        # Base Color
        base_rgb = resolver(self.style.base_color)
        self.prog['u_base_color'].value = base_rgb

        # Texture
        if self.surface.texture:
            self.surface.texture.use(location=0)
            self.prog['u_texture'].value = 0
            self.prog['u_texture_opacity'].value = float(self.style.texture_opacity)
            self.prog['u_has_texture'].value = True
        else:
            self.prog['u_has_texture'].value = False

        # Vignette
        if self.style.vignette:
            self.prog['u_vignette_strength'].value = float(self.style.vignette.strength)
            self.prog['u_vignette_radius'].value = float(self.style.vignette.radius)
            self.prog['u_vignette_softness'].value = float(self.style.vignette.softness)
        else:
            self.prog['u_vignette_strength'].value = 0.0

        # Noise
        if self.style.noise:
            self.prog['u_noise_strength'].value = float(self.style.noise.strength)
        else:
            self.prog['u_noise_strength'].value = 0.0

        # Ambient Glow
        if self.style.ambient_glow:
            self.prog['u_ambient_color'].value = resolver(self.style.ambient_glow.color)
            self.prog['u_ambient_opacity'].value = float(self.style.ambient_glow.opacity)
            self.prog['u_ambient_radius'].value = float(self.style.ambient_glow.radius)
            self.prog['u_ambient_softness'].value = float(self.style.ambient_glow.softness)
        else:
            self.prog['u_ambient_opacity'].value = 0.0

        # Reactive Glow
        if self.style.reactive_glow:
            self.prog['u_reactive_color'].value = resolver(self.style.reactive_glow.color)
            self.prog['u_reactive_intensity'].value = self.lighting.reactive_intensity
        else:
            self.prog['u_reactive_intensity'].value = 0.0

        # Peak Accent
        if self.style.peak_accent:
            self.prog['u_peak_accent_color'].value = resolver(self.style.peak_accent.color)
            self.prog['u_peak_intensity'].value = self.lighting.peak_intensity
        else:
            self.prog['u_peak_intensity'].value = 0.0

        self.quad_vao.render(moderngl.TRIANGLE_STRIP)

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

        self.lighting = BackgroundLighting(style)
        self.surface = BackgroundSurface(style, self.engine.render_context)
        self.render_pass = BackgroundRenderPass(self.engine.render_context, style, self.surface, self.lighting)
        
        # Inject color resolver into render pass
        self.render_pass.color_resolver = self._resolve_color

    def _resolve_color(self, color_name):
        """Helper to convert theme color names to (r,g,b) floats"""
        if not color_name: return (0.0, 0.0, 0.0)
        # Use Frame's Colour object to lookup
        # Colour.get returns (r,g,b) or (r,g,b,a) 0-255 integers
        col = self.frame.colours.get(color_name)
        return tuple(c / 255.0 for c in col[:3])

    def update(self):
        # Update lighting state based on audio
        if hasattr(self.frame.platform, 'audio_available') and self.frame.platform.audio_available:
            self.lighting.update(self.frame.platform)

    def draw(self):
        # Register the render pass with the compositor for this frame
        if hasattr(self.engine, 'compositor'):
            # Calculate viewport for this frame
            # abs_rect returns (x, y, w, h) in Pygame coords (Top-Left origin)
            # OpenGL needs Bottom-Left origin.
            # Geometry.abs_rect returns [x, y, w, h] where y is top-left.
            # Geometry.norm() returns [a, b, c, d] where b is bottom-y relative to screen height?
            # Let's use the frame's absolute coordinates carefully.
            
            x, y, w, h = self.frame.abs_rect()
            
            # Convert Pygame Y (Top-Left) to OpenGL Y (Bottom-Left)
            # GL_Y = ScreenHeight - (Pygame_Y + Height)
            # Wait, Frame.abs_rect() calculation:
            # rect = [x, int(screen_h - (y0 + h)), w, h]
            # So rect[1] is the Top-Left Y.
            # The Bottom-Left Y is simply screen_h - rect[1] - h?
            # Actually, Frame.y0 is the bottom coordinate in normalized space.
            # Let's look at Geometry.abs():
            # rect = [x0, screen_h - (y0 + h), w, h]
            # So y0 is the bottom Y.
            # So for OpenGL viewport, we can just use (x0, y0, w, h) directly from the normalized coords!
            # But we need to account for margins/padding which abs_rect does.
            
            # Let's recalculate GL viewport from Frame geometry:
            # x = self.frame.x0 + outline + padding
            # y = self.frame.y0 + outline + padding
            
            shrink = self.frame.outline_w + self.frame.padding
            gl_x = self.frame.x0 + shrink
            gl_y = self.frame.y0 + shrink
            gl_w = self.frame.w - (shrink * 2)
            gl_h = self.frame.h - (shrink * 2)
            
            viewport = (int(gl_x), int(gl_y), int(gl_w), int(gl_h))
            
            self.render_pass.viewport = viewport
            self.engine.compositor.add_pre_pass(self.render_pass)
