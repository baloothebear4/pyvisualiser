#!/usr/bin/env python
"""
Display driver classes

Low level platform dynamics


v1.0 baloothebear4 1 Dec 2023   Original, based on Pygame visualiser mockups
v1.1 baloothebear4 Feb 2024     refactored as part of pyvisualiseer
v2.0 baloothebear4 Feb 2026     Refactored - spliting out componenets eg Bar, leaving Graphic primatives and OpenGL integration

"""

import  pygame, time, math
from    pygame.locals import *
import  numpy as np
# from    io import BytesIO
import  warnings
import  os

import  moderngl
from    array import array
from    .components import Outline, Background


""" Prevent image colour warnings: libpng warning: iCCP: known incorrect sRGB profile,"""
warnings.filterwarnings("ignore", category=UserWarning, module="pygame")
      

class DirtyAreaTracker:
    def __init__(self, screen_surface, alpha=0.1):
        """
        Initializes the tracker with the screen size and the EWMA smoothing factor.
        
        :param screen_surface: The main pygame.Surface for the display.
        :param alpha: The smoothing factor (0.0 to 1.0). Lower is smoother.
        """
        self.total_screen_area = screen_surface.get_width() * screen_surface.get_height()
        self.alpha = alpha
        self.rolling_avg_percent = 0.0

    def _get_merged_area(self, dirty_rects):
        """
        Calculates the net area covered by a list of rectangles.
        This is necessary because the rectangles can overlap.
        """
        if not dirty_rects:
            return 0

        union_rect = dirty_rects[0]
        for rect in dirty_rects[1:]:
            union_rect = union_rect.union(rect)

 
        total_dirty_area = union_rect.width * union_rect.height

        return total_dirty_area


    def update_average(self, dirty_rects):
        """
        Calculates the updated area percentage and updates the rolling average.
        
        :param dirty_rects: The list of Rects returned by your draw calls, 
                            which you pass to pygame.display.update().
        :return: The current rolling average of the dirty area percentage (0.0 to 100.0).
        """
        if self.total_screen_area == 0:
            return 0.0
            
        # 1. Get the net area of the updated regions
        net_dirty_area = self._get_merged_area(dirty_rects)

        # 2. Calculate the percentage of the screen that was drawn
        current_dirty_percent = (net_dirty_area / self.total_screen_area) * 100

        # 3. Apply the Exponentially Weighted Moving Average (EWMA)
        # S_t = alpha * Y_t + (1 - alpha) * S_{t-1}
        # Where S_t is the new average, Y_t is the current value, and S_{t-1} is the old average.
        self.rolling_avg_percent = (
            self.alpha * current_dirty_percent + 
            (1.0 - self.alpha) * self.rolling_avg_percent
        )
        
        return self.rolling_avg_percent


class DirtyRectManager:
    """
    A class to collect and manage "dirty" rectangles for partial screen updates.
    It provides methods to add Rects and a method to get the final list 
    for pygame.display.update().
    """
    def __init__(self):
        # The list to store all dirty pygame.Rect objects
        self.dirty_rects = []

    def add(self, rect):
        """
        Adds a single dirty rectangle to the list.
        If a tuple (x, y, w, h) is passed, it is converted to a pygame.Rect.
        """
        # print("DirtyRectManager.add", rect)

        if isinstance(rect, tuple):
            self.dirty_rects.append(pygame.Rect(rect))
        elif isinstance(rect, pygame.Rect):
            self.dirty_rects.append(rect)
        elif rect is None or True or False:
            return
        else:
            raise TypeError("DirtyRectManager.add> Expected pygame.Rect or (x, y, w, h) tuple")

    def add_list(self, rect_list: list[pygame.Rect | tuple]):
        """
        Adds a list of dirty rectangles.
        """
        for rect in rect_list:
            self.add(rect)

    def get_and_clear(self) -> list[pygame.Rect]:
        """
        Returns the list of dirty Rects and clears the internal list for the next frame.
        The union of all rects could also be calculated here for efficiency, 
        but for simplicity, we return the raw list.
        """
        # Optionally, merge overlapping rects to reduce update calls.
        # For simplicity, we just return the current list.
        rects_to_update = self.dirty_rects
        self.dirty_rects = [] # Clear the list for the next frame
        return rects_to_update
    
    def get_union_and_clear(self) -> list[pygame.Rect]:
        """
        Calculates the union of all dirty rects, returns a list with the one 
        bounding Rect, and clears the internal list. More efficient for 
        small, spread-out areas.
        """
        if not self.dirty_rects:
            return []
        
        # Calculate the union of all dirty rects
        union_rect = self.dirty_rects[0].unionall(self.dirty_rects[1:])

        self.dirty_rects = [] # Clear for the next frame
        return [union_rect]

    def clear(self):
        """
        Clears the list of dirty rectangles without returning them.
        """
        self.dirty_rects = []


