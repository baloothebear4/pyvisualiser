#!/usr/bin/env python
"""
Display driver classes

Low level platform dynamics


v1.0 baloothebear4 1 Dec 2023   Original, based on Pygame visualiser mockups
v1.1 baloothebear4 Feb 2024     refactored as part of pyvisualiseer
v2.0 baloothebear4 Feb 2026     Major upgrade to port to OpenGL for speed and visual complexity

"""

import pygame
from   pygame.locals import *
import numpy as np
from   framecore import Frame, Cache, Colour
from   textwrap import shorten, wrap
from   io import BytesIO
import requests
import warnings
import os
import random
""" Prevent image coolour warnings: libpng warning: iCCP: known incorrect sRGB profile,"""
warnings.filterwarnings("ignore", category=UserWarning, module="pygame")

PI = np.pi

class Effects:
    def __init__(self, threshold=0.75, scale=2.5, blur=1.0, alpha=150, attack=0.4, decay=0.1, power=2.0):
        self.threshold = threshold
        self.scale     = scale
        self.blur      = blur
        self.alpha     = alpha
        self.attack    = attack
        self.decay     = decay
        self.power     = power

StrongEffect = Effects(threshold=0.75, scale=2.5, blur=1.0, alpha=150, attack=0.4, decay=0.1)
DreamEffect = Effects(threshold=0.75, scale=3.0, blur=3.0, alpha=150, attack=0.4, decay=0.1)
NeonGlow     = Effects(threshold=0.1, scale=2.0, blur=0.5, alpha=220, attack=0.8, decay=0.1, power=1.0)

class BarStyle:
    def __init__(self, led_h=10, led_gap=4, peak_h=1, right_offset=0, flip=False, radius=0, tip=False, orient='vert', col_mode=None, segment_size=None, segment_gap=None, corner_radius=None, edge_softness=0.0):
        self.segment_size = segment_size if segment_size is not None else led_h
        self.segment_gap  = segment_gap  if segment_gap  is not None else led_gap
        self.corner_radius = corner_radius if corner_radius is not None else radius
        self.peak_h     = peak_h
        self.right_offset = right_offset
        self.flip       = flip
        self.orient     = orient
        self.col_mode   = col_mode if col_mode is not None else orient
        self.tip        = tip
        self.edge_softness = edge_softness

class SpectrumStyle:
    def __init__(self, bar_space=0.5, barw_min=1, barw_max=20):
        self.bar_space = bar_space
        self.barw_min  = barw_min
        self.barw_max  = barw_max

