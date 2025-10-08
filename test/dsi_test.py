#!/usr/bin/env python3
import pygame
import sys
import os
import math
import time

def test_dsi_display():
    """Test pygame on DSI display with basic graphics and touch"""
    
    # Try different video drivers in order of preference
    video_drivers = [
        ('kmsdrm', '/dev/dri/card1'),  # KMS/DRM - modern approach
        ('kmsdrm', '/dev/dri/card0'),  # Try card0 if card1 fails
        ('directfb', None),            # DirectFB fallback
        (None, None)                   # Auto-detect
    ]
    
    screen = None
    for driver, device in video_drivers:
        try:
            # Clear any previous settings
            for key in ['SDL_VIDEODRIVER', 'SDL_VIDEODEVICE', 'SDL_FBDEV']:
                if key in os.environ:
                    del os.environ[key]
            
            # Set driver-specific environment
            if driver:
                os.environ['SDL_VIDEODRIVER'] = driver
                print(f"Trying SDL video driver: {driver}")
                if device:
                    os.environ['SDL_VIDEODEVICE'] = device
                    print(f"Using device: {device}")
            else:
                print("Trying auto-detect video driver")
            
            # Initialize pygame
            pygame.quit()  # Clean up any previous init
            pygame.init()
            pygame.display.init()
            
            # Try to create display
            screen = pygame.display.set_mode((1280,400))
            print(f"✅ Successfully initialized with driver: {driver or 'auto'}")
            break
            
        except pygame.error as e:
            print(f"❌ Failed with {driver or 'auto'}: {e}")
            continue
    
    if not screen:
        print("❌ Could not initialize any video driver!")
        return
    
    # Get actual display info after successful initialization
    try:
        info = pygame.display.Info()
        width, height = screen.get_size()
        print(f"Display initialized: {width} x {height}")
    except:
        width, height = 1280,400
        print(f"Using default resolution: {width} x {height}")
    pygame.display.set_caption("HiFi Preamp Display Test")
    
    # Enable mouse (touchscreen) input
    pygame.mouse.set_visible(True)
    
    # Colors
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GREEN = (0, 255, 0)
    BLUE = (0, 100, 255)
    RED = (255, 0, 0)
    YELLOW = (255, 255, 0)
    
    # Font for text
    try:
        font_large = pygame.font.Font(None, 48)
        font_small = pygame.font.Font(None, 24)
    except:
        font_large = pygame.font.SysFont('arial', 48)
        font_small = pygame.font.SysFont('arial', 24)
    
    clock = pygame.time.Clock()
    running = True
    frame_count = 0
    touch_pos = None
    
    print("Display test running - touch screen or press ESC to exit")
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                print(f"Key pressed: {event.key}")
            elif event.type == pygame.MOUSEBUTTONDOWN:
                touch_pos = event.pos
                print(f"Touch detected at: {touch_pos}")
            elif event.type == pygame.MOUSEBUTTONUP:
                touch_pos = None
        
        # Clear screen
        screen.fill(BLACK)
        
        # Draw title (smaller for narrow width)
        title_text = font_large.render("HiFi Preamp", True, WHITE)
        title_rect = title_text.get_rect(center=(width//2, 40))
        screen.blit(title_text, title_rect)
        
        subtitle_text = font_small.render("Display Test", True, GREEN)
        subtitle_rect = subtitle_text.get_rect(center=(width//2, 70))
        screen.blit(subtitle_text, subtitle_rect)
        
        # Draw system info
        info_lines = [
            f"Resolution: {width} x {height}",
            f"Frame: {frame_count}",
            f"FPS: {clock.get_fps():.1f}",
            f"Touch: {'Active' if touch_pos else 'None'}"
        ]
        
        for i, line in enumerate(info_lines):
            text = font_small.render(line, True, GREEN)
            screen.blit(text, (10, 100 + i * 25))  # Smaller margins for narrow screen
        
        # Draw animated waveform simulation
        center_y = height // 2
        amplitude = 50
        frequency = 0.02
        
        points = []
        for x in range(0, width, 4):
            y = center_y + amplitude * math.sin(frequency * x + frame_count * 0.1)
            points.append((x, y))
        
        if len(points) > 1:
            pygame.draw.lines(screen, BLUE, False, points, 2)
        
        # Draw vertical spectrum bars for portrait layout
        bar_height = 30
        num_bars = (height - 300) // (bar_height + 2)  # Fit bars in available space
        
        for i in range(min(32, num_bars)):
            y = 250 + i * (bar_height + 2)
            # Simulate spectrum data
            width_mult = abs(math.sin(frame_count * 0.05 + i * 0.2)) * 0.8 + 0.2
            bar_width = int(width_mult * (width - 40))
            
            color = (
                int(255 * width_mult),
                int(255 * (1 - width_mult)),
                128
            )
            
            pygame.draw.rect(screen, color, 
                           (20, y, bar_width, bar_height - 2))
        
        # Draw touch indicator
        if touch_pos:
            pygame.draw.circle(screen, RED, touch_pos, 20, 3)
            touch_text = font_small.render(f"Touch: {touch_pos[0]}, {touch_pos[1]}", True, WHITE)
            screen.blit(touch_text, (touch_pos[0] + 30, touch_pos[1] - 10))
        
        # Draw exit instruction
        exit_text = font_small.render("Touch screen or press ESC to exit", True, YELLOW)
        exit_rect = exit_text.get_rect(center=(width//2, height - 30))
        screen.blit(exit_text, exit_rect)
        
        # Update display
        pygame.display.flip()
        clock.tick(30)  # 30 FPS
        frame_count += 1
        
        # Auto-exit after demo
        if frame_count > 900:  # 30 seconds at 30fps
            print("Demo complete")
            break
    
    pygame.quit()
    print("Display test completed")

def check_display_setup():
    """Check if display is properly configured"""
    print("=== Display Configuration Check ===")
    
    # Check framebuffer
    try:
        with open('/sys/class/graphics/fb0/virtual_size', 'r') as f:
            fb_size = f.read().strip()
            print(f"Framebuffer size: {fb_size}")
        
        with open('/sys/class/graphics/fb0/name', 'r') as f:
            fb_name = f.read().strip()
            print(f"Framebuffer name: {fb_name}")
            
    except FileNotFoundError:
        print("⚠️  Framebuffer not found - DSI may not be configured")
    
    # Check DRM displays
    try:
        import glob
        drm_cards = glob.glob('/sys/class/drm/card*')
        if drm_cards:
            print("DRM cards found:")
            for card in drm_cards:
                try:
                    status_files = glob.glob(f"{card}/card*-DSI*/status")
                    for status_file in status_files:
                        with open(status_file, 'r') as f:
                            status = f.read().strip()
                            connector = status_file.split('/')[-2]
                            print(f"  {connector}: {status}")
                except:
                    pass
        else:
            print("No DRM cards found")
    except:
        print("Could not check DRM status")
    
    # Check DSI in dmesg
    try:
        import subprocess
        result = subprocess.run(['dmesg'], capture_output=True, text=True)
        dsi_lines = [line for line in result.stdout.split('\n') if 'dsi' in line.lower()]
        if dsi_lines:
            print("DSI messages in dmesg:")
            for line in dsi_lines[-3:]:  # Show last 3 DSI-related messages
                print(f"  {line.strip()}")
    except:
        print("Could not check dmesg")
    
    # Check I2C devices (for touchscreen)
    try:
        result = subprocess.run(['i2cdetect', '-y', '1'], capture_output=True, text=True)
        if result.returncode == 0 and any(c.isalnum() for c in result.stdout):
            print("I2C devices detected on bus 1")
        else:
            print("No I2C devices found on bus 1 - check touchscreen connection")
    except FileNotFoundError:
        print("i2cdetect not available - install i2c-tools")

if __name__ == "__main__":
    check_display_setup()
    print("\nStarting pygame display test...")
    test_dsi_display()