class PygameRenderer:
    def __init__(self, surface):
        self.surface = surface

    def draw_rect(self, color, rect, width=0, **kwargs):
        pygame.draw.rect(self.surface, color, rect, width, **kwargs)

    def blit(self, source, dest, area=None, special_flags=0, **kwargs):
        self.surface.blit(source, dest, area, special_flags)

    def draw_line(self, color, start_pos, end_pos, width=1):
        pygame.draw.line(self.surface, color, start_pos, end_pos, width)

    def draw_lines(self, color, closed, points, width=1):
        pygame.draw.lines(self.surface, color, closed, points, width)

class GraphicsDriverPi:
    """ Raspberry PI-4B Waveshare 7.9" DSI based platform """
    H       = 400
    W       = 1280
    PANEL   = [W, H]   # h x w
    FPS     = 48
    BACKGROUND_COLOR = (10, 10, 20)  # Dark Blue/Grey, a nice HiFi screen background    


    """
    Base class to manage all the graphics i/o functions
    """
    def __init__(self, events):
        self.W      = GraphicsDriverPi.W
        self.H      = GraphicsDriverPi.H
        self.FPS    = GraphicsDriverPi.FPS
        self.events = events
        self.dirty_mgr = DirtyRectManager()


        self.clock  = pygame.time.Clock()
        self.screen = self.init_display()
        self.renderer = PygameRenderer(self.screen)

        self.area_tracker = DirtyAreaTracker(self.screen, alpha=0.05)



        print("\nGraphicsDriverPI.init_display> Pi ", self.screen.get_size())


    def init_display(self):
        """Initialize pygame for Waveshare 7.9" horizontal display"""
    
        # Force pygame to use framebuffer
        os.environ['SDL_VIDEODRIVER'] = 'kmsdrm'
        os.environ['SDL_VIDEODEVICE'] = '/dev/dri/card1'
       
        # 2. Hardening LD_LIBRARY_PATH for ALL required custom and system libraries
        custom_lib_path = '/usr/local/lib'
        # CRITICAL: This path holds the system's runtime libraries (libpng, libjpeg, libfreetype)
        # that the Pygame modules require.
        system_lib_path_aarch64 = '/usr/lib/aarch64-linux-gnu' 
        
        # Prioritize custom path first, then system path
        paths_to_add = [custom_lib_path, system_lib_path_aarch64]
        
        current_ld_path = os.environ.get('LD_LIBRARY_PATH', '')
        # Filter empty strings from the path list
        ld_path_list = [p for p in current_ld_path.split(':') if p] 
        
        added_paths = []

        for path in paths_to_add:
            if path not in ld_path_list:
                # Prepend the path to ensure it is found before default system paths
                ld_path_list.insert(0, path)
                added_paths.append(path)

        os.environ['LD_LIBRARY_PATH'] = ':'.join(ld_path_list)

        # Remove any rotation overrides - let hardware handle it
        if 'SDL_VIDEO_KMSDRM_ROTATION' in os.environ:
            del os.environ['SDL_VIDEO_KMSDRM_ROTATION']    
        #os.environ['SDL_VIDEO_KMSDRM_ROTATION'] = '90'

        os.environ['SDL_NOMOUSE']     = '1'  # Hide mouse cursor initially
    
        pygame.display.init()
        pygame.font.init()   
    
        # The physical screen is reported by the OS as 400x1280 (tall).
        self._physical_screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        actual_size = self._physical_screen.get_size()
        
        # Create a virtual surface with our desired drawing dimensions (1280x400)
        self.virtual_surface = pygame.Surface((GraphicsDriverPi.W, GraphicsDriverPi.H))
        
        # Hide mouse cursor for a cleaner look.
        pygame.mouse.set_visible(False)
        
        # --- Create the Background Surface ---
        self.background_surface = pygame.Surface(GraphicsDriverPi.PANEL)
        self.background_surface.fill(GraphicsDriverPi.BACKGROUND_COLOR)
        self.background_surface = self.background_surface.convert()

        # Return the virtual surface for all drawing operations
        return self.virtual_surface        # Waveshare 7.9" resolution: 400x1280 native (portrait)


    def draw_start(self, text=None):
        # Without dirty rects
        # self.screen.fill((0,0,0))       # erase whole screen
        # All drawing now happens on the virtual surface.
        # self.virtual_surface.fill(GraphicsDriverPi.BACKGROUND_COLOR)       # erase the virtual screen
        if text is not None: pygame.display.set_caption(text)
 
  

    """ Draw on the transformed parts -optimised algorithm"""
    def draw_end(self):
        dirty_rects = self.dirty_mgr.get_and_clear()
        
        if not dirty_rects:
            # If nothing is dirty, don't update anything
            self.ave_area_pc = self.area_tracker.update_average([])
            print("GraphicsDriverPi.draw_end> NO dirty rects")
            return
            
        transformed_rects = []
        # Get the dimensions of the non-rotated virtual surface
        Wv, Hv = self.virtual_surface.get_size() # e.g., (800, 480)

        # 1. Clear the old physical screen areas (important for dirty rects!)
        #    This step is ONLY needed if you don't clear the virtual surface (which you should)
        
        # 2. Draw the virtual surface content (including clearing)
        #    Assuming your main loop draws to self.virtual_surface, no change needed here.
        
        # 3. Rotate the ENTIRE virtual surface
        rotated_surface = pygame.transform.rotate(self.virtual_surface, -90)
        
        # 4. Blit the rotated surface to the physical screen (to show ALL changes)
        rotated_rect = rotated_surface.get_rect(center=self._physical_screen.get_rect().center)
        self._physical_screen.blit(rotated_surface, rotated_rect)
        
        # 5. Transform each dirty rect to the physical, rotated screen coordinates
        for rect in dirty_rects:
            # We are rotating the coordinate system -90 degrees (clockwise)
            
            # New X: Old Y distance from the TOP (Hv)
            # The top edge of the old rect (rect.y) becomes the right edge of the new rect (rotated H_v - rect.y)
            # To get the new TOP-LEFT X (x'): we need to subtract the old rect's full extent from H_v
            x_prime = rect.y
            
            # New Y: The old X
            # The top edge of the old rect (rect.x) becomes the top edge of the new rect
            y_prime = rect.x
            
            # New Width: Old Height
            w_prime = rect.height
            
            # New Height: Old Width
            h_prime = rect.width
            
            # Adjust the x coordinate to correctly shift from top-left to top-left after rotation
            # The new X is the distance from the top, minus the new height
            # (If the original rect was at the bottom, its x' should be near 0)
            
            # Correction: The new X should be referenced from the virtual height, 
            # and then shifted by the new height (old width)
            x_prime = Wv - rect.x - rect.width
            y_prime = rect.y
            
            # FINAL CORRECTION FOR -90 DEGREE ROTATION
            # If Wv x Hv is 800 x 480, screen is 480 x 800
            
            x_prime = rect.y # The new X is the old Y
            y_prime = Wv - (rect.x + rect.width) # The new Y is the old X inverted from the right
            w_prime = rect.height # New width is old height
            h_prime = rect.width # New height is old width
            
            # Reverting to the formula that matches -90 degrees in a standard coordinate rotation:
            # (x, y) -> (y, -x)
            # But since Pygame's Y is positive down, and we are working with top-left rects:
            
            x_prime = rect.y
            y_prime = Wv - (rect.x + rect.width)

            # Create the new rect in the physical screen's space
            # Note: We must adjust the y_prime based on the new dimensions
            transformed_rect = pygame.Rect(x_prime, y_prime, w_prime, h_prime)

            # THE CRITICAL ADJUSTMENT: The rotation may shift the origin.
            # We must account for the difference between the physical screen size (Hp, Wp) 
            # and the rotated surface size (Hv, Wv).
            
            # Assuming the physical screen is HxW (480x800) and virtual is WxH (800x480)
            # The simple transformation above is likely off by an offset.
            
            # Let's try the rotation: (x, y) -> (H - y, x) for 90 degrees CCW
            # For 90 degrees CW (-90): (x, y) -> (y, W - x) 
            
            # X' = y (This maps the vertical extent to the new horizontal one)
            x_prime = rect.y
            
            # Y' = W - (x + w) (This maps the horizontal extent to the new vertical one)
            y_prime = Wv - (rect.x + rect.width)
            
            # The formula that often fails with only 25% updated is because of the Wv reference
            
            # Let's use the simplest algebraic form:
            x_prime = rect.y
            y_prime = Wv - rect.x - rect.width
            w_prime = rect.height
            h_prime = rect.width
            
            transformed_rect = pygame.Rect(x_prime, y_prime, w_prime, h_prime)
            transformed_rects.append(transformed_rect)

        # 6. Update the display using the SMALL, transformed rects
        # This is the line that will fix the visual incompleteness
        pygame.display.update(transformed_rects)

        # 7. Update the area tracker
        self.ave_area_pc = self.area_tracker.update_average(transformed_rects)
        

