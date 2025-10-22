#!/usr/bin/env python
"""
Display driver classes

Low level platform dynamics


v1.0 baloothebear4 1 Dec 2023   Original, based on Pygame visualiser mockups
v1.1 baloothebear4 Feb 2024   refactored as part of pyvisualiseer

"""

import pygame, time
from   pygame.locals import *
import numpy as np
from   framecore import Frame, Cache, Colour
from   textwrap import shorten, wrap
from    io import BytesIO
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
            coords = self.abs_rect( offset=(offset, 0),  wh=[w, self.h*ypc] )

            for led_y in range( int(coords[1]), int(coords[1]+coords[3]) ,(self.led_h+self.led_gap)):
                colour = self.colours.get(led_y-coords[1], False) if colour_index is None else self.colours.get(colour_index) # height based
                pygame.draw.rect(self.platform.screen, colour, (coords[0], led_y, coords[2], self.led_h), border_radius=self.radius)
            else:
                if self.tip and ypc>0:
                    colour = self.colours.get(coords[3], not self.flip) if colour_index is None else self.colours.get(colour_index)
                    pygame.draw.rect(self.platform.screen, colour, (coords[0], coords[1]+coords[3], coords[2], self.led_h), border_bottom_left_radius=self.tip_radius, border_bottom_right_radius=self.tip_radius )

            pcoords = self.abs_rect( offset=(offset, peak*self.h),  wh=[w, self.peak_h] )
            self.draw_peak(peak*self.h, False, pcoords)

            # print("Bar.draw (flip)> coords ", coords, "peak coords", coords, "ypc", ypc, "peak", peak)
        else:
            coords = self.abs_rect( offset=(offset, self.h*(1-ypc)),  wh=[w, self.h*ypc] )
            # print("Bar.draw V> coords", coords)
            for led_y in range( int(coords[1]+coords[3]), int(coords[1]) ,-(self.led_h+self.led_gap)):
                col    = coords[1] + coords[3]-led_y
                colour = self.colours.get(col, False) if colour_index is None else self.colours.get(colour_index) # height based

                pygame.draw.rect(self.platform.screen, colour, (coords[0], led_y , coords[2], self.led_h), border_radius=self.radius )
            else:
                if self.tip and ypc>0:
                    col    = coords[3] #self.led_h+self.led_gap
                    colour = self.colours.get(col, self.flip) if colour_index is None else self.colours.get(colour_index) # height based
                    pygame.draw.rect(self.platform.screen, colour, (coords[0], coords[1], coords[2], self.led_h), border_top_left_radius=self.tip_radius, border_top_right_radius=self.tip_radius )

            pcoords = self.abs_rect( offset=(offset, self.h*(1-peak)),  wh=[w, self.peak_h] )
            self.draw_peak(peak*self.h, False, pcoords)

            # print("Bar.draw > coords ", coords, "peak coords", coords, "ypc", ypc, "peak", peak, "col", col)

    """ Draw a horizontal bar """
    def drawH(self, offset, ypc, w, peak=0, colour_index=None):

        if self.flip:
            coords = self.abs_rect( offset=(self.w*(1-ypc), offset),  wh=[self.w*ypc, w] )
            # print("Bar.drawH - flip> coords", coords)
            for led_l in range( int(coords[0]+ coords[2]), int(coords[0]) ,-(self.led_h+self.led_gap)):
                colour = self.colours.get(coords[0]+ coords[2]-led_l, False) if colour_index is None else self.colours.get(colour_index)
                pygame.draw.rect(self.platform.screen, colour, (led_l, coords[1], self.led_h, coords[3]), border_radius=self.radius )
            else:
                if self.tip and ypc>0:
                    colour = self.colours.get(coords[2], True) if colour_index is None else self.colours.get(colour_index)
                    pygame.draw.rect(self.platform.screen, colour, (int(coords[0]+ coords[2]), coords[1], self.led_h, coords[3]), border_bottom_left_radius=self.tip_radius, border_top_left_radius=self.tip_radius )

            peak_w  = self.w*(peak)
            pcoords = self.abs_rect( offset=(self.w*(1-peak), offset),  wh=[self.peak_h, w] )
            self.draw_peak(peak_w, False, pcoords)

        else:
            coords = self.abs_rect( offset=(0, offset),  wh=[self.w*ypc, w] )
            # print("Bar.drawH> coords", coords)
            for led_l in range( int(coords[0]), int(coords[0]+ coords[2]) ,(self.led_h+self.led_gap)):
                colour = self.colours.get(led_l-coords[0], self.flip) if colour_index is None else self.colours.get(colour_index)
                pygame.draw.rect(self.platform.screen, colour, (led_l, coords[1], self.led_h, coords[3]), border_radius=self.radius )
            else:
                if self.tip and ypc>0:
                    colour = self.colours.get(coords[2], False) if colour_index is None else self.colours.get(colour_index)
                    pygame.draw.rect(self.platform.screen, colour, (int(coords[0]+ coords[2]), coords[1], self.led_h, coords[3]), border_bottom_right_radius=self.tip_radius, border_top_right_radius=self.tip_radius )

            peak_w  = peak * self.w
            pcoords = self.abs_rect( offset=(peak_w, offset),  wh=[self.peak_h, w] )
            self.draw_peak(peak_w, False, pcoords)

