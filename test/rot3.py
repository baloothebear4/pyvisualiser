import pygame
import os
import sys

# --- 1. Set the display environment variables ---
# These must be set BEFORE pygame.init()
print("Setting display environment variables...")
os.environ['SDL_VIDEODRIVER'] = 'kmsdrm'
os.environ['SDL_VIDEODEVICE'] = '/dev/dri/card1'
os.environ['SDL_NOMOUSE'] = '1'

# --- 2. Initialize Pygame and the physical screen ---
pygame.init()

pygame.mouse.set_visible(False)

# Get the size of the physical screen as reported by the system.
physical_screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
physical_size = physical_screen.get_size()
print(f"Fullscreen mode size reported by Pygame: {physical_size}")

# Update the window caption
pygame.display.set_caption("Virtual Canvas Rotation")

# --- 3. Create a virtual surface with our desired drawing dimensions ---
# This is our drawing canvas, which is the actual size of the physical panel.
virtual_width = 1280
virtual_height = 400
virtual_surface = pygame.Surface((virtual_width, virtual_height))

# --- 4. Draw a simple test shape on the virtual surface ---
# We'll draw a rectangle that is wider than it is tall.
rect_width = int(virtual_width * 0.8)
rect_height = int(virtual_height * 0.2)
rect = pygame.Rect(0, 0, rect_width, rect_height)
rect.center = (virtual_width // 2, virtual_height // 2)

# --- 5. Main loop to keep the window open ---
running = True
while running:
    # Handle events to allow for graceful exit
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

    # Clear both surfaces for fresh drawing
    physical_screen.fill((0, 0, 0))
    virtual_surface.fill((0, 0, 0))

    # Draw the wide rectangle onto the virtual surface
    pygame.draw.rect(virtual_surface, (255, 0, 0), rect)

    # Rotate the virtual surface by -90 degrees to "undo" the OS rotation
    rotated_surface = pygame.transform.rotate(virtual_surface, -90)

    # Blit the rotated surface onto the physical screen
    physical_screen.blit(rotated_surface, rotated_surface.get_rect(center=physical_screen.get_rect().center))

    # Update the display
    pygame.display.flip()

# --- 6. Quit Pygame gracefully ---
print("Exiting...")
pygame.quit()
sys.exit()