class GraphicsDriverGL:
    """ OpenGL based platform using ModernGL """
    H       = 400
    W       = 1280
    PANEL   = [W, H]   # h x w
    FPS     = 60
    BACKGROUND_COLOR = (10, 10, 20)

    def __init__(self, events):
        self.events = events
        self.W      = GraphicsDriverGL.W
        self.H      = GraphicsDriverGL.H
        self.FPS    = GraphicsDriverGL.FPS
        
        self.clock  = pygame.time.Clock()
        self.window = self.init_display()
        
        # Initialize GLManager as the renderer
        self.renderer = GLManager(self)
        self.renderer.current_texture = None
        
        # Legacy support: Create a dummy surface for components (like Text) 
        # that still try to blit to 'screen'. This prevents crashes, though 
        # they won't be visible until ported to GL.
        self.screen = pygame.Surface((self.W, self.H))
        
        self.dirty_mgr = DirtyRectManager()
        self.area_tracker = DirtyAreaTracker(self.screen, alpha=0.05)
        self.ave_area_pc = 0
        print("\nGraphicsDriverGL.init_display> OpenGL Mode")

    def init_display(self):
        pygame.init()
        # Request OpenGL 3.3 Core
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)
        
        return pygame.display.set_mode((self.W, self.H), pygame.OPENGL | pygame.DOUBLEBUF)

    def draw_start(self, text=None):
        if text: pygame.display.set_caption(text)
        self.renderer.clear()

    def draw_end(self):
        self.renderer.render()
        pygame.display.flip()
        self.dirty_mgr.clear()



