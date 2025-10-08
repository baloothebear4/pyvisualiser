import pygame
import os
import sys

# Set the environment variables for the KMS/DRM driver
os.environ['SDL_VIDEODRIVER'] = 'kmsdrm'
os.environ['SDL_VIDEODEVICE'] = '/dev/dri/card1'

# Initialize Pygame
try:
    pygame.init()
except pygame.error as e:
    print(f"Error initializing Pygame: {e}")
    sys.exit()

# Get display information
info = pygame.display.Info()

# Print the screen size
print(f"Fullscreen mode size reported by Pygame: ({info.current_w}, {info.current_h})")

# Print all available display information
print("\n--- Pygame Display Info ---")
for attr in dir(info):
    if not attr.startswith('__'):
        value = getattr(info, attr)
        print(f"{attr}: {value}")

# A small delay to keep the window open for a moment (optional)
# This will also allow you to see the screen's behavior before it closes.
# You can remove the pygame.quit() and sys.exit() lines to see the screen state.
# I've added a try/except to catch a KeyboardInterrupt if you need to exit
try:
    print("\nPress Ctrl+C to exit...")
    pygame.time.wait(5000)
except KeyboardInterrupt:
    pass

# Quit gracefully
pygame.quit()
sys.exit()