class Image(Frame):
    DEFAULT_OPACITY = 255
    DEFAULT_CACHE   = 300
    def __init__(self, parent, wh=None, path=None, align=None, scalers=None, opacity=None, outline=None):

        self.image_cache = Cache(Image.DEFAULT_CACHE)
        self.path        = path
        Frame.__init__(self, parent, align=align, scalers=scalers, outline=outline)
        self.opacity     = Image.DEFAULT_OPACITY if opacity is None else opacity
        self.old_image_data = None
        if path is not None:
            self.scaleInProportion(path, self.boundswh[1])

        # print("Image.__init__>", self.framestr())

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

    def scaleInProportion(self, image_ref, tgt_height):
        if image_ref is None: return

        # path = self.download_image(image_ref) if 'http' in image_ref else image_ref
        # imagesurface = pygame.image.load(path).convert_alpha()

        imagesurface = None
        try:
            if 'http' in image_ref:
                path = self.download_image(image_ref) 
                if path is None: return None # Download failed, log already printed
            else:
                path = image_ref

            # CRITICAL POINT: Load the image into a Pygame surface
            imagesurface = pygame.image.load(path).convert_alpha()
            
        except pygame.error as e:
            print(f"Image.scaleInProportion ERROR: Pygame failed to load image '{image_ref}'. Error: {e}")
            return None
        except Exception as e:
             print(f"Image.scaleInProportion UNEXPECTED ERROR during load '{image_ref}': {e}")
             return None

        if imagesurface is None:
            return None


        original_width, original_height = imagesurface.get_size()
        aspect_ratio = original_width / original_height
        frame_width  = 0 if self.outline is None else self.outline.width 
        new_width = int((tgt_height) * aspect_ratio)
        if new_width > self.boundswh[0]:
            new_width  = self.boundswh[0]
            new_height = int(new_width / aspect_ratio)
        else:
            new_height = tgt_height

        wh=(new_width, new_height)
        image = pygame.transform.scale(imagesurface, (new_width-(frame_width*2), new_height-(frame_width*2)))
        self.image_cache.add(image_ref, image)
        self.resize( wh )

        # print("Image.scaleinproportion> from", original_width, original_height, "to", wh, "target", tgt_height, frame_width, self.framestr())
        return image

    # Drawing is possibly a two step process
    # 1. work out if anything has changed
    # 2. draw unconditionally the current Image, assume the background has been cleaned

    def new_content_available(self, image_data=None):
        # print("Image.draw>", self.boundswh[1], self.framestr(), self.geostr())
        if image_data is None:  image_data = self.path  
        return image_data != self.old_image_data

    def draw(self, image_data=None):   
        if image_data is None:  image_data = self.path   
        image = self.image_cache.find(image_data)
        if image is None:   
            image = self.scaleInProportion(image_data, self.boundswh[1])

        if image is not None:
            image.set_alpha(self.opacity)
            frame_width  = 0 if self.outline is None else self.outline.width 
            self.platform.screen.blit(image, self.abs_origin(offset=(frame_width,frame_width)))
            self.draw_outline(True)

            # print("Image.draw> New image", image_data, ">>>>>", self.old_image_data)
            self.old_image_data = image_data

        else:
            pass
            # print("Image.draw> attempt to draw an None image", image, image_data)
        


