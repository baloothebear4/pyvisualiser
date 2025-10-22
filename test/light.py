import pygame
import math

pygame.init()
WIDTH, HEIGHT = 1280, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Create gradient helper
def radial_gradient(radius, inner_color, outer_color):
    """Return a circular surface with a smooth gradient."""
    gradient = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
    for r in range(radius, 0, -1):
        color = [
            inner_color[i] + (outer_color[i] - inner_color[i]) * (r / radius)
            for i in range(3)
        ]
        alpha = int(255 * (1 - (r / radius)))
        pygame.draw.circle(gradient, (*color, alpha), (radius, radius), r)
    return gradient

def draw_panel():
    # Dark base background
    screen.fill((10, 10, 10))

    # Vignette lighting
    vignette = radial_gradient(int(WIDTH * 0.7), (80, 80, 80), (10, 10, 10))
    vignette_rect = vignette.get_rect(center=(WIDTH//2, HEIGHT//2))
    screen.blit(vignette, vignette_rect, special_flags=pygame.BLEND_RGBA_ADD)

    # Glass-like panel area
    panel_rect = pygame.Rect(100, 60, WIDTH-200, HEIGHT-120)
    pygame.draw.rect(screen, (30, 30, 30), panel_rect, border_radius=20)
    pygame.draw.rect(screen, (60, 60, 60, 80), panel_rect, 2, border_radius=20)

    # Top light reflection
    top_glow = pygame.Surface((WIDTH, HEIGHT//3), pygame.SRCALPHA)
    pygame.draw.ellipse(top_glow, (255, 255, 255, 40),
                        (0, -HEIGHT//3, WIDTH, HEIGHT))
    screen.blit(top_glow, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    draw_panel()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
