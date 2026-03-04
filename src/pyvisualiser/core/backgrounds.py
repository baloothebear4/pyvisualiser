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

        # print("Background.__init__>", background, self.frame.colours.is_colour(self.background))

        if background is None:
            self.background       = None #Background.BACKGROUND_DEFAULT['colour']

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

    def update(self, audio_level: float, peak_level: float):
        # Update Reactive Glow intensity
        target_reactive = 1.0 if audio_level > self.style.reactive_glow.threshold else 0.0
        if target_reactive > self.reactive_intensity:
            self.reactive_intensity += (target_reactive - self.reactive_intensity) * self.style.reactive_glow.attack
        else:
            self.reactive_intensity += (target_reactive - self.reactive_intensity) * self.style.reactive_glow.decay

        # Update Peak Accent intensity
        target_peak = 1.0 if peak_level > self.style.peak_accent.threshold else 0.0
        if target_peak > self.peak_intensity:
            self.peak_intensity += (target_peak - self.peak_intensity) * self.style.peak_accent.attack
        else:
            self.peak_intensity += (target_peak - self.peak_intensity) * self.style.peak_accent.decay
        
        self.peak_intensity = max(0.0, min(1.0, self.peak_intensity))
        self.reactive_intensity = max(0.0, min(1.0, self.reactive_intensity))


class BackgroundSurface:
    """
    Manages static surface properties, like loading textures.
    """
    def __init__(self, style: BackgroundStyle):
        self.style = style
        self.texture = None
        self.image_surface = None
        if style.texture_path:
            try:
                path = get_asset_path('backgrounds', style.texture_path)
                self.image_surface = pygame.image.load(path).convert_alpha()
            except Exception as e:
                print(f"Warning: Failed to load background texture '{style.texture_path}': {e}")

    def get_texture(self, ctx: moderngl.Context) -> moderngl.Texture:
        """Creates and caches the moderngl texture from the pygame surface."""
        if self.image_surface and self.texture is None:
            rgba_data = pygame.image.tostring(self.image_surface, "RGBA", True) # Flipped for GL
            self.texture = ctx.texture(self.image_surface.get_size(), 4, rgba_data)
            self.texture.repeat_x = True
            self.texture.repeat_y = True
        return self.texture


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
        self.colours = Colour(self.style.theme, 1)
        self.viewport = None

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

                uniform float u_vignette_strength;
                uniform float u_vignette_radius;
                uniform float u_vignette_softness;

                uniform float u_noise_strength;
                uniform float u_noise_speed;

                uniform vec3 u_ambient_glow_color;
                uniform float u_ambient_glow_opacity;
                uniform float u_ambient_glow_radius;
                uniform float u_ambient_glow_softness;

                uniform vec3 u_reactive_glow_color;
                uniform float u_reactive_intensity;

                uniform vec3 u_peak_accent_color;
                uniform float u_peak_intensity;

                uniform sampler2D u_texture;
                uniform bool u_has_texture;
                uniform float u_texture_opacity;

                float random(vec2 st) {
                    return fract(sin(dot(st.xy, vec2(12.9898, 78.233))) * 43758.5453123);
                }

                void main() {
                    vec2 uv = v_uv;
                    vec4 color = vec4(u_base_color, 1.0);

                    if (u_has_texture) {
                        vec4 tex_color = texture(u_texture, uv);
                        color = mix(color, tex_color, u_texture_opacity);
                    }

                    float d_center = length(uv - 0.5);
                    float vignette = 1.0 - smoothstep(u_vignette_radius - u_vignette_softness, u_vignette_radius, d_center);
                    color.rgb *= mix(1.0, vignette, u_vignette_strength);

                    float noise = (random(uv * 2.0 + u_time * u_noise_speed) - 0.5) * u_noise_strength;
                    color.rgb += noise;

                    float ambient_glow = 1.0 - smoothstep(u_ambient_glow_radius - u_ambient_glow_softness, u_ambient_glow_radius, d_center);
                    color.rgb += u_ambient_glow_color * ambient_glow * u_ambient_glow_opacity;

                    float reactive_dist = length(uv - vec2(0.5, 0.4));
                    float reactive_glow = (1.0 - smoothstep(0.3, 0.7, reactive_dist)) * u_reactive_intensity;
                    color.rgb += u_reactive_glow_color * reactive_glow;

                    float peak_dist = length(uv - vec2(0.5, 0.8));
                    float peak_glow = (1.0 - smoothstep(0.05, 0.2, peak_dist)) * u_peak_intensity;
                    color.rgb += u_peak_accent_color * peak_glow;

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
            c = self.colours.get(color_name)
            return (c[0] / 255.0, c[1] / 255.0, c[2] / 255.0)

        # Set uniforms from style and state objects
        self.prog['u_base_color'].value = get_rgb(self.style.base_color)
        
        s_vignette = self.style.vignette
        self.prog['u_vignette_strength'].value = s_vignette.strength
        self.prog['u_vignette_radius'].value = s_vignette.radius
        self.prog['u_vignette_softness'].value = s_vignette.softness

        s_noise = self.style.noise
        self.prog['u_noise_strength'].value = s_noise.strength
        self.prog['u_noise_speed'].value = s_noise.speed

        s_ambient = self.style.ambient_glow
        self.prog['u_ambient_glow_color'].value = get_rgb(s_ambient.color)
        self.prog['u_ambient_glow_opacity'].value = s_ambient.opacity
        self.prog['u_ambient_glow_radius'].value = s_ambient.radius
        self.prog['u_ambient_glow_softness'].value = s_ambient.softness

        self.prog['u_reactive_glow_color'].value = get_rgb(self.style.reactive_glow.color)
        self.prog['u_reactive_intensity'].value = self.lighting.reactive_intensity

        self.prog['u_peak_accent_color'].value = get_rgb(self.style.peak_accent.color)
        self.prog['u_peak_intensity'].value = self.lighting.peak_intensity

        tex = self.surface.get_texture(self.ctx)
        if tex:
            tex.use(location=0)
            self.prog['u_texture'].value = 0
            self.prog['u_has_texture'].value = True
            self.prog['u_texture_opacity'].value = self.style.texture_opacity
        else:
            self.prog['u_has_texture'].value = False

        self.quad_vao.render(moderngl.TRIANGLE_STRIP)

        # Restore viewport
        if original_viewport:
            self.ctx.viewport = original_viewport

class BackgroundBase:
    """
    The main public-facing class for the background system.
    It holds the style, manages state, and provides the render pass to the compositor.
    """
    def __init__(self, platform, style: BackgroundStyle):
        self.platform = platform
        self.style = style
        self.surface = BackgroundSurface(style)
        self.lighting = BackgroundLighting(style)
        self._render_pass = BackgroundRenderPass(platform.render_context, style, self.surface, self.lighting)

    def set_viewport(self, viewport):
        self._render_pass.viewport = viewport

    def get_render_pass(self) -> BackgroundRenderPass:
        return self._render_pass

    def update(self, audio_data: dict):
        """Call this every frame to update reactive lighting."""
        mono_level = audio_data.get('mono', 0.0)
        peak_level = audio_data.get('peak_mono', 0.0)
        self.lighting.update(mono_level, peak_level)