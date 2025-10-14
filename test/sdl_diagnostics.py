import os
import pygame
import sys
from pygame import font as pgfont

def init_display():
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

    # pygame.display.init()
    # pygame.font.init() 
    print("Environment hardening complete")


def run_diagnostics():
    """
    Runs a series of tests to diagnose Pygame and SDL linking issues,
    specifically checking environment variables and loaded modules.
    """
    
    print("-" * 60)
    print("1. ENVIRONMENT VARIABLE CHECK (What Pygame Sees)")
    print("-" * 60)
    
    # Check if the environment variables are actually present
    ld_path = os.environ.get('LD_LIBRARY_PATH', 'NOT SET (Default System Paths)')
    sdl_driver = os.environ.get('SDL_VIDEODRIVER', 'NOT SET (Default Pygame/OS Selection)')
    
    print(f"  [LD_LIBRARY_PATH]: {ld_path}")
    print(f"  [SDL_VIDEODRIVER]: {sdl_driver}")
    
    if "usr/lib/aarch64-linux-gnu" not in ld_path:
         print("  >>> WARNING: Critical library path missing from LD_LIBRARY_PATH.")
    
    print("-" * 60)
    
    try:
        # 2. Pygame Core Initialization and Driver Check
        pygame.init()
        print("2. PYGAME CORE INITIALIZATION")
        print(f"  Pygame initialized successfully.")
        
        active_driver = pygame.display.get_driver()
        print(f"  ACTIVE Display Driver: {active_driver}")
        
        if "kmsdrm" not in active_driver.lower():
             print("\n  !!! WARNING: KMS/DRM is NOT the active driver. !!!")
             print("  If you expected KMS/DRM, your SDL_VIDEODRIVER setting may be missing or wrong.")
             
        # 3. Add-on Module Checks (Image and Font linking)
        print("\n3. ADD-ON MODULE CHECK (Testing SDL_image and SDL_ttf)")

        # Test Image Module (relies on SDL_image linking)
        if pygame.image.get_extended():
            print(f"  pygame.image is linked and supports extended formats (SDL_image is OK).")
        else:
            print(f"  pygame.image is available but extended support (SDL_image) is NOT linked.")

        # Test Font Module (relies on SDL_ttf linking)
        if pgfont.get_init():
            print(f"  pygame.font (SDL_ttf) is initialized and ready.")
            test_font = pgfont.SysFont(None, 24)
            print(f"  Test system font loaded successfully.")
        else:
            print(f"  pygame.font (SDL_ttf) failed to initialize.")
            
        # 4. Display Check (Attempt to set a mode)
        try:
            screen = pygame.display.set_mode((10, 10))
            print(f"\n4. DISPLAY MODE CHECK")
            print(f"  Display set to 10x10 successfully. (Driver Confirmed)")
            screen.fill((0, 0, 0))
            pygame.display.flip()
            
        except pygame.error as e:
            print(f"  !!! CRITICAL ERROR: Display mode failed to set. Details: {e}")
            print("  This confirms a driver/backend issue.")
        
    except pygame.error as e:
        print(f"  !!! CRITICAL PYGAME ERROR: Pygame failed to initialize. Details: {e}")
        print("  This means the core SDL2 library or video driver failed to load.")
    
    finally:
        if 'screen' in locals():
            pygame.quit()
        print("-" * 60)
        print("Diagnostics complete.")

if __name__ == "__main__":
    init_display()
    run_diagnostics()
