import pygame
import os
import sys

# Assume these classes exist in your project for the example to make sense
# You can remove these placeholder classes once you have your actual ones.
class Colour:
    def __init__(self, *args, **kwargs):
        pass
    def get(self, index):
        if index == 'background':
            return (0, 0, 0)
        return (255, 255, 255)

class Frame:
    def __init__(self, driver):
        pass

class Image:
    def __init__(self, background, align, scalers):
        pass
    def draw(self, image):
        pass

class GraphicsDriver:
    """ Pygame based platform """
    H       = 400
    W       = 1280
    PANEL   = [W, H]   # w x h

    """
    Base class to manage all the graphics i/o functions
    """
    def __init__(self, events, FPS):
        self.events         = events
        self.screen         = self.init_display()
        self.clock          = pygame.time.Clock()
        self.FPS            = FPS
        pygame.display.set_caption('Visualiser')

        self.colour         = Colour('std', self.w)
        self.background     = Frame(self)
        self.image_container = Image(self.background, align=('centre','middle'), scalers=(1.0,1.0)) # make square

    def init_display(self):
        """Initialize pygame for Waveshare 7.9" horizontal display"""
        
        # Set the correct display environment variables before initializing Pygame.
        os.environ['SDL_VIDEODRIVER'] = 'kmsdrm'
        os.environ['SDL_VIDEODEVICE'] = '/dev/dri/card1'
        os.environ['SDL_NOMOUSE']     = '1'  # Hide mouse cursor initially
        
        # Avoid any rotation variables here, as the rotation is handled by our
        # virtual surface approach in the draw_end method.
        if 'SDL_VIDEO_KMSDRM_ROTATION' in os.environ:
            del os.environ['SDL_VIDEO_KMSDRM_ROTATION']     
        
        pygame.init()
        
        # The physical screen is reported by the OS as 400x1280 (tall).
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        actual_size = screen.get_size()
        print(f"Fullscreen mode size: {actual_size}")
        
        # Create a virtual surface with our desired drawing dimensions (1280x400)
        self.virtual_surface = pygame.Surface((GraphicsDriver.W, GraphicsDriver.H))
        
        # Hide mouse cursor for a cleaner look.
        pygame.mouse.set_visible(False)
        
        return screen

    def draw_start(self, text=None):
        # All drawing now happens on the virtual surface.
        self.virtual_surface.fill((0,0,0))       # erase the virtual screen
        if text is not None: pygame.display.set_caption(text)

    def draw_end(self):
        # Clear the physical screen
        self.screen.fill((0, 0, 0))
        
        # Rotate the virtual surface by -90 degrees to "undo" the OS rotation
        rotated_surface = pygame.transform.rotate(self.virtual_surface, -90)
        
        # Blit the rotated surface onto the physical screen
        rotated_rect = rotated_surface.get_rect(center=self.screen.get_rect().center)
        self.screen.blit(rotated_surface, rotated_rect)
        
        # Update the display to show the changes
        pygame.display.flip()
        
        # Control the frame rate
        self.clock.tick(self.FPS)

    def refresh(self, rect=None):
        # We now update the physical screen from the virtual surface.
        # This will update the entire screen to reflect the changes.
        pygame.display.update()

    def fill(self, rect=None, colour=None, colour_index='background', image=None):
        if rect is None: rect = self.boundary
        if colour_index is None: colour_index = 'background'
        if colour is None: colour=self.colour
        colour = colour.get(colour_index)
        # All drawing happens on the virtual surface
        pygame.draw.rect(self.virtual_surface, colour, pygame.Rect(rect))
        if image is not None:
            self.image_container.draw(image)

    @property
    def boundary(self):
        return [0 , 0, self.w-1, self.h-1]

    @property
    def h(self):
        return GraphicsDriver.H

    @property
    def w(self):
        return GraphicsDriver.W

    @property
    def wh(self):
        return (self.w, self.h)

# --- A simple example of how to use the GraphicsDriver class ---
if __name__ == '__main__':
    # Assume a simple events class and a desired FPS
    class Events:
        def get(self):
            return pygame.event.get()

    events = Events()
    FPS = 60

    # Instantiate the graphics driver
    driver = GraphicsDriver(events, FPS)

    # Main application loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
        
        # Start the drawing process
        driver.draw_start()
        
        # Draw a wide red rectangle using the class's methods
        rect_width = int(driver.w * 0.8)
        rect_height = int(driver.h * 0.2)
        rect = pygame.Rect(0, 0, rect_width, rect_height)
        rect.center = (driver.w // 2, driver.h // 2)
        
        # Draw the rectangle on the virtual surface
        pygame.draw.rect(driver.virtual_surface, (255, 0, 0), rect)

        # Finalize drawing and flip the display
        driver.draw_end()
    
    # Quit Pygame gracefully
    pygame.quit()
    sys.exit()