class GraphicsDriverMac:
    """ Pygame based platform """
    H       = 400
    W       = 1280
    PANEL   = [W, H]   # h x w
    FPS     = 50

    """
    Base class to manage all the graphics i/o functions
    """
    def __init__(self, events):
        self.events = events
        self.W      = GraphicsDriverMac.W
        self.H      = GraphicsDriverMac.H
        self.FPS    = GraphicsDriverMac.FPS
        self.dirty_mgr = DirtyRectManager()

        self.screen = self.init_display()
        self.renderer = PygameRenderer(self.screen)
        self.clock  = pygame.time.Clock()
        self.area_tracker = DirtyAreaTracker(self.screen, alpha=0.05)
        print("\nGraphicsDriverMac.init_display> Mac ", self.screen.get_size())

    def init_display(self):
        pygame.init()   #create the drawing canvas
        return pygame.display.set_mode(GraphicsDriverMac.PANEL)

    def draw_start(self, text=None):
        # self.screen.fill((0,0,0))       # erase whole screen
        if text is not None: pygame.display.set_caption(text)

    def draw_end(self):
        # print("Screen.draw [END]")
        # pygame.display.flip()

        # Update only the dirty areas - to save draw and render time
        dirty_rects = self.dirty_mgr.get_and_clear()
        if dirty_rects:
            pygame.display.update(dirty_rects)

         # 7. Update the area tracker
        self.ave_area_pc = self.area_tracker.update_average(dirty_rects)               

            