class Bar(Frame):
    """
    Bars have parameters:
        - colour modes:
            'vert' according to y
            's' solid colour
            'horz' colour according to x
        - colour theme:  tuple of colours over which the colours range - one colour is fixed colour
        - leds ie discrete with colours -> LEDs have characteristics like, glow, intensity, colour, brick firmsness etc
        - vertical or horizontal,
        - left or right
        - peak lines
    """
    def __init__(self, parent, scalers=None, align=('centre', 'bottom'), theme=None, \
                 box_size=(100,100), style=None, effects=None, \
                 # Legacy/Individual params
                 led_h=10, led_gap=4, peak_h=1, right_offset=0, \
                 flip=False, radius=0, tip=False, orient='vert', col_mode=None, \
                 segment_size=None, segment_gap=None, corner_radius=None, edge_softness=0.05, \
                 # Effects params
                 intensity_threshold=0.75, intensity_scale=2.5, intensity_blur=1.0, intensity_alpha=100):

        Frame.__init__(self, parent, align=align,theme=theme, scalers=scalers)
        self.resize( box_size )

        if style is None:
            style = BarStyle(led_h=led_h, led_gap=led_gap, peak_h=peak_h, right_offset=right_offset,
                             flip=flip, radius=radius, tip=tip, orient=orient, col_mode=col_mode,
                             segment_size=segment_size, segment_gap=segment_gap, corner_radius=corner_radius, edge_softness=edge_softness)
        self.style = style

        if effects:
            self.effects = effects
        else:
            self.effects = Effects(threshold=intensity_threshold, scale=intensity_scale, blur=intensity_blur, alpha=intensity_alpha)
        
        colour_range = self.h if self.style.col_mode == 'vert' else self.w
        self.colours = Colour(self.theme, colour_range)
        
        self.gradient_surface = self._create_gradient_surface()
        self._gl_texture = None
        self.bloom_states = {} # Stores smoothed bloom intensity per bar (keyed by offset)

        # parent += self
        # print("Bar.__init__", self.geostr())

    def _create_gradient_surface(self):
        colors = self.colours.colours
        w = len(colors)
        if w == 0: return None
        # Create a 1D horizontal texture
        surf = pygame.Surface((w, 1))
        for i, c in enumerate(colors):
            surf.set_at((i, 0), c)
        return surf

    def float_abs_rect(self, offset=(0,0), wh=None):
        """ Calculates absolute coordinates keeping float precision to prevent jitter """
        xy_shrink = self.outline_w + self.padding
        wh_shrink = xy_shrink * 2
        
        w_frame = self.w
        h_frame = self.h
        
        w_target = w_frame - wh_shrink if wh is None else wh[0]
        h_target = h_frame - wh_shrink if wh is None else wh[1]
        
        x = self.x0 + xy_shrink + offset[0]
        y = self.screen_wh[1] - (self.y0 + h_frame - xy_shrink - offset[1])
        
        return (x, y, w_target, h_target)

    def draw_peak(self, peak_h, flip, peak_coords):
        if peak_h> 0.0:
            colour = self.colours.get( colour_index=peak_h , flip=flip)  #
            self.platform.renderer.draw_rect(colour, peak_coords, softness=self.style.edge_softness)

    def _get_smoothed_bloom(self, key, target):
        current = self.bloom_states.get(key, 0.0)
        if target > current:
            # Attack (Fast) - 40% of the difference per frame
            current += (target - current) * self.effects.attack
        else:
            # Decay (Slow) - 10% of the difference per frame
            current += (target - current) * self.effects.decay
        
        if current < 0.001: current = 0.0
        self.bloom_states[key] = current
        return current

    def draw(self, offset, ypc, w, peak=0, colour_index=None):
        self.tip_radius = int(w/2)
        if self.style.orient == 'horz':
            self.drawH(offset, ypc, w, peak, colour_index)
        else:
            self.drawV(offset, ypc, w, peak, colour_index)

    def drawV(self, offset, ypc, w, peak=0, colour_index=None):
        """ Draw Vertical Bar """
        if self.style.flip:
            coords = self.float_abs_rect( offset=(offset, 0),  wh=[w, self.abs_h] )

            # Determine colors for gradient (Top, Bottom)
            # Flip=True means bar grows downwards (usually). 
            # coords[1] is top. coords[1]+coords[3] is bottom.
            c_top = self.colours.get(0, False)
            c_bot = self.colours.get(self.colours.num_colours, False)
            
            if colour_index is not None:
                c_top = c_bot = self.colours.get(colour_index)

            # --- Bloom Logic (Vertical Flip=True, Grows Down) ---
            # 1. Calculate Raw Target Intensity
            if ypc > self.effects.threshold:
                range_above = max(0.001, 1.0 - self.effects.threshold)
                excess_ratio = (ypc - self.effects.threshold) / range_above
                excess_ratio = max(0.0, min(1.0, excess_ratio))
                # Power curve for "heat up" effect
                alpha_ratio = excess_ratio ** self.effects.power
            else:
                alpha_ratio = 0.0

            # 2. Temporal Smoothing (Attack/Release)
            smoothed_ratio = self._get_smoothed_bloom(offset, alpha_ratio)

            if smoothed_ratio > 0.01:
                # Jitter for electrical noise effect
                jitter = random.uniform(0.98, 1.02)
                current_alpha = self.effects.alpha * smoothed_ratio * jitter
                
                bloom_h = (ypc - self.effects.threshold) * self.abs_h
                bloom_y = coords[1] + self.effects.threshold * self.abs_h
                
                c_tip = list(self.colours.get(ypc * self.colours.num_colours)[:3]) + [current_alpha]
                c_thresh = list(self.colours.get(self.effects.threshold * self.colours.num_colours)[:3]) + [current_alpha]
                
                # Layer 1: Inner Glow (Tight, Bright)
                inner_scale = 1.0 + (self.effects.scale - 1.0) * 0.2
                b_w_inner = coords[2] * (inner_scale - 1.0)
                b_rect_inner = (coords[0] - b_w_inner/2, bloom_y - b_w_inner/2, coords[2] + b_w_inner, bloom_h + b_w_inner)
                self.platform.renderer.draw_rect(c_thresh, b_rect_inner, softness=self.effects.blur, gradient=(c_thresh, c_tip), axis=1.0, level=10.0, additive=True)

                # Layer 2: Outer Bloom (Wide, Soft, Dynamic Size)
                outer_scale = 1.0 + (self.effects.scale - 1.0) * (0.5 + 0.5 * smoothed_ratio)
                b_w_outer = coords[2] * (outer_scale - 1.0)
                b_rect_outer = (coords[0] - b_w_outer/2, bloom_y - b_w_outer/2, coords[2] + b_w_outer, bloom_h + b_w_outer)
                c_outer_tip = c_tip[:3] + [current_alpha * 0.6] # Lower alpha for outer
                c_outer_thresh = c_thresh[:3] + [current_alpha * 0.6]
                self.platform.renderer.draw_rect(c_outer_thresh, b_rect_outer, softness=self.effects.blur * 2.5, gradient=(c_outer_thresh, c_outer_tip), axis=1.0, level=10.0, additive=True)

            # Draw the main segmented bar
            self.platform.renderer.draw_rect(c_top, coords, 
                                             border_radius=self.style.corner_radius, 
                                             softness=self.style.edge_softness,
                                             segments=(self.style.segment_size, self.style.segment_gap),
                                             gradient=(c_top, c_bot),
                                             axis=1,
                                             level=ypc,
                                             gradient_image=self.gradient_surface,
                                             texture_holder=self)

            # Tip drawing (optional, can be added back if needed, but segments usually look good enough)

            pcoords = self.float_abs_rect( offset=(offset, peak*self.abs_h),  wh=[w, self.style.peak_h] )
            self.draw_peak(peak*self.h, False, pcoords)

            # print("Bar.draw (flip)> coords ", coords, "peak coords", coords, "ypc", ypc, "peak", peak)
        else:
            coords = self.float_abs_rect( offset=(offset, 0),  wh=[w, self.abs_h] )
            
            # Gradient: Bottom of bar (high Y) is low value. Top of bar (low Y) is high value.
            # coords[1] is Top (High Value). coords[1]+coords[3] is Bottom (Low Value).
            c_top = self.colours.get(self.colours.num_colours, False) # High value color
            c_bot = self.colours.get(0, False)         # Low value color
            
            if colour_index is not None:
                c_top = c_bot = self.colours.get(colour_index)

            # --- Bloom Logic (Standard Vertical) ---
            if ypc > self.effects.threshold:
                range_above = max(0.001, 1.0 - self.effects.threshold)
                excess_ratio = (ypc - self.effects.threshold) / range_above
                excess_ratio = max(0.0, min(1.0, excess_ratio))
                alpha_ratio = excess_ratio ** self.effects.power
            else:
                alpha_ratio = 0.0

            smoothed_ratio = self._get_smoothed_bloom(offset, alpha_ratio)

            if smoothed_ratio > 0.01:
                jitter = random.uniform(0.98, 1.02)
                current_alpha = self.effects.alpha * smoothed_ratio * jitter
                
                bloom_h = (ypc - self.effects.threshold) * self.abs_h
                bloom_y = coords[1] + (1.0 - ypc) * self.abs_h
                
                c_tip = list(self.colours.get(ypc * self.colours.num_colours)[:3]) + [current_alpha]
                c_thresh = list(self.colours.get(self.effects.threshold * self.colours.num_colours)[:3]) + [current_alpha]
                
                # Inner Glow
                inner_scale = 1.0 + (self.effects.scale - 1.0) * 0.2
                b_w_inner = coords[2] * (inner_scale - 1.0)
                b_rect_inner = (coords[0] - b_w_inner/2, bloom_y - b_w_inner/2, coords[2] + b_w_inner, bloom_h + b_w_inner)
                self.platform.renderer.draw_rect(c_tip, b_rect_inner, softness=self.effects.blur, gradient=(c_tip, c_thresh), axis=1.0, level=10.0, additive=True)

                # Outer Bloom
                outer_scale = 1.0 + (self.effects.scale - 1.0) * (0.5 + 0.5 * smoothed_ratio)
                b_w_outer = coords[2] * (outer_scale - 1.0)
                b_rect_outer = (coords[0] - b_w_outer/2, bloom_y - b_w_outer/2, coords[2] + b_w_outer, bloom_h + b_w_outer)
                
                c_outer_tip = c_tip[:3] + [current_alpha * 0.6]
                c_outer_thresh = c_thresh[:3] + [current_alpha * 0.6]
                
                self.platform.renderer.draw_rect(c_outer_tip, b_rect_outer, softness=self.effects.blur * 2.5, gradient=(c_outer_tip, c_outer_thresh), axis=1.0, level=10.0, additive=True)

            self.platform.renderer.draw_rect(c_top, coords, 
                                             border_radius=self.style.corner_radius, 
                                             softness=self.style.edge_softness,
                                             segments=(self.style.segment_size, self.style.segment_gap),
                                             gradient=(c_top, c_bot),
                                             axis=-1.0, # Bottom anchored
                                             level=ypc,
                                             gradient_image=self.gradient_surface,
                                             texture_holder=self)

            pcoords = self.float_abs_rect( offset=(offset, self.abs_h*(1-peak)),  wh=[w, self.style.peak_h] )
            self.draw_peak(peak*self.h, False, pcoords)

            # print("Bar.draw > coords ", coords, "peak coords", coords, "ypc", ypc, "peak", peak, "col", col)

    """ Draw a horizontal bar """
    def drawH(self, offset, ypc, w, peak=0, colour_index=None):
        width  = self.abs_w
        if self.style.flip:

            coords = self.float_abs_rect( offset=(0, offset),  wh=[width, w] )
            
            c_left = self.colours.get(self.colours.num_colours, False) # High value (Red) on the moving left edge
            c_right = self.colours.get(0, False)        # Low value (Green) on the fixed right edge
            
            if colour_index is not None:
                c_left = c_right = self.colours.get(colour_index)

            # --- Bloom Logic (Horizontal Flip=True, Grows Left) ---
            if ypc > self.effects.threshold:
                range_above = max(0.001, 1.0 - self.effects.threshold)
                excess_ratio = (ypc - self.effects.threshold) / range_above
                excess_ratio = max(0.0, min(1.0, excess_ratio))
                alpha_ratio = excess_ratio ** self.effects.power
            else:
                alpha_ratio = 0.0

            smoothed_ratio = self._get_smoothed_bloom(offset, alpha_ratio)

            if smoothed_ratio > 0.01:
                jitter = random.uniform(0.98, 1.02)
                current_alpha = self.effects.alpha * smoothed_ratio * jitter
                
                bloom_w = (ypc - self.effects.threshold) * self.abs_w
                bloom_x = coords[0] + (1.0 - ypc) * self.abs_w
                
                c_tip = list(self.colours.get(ypc * self.colours.num_colours)[:3]) + [current_alpha]
                c_thresh = list(self.colours.get(self.effects.threshold * self.colours.num_colours)[:3]) + [current_alpha]

                # Inner
                inner_scale = 1.0 + (self.effects.scale - 1.0) * 0.2
                b_h_inner = coords[3] * (inner_scale - 1.0)
                b_rect_inner = (bloom_x - b_h_inner/2, coords[1] - b_h_inner/2, bloom_w + b_h_inner, coords[3] + b_h_inner)
                self.platform.renderer.draw_rect(c_tip, b_rect_inner, softness=self.effects.blur, gradient=(c_tip, c_thresh), axis=2.0, level=10.0, additive=True)

                # Outer
                outer_scale = 1.0 + (self.effects.scale - 1.0) * (0.5 + 0.5 * smoothed_ratio)
                b_h_outer = coords[3] * (outer_scale - 1.0)
                b_rect_outer = (bloom_x - b_h_outer/2, coords[1] - b_h_outer/2, bloom_w + b_h_outer, coords[3] + b_h_outer)
                
                c_outer_tip = c_tip[:3] + [current_alpha * 0.6]
                c_outer_thresh = c_thresh[:3] + [current_alpha * 0.6]
                self.platform.renderer.draw_rect(c_outer_tip, b_rect_outer, softness=self.effects.blur * 2.5, gradient=(c_outer_tip, c_outer_thresh), axis=2.0, level=10.0, additive=True)

            self.platform.renderer.draw_rect(c_left, coords, 
                                             border_radius=self.style.corner_radius, 
                                             softness=self.style.edge_softness,
                                             segments=(self.style.segment_size, self.style.segment_gap),
                                             gradient=(c_left, c_right),
                                             axis=-2.0, # Right anchored
                                             level=ypc,
                                             gradient_image=self.gradient_surface,
                                             texture_holder=self)

            peak_w  = width*(peak)
            pcoords = self.float_abs_rect( offset=(width*(1-peak), offset),  wh=[self.style.peak_h, w] )
            self.draw_peak(peak_w, False, pcoords)

        else:
            coords = self.float_abs_rect( offset=(0, offset),  wh=[width, w] )
            
            c_left = self.colours.get(0, False)
            c_right = self.colours.get(self.colours.num_colours, False)
            
            if colour_index is not None:
                c_left = c_right = self.colours.get(colour_index)

            # --- Bloom Logic (Horizontal Flip=False, Grows Right) ---
            if ypc > self.effects.threshold:
                range_above = max(0.001, 1.0 - self.effects.threshold)
                excess_ratio = (ypc - self.effects.threshold) / range_above
                excess_ratio = max(0.0, min(1.0, excess_ratio))
                alpha_ratio = excess_ratio ** self.effects.power
            else:
                alpha_ratio = 0.0

            smoothed_ratio = self._get_smoothed_bloom(offset, alpha_ratio)

            if smoothed_ratio > 0.01:
                jitter = random.uniform(0.98, 1.02)
                current_alpha = self.effects.alpha * smoothed_ratio * jitter
                
                bloom_w = (ypc - self.effects.threshold) * self.abs_w
                bloom_x = coords[0] + self.effects.threshold * self.abs_w
                
                c_tip = list(self.colours.get(ypc * self.colours.num_colours)[:3]) + [current_alpha]
                c_thresh = list(self.colours.get(self.effects.threshold * self.colours.num_colours)[:3]) + [current_alpha]

                # Inner
                inner_scale = 1.0 + (self.effects.scale - 1.0) * 0.2
                b_h_inner = coords[3] * (inner_scale - 1.0)
                b_rect_inner = (bloom_x - b_h_inner/2, coords[1] - b_h_inner/2, bloom_w + b_h_inner, coords[3] + b_h_inner)
                self.platform.renderer.draw_rect(c_thresh, b_rect_inner, softness=self.effects.blur, gradient=(c_thresh, c_tip), axis=2.0, level=10.0, additive=True)

                # Outer
                outer_scale = 1.0 + (self.effects.scale - 1.0) * (0.5 + 0.5 * smoothed_ratio)
                b_h_outer = coords[3] * (outer_scale - 1.0)
                b_rect_outer = (bloom_x - b_h_outer/2, coords[1] - b_h_outer/2, bloom_w + b_h_outer, coords[3] + b_h_outer)
                
                c_outer_tip = c_tip[:3] + [current_alpha * 0.6]
                c_outer_thresh = c_thresh[:3] + [current_alpha * 0.6]
                self.platform.renderer.draw_rect(c_outer_thresh, b_rect_outer, softness=self.effects.blur * 2.5, gradient=(c_outer_thresh, c_outer_tip), axis=2.0, level=10.0, additive=True)

            self.platform.renderer.draw_rect(c_left, coords, 
                                             border_radius=self.style.corner_radius, 
                                             softness=self.style.edge_softness,
                                             segments=(self.style.segment_size, self.style.segment_gap),
                                             gradient=(c_left, c_right),
                                             axis=2.0, # Left anchored
                                             level=ypc,
                                             gradient_image=self.gradient_surface,
                                             texture_holder=self)

            peak_w  = peak * width
            pcoords = self.float_abs_rect( offset=(peak_w, offset),  wh=[self.style.peak_h, w] )
            self.draw_peak(peak_w, False, pcoords)

