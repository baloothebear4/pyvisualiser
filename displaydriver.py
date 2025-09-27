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
            'h' according to y
            's' solid colour
            'w' colour according to x
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

        if path is not None:
            self.scaleInProportion(path, self.boundswh[1])

        # print("Image.__init__>", self.framestr())

    def download_image(self, url):
        response = requests.get(url)
        return BytesIO(response.content)

    def scaleInProportion(self, image_ref, tgt_height):
        if image_ref is None: return
        path = self.download_image(image_ref) if 'http' in image_ref else image_ref
        imagesurface = pygame.image.load(path).convert_alpha()
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

    def draw(self, image_data=None):
        # print("Image.draw>", self.boundswh[1], self.framestr(), self.geostr())
        if image_data is None:  image_data = self.path  
        image = self.image_cache.find(image_data)
        if image is None:   
            image = self.scaleInProportion(image_data, self.boundswh[1])

        if image is not None:
            image.set_alpha(self.opacity)
            frame_width  = 0 if self.outline is None else self.outline.width 
            self.platform.screen.blit(image, self.abs_origin(offset=(frame_width,frame_width)))
            self.draw_outline()
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
    TYPEFACE = 'helvetica'
    READABLE = 16   # smallest readable font size
    MAX_LINES= 2

    def __init__(self, parent, text='Default text', fontmax=None, reset=False, wrap=False, align=None, scalers=None,\
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
        # print("Text.__init__> ", self.fontwh, self.font, self.text, self.scalers, self.alignment,self.geostr())

    def update(self, text=None, fontmax=None):
        try:
            if text is None: text=self.text
            self.drawtext = self.cache.find(text)
            if self.drawtext is None:
                self.font, self.fontwh = self.scalefont(self.boundswh, text, fontmax)  # You can specify a font
                self.cache.add(text, self.drawtext)
                if self.reset: self.resize( self.fontwh )
        except Exception as e:
            print("Text.update> ERROR > %s > wh %s, fontwh %s, text<%s>, %s " % (e,self.wh, self.fontwh, self.text, self.alignment ))

    @property
    def fontsize(self):
        return self.fontwh[1]
    
    def shrink_fontsize(self, wh, text, fontmax=None, min=5):
        # print("Text.shrink_fontsize> attempt", text, wh, self.fontmax, self.boundswh)
        fontsize    = self.fontmax if fontmax is None else fontmax
        font        = pygame.font.SysFont(Text.TYPEFACE, int(fontsize))
        fontwh      = self.textsize(text, font) 
        if fontwh[0]> wh[0]:  
            fontsize   = fontsize * wh[0]/ fontwh[0]
            font        = pygame.font.SysFont(Text.TYPEFACE, int(fontsize))
            fontwh      = self.textsize(text, font)
        if fontwh[1]> wh[1]:  
            fontsize    = fontsize *  wh[1]/fontwh[1]
            font        = pygame.font.SysFont(Text.TYPEFACE, int(fontsize))
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
        if coords == None       : coords = self.abs_origin()
        fontmax = self.fontmax if fontmax is None else fontmax
        if self.reset: 
            self.drawtext = None #self.cache.find(text)
            if self.drawtext is None: self.update(text, fontmax)
        if colour_index is None : colour_index = self.colour_index
        colour = self.colours.get(colour_index)

        for line_number, line in enumerate(self.drawtext):
            info = self.font.render(line, True, colour)
            size = info.get_rect()
            self.platform.screen.blit( info, (coords[0], coords[1]+ line_number*size[Text.MAX_LINES])  )  # position the text upper left

        # print("Text.draw > ", self.reset, self.drawtext, text, offset, coords, colour, colour_index, self.scalers, self.alignment, size)


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

class GraphicsDriver:
    """ Pygame based platform """
    H       = 400
    W       = 1280
    PANEL   = [W, H]   # h x w

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
        self.image_container= Image(self.background, align=('centre','middle'), scalers=(1.0,1.0))  # make square

    def init_display(self):
        """Initialize pygame for Waveshare 7.9" horizontal display"""
    
        # Force pygame to use framebuffer
        os.environ['SDL_VIDEODRIVER'] = 'kmsdrm'
        os.environ['SDL_VIDEODEVICE'] = '/dev/dri/card1'
        # Remove any rotation overrides - let hardware handle it
        if 'SDL_VIDEO_KMSDRM_ROTATION' in os.environ:
            del os.environ['SDL_VIDEO_KMSDRM_ROTATION']    
        #os.environ['SDL_VIDEO_KMSDRM_ROTATION'] = '90'

        os.environ['SDL_NOMOUSE']     = '1'  # Hide mouse cursor initially
    
        pygame.init()
    
        # The physical screen is reported by the OS as 400x1280 (tall).
        self._physical_screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        actual_size = self._physical_screen.get_size()
        print(f"Fullscreen mode size: {actual_size}")
        
        # Create a virtual surface with our desired drawing dimensions (1280x400)
        self.virtual_surface = pygame.Surface((GraphicsDriver.W, GraphicsDriver.H))
        
        # Hide mouse cursor for a cleaner look.
        pygame.mouse.set_visible(False)
        
        # Return the virtual surface for all drawing operations
        return self.virtual_surface        # Waveshare 7.9" resolution: 400x1280 native (portrait)


    def draw_start(self, text=None):
        # self.screen.fill((0,0,0))       # erase whole screen
        # All drawing now happens on the virtual surface.
        self.virtual_surface.fill((0,0,0))       # erase the virtual screen
        if text is not None: pygame.display.set_caption(text)

    def draw_end(self):
        # Clear the physical screen
        self._physical_screen.fill((0, 0, 0))
        
        # Rotate the virtual surface by -90 degrees to "undo" the OS rotation
        rotated_surface = pygame.transform.rotate(self.virtual_surface, -90)
        
        # Blit the rotated surface onto the physical screen
        rotated_rect = rotated_surface.get_rect(center=self._physical_screen.get_rect().center)
        self._physical_screen.blit(rotated_surface, rotated_rect)
        
        # Update the display to show the changes
        pygame.display.flip()
        
        # Control the frame rate
        self.clock.tick(self.FPS)


    def refresh(self, rect=None):
        # if rect is None: rect = [0,0]+self.wh
        pygame.display.update(pygame.Rect(rect))

    def fill(self, rect=None, colour=None, colour_index='background', image=None):
        if rect is None: rect = self.boundary
        if colour_index is None: colour_index = 'background'
        if colour is None: colour=self.colour
        colour = colour.get(colour_index)
        #self.screen.fill(colour, pygame.Rect(rect))
        self.virtual_surface.fill(colour, pygame.Rect(rect))
        if image is not None:
            self.image_container.draw(image)

    def create_outline(self, theme, outline, w):
        return Outline(theme, w, self.screen, outline)

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

    def graphics_end(self):
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