class GraphicsDriver:
    def __init__(self, events, gfx='mac'):
        if gfx=='pi_kms':
            self.gfx_driver=GraphicsDriverPi(events)
        elif gfx=='gl':
            self.gfx_driver=GraphicsDriverGL(events)
        else:
            self.gfx_driver=GraphicsDriverMac(events)

        pygame.display.set_caption('Visualiser')

        self.screen         = self.gfx_driver.screen

    def __getattr__(self, item):
        """Delegate calls to the implementation"""
        return getattr(self.gfx_driver, item)

    def refresh(self, rect=None):
        # if rect is None: rect = [0,0]+self.wh
        pygame.display.update(pygame.Rect(rect))    

    def create_background(self, frame, background):
        return Background(frame, background)          

    def create_outline(self, frame, outline):
        return Outline(frame, outline)    
    
    def regulate_fps(self):
        self.gfx_driver.clock.tick(self.gfx_driver.FPS)

    def area_drawn(self):
        return self.gfx_driver.ave_area_pc    

    def clear_screen(self):
        self.screen.fill((0,0,0))       # erase whole screen    

    @property
    def boundary(self):
        return [0 , 0, self.gfx_driver.W-1, self.gfx_driver.H-1]

    @property
    def h(self):
        return self.gfx_driver.H

    @property
    def w(self):
        return self.gfx_driver.W

    @property
    def fps(self):
        return self.gfx_driver.FPS    

    @property
    def wh(self):
        return (self.gfx_driver.W, self.gfx_driver.H)

    def graphics_end(self):
        # print("GraphicsDriver.graphics_end>")
        # pygame.mixer.quit()
        pygame.quit()

    def checkKeys(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.events.KeyPress('exit')
            elif event.type == KEYDOWN:
                self.events.KeyPress(event.key)


'''
Entry point to OpenGL and the GPU based graphics processing

'''
class GLManager:
    def __init__(self, platform):
        self.platform = platform
        # Create a context from the existing Pygame window
        self.ctx = moderngl.create_context()
        
        # Configure transparency/blending to match your 'opacity' logic
        self.ctx.enable(moderngl.BLEND)
        self.ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA
        self.is_additive = False

        # Simple shader for Outlines and Backgrounds
        # It handles: Flat Colors, Opacity, and Rounded Corners (via Fragment Shader)
        self.prog = self.ctx.program(
            vertex_shader="""
                #version 330
                in vec2 in_vert;
                in vec2 in_uv;
                in vec4 in_color;
                in float in_softness;
                in vec3 in_params; // width, height, radius
                in float in_stroke; // stroke width (0 = fill)
                in vec2 in_segments; // segment_size, gap_size
                in float in_axis; // 0 = x (horz), 1 = y (vert)
                in float in_level; // 0.0 to 1.0 fill level
                in float in_use_tex; // 0.0 = vertex colors, 1.0 = texture
                out vec4 v_color;
                out vec2 v_uv;
                out float v_softness;
                out vec3 v_params;
                out float v_stroke;
                out vec2 v_segments;
                out float v_axis;
                out float v_level;
                out float v_use_tex;
                void main() {
                    gl_Position = vec4(in_vert, 0.0, 1.0);
                    v_color = in_color;
                    v_uv = in_uv;
                    v_softness = in_softness;
                    v_params = in_params;
                    v_stroke = in_stroke;
                    v_segments = in_segments;
                    v_axis = in_axis;
                    v_level = in_level;
                    v_use_tex = in_use_tex;
                }
            """,
            fragment_shader="""
                #version 330
                in vec4 v_color;
                in vec2 v_uv;
                in float v_softness;
                in vec3 v_params;
                in float v_stroke;
                in vec2 v_segments;
                in float v_axis;
                in float v_level;
                in float v_use_tex;
                out vec4 f_color;
                
                uniform sampler2D gradient_tex;

                // SDF for a rounded box
                float sdRoundedBox(vec2 p, vec2 b, float r) {
                    vec2 q = abs(p) - b + r;
                    return length(max(q, 0.0)) + min(max(q.x, q.y), 0.0) - r;
                }

                void main() {
                    vec2 size = v_params.xy;
                    float radius = v_params.z;
                    vec2 half_size = size * 0.5;
                    
                    // Pixel coordinates relative to center
                    vec2 pos = (v_uv - 0.5) * size;
                    
                    // Clamp radius to half size to prevent artifacts
                    float r = min(radius, min(half_size.x, half_size.y));
                    
                    // Calculate Signed Distance (negative inside, positive outside)
                    float dist = sdRoundedBox(pos, half_size, r);
                    
                    // 1. Level Masking (Global)
                    // Determine coordinate based on axis and anchor
                    // abs(axis) < 1.5 is Vertical (1.0 or -1.0)
                    // axis < 0.0 is End-Anchored (Bottom or Right)
                    
                    bool is_vert = (abs(v_axis) < 1.5);
                    float coord_uv = is_vert ? v_uv.y : v_uv.x;
                    
                    if (v_axis < 0.0) coord_uv = 1.0 - coord_uv;
                    
                    // Discard pixels above the current level
                    if (coord_uv > v_level) discard;

                    // 2. Segment/LED Logic
                    float seg_alpha = 1.0;
                    
                    if (v_segments.x > 0.0 && v_segments.y > 0.0) {
                        float total_seg = v_segments.x + v_segments.y;
                        float size_px = is_vert ? size.y : size.x;
                        
                        float coord_px = coord_uv * size_px;
                        
                        float m = mod(coord_px, total_seg);
                        
                        // Strict discard for gaps
                        if (m > v_segments.x) discard;
                    }

                    float alpha = 0.0;
                    
                    if (v_stroke > 0.0) {
                        // Outline Rendering
                        // We want pixels where dist is between 0 and -v_stroke (inner stroke)
                        // Outer edge AA
                        float outer_alpha = 1.0 - smoothstep(-0.5, 0.5, dist);
                        // Inner edge AA
                        float inner_alpha = 1.0 - smoothstep(-0.5, 0.5, dist + v_stroke);
                        alpha = outer_alpha - inner_alpha;
                    } else {
                        // Filled Rendering
                        // Calculate blur amount based on softness
                        // Use a dynamic blur radius: proportional to size for large glows, but at least 20px for small items
                        float min_dim = min(size.x, size.y);
                        float blur = v_softness * max(20.0, min_dim * 0.8); 
                        
                        alpha = 1.0 - smoothstep(-blur, blur, dist);
                        
                        // Optional: Inner Glow boost for soft filled shapes (Bar LEDs)
                        if (v_softness > 0.01) {
                             float center_glow = 1.0 + (1.0 - length(v_uv - 0.5)) * 0.3;
                             // Note: We apply color logic below, so just modify alpha here or defer
                        }
                    }
                    
                    alpha *= seg_alpha;
                    
                    vec4 final_color = v_color;
                    
                    if (v_use_tex > 0.5) {
                        // Sample gradient texture based on coord_uv (0..1 along bar)
                        vec4 tex_col = texture(gradient_tex, vec2(coord_uv, 0.5));
                        final_color = vec4(tex_col.rgb, v_color.a); // Use texture RGB, vertex Alpha
                    }
                    
                    f_color = vec4(final_color.rgb, final_color.a * alpha);
                }
            """
        )

        # Texture Shader Program
        self.tex_prog = self.ctx.program(
            vertex_shader="""
                #version 330
                in vec2 in_vert;
                in vec2 in_uv;
                in float in_alpha;
                out vec2 v_uv;
                out float v_alpha;
                void main() {
                    gl_Position = vec4(in_vert, 0.0, 1.0);
                    v_uv = in_uv;
                    v_alpha = in_alpha;
                }
            """,
            fragment_shader="""
                #version 330
                uniform sampler2D texture0;
                uniform float opacity;
                in vec2 v_uv;
                in float v_alpha;
                out vec4 f_color;
                void main() {
                    vec4 color = texture(texture0, v_uv);
                    f_color = vec4(color.rgb, color.a * opacity * v_alpha);
                }
            """
        )

        # Buffer to hold vertex data (x, y, u, v, r, g, b, a, s, w, h, rad, stroke, seg_w, seg_gap, axis, level, use_tex) -> 18 floats per vertex
        self.vbo = self.ctx.buffer(reserve=4 * 1024 * 1024) 
        self.vao = self.ctx.simple_vertex_array(self.prog, self.vbo, 'in_vert', 'in_uv', 'in_color', 'in_softness', 'in_params', 'in_stroke', 'in_segments', 'in_axis', 'in_level', 'in_use_tex')
        
        self.render_queue = []
        
        # Quad buffer for textures (x, y, u, v, alpha)
        self.quad_buffer = self.ctx.buffer(reserve=4 * 5 * 4) # 5 floats * 4 vertices
        self.quad_vao = self.ctx.simple_vertex_array(self.tex_prog, self.quad_buffer, 'in_vert', 'in_uv', 'in_alpha')

        self.current_texture = None

    def clear(self):
        """Replaces screen.fill for the GPU"""
        # Matches your GraphicsDriverPi.BACKGROUND_COLOR
        bg = [c/255.0 for c in self.platform.BACKGROUND_COLOR]
        self.ctx.clear(bg[0], bg[1], bg[2], 1.0)
        self.render_queue = []

    def set_additive(self, additive):
        if additive != self.is_additive:
            self.flush()
            self.is_additive = additive
            if self.is_additive:
                self.ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE
            else:
                self.ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA

    def draw_rect(self, color, rect, width=0, **kwargs):
        """ Adapter to match PygameRenderer interface """
        # Convert pygame.Rect to tuple if necessary
        if hasattr(rect, 'rect'): # It's a Rect object
             coords = (rect.x, rect.y, rect.width, rect.height)
        elif isinstance(rect, (list, tuple)):
             coords = rect
        else:
             coords = (rect.x, rect.y, rect.width, rect.height)

        # Extract radius (handle specific corners by taking the max if generic is 0)
        radius = kwargs.get('border_radius', 0.0)
        if radius == 0:
             radius = max(
                 kwargs.get('border_top_left_radius', 0),
                 kwargs.get('border_top_right_radius', 0),
                 kwargs.get('border_bottom_left_radius', 0),
                 kwargs.get('border_bottom_right_radius', 0)
             )

        # Extract segments (LED effect)
        segments = kwargs.get('segments', (0.0, 0.0))

        # Draw Shadow (if requested)
        shadow = kwargs.get('shadow')
        if shadow:
            s_offset = shadow.get('offset', (10, 10))
            s_color = shadow.get('color', (0, 0, 0))
            s_opacity = shadow.get('opacity', 128)
            s_softness = shadow.get('softness', 0.5)
            
            # Shadow geometry (offset from main rect)
            s_coords = (coords[0] + s_offset[0], coords[1] + s_offset[1], coords[2], coords[3])
            
            # Add shadow rect (filled, so stroke=0)
            self.add_rect(s_coords, s_color, s_opacity, s_softness, 0, radius, (0.0, 0.0), axis=1.0)

        # Draw Main Rect
        # Handle opacity if present in color tuple (R, G, B, A)
        opacity = 255
        if len(color) > 3:
            opacity = color[3]
            
        # Extract softness from kwargs, default to 0.0
        softness = kwargs.get('softness', 0.0)
        
        # Handle Gradient: if 'gradient' is passed, it overrides 'color'
        # gradient should be a tuple (color_start, color_end)
        gradient = kwargs.get('gradient')
        axis = kwargs.get('axis', 1.0) # 1.0 = Vertical, 0.0 = Horizontal
        level = kwargs.get('level', 1.0) # Default to full fill
        gradient_image = kwargs.get('gradient_image')
        texture_holder = kwargs.get('texture_holder')
        additive = kwargs.get('additive', False)

        self.set_additive(additive)

        if gradient_image:
            # Handle texture creation/caching
            texture = None
            if texture_holder and hasattr(texture_holder, '_gl_texture') and texture_holder._gl_texture:
                texture = texture_holder._gl_texture
            
            if texture is None:
                # If we are creating a new texture, we must flush previous draws to avoid state mix-up
                # (though strictly speaking, if we bind to unit 0, it affects next draw call)
                # But here we only flush if we are changing the bound texture.
                
                rgba_data = pygame.image.tostring(gradient_image, "RGBA", False)
                texture = self.ctx.texture(gradient_image.get_size(), 4, rgba_data)
                
                if texture_holder:
                    texture_holder._gl_texture = texture
            
            # Only flush and rebind if the texture has changed
            if self.current_texture != texture:
                self.flush()
                texture.use(location=0)
                self.current_texture = texture
                self.prog['gradient_tex'].value = 0
            
            self.add_rect(coords, color, opacity, softness, width, radius, segments, gradient, axis, level, use_tex=1.0)
        else:
            self.add_rect(coords, color, opacity, softness, width, radius, segments, gradient, axis, level, use_tex=0.0)

    def add_rect(self, coords, color, opacity, softness, stroke_width, radius, segments, gradient=None, axis=1.0, level=1.0, use_tex=0.0):
        """
        Converts Pygame coords (x, y, w, h) to GL coords (-1 to 1)
        and adds them to the batch queue.
        """
        x, y, w, h = coords
        
        if w <= 0 or h <= 0:
            return
        
        # Calculate padding for softness to avoid clipping
        padding = 0.0
        if softness > 0.0:
             # Match shader logic: float blur = v_softness * max(20.0, min_dim * 0.8);
             min_dim = min(w, h)
             blur_radius = softness * max(20.0, min_dim * 0.8)
             padding = blur_radius + 1.0 # Add 1px safety margin

        # Normalize to OpenGL Clip Space
        sw, sh = self.platform.W, self.platform.H
        
        x1, y1 = ((x - padding) / sw) * 2 - 1, 1 - ((y - padding) / sh) * 2
        x2, y2 = ((x + w + padding) / sw) * 2 - 1, 1 - ((y + h + padding) / sh) * 2
        
        # Base color (default)
        r0, g0, b0 = [c/255.0 for c in color[:3]]
        a = opacity / 255.0
        
        # Initialize corner colors
        c_tl = c_tr = c_bl = c_br = (r0, g0, b0)

        # Gradient colors
        if gradient:
            c_start, c_end = gradient
            rs, gs, bs = [c/255.0 for c in c_start[:3]]
            re, ge, be = [c/255.0 for c in c_end[:3]]
            
            if abs(axis) < 1.5: # Vertical Gradient (Top -> Bottom)
                c_tl = c_tr = (rs, gs, bs)
                c_bl = c_br = (re, ge, be)
            else: # Horizontal Gradient (Left -> Right)
                c_tl = c_bl = (rs, gs, bs)
                c_tr = c_br = (re, ge, be)

        s = softness
        w_px, h_px = w, h
        seg_w, seg_gap = segments

        # UVs need to be adjusted so 0..1 maps to the original w,h
        u_start = -padding / w
        u_end = 1.0 + padding / w
        v_start = -padding / h
        v_end = 1.0 + padding / h

        # Define two triangles (Standard GL Rect) with UVs, Softness, Size, Radius, Stroke, Segments, Axis, Level, UseTex
        # Format: x, y, u, v, r, g, b, a, s, w, h, rad, stroke, seg_w, seg_gap, axis, level, use_tex
        # Note: y1 is Top, y2 is Bottom in GL coords here (because of 1 - y calculation)
        rect_data = [
            x1, y1, u_start, v_start, c_tl[0], c_tl[1], c_tl[2], a, s, w_px, h_px, radius, stroke_width, seg_w, seg_gap, axis, level, use_tex, # Top-Left
            x2, y1, u_end,   v_start, c_tr[0], c_tr[1], c_tr[2], a, s, w_px, h_px, radius, stroke_width, seg_w, seg_gap, axis, level, use_tex, # Top-Right
            x1, y2, u_start, v_end,   c_bl[0], c_bl[1], c_bl[2], a, s, w_px, h_px, radius, stroke_width, seg_w, seg_gap, axis, level, use_tex, # Bottom-Left
            
            x1, y2, u_start, v_end,   c_bl[0], c_bl[1], c_bl[2], a, s, w_px, h_px, radius, stroke_width, seg_w, seg_gap, axis, level, use_tex, # Bottom-Left
            x2, y1, u_end,   v_start, c_tr[0], c_tr[1], c_tr[2], a, s, w_px, h_px, radius, stroke_width, seg_w, seg_gap, axis, level, use_tex, # Top-Right
            x2, y2, u_end,   v_end,   c_br[0], c_br[1], c_br[2], a, s, w_px, h_px, radius, stroke_width, seg_w, seg_gap, axis, level, use_tex  # Bottom-Right
        ]
        
        if (len(self.render_queue) + len(rect_data)) * 4 > self.vbo.size:
            self.flush()
            
        self.render_queue.extend(rect_data)

    def draw_line(self, color, start_pos, end_pos, width=1, softness=0.0):
        """
        Draws a line by constructing a rotated rectangle and using the SDF shader.
        """
        x1, y1 = start_pos
        x2, y2 = end_pos
        
        dx = x2 - x1
        dy = y2 - y1
        length = math.hypot(dx, dy)
        
        if length < 0.1: # Skip invisible lines
            return

        # Normalize direction vector
        ux = dx / length
        uy = dy / length
        
        # Perpendicular vector (rotated 90 degrees) scaled by half width
        px = -uy * width * 0.5
        py = ux * width * 0.5
        
        # Calculate the 4 corners of the rotated rectangle
        # Top-Left (Start + Perp)
        x_tl, y_tl = x1 + px, y1 + py
        # Top-Right (End + Perp)
        x_tr, y_tr = x2 + px, y2 + py
        # Bottom-Left (Start - Perp)
        x_bl, y_bl = x1 - px, y1 - py
        # Bottom-Right (End - Perp)
        x_br, y_br = x2 - px, y2 - py

        # Normalize to OpenGL Clip Space (-1 to 1)
        sw, sh = self.platform.W, self.platform.H
        
        def to_gl(x, y):
            return (x / sw) * 2 - 1, 1 - (y / sh) * 2

        xtl, ytl = to_gl(x_tl, y_tl)
        xtr, ytr = to_gl(x_tr, y_tr)
        xbl, ybl = to_gl(x_bl, y_bl)
        xbr, ybr = to_gl(x_br, y_br)

        # Color and params
        r, g, b = [c/255.0 for c in color[:3]]
        a = (color[3]/255.0) if len(color) > 3 else 1.0
        
        # Params: width (length of line), height (thickness), radius (0 for square ends), stroke (0 for filled)
        # We map UVs so that U goes along length, V goes along thickness
        
        s = softness
        # Vertices: x, y, u, v, r, g, b, a, s, w, h, rad, stroke, seg_w, seg_gap, axis, level, use_tex
        # We use 2 triangles (TL, TR, BL) and (BL, TR, BR)
        rect_data = [
            xtl, ytl, 0.0, 0.0, r, g, b, a, s, length, width, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, # Top-Left
            xtr, ytr, 1.0, 0.0, r, g, b, a, s, length, width, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, # Top-Right
            xbl, ybl, 0.0, 1.0, r, g, b, a, s, length, width, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, # Bottom-Left
            
            xbl, ybl, 0.0, 1.0, r, g, b, a, s, length, width, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, # Bottom-Left
            xtr, ytr, 1.0, 0.0, r, g, b, a, s, length, width, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, # Top-Right
            xbr, ybr, 1.0, 1.0, r, g, b, a, s, length, width, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0  # Bottom-Right
        ]
        
        if (len(self.render_queue) + len(rect_data)) * 4 > self.vbo.size:
            self.flush()
            
        self.render_queue.extend(rect_data)

    def draw_lines(self, color, closed, points, width=1, softness=0.0):
        """
        Draws a sequence of connected lines.
        """
        if len(points) < 2:
            return
            
        for i in range(len(points) - 1):
            self.draw_line(color, points[i], points[i+1], width, softness)
            
        if closed:
            self.draw_line(color, points[-1], points[0], width, softness)

    def flush(self):
        """Draws all queued rects"""
        if not self.render_queue:
            return

        data = np.array(self.render_queue, dtype='f4')
        self.vbo.write(data)
        self.vao.render(moderngl.TRIANGLES, vertices=len(data)//18)
        self.render_queue = []

    def render(self):
        self.flush()

    def blit(self, source, dest, area=None, special_flags=0, **kwargs):
        """
        Renders a Pygame Surface as a texture.
        This flushes the current batch of rects to ensure Z-order.
        """
        self.set_additive(False) # Ensure standard blending for images
        self.flush()
        
        # Invalidate current texture because blit uses a different shader/program
        # and might change the bound texture on unit 0
        self.current_texture = None
        
        texture = None
        texture_holder = kwargs.get('texture_holder')

        # Check for cached texture on the holder object
        if texture_holder and hasattr(texture_holder, '_gl_texture') and texture_holder._gl_texture:
             texture = texture_holder._gl_texture
        
        if texture is None:
             # Convert Pygame Surface to Texture
             rgba_data = pygame.image.tostring(source, "RGBA", False)
             texture = self.ctx.texture(source.get_size(), 4, rgba_data)
             
             # Cache it if a holder is provided
             if texture_holder:
                 texture_holder._gl_texture = texture
             
        texture.use(location=0)
        
        # Calculate Normalized Device Coordinates
        if hasattr(dest, 'x'):
             x, y = dest.x, dest.y
        else:
             x, y = dest[:2]
             
        # Handle opacity
        opacity = kwargs.get('opacity', 255) / 255.0
        reflection = kwargs.get('reflection')

        w, h = source.get_size()
        sw, sh = self.platform.W, self.platform.H
        
        # GL coords: -1 to 1. Y is up. Pygame Y is down.
        x1 = (x / sw) * 2 - 1
        y1 = 1 - (y / sh) * 2
        x2 = ((x + w) / sw) * 2 - 1
        y2 = 1 - ((y + h) / sh) * 2
        
        # Triangle Strip: TL, TR, BL, BR (Alpha 1.0 for main image)
        vertices = [
            x1, y1, 0.0, 0.0, 1.0,
            x2, y1, 1.0, 0.0, 1.0,
            x1, y2, 0.0, 1.0, 1.0,
            x2, y2, 1.0, 1.0, 1.0
        ]
        
        self.quad_buffer.write(np.array(vertices, dtype='f4'))
        
        # Render
        self.tex_prog['opacity'].value = opacity
        self.quad_vao.render(moderngl.TRIANGLE_STRIP)

        # Draw Reflection if requested
        if reflection:
            ref_size = 0.3
            ref_opacity = 0.5
            if isinstance(reflection, dict):
                ref_size = reflection.get('size', ref_size)
                ref_opacity = reflection.get('opacity', ref_opacity)
            
            # Reflection geometry (Below main image)
            h_gl = y1 - y2
            h_ref_gl = h_gl * ref_size
            y1_ref = y2
            y2_ref = y2 - h_ref_gl
            
            # Vertices for reflection (Flipped UVs, Gradient Alpha)
            ref_vertices = [
                x1, y1_ref, 0.0, 1.0, ref_opacity,          # Top of reflection (matches bottom of image)
                x2, y1_ref, 1.0, 1.0, ref_opacity,
                x1, y2_ref, 0.0, 1.0 - ref_size, 0.0,       # Bottom of reflection (fades out)
                x2, y2_ref, 1.0, 1.0 - ref_size, 0.0
            ]
            
            self.quad_buffer.write(np.array(ref_vertices, dtype='f4'))
            self.quad_vao.render(moderngl.TRIANGLE_STRIP)
        
        # texture.release() # Do not release, keep it cached on the surface