class Lightback(Frame):
    # Draw the colorful arc background for the full frame
    def __init__(self, parent, scalers=None, align=None, theme=None, colour_index='light', flip=False):

        Frame.__init__(self, parent, align=align, scalers=scalers, theme=theme)
        self.colour = Colour(self.theme, self.h)
        self.colour_index = colour_index
        self.flip   = flip

        # Create a surface for the glow
        self.glow_surface = pygame.Surface(self.boundswh, pygame.SRCALPHA)
        

        # Draw the light illumination in the center on the glow surface
        self.max_radius = self.h//2
        for radius in range(self.max_radius, 0, -1):
            alpha = int(255 * (radius / self.max_radius)**3)  # Adjust alpha based on radius
            opacity = alpha if flip else 255-alpha
            col = self.colour.get(colour_index, opacity=opacity)
            pygame.draw.circle(self.glow_surface, col, self.abs_centre(), radius)

        # print("Lightback.__init__>", self.wh, self.h, self.abs_origin(), self.centre, self.geostr())

    def draw(self):
        # Blit the glow surface onto the screen

        # col = self.colour.get(self.colour_index)
        # for radius in range(self.max_radius, 0, -1):
        #     alpha = int(255 * (radius / self.max_radius)**3)  # Adjust alpha based on radius
        #     pygame.draw.circle(self.glow_surface, col + (255-alpha,), self.abs_centre(), radius)
        self.platform.screen.blit(self.glow_surface, (0,0) )

