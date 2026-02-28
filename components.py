#!/usr/bin/env python
"""
Display driver classes

Low level platform dynamics


v1.0 baloothebear4 1 Dec 2023   Original, based on Pygame visualiser mockups
v1.1 baloothebear4 Feb 2024   refactored as part of pyvisualiseer

"""

import pygame, time
# import collections
from   pygame.locals import *
import numpy as np
from   framecore import Frame, Cache, Colour
from   textwrap import shorten, wrap
from   io import BytesIO
import requests
import warnings
import os
""" Prevent image coolour warnings: libpng warning: iCCP: known incorrect sRGB profile,"""
warnings.filterwarnings("ignore", category=UserWarning, module="pygame")

PI = np.pi


class Bar(Frame):
    """
    Bars have parameters:
        - colour modes:
            'vert' according to y
            's' solid colour
            'horz' colour according to x
        - colour theme:  tuple of colours over which the colours range - one colour is fixed colour
        - leds ie discrete with colours
        - vertical or horizontal,
        - left or right
        - peak lines
    """
    def __init__(self, parent, scalers=None, align=('centre', 'bottom'), theme=None, \
                 box_size=(100,100), led_h=10, led_gap=4, peak_h=1, right_offset=0, \
                 flip=False, radius=0, tip=False, orient='vert', col_mode=None):

        self.right_offset = right_offset

        Frame.__init__(self, parent, align=align,theme=theme, scalers=scalers)
        self.resize( box_size )
        # parent += self

        self.led_h      = led_h
        self.led_gap    = led_gap
        self.peak_h     = peak_h
        self.radius     = radius    # this makes rounded corners 0= Rectangle - works really as a % of the height
        if col_mode is None: col_mode = orient
        colour_range    = self.h if col_mode == 'vert' else self.w
        self.colours    = Colour(self.theme, colour_range)
        self.flip       = flip
        self.tip        = tip       # creates a rounded tip to the bar
        self.orient     = orient
        # parent += self
        # print("Bar.__init__", self.geostr())

    def draw_peak(self, peak_h, flip, peak_coords):
        if peak_h> 0.0:
            colour = self.colours.get( colour_index=peak_h , flip=flip)  #
            pygame.draw.rect(self.platform.screen, colour, peak_coords)

    def draw(self, offset, ypc, w, peak=0, colour_index=None):
        self.tip_radius = int(w/2)
        if self.orient == 'horz':
            self.drawH(offset, ypc, w, peak, colour_index)
        else:
            self.drawV(offset, ypc, w, peak, colour_index)

    def drawV(self, offset, ypc, w, peak=0, colour_index=None):
        """ Draw Vertical Bar """
        if self.flip:
            coords = self.abs_rect( offset=(offset, 0),  wh=[w, self.abs_h*ypc] )

            for led_y in range( int(coords[1]), int(coords[1]+coords[3]) ,(self.led_h+self.led_gap)):
                colour = self.colours.get(led_y-coords[1], False) if colour_index is None else self.colours.get(colour_index) # height based
                pygame.draw.rect(self.platform.screen, colour, (coords[0], led_y, coords[2], self.led_h), border_radius=self.radius)
            else:
                if self.tip and ypc>0:
                    colour = self.colours.get(coords[3], not self.flip) if colour_index is None else self.colours.get(colour_index)
                    pygame.draw.rect(self.platform.screen, colour, (coords[0], coords[1]+coords[3], coords[2], self.led_h), border_bottom_left_radius=self.tip_radius, border_bottom_right_radius=self.tip_radius )

            pcoords = self.abs_rect( offset=(offset, peak*self.abs_h),  wh=[w, self.peak_h] )
            self.draw_peak(peak*self.h, False, pcoords)

            # print("Bar.draw (flip)> coords ", coords, "peak coords", coords, "ypc", ypc, "peak", peak)
        else:
            coords = self.abs_rect( offset=(offset, self.abs_h*(1-ypc)),  wh=[w, self.abs_h*ypc] )
            # print("Bar.draw V> coords", coords)
            for led_y in range( int(coords[1]+coords[3])-self.led_h, int(coords[1]) ,-(self.led_h+self.led_gap)):
                col    = coords[1] + coords[3]-led_y
                colour = self.colours.get(col, False) if colour_index is None else self.colours.get(colour_index) # height based

                pygame.draw.rect(self.platform.screen, colour, (coords[0], led_y , coords[2], self.led_h), border_radius=self.radius )
            else:
                if self.tip and ypc>0:
                    col    = coords[3] #self.led_h+self.led_gap
                    colour = self.colours.get(col, self.flip) if colour_index is None else self.colours.get(colour_index) # height based
                    pygame.draw.rect(self.platform.screen, colour, (coords[0], coords[1], coords[2], self.led_h), border_top_left_radius=self.tip_radius, border_top_right_radius=self.tip_radius )

            pcoords = self.abs_rect( offset=(offset, self.abs_h*(1-peak)),  wh=[w, self.peak_h] )
            self.draw_peak(peak*self.h, False, pcoords)

            # print("Bar.draw > coords ", coords, "peak coords", coords, "ypc", ypc, "peak", peak, "col", col)

    """ Draw a horizontal bar """
    def drawH(self, offset, ypc, w, peak=0, colour_index=None):
        width  = self.abs_w
        if self.flip:

            coords = self.abs_rect( offset=(width*(1-ypc), offset),  wh=[width*ypc, w] )
            # print("Bar.drawH - flip> coords", coords)
            for led_l in range( int(coords[0]+ coords[2])-self.led_h, int(coords[0]) ,-(self.led_h+self.led_gap)):
                colour = self.colours.get(coords[0]+ coords[2]-led_l, False) if colour_index is None else self.colours.get(colour_index)
                pygame.draw.rect(self.platform.screen, colour, (led_l, coords[1], self.led_h, coords[3]), border_radius=self.radius )
            else:
                if self.tip and ypc>0:
                    colour = self.colours.get(coords[2], True) if colour_index is None else self.colours.get(colour_index)
                    pygame.draw.rect(self.platform.screen, colour, (int(coords[0]+ coords[2]), coords[1], self.led_h, coords[3]), border_bottom_left_radius=self.tip_radius, border_top_left_radius=self.tip_radius )

            peak_w  = width*(peak)
            pcoords = self.abs_rect( offset=(width*(1-peak), offset),  wh=[self.peak_h, w] )
            self.draw_peak(peak_w, False, pcoords)

        else:
            coords = self.abs_rect( offset=(0, offset),  wh=[width*ypc, w] )
            # print("Bar.drawH> coords", coords)
            for led_l in range( int(coords[0]), int(coords[0]+ coords[2]) ,(self.led_h+self.led_gap)):
                colour = self.colours.get(led_l-coords[0], self.flip) if colour_index is None else self.colours.get(colour_index)
                pygame.draw.rect(self.platform.screen, colour, (led_l, coords[1], self.led_h, coords[3]), border_radius=self.radius )
            else:
                if self.tip and ypc>0:
                    colour = self.colours.get(coords[2], False) if colour_index is None else self.colours.get(colour_index)
                    pygame.draw.rect(self.platform.screen, colour, (int(coords[0]+ coords[2]), coords[1], self.led_h, coords[3]), border_bottom_right_radius=self.tip_radius, border_top_right_radius=self.tip_radius )

            peak_w  = peak * width
            pcoords = self.abs_rect( offset=(peak_w, offset),  wh=[self.peak_h, w] )
            self.draw_peak(peak_w, False, pcoords)