class Image:
    DEFAULT_OPACITY = 255
    DEFAULT_CACHE   = 300
    def __init__(self, parent, wh=None, path=None, align=None, scalers=None, opacity=None, outline=None, target_wh=None, reflection=None):

        self.image_cache = Cache(Image.DEFAULT_CACHE)
        self.path        = path #This is the tag for the image ie str of filename or URL - used as the key for the cache
        self.parent      = parent
        self.opacity     = Image.DEFAULT_OPACITY if opacity is None else opacity
        self.old_image_data = None
        self.target_wh   = parent.abs_rect()[-2:] if target_wh is None else target_wh 
        self._gl_texture = None
        self.reflection  = reflection

        if path is not None:
            self.scaleInProportion(path)

        # print("Image.__init__>", self.opacity, parent.framestr())

    def download_image(self, url):
        # response = requests.get(url)
        # return BytesIO(response.content)
        try:
            # Use a short timeout for network requests
            response = requests.get(url, timeout=5)
            response.raise_for_status() # Raise exception for bad status codes (4xx or 5xx)
            return BytesIO(response.content)
        except requests.exceptions.RequestException as e:
            print(f"Image.download_image ERROR: Failed to fetch image from URL {url}: {e}")
            return None
        
    def scaleInProportion_and_crop(self, imagesurface, target_wh):
        # target_wh is the final frame dimensions (W_target, H_target)
        W_target, H_target = target_wh
        W_orig, H_orig = imagesurface.get_size()

        # 1. Calculate the scale factor to ensure the image COVERS the frame
        # We want max(W_scaled / W_target, H_scaled / H_target) >= 1
        # To cover, the scale factor must be MAX(W_target/W_orig, H_target/H_orig)
        scale_w = W_target / W_orig
        scale_h = H_target / H_orig
        
        scale_factor = max(scale_w, scale_h)

        # 2. Calculate the dimensions of the oversized, scaled image
        W_scaled = int(W_orig * scale_factor)
        H_scaled = int(H_orig * scale_factor)
        
        # 3. Perform the scaling
        scaled_image = pygame.transform.scale(imagesurface, (W_scaled, H_scaled))

        # 4. Determine the offset for centering the scaled image
        # We want to crop from the middle. Calculate how much to shift.
        # The oversized amount is W_scaled - W_target and H_scaled - H_target.
        # We shift half of that amount to center it.
        crop_x_offset = (W_scaled - W_target) // 2
        crop_y_offset = (H_scaled - H_target) // 2
        
        # 5. Crop the scaled image by blitting the centered portion
        
        # Create a new Surface of the final target size
        cropped_surface = pygame.Surface((W_target, H_target), pygame.SRCALPHA)
        
        # Blit the scaled image onto the new surface, starting the blit 
        # at a negative offset to grab the center portion.
        # A negative (x, y) argument to blit is what performs the "crop" effect.
        cropped_surface.blit(scaled_image, (-crop_x_offset, -crop_y_offset))
        
        # print for debug (use your existing logging)
        # print("Image.scaleinproportion and Crop> from", W_orig, H_orig, 
        #     "scaled to", (W_scaled, H_scaled), 
        #     "cropped to target", target_wh)
          
        return cropped_surface

    def scaleInProportion(self, image_ref, target_wh=None):
        if image_ref is None: return
        if target_wh is None: target_wh = self.target_wh

        # path = self.download_image(image_ref) if 'http' in image_ref else image_ref
        # imagesurface = pygame.image.load(path).convert_alpha()

        imagesurface = None
        try:
            if 'http' in image_ref:
                path = self.download_image(image_ref) 
                if path is None: return None # Download failed, log already printed
            else:
                path = image_ref

            imagesurface = pygame.image.load(path).convert_alpha()
            
        except pygame.error as e:
            print(f"Image.scaleInProportion ERROR: Pygame failed to load image '{image_ref}'. Error: {e}")
            return None
        except Exception as e:
             print(f"Image.scaleInProportion UNEXPECTED ERROR during load '{image_ref}': {e}")
             return None

        if imagesurface is None:
            return None

        image = self.scaleInProportion_and_crop(imagesurface, target_wh)
        self.image_cache.add(image_ref, image)
        # print("Image.scaleinproportion> from", original_width, original_height, "to", wh, "target", self.target_wh, self.parent.geostr())
        return image

    # Drawing is possibly a two step process
    # 1. work out if anything has changed
    # 2. draw unconditionally the current Image, assume the background has been cleaned

    def new_content_available(self, image_data=None):
        # print("Image.draw>", self.boundswh[1], self.framestr(), self.geostr())

        if image_data is None:  image_data = self.path  
        return image_data != self.old_image_data

    def draw(self, image_data=None, coords=None):   
        if coords is None: coords = self.parent.abs_origin()
        if image_data is None:  image_data = self.path   

        image = self.image_cache.find(image_data)
        if image is None:   
            image = self.scaleInProportion(image_data)


        if image is not None:
            
            if image_data != self.old_image_data:
                self._gl_texture = None

            # frame_width  = 0 if self.outline is None else self.outline.width 
            self.parent.platform.renderer.blit(image, coords, texture_holder=self, opacity=self.opacity, reflection=self.reflection)
            self.old_image_data = image_data
            # print("Image.draw> New image", self.opacity, coords, image_data)
        else:
            pass
            # print("Image.draw> attempt to draw an None image", image, image_data)
        