class ArcsOctaves(Frame):
    """ Lines are for drawing meter needles, oscilogrammes etc """
    def __init__(self, parent, wh=None, colour=None, align=('centre', 'middle'), theme='std', NumOcts=5, scalers=None):

        self.NumOcts = NumOcts
        Frame.__init__(self, parent, align=align)
        self.resize( wh )

        self.scalar  = self.h/(NumOcts)/2
        self.colour  = Colour(self.theme,12)

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
            colour = self.colour.get(i) #need to work out how many colours there needs to be
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
    def __init__( self, parent, colour_index=None, width=1, align=None, theme=None, scalers=(1.0,1.0),\
                  circle=True, endstops=(PI/2, 3* PI/2), radius=100, centre_offset=0, tick_pc=1.0, amp_scale=0.9):

        self.width     = width
        self.circle    = circle
        self.radius    = radius
        self.tick_pc   = tick_pc
        self.linespace = []   # array of line circles
        self.amp_scale = amp_scale

        Frame.__init__(self, parent, align=align, theme=theme, scalers=scalers)
        self.anglescale(radius, endstops, centre_offset)  # True if val is 0-1, False if -1 to 1

        self.colour_index = colour_index
        self.colours      = Colour(self.theme, self.radius)
        # print("Line.init> ", bounds, self.geostr(), self.anglestr())

    def draw(self, offset, colour_index=0):   #(x,y) offset
        if colour_index is None: colour_index = self.colour_index
        coords = self.abs_rect()
        colour = self.colours.get(colour_index)
        pygame.draw.line(self.platform.screen, colour, coords, self.width)
        # print("Line.draw> offset", self.platform.h, offset, "coords", coords, "top", self.top, self.geostr())


    def drawFrameCentredVector(self, val, colour_index=None, width=0, amplitude=1.0, gain=0, tick_pc=None):
        """ tick_pc is the percent of the line to draw from outside in, useful if the pivot is below the line
            val is the angle to draw the line
        """
        if colour_index is None: colour_index = self.colour_index
        if width == 0: width = self.width
        if tick_pc is None: tick_pc = self.tick_pc
        xy         = self.anglexy(val, self.radius,  amp_scale=amplitude, gain=gain)#, xyscale=self.xyscale)
        ab         = self.anglexy(val, self.radius*(1-tick_pc))#, xyscale=self.xyscale)

        colour = self.colours.get(colour_index)  # Add a get col
        # print("Line.drawFrameCentredVector: val %f, ab %s, xy %s, yoff %f, len %d" % (val, ab, xy, self.centre_offset, self.radius))
        pygame.draw.line(self.platform.screen, colour, ab, xy, width)


    def draw_mod_line(self, points, colour_index=None, amplitude=1.0, gain=1.0):
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


        colour_index = self.radius*(self.amp_scale*amplitude) if colour_index is None else 'alert' # Add a get col
        colour = self.colours.get(colour_index)
        pygame.draw.lines(self.platform.screen, colour, self.circle, line)


    def make_ripple(self, size):
        wh     = (self.xyscale[0]*size, self.xyscale[1]*size)
        xy     = self.abs_origin( offset=(self.centre[0]-wh[0]//2, self.centre[1]-wh[1]//2))
        return pygame.Rect(xy, wh)

    def draw_mod_ripples(self, points, trigger={}, colour_index=None, amplitude=1.0):
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
            colour = self.colours.get(col)
            self.linespace.append((ripple,colour))

        for ripple in self.linespace:
            pygame.draw.ellipse(self.platform.screen, ripple[1], ripple[0], width=1)

    def drawFrameCentredArc(self, val, colour_index=None):
        if colour_index is None: colour_index = self.colour_index
        xy     = self.anglexy(val, self.radius)
        colour = self.colours.get(colour_index)  # Add a get col
        arcwh  = [self.radius*2, self.radius*2]
        coords = self.abs_centre( offset=(-arcwh[0]/2, -arcwh[1]/2) )+arcwh
        # print("Line.drawFrameCentredArc>", coords, self.h*(self.centre_offset), self.geostr())
        pygame.draw.arc(self.platform.screen, colour, coords, 3*PI/2+self.endstops[0], 3*PI/2+self.endstops[1], self.width)


class Text(Frame):
    """
    Text is all about creating words & numbers that are scaled to fit within
    rectangles

    Fonts are scaled to fit
    update triggers a resizing of the text each time its drawn
    """
    TYPEFACE = 'fonts/Inter/Inter-VariableFont_opsz,wght.ttf'
    READABLE = 18   # smallest readable font size
    MAX_LINES= 1

    def __init__(self, parent, text='Default text', fontmax=None, reset=True, wrap=False, align=None, scalers=None,\
                 endstops=(PI/2, 3* PI/2), radius=100, centre_offset=0, theme=None, colour_index=None):  #Create a font to fit a rectangle

        self.text     = text
        self.wrap     = wrap
        self.reset    = reset
        self.radius   = radius
        self.theme    = theme

        self.cache    = Cache()
        self.colour_index = colour_index
        Frame.__init__(self, parent, align=align, scalers=scalers, theme=theme)
        self.colours  = Colour(self.theme, self.w)
        self.fontmax  = self.boundswh[1] if fontmax is None else fontmax 

        self.anglescale(radius, endstops, centre_offset)  # True if val is 0-1, False if -1 to 1
        self.update()
        # print("Text.__init__> ", self.fontwh, self.text, self.scalers, self.alignment,self.geostr())

    def update(self, text=None, fontmax=None):
        try:
            if text is None: text=self.text
            self.drawtext = self.cache.find(text)
            self.font, self.fontwh = self.scalefont(self.boundswh, text, fontmax)  # You can specify a font

            if self.drawtext is None:
                # self.font, self.fontwh = self.scalefont(self.boundswh, text, fontmax)  # You can specify a font
                self.cache.add(text, self.drawtext)
                # print("Text.update> new text cached & reset", text, self.fontwh, self.geostr())  
            else:
                # print("Text.update> text found", text, self.fontwh, self.geostr())
                pass
            if self.reset: 
                self.resize( self.fontwh )
  

        except Exception as e:
            print("Text.update> ERROR > %s > wh %s, fontwh %s, text<%s>, %s " % (e,self.wh, self.fontwh, self.text, self.alignment ))

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

    def draw(self, text=None, offset=(0,0), coords=None, colour_index=None, fontmax=None):  #Draw the text in the corner of the frame
        if text   is None:
            text = self.text 
        else:
            self.text = text

        fontmax = self.fontmax if fontmax is None else fontmax

        if self.reset: self.update(text, fontmax)

        if coords is None : coords = self.abs_origin()    
        if colour_index is None : colour_index = self.colour_index
        colour = self.colours.get(colour_index)

        if hasattr(self, 'font') and self.font is not None:
            for line_number, line in enumerate(self.drawtext):
                try:
                    info = self.font.render(line, True, colour)
                    size = info.get_rect()
                    self.platform.screen.blit( info, (coords[0], coords[1]+ line_number*size[Text.MAX_LINES])  )  # position the text upper left
                    # print("Text.draw> drawn text>", line, "<at", (coords[0], coords[1]+ line_number*size[Text.MAX_LINES]), line_number, size, size[Text.MAX_LINES])
                except pygame.error as e:
                    print(f"Text.draw Pygame Render ERROR for line '{line}': {e}")
                    # Skip drawing this line but continue the loop


    def drawVectoredText(self, val, text=None, offset=(0,0), coords=None, colour_index=None):
        if text is None : text   = self.text
        xy   = self.anglexy(val, self.radius)
        size = self.textsize(text)
        text_offset = (xy[0]-size[0]/2, xy[1], size[0], size[1])
        self.draw(text=text, coords=text_offset, colour_index=colour_index)

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

    def draw_mod_dots(self, points, trigger={}, colour_index=None, amplitude=1.0, gain=0.8):
        size         = len(points)
        xc, yc       = self.centre[0], self.centre[1]
        col          = self.radius*(self.amp_scale*amplitude) if colour_index is None else colour_index # Add a get col
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
    OUTLINE = { 'width' : 3, 'radius' : 0, 'colour_index' : 'foreground', 'opacity': 255}
    def __init__(self, theme, w, screen, outline):
        self.outline_colour = Colour(theme, w)
        self.outline        = outline
        self.screen         = screen


    def draw(self, coords):
        colour_index = self.outline['colour_index']  if 'colour_index' in self.outline else Outline.OUTLINE['colour_index']
        opacity      = self.outline['opacity']       if 'opacity' in self.outline else Outline.OUTLINE['opacity']
        radius       = self.outline['radius']        if 'radius' in self.outline else Outline.OUTLINE['radius']
        width        = self.outline['width']         if 'width' in self.outline else Outline.OUTLINE['width']
        colour  = self.outline_colour.get(colour_index, opacity=opacity)
        surface = pygame.Surface( (self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)
        #adjust the outline to the outside of the coords ie add the width
        # coords = (coords[0]-width, coords[1]-width, coords[2]+width*2, coords[3]+width*2) if radius>0 else coords
        pygame.draw.rect(surface, colour, coords, border_radius=radius, width=width)
        self.screen.blit(surface, (0,0) )
        # print("Outline.draw>", coords, ncoords, colour, opacity )        

    @property
    def width(self):
        width        = self.outline['width'] if 'width' in self.outline else Outline.OUTLINE['width']
        return width

import pygame
import collections

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
        
        # 1. Union all the Rects into a minimal list of non-overlapping Rects.
        #    pygame.Rect.unionall() is helpful but still leaves overlaps,
        #    so we use the slower, but more accurate, process of summing 
        #    the area of the minimal bounding box of all rectangles. 
        
        # A simple, practical approach:
        # Instead of a complex merging algorithm, we use Rect.unionall()
        # which is *good enough* for an estimate and is fast.
        
        # If the list is a list of Rects, use unionall() to get a single bounding Rect
        union_rect = dirty_rects[0]
        for rect in dirty_rects[1:]:
            union_rect = union_rect.union(rect)

        # The union rect's area is the *maximum possible* area that needs update.
        # For a more precise measure of *actual* updated pixels (not just the bounding box), 
        # a dedicated merger function (like pygame.Rect.unionall) followed by 
        # summing the areas is ideal, but complicated. For monitoring, a simple union
        # of the outer bounding box is a decent, fast estimate.
        
        # However, to be more accurate, we need to sum the individual areas 
        # after merging overlapping regions. Pygame doesn't have a simple function for this.
        
        # A reasonable compromise: sum the areas of the merged rects.
        # For true non-overlapping area, you need a geometry library, but for a
        # quick metric, let's use the simplest: summing the area of the unioned rect.
        # A more advanced but still simple-to-implement approach is to union them all
        # into one large bounding box.

        # We'll use the bounding box area as a simple metric (it's slightly an overestimate)
        # Correct Way 1: Use width * height
        total_dirty_area = union_rect.width * union_rect.height
        
        # For a simple, non-overlapping sum, we rely on pygame.display.update() to 
        # have already done the difficult work of minimizing the areas before calling it.
        # But since we get the raw list, we must estimate.

        # Let's use a simpler total sum for demonstration, assuming rects are reasonably separated:
        # NOTE: This method below will OVERCOUNT areas if rectangles overlap.
        # area_sum = sum(rect.area for rect in dirty_rects)
        # return area_sum 
        
        # For simplicity and speed (and it provides a useful upper bound metric):
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

    def add(self, rect: pygame.Rect | tuple):
        """
        Adds a single dirty rectangle to the list.
        If a tuple (x, y, w, h) is passed, it is converted to a pygame.Rect.
        """
        # print("DirtyRectManager.add", rect)
        if isinstance(rect, tuple):
            self.dirty_rects.append(pygame.Rect(rect))
        elif isinstance(rect, pygame.Rect):
            self.dirty_rects.append(rect)
        else:
            raise TypeError("Expected pygame.Rect or (x, y, w, h) tuple")

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
 
    """ Stable and works well - but has a flip so least efficient """
    # def draw_end(self):
    #     # NOTE: When rotating the entire virtual surface, you effectively
    #     # must update the entire physical screen. Dirty rect optimization 
    #     # is incompatible with this approach.

        
    #     # 1. Clear the physical screen (Necessary if physical screen size != virtual size)
    #     self._physical_screen.fill((0, 0, 0))
        
    #     # 2. Rotate the virtual surface by the required angle (e.g., -90 degrees)
    #     # This returns a NEW surface with its own dimensions
    #     rotated_surface = pygame.transform.rotate(self.virtual_surface, -90)
        
    #     # 3. Get the rect for the physical screen, NOT the rotated surface.
    #     # This keeps the image centered correctly.
    #     screen_rect = self._physical_screen.get_rect()
        
    #     # 4. Get the rect of the rotated surface and center it on the physical screen's center
    #     # This ensures the rotated image stays centered on the physical display.
    #     rotated_rect = rotated_surface.get_rect(center=screen_rect.center)
        
    #     # 5. Blit the rotated surface onto the physical screen
    #     self._physical_screen.blit(rotated_surface, rotated_rect)
        
    #     # 6. Update the ENTIRE display.
    #     # If any part of the screen is updated via a full-surface rotation,
    #     # you need to update the whole physical screen for correctness.
    #     pygame.display.flip() 
        
    #     # 7. IMPORTANT: Disable Dirty Rect Tracking!
    #     # Because we updated the whole screen, the efficiency is 100% (or 1.0)
    #     # You are intentionally sacrificing Dirty Rect optimization for screen rotation.
    #     self.ave_area_pc = 100.0 
    #     # Note: You should not call self.dirty_mgr.get_and_clear() or update area_tracker here.
  

    """ Draw on the transformed parts -optimised algorithm"""
    def draw_end(self):
        dirty_rects = self.dirty_mgr.get_and_clear()
        
        if not dirty_rects:
            # If nothing is dirty, don't update anything
            self.ave_area_pc = self.area_tracker.update_average([])
            # print("GraphicsDriverPi.draw_end> NO dirty rects")
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
        


    def fill(self, rect=None, colour=None, colour_index='background', image=None):
        if rect is None: rect = self.boundary
        if colour_index is None: colour_index = 'background'
        if colour is None: colour=self.colour
        colour = colour.get(colour_index)
        #self.screen.fill(colour, pygame.Rect(rect))
        self.virtual_surface.fill(colour, pygame.Rect(rect))
        if image is not None:
            self.image_container.draw(image)
        # print("GraphicsDriverPI.fill>. clear screen >", rect)




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


    """ No evidence this is evver called """
    def fill(self, rect=None, colour=None, colour_index='background', image=None):
        if rect is None: rect = self.boundary
        if colour_index is None: colour_index = 'background'
        if colour is None: colour=self.colour
        colour = colour.get(colour_index)
        self.screen.fill(colour, pygame.Rect(rect))
        if image is not None:
            self.image_container.draw(image)


class GraphicsDriver:
    def __init__(self, events, gfx='mac'):
        if gfx=='pi_kms':
            self.gfx_driver=GraphicsDriverPi(events)
        else:
            self.gfx_driver=GraphicsDriverMac(events)

        pygame.display.set_caption('Visualiser')

        self.screen         = self.gfx_driver.screen
        self.colour         = Colour('std', self.w)
        self.background     = Frame(self)
        self.image_container= Image(self.background, align=('centre','middle'), scalers=(1.0,1.0))  # make square


    def __getattr__(self, item):
        """Delegate calls to the implementation"""
        return getattr(self.gfx_driver, item)

    def refresh(self, rect=None):
        # if rect is None: rect = [0,0]+self.wh
        pygame.display.update(pygame.Rect(rect))    

    def create_outline(self, theme, outline, w):
        return Outline(theme, w, self.screen, outline)    
    
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
    def w(self):
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


"""
Test code
"""
# from    framecore import Frame, Geometry
# from    events import Events
#
# e        = Events(( 'Platform', 'CtrlTurn', 'CtrlPress', 'VolKnob', 'Audio', 'RemotePress'))
# d        = GraphicsDriver(e, 60)
# f        = Frame(platform=d, scalers=(1.0,1.0), align=('left','top'))
#
# # p = Platform(events)
# # self.events         = Events(( 'Audio', 'KeyPress'))
# # self.platform       = Platform(self.events)
#
#
# def testBar():
#
#     # b = Bar()
#     d.draw_start('test')
#     # def drawFrameBar(self, geo, x, ypc, w, colour ):
#     d.drawFrameBar(f, 10, 0.1, 10, Screen.white)
#     #
#     d.draw()
#
#     d.end()
#
#
#
# if __name__ == "__main__":
#     try:
#         # geometrytest()
#         # frametest('front')
#         testBar()
#
#         time.sleep(10)
#
#     except KeyboardInterrupt:
#         pass
