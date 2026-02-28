#!/usr/bin/env python
"""
Display driver classes

Low level platform dynamics


v1.0 baloothebear4 1 Dec 2023   Original, based on Pygame visualiser mockups
v1.1 baloothebear4 Feb 2024     refactored as part of pyvisualiseer
v2.0 baloothebear4 Feb 2026     Refactored - spliting out componenets eg Bar, leaving Graphic primatives and OpenGL integration

"""

import  pygame, time
from    pygame.locals import *
import  numpy as np
# from   framecore import Frame, Cache, Colour
# from   textwrap import shorten, wrap
from    io import BytesIO
import  warnings
import  os

import  moderngl
from    array import array
from    components import Outline, Background


""" Prevent image colour warnings: libpng warning: iCCP: known incorrect sRGB profile,"""
warnings.filterwarnings("ignore", category=UserWarning, module="pygame")

PI = np.pi
      

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

        # Simple shader for Outlines and Backgrounds
        # It handles: Flat Colors, Opacity, and Rounded Corners (via Fragment Shader)
        self.prog = self.ctx.program(
            vertex_shader="""
                #version 330
                in vec2 in_vert;
                in vec4 in_color;
                out vec4 v_color;
                void main() {
                    gl_Position = vec4(in_vert, 0.0, 1.0);
                    v_color = in_color;
                }
            """,
            fragment_shader="""
                #version 330
                in vec4 v_color;
                out vec4 f_color;
                void main() {
                    f_color = v_color;
                }
            """
        )

        # Buffer to hold vertex data (x, y, r, g, b, a)
        self.vbo = self.ctx.buffer(reserve=1024 * 24) # Reserve space for 1000+ rects
        self.vao = self.ctx.simple_vertex_array(self.prog, self.vbo, 'in_vert', 'in_color')
        
        self.render_queue = []

    def clear(self):
        """Replaces screen.fill for the GPU"""
        # Matches your GraphicsDriverPi.BACKGROUND_COLOR
        bg = [c/255.0 for c in self.platform.BACKGROUND_COLOR]
        self.ctx.clear(bg[0], bg[1], bg[2], 1.0)
        self.render_queue = []

    def add_rect(self, coords, color, opacity):
        """
        Converts Pygame coords (x, y, w, h) to GL coords (-1 to 1)
        and adds them to the batch queue.
        """
        x, y, w, h = coords
        # Normalize to OpenGL Clip Space
        sw, sh = self.platform.W, self.platform.H
        
        x1, y1 = (x / sw) * 2 - 1, 1 - (y / sh) * 2
        x2, y2 = ((x + w) / sw) * 2 - 1, 1 - ((y + h) / sh) * 2
        
        r, g, b = [c/255.0 for c in color[:3]]
        a = opacity / 255.0

        # Define two triangles (Standard GL Rect)
        # Format: x, y, r, g, b, a
        rect_data = [
            x1, y1, r, g, b, a,
            x2, y1, r, g, b, a,
            x1, y2, r, g, b, a,
            x1, y2, r, g, b, a,
            x2, y1, r, g, b, a,
            x2, y2, r, g, b, a
        ]
        self.render_queue.extend(rect_data)

    def render(self):
        """Draws all queued rects in one hardware call"""
        if not self.render_queue:
            return

        data = np.array(self.render_queue, dtype='f4')
        self.vbo.write(data)
        self.vao.render(moderngl.TRIANGLES, vertices=len(data)//6)