class ArcsOctaves(Frame):
    """ Lines are for drawing meter needles, oscilogrammes etc """
    def __init__(self, parent, wh=None, colour=None, align=('centre', 'middle'), theme='std', NumOcts=5, scalers=None):

        self.NumOcts = NumOcts
        Frame.__init__(self, parent, align=align)
        self.resize( wh )

        self.scalar  = self.h/(NumOcts)/2
        self.colours = Colour(self.theme,12)

        # print("Arcs.init> ", self.geostr())

    def draw(self, octave, notes ):
        # print("Octave ", octave, " notes", notes, "Max ", MaxOcts)
        """ This draws a set of arcs that are at a radius 'octave'.
            each arc coloured according to the intensity of the note value.
            There are len(note) arcs drawn """

        Oct1    = self.h/self.NumOcts
        arc     = 2*PI/len(notes)
        top     = -PI/2
        box     = Oct1 * (octave+1)
    #     # set colour according to amplitude, fixed width
        for i in range(0 , len(notes)):

            if np.isinf(notes[i]): break
            amp = int(self.bounds( (notes[i]*self.scalar),0,100))
            colour = self.colours.get(i) #need to work out how many colours there needs to be
            pygame.draw.arc(self.platform.screen, colour, [self.centre[0]-box//2,self.centre[1]-box//2, box, box], arc*i+top, arc*i+(0.9*arc)+top, amp)
            # print("ArcsOctaves.draw> a", a, "note", i, "octave", octave)

    def bounds(self, v, a=0, b=255):
        if v > b:
            return b
        elif v< a:
            return a
        else:
            return v

class Box(Frame):
    def __init__( self, parent, colour_index=0, theme='std', box=None, width=None, radius=5, align=('centre', 'middle') ):

        self.width    = box[1] if width is None else width
        self.radius   = radius

        Frame.__init__(self, parent, align=align)
        if box is not None:  self.resize( box )

        self.colour_index = colour_index
        self.colours      = Colour(self.theme, self.w)
        # print("Box.init> wh", bounds, self.wh, self.geostr())

    def draw(self, offset=(0,0), colour_index=0, wh=None, pc=None):
        if colour_index is None: colour_index = self.colour_index
        if wh is None: wh = self.wh
        if pc is not None: wh = [self.wh[0]*pc, self.wh[1]]
        coords = self.abs_rect(offset=offset,  wh=wh)
        colour = self.colours.get(colour_index)
        self.platform.renderer.draw_rect(colour, coords, width=self.width)
        # print("Box.draw> offset", self.platform.h, offset, "coords", coords, "top", self.top, self.geostr())

    def drawH(self, pc, flip=False, colour_index=None, offset=(0,0)):
        if flip:
            coords = self.abs_rect( offset=(self.w*pc+offset[0], offset[1]),  wh=[self.w*(1-pc), self.width] )
        else:
            coords = self.abs_rect( offset=offset,  wh=[self.w*pc, self.width] )

        colour = self.colours.get(self.w*pc, False) if colour_index is None else self.colours.get(colour_index)
        self.platform.renderer.draw_rect(colour, coords, border_radius=self.radius)

"""
Lines are for drawing meter needles, oscilogrammes etc
"""
class Line(Frame):
    def __init__( self, parent, colour=None, width=1, align=None, theme=None, scalers=(1.0,1.0), background=None,\
                  circle=True, endstops=(PI/2, 3* PI/2), radius=100, centre_offset=0, tick_pc=1.0, amp_scale=0.9):

        self.width     = width
        self.circle    = circle
        self.radius    = radius
        self.tick_pc   = tick_pc
        self.linespace = []   # array of line circles
        self.amp_scale = amp_scale

        Frame.__init__(self, parent, align=align, theme=theme, scalers=scalers, background=background)
        self.anglescale(radius, endstops, centre_offset)  # True if val is 0-1, False if -1 to 1

        self.colour    = colour
        self.colours   = Colour(self.theme, self.radius)
        # print("Line.init> ", bounds, self.geostr(), self.anglestr())

    def draw(self, offset, colour=None):   #(x,y) offset
        if colour is None: colour = self.colour
        coords = self.abs_rect()
        colour_index = self.colours.get(colour)
        self.platform.renderer.draw_line(colour_index, coords[:2], coords[2:], self.width)
        # print("Line.draw> offset", self.platform.h, offset, "coords", coords, "top", self.top, self.geostr())


    def drawFrameCentredVector(self, val, colour=None, width=0, amplitude=1.0, gain=0, tick_pc=None):
        """ tick_pc is the percent of the line to draw from outside in, useful if the pivot is below the line
            val is the angle to draw the line
        """
        if colour is None: colour = self.colour
        if width == 0: width = self.width
        if tick_pc is None: tick_pc = self.tick_pc
        xy         = self.anglexy(val, self.radius,  amp_scale=amplitude, gain=gain)#, xyscale=self.xyscale)
        ab         = self.anglexy(val, self.radius*(1-tick_pc))#, xyscale=self.xyscale)

        colour_index = self.colours.get(colour)  # Add a get col
        # print("Line.drawFrameCentredVector: val %f, ab %s, xy %s, yoff %f, len %d" % (val, ab, xy, self.centre_offset, self.radius))
        self.platform.renderer.draw_line(colour_index, ab, xy, width)


    def draw_mod_line(self, points, colour=None, amplitude=1.0, gain=1.0):
        size   = len(points)
        # Linear scalars
        yscale = self.h       # scalar for the height amplitude of the line modulation
        xscale = self.w/size  # x scalar

        # Circular scalars
        line   = []

        for i, v in enumerate(points):
            if self.circle:
                line.append(self.anglexy(i/size, self.radius, gain=v*gain,amp_scale=self.amp_scale*amplitude,  xyscale=self.xyscale) )
            else:
                line.append(self.abs_origin(  offset=(xscale*i, 0.5*yscale*(1+v*amplitude*self.amp_scale)) ))


        colour = self.radius*(self.amp_scale*amplitude) if colour is None else 'alert' # Add a get col
        colour_index = self.colours.get(colour)
        self.platform.renderer.draw_lines(colour_index, self.circle, line, width=self.width)


    def make_ripple(self, size):
        wh     = (self.xyscale[0]*size, self.xyscale[1]*size)
        xy     = self.abs_origin( offset=(self.centre[0]-wh[0]//2, self.centre[1]-wh[1]//2))
        return pygame.Rect(xy, wh)

    def draw_mod_ripples(self, points, trigger={}, colour=None, amplitude=1.0):
        xc, yc       = self.centre[0], self.centre[1]
        aspect_ratio = self.w/self.h
        xyscale      = (aspect_ratio, 1.0) if self.w > self.h else (1.0, aspect_ratio)
        frame        = pygame.Rect(self.abs_rect(screen_h=self.platform.h))
        gain         = 1.01
        col          = 'light'

        if 'bass' in trigger:
            col = 'alert'

        if 'treble' in trigger:
            col  = 'foreground'  # velocity the dots move outward

        # For all the line space, calculate the velocities and move
        # a ripple is simple the size - one value
        for ripple in self.linespace:
            self.linespace.remove(ripple)
            new_size = int(gain*ripple[0].height)
            new_ripple = self.make_ripple(new_size)
            if frame.contains(new_ripple) and len(self.linespace)<1:
                self.linespace.append((new_ripple, ripple[1]))

        if amplitude>0.8 and len(self.linespace)<1:
            ripple = self.make_ripple(self.radius*(self.amp_scale*amplitude)*2)
            colour_index = self.colours.get(col)
            self.linespace.append((ripple,colour_index))

        for ripple in self.linespace:
            pygame.draw.ellipse(self.platform.screen, ripple[1], ripple[0], width=1)

    def drawFrameCentredArc(self, val, colour=None):
        if colour is None: colour = self.colour
        xy     = self.anglexy(val, self.radius)
        colour_index = self.colours.get(colour)  # Add a get col
        arcwh  = [self.radius*2, self.radius*2]
        coords = self.abs_centre( offset=(-arcwh[0]/2, -arcwh[1]/2) )+arcwh
        # print("Line.drawFrameCentredArc>", coords, self.h*(self.centre_offset), self.geostr())
        pygame.draw.arc(self.platform.screen, colour_index, coords, 3*PI/2+self.endstops[0], 3*PI/2+self.endstops[1], self.width)


class Text:
    """
    Text is all about creating words & numbers that are scaled to fit within
    rectangles

    Fonts are scaled to fit
    update triggers a resizing of the text each time its drawn
    """
    TYPEFACE = 'fonts/Inter/Inter-VariableFont_opsz,wght.ttf'
    READABLE = 18   # smallest readable font size
    MAX_LINES= 1

    def __init__(self, parent, text='Default text', fontmax=None, reset=True, wrap=False, justify=('centre','middle'),\
                 endstops=(PI/2, 3* PI/2), radius=100, centre_offset=0, colour=None):  #Create a font to fit a rectangle

        self.text     = text
        self.wrap     = wrap
        self.reset    = reset   # need to assume that justifying is done differently
        self.radius   = radius
        self.justify  = justify if len(justify) == 2 else (justify, 'middle') # 'left', 'centre', right' --> text is always aligned into the middle of the screen (could use an align attribute)
        self.parent   = parent

        self.cache    = Cache()
        self.colour   = colour
        self.colours  = parent.colours
        self.fontmax  = parent.abs_h if fontmax is None else fontmax 
        self.rendered_surface = None
        self.last_params      = None
        self._gl_texture      = None

        # self.parent.anglescale(radius, endstops, centre_offset)  # True if val is 0-1, False if -1 to 1
        self.update()
        # print("Text.__init__> ", self.colours, self.fontwh, self.text,self.parent.geostr())

    def update(self, text=None, fontmax=None):
        try:
            if text is None: text=self.text
            self.drawtext = self.cache.find(text)
            self.font, self.fontwh = self.scalefont(self.parent.abs_wh, text, fontmax)  # You can specify a font

            if self.drawtext is None:
                # self.font, self.fontwh = self.scalefont(self.boundswh, text, fontmax)  # You can specify a font
                self.cache.add(text, self.drawtext)
                # print("Text.update> new text cached & reset", text, self.fontwh, self.geostr())  
            else:
                # print("Text.update> text found", text, self.fontwh, self.geostr())
                pass
            if self.reset: 
                # self.resize( self.fontwh )
                # print("Text.update> reset disabled")
                pass
  

        except Exception as e:
            print("Text.update> ERROR > %s > wh %s, fontwh %s, text<%s>, %s " % (e, self.parent.geostr() ))

    def new_content_available(self, text=None):
        if text is None: text = self.text
        # print("Text.new_content_available>", text != self.text, self.boundswh[1], self.framestr(), self.geostr())
        return text != self.text        

    @property
    def fontsize(self):
        return self.fontwh[1]
    
    def shrink_fontsize(self, wh, text, fontmax=None):  #shrink the font to fit the rect
        # print("Text.shrink_fontsize> attempt", text, wh, self.fontmax, self.boundswh)
        fontsize    = self.fontmax if fontmax is None else fontmax
        font        = pygame.font.Font(Text.TYPEFACE, int(fontsize))
        fontwh      = self.textsize(text, font) 
        if fontwh[0]> wh[0]:  
            fontsize   = fontsize * wh[0]/ fontwh[0]
            font        = pygame.font.Font(Text.TYPEFACE, int(fontsize))
            fontwh      = self.textsize(text, font)
        if fontwh[1]> wh[1]:  
            fontsize    = fontsize *  wh[1]/fontwh[1]
            font        = pygame.font.Font(Text.TYPEFACE, int(fontsize))
            fontwh      = self.textsize(text, font)

        # print("Text.shrink_fontsize>", text, wh, fontwh, fontsize, fontmax)
        return font, list(fontwh)


    def scalefont(self, wh, text, fontmax):  #scale the font to fit the rect, with a min fontsize
        # self.fontsize = wh[1] if self.fontmax == 0 else self.fontmax
        
        # Handle explicit newlines first
        if '\n' in text:
            self.drawtext = text.split('\n')
            num_lines = len(self.drawtext)
            # Use the longest line to determine font size, with height adjusted for number of lines
            longest_line = max(self.drawtext, key=len)
            line_wh = (wh[0], wh[1] / num_lines)
            font, fontwh = self.shrink_fontsize(line_wh, longest_line, fontmax)
            # Adjust height for multiple lines
            fontwh[1] *= num_lines
            return font, fontwh

        font, fontwh = self.shrink_fontsize(wh, text, fontmax)

        if self.wrap and fontwh[1] < Text.READABLE:  # split into two lines and draw half size
            try:
                self.drawtext = wrap(text, width=1+len(text)//2, max_lines=Text.MAX_LINES)
                # print("wrap", self.drawtext)
                font, fontwh  = self.shrink_fontsize(wh, self.drawtext[0], fontmax)
                fontwh[1]    *= 2  # double height, 2 lines
            except ValueError as error:
                print("Text.scalefont> textwrap failed" , error )
                self.drawtext = [text[:(1+len(text)//2)]]
                # print("wrap", self.drawtext)
                font, fontwh  = self.shrink_fontsize(wh, self.drawtext[0], fontmax)
        else:
            self.drawtext = [text]

        # print("Text.scalefont> max %s, target wh %s, fontwh %s, text<%s>, %s" % (self.whmax, wh, fontwh, text, self.drawtext))
        return font, fontwh

    def draw(self, text=None, offset=(0,0), coords=None, colour=None, fontmax=None):  #Draw the text in the corner of the frame
        if text is not None and text != self.text:
            self._gl_texture = None
            self.text = text
        elif text is None:
            text = self.text 

        fontmax = self.fontmax if fontmax is None else fontmax

        if self.reset: self.update(text, fontmax)

        if coords is None : coords = self.parent.abs_origin()    
        if colour is None : colour = self.colour
        colour_index = self.colours.get(colour)

        if hasattr(self, 'font') and self.font is not None:
            
            lines = self.drawtext if isinstance(self.drawtext, list) else [self.drawtext[0]]
            line_height = self.font.get_height()
            total_height = line_height * len(lines)
            
            # Only cache texture if single line, otherwise we overwrite the cache for each line
            holder = self if len(lines) == 1 else None
            
            # Calculate starting Y based on total height to keep it centered vertically if needed
            # But align_coords handles the block. We just need to stack them.
            
            # Check cache
            # current_params = (line, colour_index, id(self.font))
            
            for i, line in enumerate(lines):
                try:
                    info = self.font.render(line, True, colour_index)
                    
                    size = info.get_rect()
                    # Align the block of text, then offset for this specific line
                    # Note: align_coords aligns the *whole* block usually, but here we align line by line
                    # relative to the center of the text block.
                    
                    # Simple vertical stacking:
                    line_coords = list(self.parent.align_coords(coords, size[-2:], self.justify))
                    # Adjust Y for line number (centering the block of text)
                    start_y_offset = -(total_height / 2) + (line_height / 2)
                    line_coords[1] += int(start_y_offset + (i * line_height))
                    
                    self.parent.platform.renderer.blit(info, line_coords, texture_holder=holder)
                except pygame.error as e:
                    print(f"Text.draw Pygame Render ERROR for line '{line}': {e}")


    def drawVectoredText(self, val, text=None, colour=None):
        if text is None:
            text = self.text

        # 1) Absolute position from dial transform
        xy = self.parent.anglexy(val, self.radius)

        # 2) Get text size
        w, h = self.textsize(text)

        # 3) Centre text at absolute position
        x = int(xy[0] - w/2)
        y = int(xy[1] - h/2)
        if colour is None : colour = self.colour
        colour_index = self.colours.get(colour)

        # 4) **** DRAW DIRECT TO SCREEN, NOT VIA self.draw() ****
        # This bypasses align_coords and frame offsets entirely.
        
        # Try to use cached surface if it matches, otherwise render fresh
        if text == self.text and self.rendered_surface and self.last_params == (text, colour_index, id(self.font)):
            surface = self.rendered_surface
            self.parent.platform.renderer.blit(surface, (x, y), texture_holder=self)
        else:
            # Note: We don't cache this one as it might be transient or different from self.text
            surface = self.font.render(text, True, colour_index)
            self.parent.platform.renderer.blit(surface, (x, y))
            



    def textsize(self, text=None, font=None):  #return w, h
        if text == None: text=self.text
        if font == None: font=self.font
        text_surface = font.render(text, True, (0, 128, 255))
        text_abcd = text_surface.get_rect()
        # print("Text.textsize > ", (text_abcd[2], text_abcd[3]))
        return (text_abcd[2], text_abcd[3])

"""
Dots are for drawing circles on progress bars, mood dots in space on visualisers etc
"""
class Dots(Frame):
    def __init__( self, parent, colour_index=None, width=1, align=('centre', 'middle'), theme='std', scalers=(1.0,1.0), \
                  circle=True, endstops=(PI/2, 3* PI/2), radius=100, centre_offset=0, amp_scale=1.0, dotcount=1000):

        self.width      = width
        self.circle     = circle
        self.radius     = radius
        self.dotspace   = []
        self.dotcount   = dotcount
        self.amp_scale  = amp_scale
        Frame.__init__(self, parent, align=align, scalers=scalers)
        self.anglescale(radius, endstops, centre_offset)  # True if val is 0-1, False if -1 to 1

        self.colour_index = colour_index
        self.colours      = Colour(self.theme, radius)
        # print("Dots.init> ", bounds, self.geostr(), self.anglestr())

    def draw_circle(self, offset, colour_index=0):   #(x,y) offset
        if colour_index is None: colour_index = self.colour_index
        coords = self.abs_rect()
        colour = self.colours.get(colour_index)
        pygame.draw.ellipse(self.platform.screen, colour, coords, self.width)
        # print("Dots.draw> offset", self.platform.h, offset, "coords", coords, "top", self.top, self.geostr())

    def draw_mod_dots(self, points, trigger={}, colour=None, amplitude=1.0, gain=0.8):
        size         = len(points)
        xc, yc       = self.centre[0], self.centre[1]
        col          = self.radius*(self.amp_scale*amplitude) if colour is None else colour # Add a get col
        accelerator  = 1.01

        if 'bass' in trigger:
            accelerator = 1.05  # velocity the dots move outward
            col = 'light'

        if 'treble' in trigger:
            accelerator = 1.1
            col  = 'foreground'  # velocity the dots move outward

        # For all the dot space, calculate the velocities and move
        for dot in self.dotspace:
            self.dotspace.remove(dot)
            x1 = int(accelerator*(dot[0]-xc)+ xc)
            y1 = int(accelerator*(dot[1]-yc)+ yc)
            # x1 = int(accelerator*(dot[0]))
            # y1 = int(accelerator*(dot[1]))
            # check dot is still on the screen
            # print("Dots.draw_mod_dots> acc", [x1,y1, dot[2]], len(self.dotspace), trigger)
            if x1>=0 and x1<=self.w and y1>0 and y1<self.h and len(self.dotspace)<self.dotcount:
            # if len(self.dotspace)<self.dotcount:    
                self.dotspace.append([x1,y1, dot[2]])
            # else:

            # print("Dots.draw_mod_dots> acc", [x1,y1, dot[2]], len(self.dotspace), trigger)

        colour = self.colours.get(col)

        for i, v in enumerate(points):
            # xy = self.anglexy(i/size, self.radius, gain=1.5, amp_scale=abs(v), xyscale=(xscale,1.0))
            xy = self.anglexy(i/size, self.radius, gain=v*gain,amp_scale=self.amp_scale*amplitude,  xyscale=self.xyscale)
            # colour = self.colours.get(v*gain)
            if v>0.00: # and len(trigger)>1: 
                self.dotspace.append([ int(xy[0]),int(xy[1]),colour])

            # Draw the dot space and calculate the velocities
        for dot in self.dotspace:
            # print("Dots.draw_mod_dots", (dot[0], dot[1]), dot[2], size, self.geostr())

            # if dot[0]<0 or dot[0]>self.w or dot[1]<0 or dot[1]>self.h: # and len(self.dotspace)<self.dotcount:
            #     self.dotspace.remove(dot)
            # else:
            self.platform.screen.set_at( (dot[0], dot[1]), dot[2] )
        # print("Dots.draw_mod_dots>", len(self.dotspace), trigger)
                

"""
    Outlines can be drawn around Frames.  They are drawn at the frame edges according to the coordinates passed.
    The flexible attributes can create a range of types of outlines, all passed in a dict:
        width           - the thickness of the frame in pixels
        colour_index    - the colour of the frame according to the palette
        radius          - the degree of curvature at the corners, 0 is square
        opacity         - 255 is fully opaque, 0 is transparent.  Good for blending
"""
class Outline:
    #Default outline
    OUTLINE = { 'width' : 1, 'radius' : 0, 'colour' : 'foreground', 'opacity': 255}

    def __init__(self, frame, outline=None):
        self.frame         = frame
        self.outline       = outline
        if self.outline is None: return
        # print("Outline.init>", self.frame.framestr(), self.frame.outline)
        #only one parameter is needed, else the default is set
        if 'colour'       not in self.outline:   self.outline['colour']       = Outline.OUTLINE['colour'] 
        if 'opacity'      not in self.outline:   self.outline['opacity']      = Outline.OUTLINE['opacity']      
        if 'radius'       not in self.outline:   self.outline['radius']       = Outline.OUTLINE['radius']       
        if 'width'        not in self.outline:   self.outline['width']        = Outline.OUTLINE['width']        

    def draw(self, coords=None):
        if self.outline is None: return [0,0,0,0]
        width = 0 if  'width' not in self.outline else self.outline['width'] 
        if  width == 0: return [0,0,0,0]
        if coords       is None: coords = self.frame.abs_outline() 

        colour       = self.outline['colour'] 
        opacity      = self.outline['opacity'] 
        radius       = self.outline['radius'] 
        # print("Outline.draw>", self.frame.framestr(), self.frame.colour)    
        colour_index = self.frame.colours.get(colour, opacity=opacity)
        surface      = pygame.Surface( (self.frame.platform.screen.get_width(), self.frame.platform.screen.get_height()), pygame.SRCALPHA)

        # pygame.draw.rect(surface, colour, coords, border_radius=radius, width=width)
        # self.frame.platform.screen.blit(surface, (0,0) )
        self.frame.platform.renderer.draw_rect(colour_index, coords, border_radius=radius, width=width)

        self.frame.platform.dirty_mgr.add(tuple(self.frame.abs_outline()))
        # print("Outline.draw> coords ", coords, "radius ", radius, "width ", width )   
        return coords     

    @property
    def w(self):
        if self.outline is None or 'width' not in self.outline:
            return 0
        else: 
            return self.outline['width'] 

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
    BACKGROUND_IMAGE_PATH = 'backgrounds'


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
            path = Background.BACKGROUND_IMAGE_PATH + '/' + self.background['image']
            self.background_image = Image(self.frame, path=path, opacity=self.background['opacity'], target_wh=self.frame.abs_background()[-2:])
        print("Background.__init__> background image created", self.background)    


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
            # print("Background.draw> Drawing background", self.background, self.frame.framestr())
            # if self.is_opaque():
            #     self.frame.platform.screen.fill(BLACK, pygame.Rect(self.frame.abs_background() ))

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

                # 2. Create a temporary Surface for the semi-transparent drawing
                # alpha_surface = pygame.Surface((rect_w, rect_h), pygame.SRCALPHA)
                # alpha_surface.set_alpha(self.background['opacity']) 

                # Fill the *entire* temporary surface with the color
                colour = self.frame.colours.get(self.background['colour'])
                # alpha_surface.fill(colour)
                
                # Blit the temporary, transparent surface onto the main screen
                # self.frame.platform.screen.blit(alpha_surface, rect_coords[:2]) # Use (x, y) coordinates
                
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

                # surface = pygame.Surface( (self.frame.platform.screen.get_width(), self.frame.platform.screen.get_height()), pygame.SRCALPHA)
                # self.frame.platform.screen.fill(colour, pygame.Rect(self.frame.abs_background() ))
                # self.frame.platform.screen.blit((0,0) )
                # print("Background.draw> colour ", self.frame.abs_background() )  
 
            else:
                if self.background['image'] in ('artist', 'album'):
                    image_ref = self.update_fn()
                else:
                    image_ref =None

                self.background_image.draw(image_data=image_ref, coords=self.frame.abs_background()[:2]) 

            self.frame.platform.dirty_mgr.add(tuple(self.frame.abs_background()))
            # print("Background.draw> ", self.background )  

        # print("Background.draw> draw ", perform_update, self.background['per_frame_update'], self.background, self.frame.framestr() )  
  


#---- End Background -------        