class Image:
    DEFAULT_OPACITY = 255
    DEFAULT_CACHE   = 300
    def __init__(self, parent, wh=None, path=None, align=None, scalers=None, opacity=None, outline=None, target_wh=None):

        self.image_cache = Cache(Image.DEFAULT_CACHE)
        self.path        = path #This is the tag for the image ie str of filename or URL - used as the key for the cache
        self.parent      = parent
        self.opacity     = Image.DEFAULT_OPACITY if opacity is None else opacity
        self.old_image_data = None
        self.target_wh   = parent.abs_rect()[-2:] if target_wh is None else target_wh 

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
            image = image.copy()
            image.set_alpha(self.opacity)
            # frame_width  = 0 if self.outline is None else self.outline.width 
            self.parent.platform.screen.blit(image, coords)
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
        pygame.draw.rect(self.platform.screen, colour, coords, self.width)
        # print("Box.draw> offset", self.platform.h, offset, "coords", coords, "top", self.top, self.geostr())

    def drawH(self, pc, flip=False, colour_index=None, offset=(0,0)):
        if flip:
            coords = self.abs_rect( offset=(self.w*pc+offset[0], offset[1]),  wh=[self.w*(1-pc), self.width] )
        else:
            coords = self.abs_rect( offset=offset,  wh=[self.w*pc, self.width] )

        colour = self.colours.get(self.w*pc, False) if colour_index is None else self.colours.get(colour_index)
        pygame.draw.rect(self.platform.screen, colour, coords, border_radius=self.radius )

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
        pygame.draw.line(self.platform.screen, colour_index, coords, self.width)
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
        pygame.draw.line(self.platform.screen, colour_index, ab, xy, width)


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
        pygame.draw.lines(self.platform.screen, colour_index, self.circle, line)


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
        self.drawtext = ['']*2  # lines of text
        font, fontwh = self.shrink_fontsize(wh, text, fontmax)

        if self.wrap and fontwh[1] < Text.READABLE:  # split into two lines and draw half size
            try:
                self.drawtext = wrap(text, width=1+len(text)//2, max_lines=Text.MAX_LINES)
                # print("wrap", self.drawtext)
                font, fontwh  = self.shrink_fontsize(wh, self.drawtext[0], fontmax)
                fontwh[1]    *= 2  # double height, 2 lines
            except ValueError as error:
                print("Text.scalefont> textwrap failed" , error )
                self.drawtext = text[:(1+len(text)//2)]
                # print("wrap", self.drawtext)
                font, fontwh  = self.shrink_fontsize(wh, self.drawtext[0], fontmax)
        else:
            self.drawtext[0] = text

        # print("Text.scalefont> max %s, target wh %s, fontwh %s, text<%s>, %s" % (self.whmax, wh, fontwh, text, self.drawtext))
        return font, fontwh

    def draw(self, text=None, offset=(0,0), coords=None, colour=None, fontmax=None):  #Draw the text in the corner of the frame
        if text   is None:
            text = self.text 
        else:
            self.text = text

        fontmax = self.fontmax if fontmax is None else fontmax

        if self.reset: self.update(text, fontmax)

        if coords is None : coords = self.parent.abs_origin()    
        if colour is None : colour = self.colour
        colour_index = self.colours.get(colour)

        if hasattr(self, 'font') and self.font is not None:
            # for line_number, line in enumerate(self.drawtext):
            line = self.drawtext[0]
            line_number = 1
            try:
                info   = self.font.render(line, True, colour_index)
                size   = info.get_rect()
                coords = self.parent.align_coords(coords, size[-2:], self.justify)
                self.parent.platform.screen.blit( info, coords  )  # position the text upper left
                # self.parent.platform.screen.blit( info, (coords[0], coords[1]+ line_number*size[Text.MAX_LINES])  )  # position the text upper left
                # print(" Text.draw> drawn text>", line, "<at", (coords), line_number, size, size[Text.MAX_LINES])
                #self.parent.platform.dirty
            except pygame.error as e:
              print(f"Text.draw Pygame Render ERROR for line '{line}': {e}")
              # Skip drawing this line but continue the loop


    def drawVectoredText(self, val, text=None, offset=(0,0), coords=None, colour=None):
        if text is None : text   = self.text
        xy   = self.parent.anglexy(val, self.radius)
        size = self.textsize(text)
        text_offset = (xy[0]-size[0]/2, xy[1], size[0], size[1])
        self.draw(text=text, coords=text_offset, colour=colour)
        print(f"Text.drawVectoredText> radius {self.radius} val {val} text_offset {text_offset} text{text} text_size {size}")
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
        self.parent.platform.screen.blit(
            self.font.render(text, True, colour_index),
            (x, y))


    #Glowing text version -- does not work well
    # def drawVectoredText(self, val, text=None, colour=None):
    #     if text is None:
    #         text = self.text

    #     if colour is None : colour = self.colour
    #     colour_index = self.colours.get(colour)
    #     screen = self.parent.platform.screen

    #     # 1) Get absolute dial position
    #     x, y = self.parent.anglexy(val, self.radius)

    #     # 2) Render high-quality text surface
    #     # (True enables font-level antialiasing)
    #     txt = self.font.render(text, True, colour_index)

    #     # 3) Optional soft glow layer (bigger blurred text behind)
    #     glow = self.font.render(text, True, colour_index)
    #     glow = pygame.transform.smoothscale(
    #         glow,
    #         (int(glow.get_width() * 1.25), int(glow.get_height() * 1.25))
    #     )
    #     glow.set_alpha(80)  # strength of glow

    #     # 4) Sub-pixel perfect centring math (NOT integer truncated)
    #     w, h = txt.get_size()
    #     gx, gy = glow.get_size()

    #     px = x - w / 2.0
    #     py = y - h / 2.0

    #     # 5) Shadow offset (half-pixel crispness)
    #     sx = px + 1.0
    #     sy = py + 1.0

    #     # 6) Glow centred behind text
    #     gx_pos = x - gx / 2.0
    #     gy_pos = y - gy / 2.0

    #     # 7) Draw stack (glow → shadow → text)
    #     screen.blit(glow, (gx_pos, gy_pos))
    #     screen.blit(self.font.render(text, True, (0,0,0)), (sx, sy))  # shadow
    #     screen.blit(txt, (px, py))




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
        pygame.draw.rect(self.frame.platform.screen, colour_index, coords, border_radius=radius, width=width)

        self.frame.platform.dirty_mgr.add(tuple(self.frame.abs_outline()))
        # print("Outline.draw> coords ", coords, "radius ", radius, "width ", width )   
        return coords     

    @property
    def w(self):
        if self.outline is None or 'width' not in self.outline:
            return 0
        else: 
            return self.outline['width'] 

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
            
        elif isinstance(background, dict) and any(key in background for key in ('colour','opacity','glow')):
            self.background.update(background)
            if 'per_frame_update' not in self.background:   self.background.update({'per_frame_update': Background.BACKGROUND_DEFAULT['per_frame_update']}) 
            if 'opacity'          not in self.background:   self.background.update({'opacity': Background.BACKGROUND_DEFAULT['opacity']})   
            if 'glow'             not in self.background:   self.background.update({'glow': Background.BACKGROUND_DEFAULT['glow']})

            if self.background.get('glow'):
                self._create_blurred_glow(self.background['colour'], self.background['opacity'])


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
                # Calculate the absolute position for the glow surface
                glow_x, glow_y = self.frame.abs_perimeter()[2:]
                
                # Blit the pre-rendered glow surface
                # self.frame.platform.screen.blit(self.glow_surface, (glow_x, glow_y))
                # print("\ndrawing glow back")

            if self.background_image is None:
                if self.background['colour'] is None: return

                # 1. Get the coordinates and dimensions of the area to fill
                rect_coords = self.frame.abs_background()  # Should be (x, y, w, h)
                rect_w, rect_h = rect_coords[2:]

                # 2. Create a temporary Surface for the semi-transparent drawing
                alpha_surface = pygame.Surface((rect_w, rect_h), pygame.SRCALPHA)
                alpha_surface.set_alpha(self.background['opacity']) 

                # Fill the *entire* temporary surface with the color
                colour = self.frame.colours.get(self.background['colour'])
                alpha_surface.fill(colour)
                # Blit the temporary, transparent surface onto the main screen
                self.frame.platform.screen.blit(alpha_surface, rect_coords[:2]) # Use (x, y) coordinates

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
  

    '''
    This is an attempt with pygame to create more sophisticated graphics - but is really does not work very well at all

    '''
    GLOW_RADIUS_PERCENT = 0.05  # 5% of the frame's smallest dimension
    def _create_blurred_glow(self, colour_name='background', opacity=255, radius_pc=None):
        """
        Creates a pre-rendered surface for a smooth, blurred-edge background 
        using a fast Box Blur approximation via smooth scaling.
        """
        # Define constants/defaults
        if radius_pc is None:
            radius_pc = self.GLOW_RADIUS_PERCENT 
        
        # 1. Calculate Dimensions
        rect_coords = self.frame.abs_background()
        rect_w, rect_h = rect_coords[2:]
        
        min_dim = min(rect_w, rect_h)
        glow_padding = int(min_dim * radius_pc)
        
        # Define the final target size (frame + padding on all sides)
        target_w = rect_w + 2 * glow_padding
        target_h = rect_h + 2 * glow_padding
        
        # 2. Create the Initial Small Surface (The Core)
        # The smaller the initial surface, the blurrier the result when scaled up.
        # We use a very small factor (e.g., 1/10th of the target size).
        SCALE_FACTOR = 10 
        
        initial_w = max(1, target_w // SCALE_FACTOR)
        initial_h = max(1, target_h // SCALE_FACTOR)
        
        # Create the core surface with full alpha (will be blurred later)
        core_surface = pygame.Surface((initial_w, initial_h), pygame.SRCALPHA)
        
        # Get the color components
        base_rgb = self.frame.colours.get(colour_name)[:3]
        
        # Fill the core surface with the color (at max opacity 255)
        core_surface.fill(base_rgb + [255,])
        
        # 3. Apply the Blur (Smooth Scaling)
        # This scales the small, solid block up to the final size using a smoothing
        # algorithm, which results in a soft, blurred effect.
        self.glow_surface = pygame.transform.smoothscale(core_surface, (target_w, target_h))
        
        # 4. Apply Overall Transparency
        # The blur effect alone often results in a solid shape. We apply transparency
        # to the whole surface to make it act like a soft glow.
        GLOW_OPACITY = int(opacity * 0.4) # Use only 40% of the requested opacity for the outer glow
        self.glow_surface.set_alpha(GLOW_OPACITY)
        
        # 5. Store Offsets
        self.glow_offset_xy = (-glow_padding, -glow_padding)
        self.glow_size_wh = (target_w, target_h)
        
        print(f"Background._create_blurred_glow> Smoothscale glow pre-rendered: {self.glow_surface.get_size()}")


#---- End Background -------        
