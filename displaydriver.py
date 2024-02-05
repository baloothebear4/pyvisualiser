#!/usr/bin/env python
"""
7.9" DSI Display driver classes

Low level platform dynamics

baloothebear4

v1.0 1 Dec 2023   Original, based on OPygame visualiser mockups

"""
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import pygame, time
from   pygame.locals import *
import numpy as np
from   framecore import Frame
from   textwrap import shorten, wrap
from io import BytesIO
import requests

PI          = 3.14152

"""
Class to manage lists eg of menu items or sources to find previous and next items
    init with a a list of keys - these key are used to index a dict
    use the prev & next methods to get the previous and nexy items in the list
    use the curr method to read the current item

"""
class ListNext:
    def __init__(self, list, startItem):
        self._list = list
        self._curr = startItem

    def findItemIndex(self, item):
        for index, element in enumerate(self._list):
            if element == item: return index
        raise ValueError("ListNext.findItemIndex> item not found in list", item, self._list)

    @property
    def curr(self):
        return self._curr

    @curr.setter
    def curr(self, v):
        if v in self._list:
            self._curr = v
        else:
            raise ValueError("ListNext.curr> item not found in list", v, self._list)

    @property
    def prev(self):
        i = self.findItemIndex(self._curr)
        if i > 0:
            self.curr = self._list[i-1]
        else:
            self.curr = self._list[-1]
        return self.curr

    @property
    def next(self):
        i = self.findItemIndex(self._curr)
        if i < len(self._list)-1:
            self.curr =  self._list[i+1]
        else:
            self.curr =  self._list[0]
        return self.curr

    def __str__(self):
        return "list>%s, current>%s" % (self._list, self.curr)



# COLOUR_SCHEME = [[green, amber, red, purple],
#                 [[121, 163, 146],[3, 116, 105],[1, 89, 86],[0, 53, 66],[0, 29, 41]], # colorScheme 2
#                 [[86, 166, 50],[217, 4, 4]], # colorScheme 1
#                 [[143, 142, 191],[79, 77, 140],[71, 64, 115],[46, 65, 89],[38, 38, 38]], # colorScheme 4
#                 [[85, 89, 54,],[108, 115, 60],[191, 182, 48],[166, 159, 65],[242, 242, 242]], # colorScheme 5
#                 [[1, 38, 25],[1, 64, 41],[2, 115, 74],[59, 191, 143],[167, 242, 228]], # colorScheme 3
#                 [[1, 40, 64],[75, 226, 242], [75, 195, 242,]], # colorScheme 6 ==> Blue one
#                 [[1, 40, 64],[2, 94, 115],[4, 138, 191],[75, 195, 242,],[75, 226, 242]], # old blue one colorScheme 6
#                 [[28, 56, 140],[217, 121, 201,],[242, 162, 92]], # colorScheme 9
#                 [[144, 46, 242],[132, 102, 242],[164, 128, 242],[206, 153, 242],[241, 194, 242]]] # colorScheme 12



white   = (255, 255, 255)
grey    = (125, 125, 125)
green   = (0, 128, 0)
amber   = (255, 215, 0)
red     = (255, 0, 0)
purple  = (128, 0, 128)
blue    = (0, 0, 255)
black   = (0, 0, 0)
yellow  = (255,255,0)

COLOUR_THEME = {    'white' : {'light':(255,255,175), 'mid':(200,200,125), 'dark':grey, 'foreground':white, 'background':black, 'alert':red,'range':[(255,255,75), (255,255,175), white] },
                    'std'   : {'light':(175,0,0), 'mid':grey, 'dark':(50,50,50), 'foreground':white, 'background':black, 'alert':red,'range':[green, amber, red, purple] },
                    'blue'  : {'light':[75, 195, 242,], 'mid':[4, 138, 191], 'dark':[1, 40, 64], 'foreground':white, 'background':black, 'alert':[75, 226, 242],'range':[ [1, 40, 64],[2, 94, 115],[4, 138, 191],[75, 195, 242,],[75, 226, 242] ] }, #[(0,10,75), (0,100,250)],
                    'red'   : {'light':[241, 100, 75], 'mid':[164, 46, 4], 'dark':[144, 46, 1], 'foreground':white, 'background':black, 'alert':red,'range':[ [144, 46, 1],[132, 46, 2],[164, 46, 4],[206, 100, 75],[241, 100, 75]] },  #[(75,10,0), (250,100,0)],
                    'leds'  : {'range':[ [1, 40, 64],[75, 226, 242], [75, 195, 242]] },
                    'back'  : {'range':[ blue, black ] },
                    'grey'  : {'range':[ white,[75, 226, 242], [75, 195, 242] ] },
                    'meter1': {'light':(200,200,200), 'mid':grey, 'dark':(50,50,50), 'foreground':white, 'background':black, 'alert':red, 'range':[ white, red, grey]},
                    'rainbow': {'white': white, 'grey': grey, 'green': green, 'amber': amber, 'red': red, 'purple': purple, 'blue': blue,  'black': black,  'yellow': yellow, 'range':[grey, red, yellow, green, blue, purple, white]}
                }

class Colour:
    def __init__(self, theme, num_colours):
        self.theme      = theme                 # array of colour tuples that are blended together
        self.num_colours= num_colours           # size of array of colours to index
        self.colours    = self.colourmap(theme) # lookup of a colour tuple from an index
        # print("Colour.__init__> theme", theme, self.num_colours )

    """
    Colour primitives
    """
    def colourmap(self, theme):
        def rgb_to_hex(color_tuple):
            return "#{:02x}{:02x}{:02x}".format(*color_tuple)

        hex_colours = [rgb_to_hex(color) for color in COLOUR_THEME[theme]['range']]
        values = np.arange(0, self.num_colours+1)

        # Normalize values to be in the range [0, 1]
        norm = plt.Normalize(vmin=0, vmax=self.num_colours)

        # Create a custom colormap ranging from green to amber to red
        # cmap = mcolors.LinearSegmentedColormap.from_list('green_amber_red', ['#008000', '#FFD700', '#FF0000'])
        cmap = mcolors.LinearSegmentedColormap.from_list('green_amber_red', hex_colours)
        # Get colors corresponding to the normalized values
        colors = cmap(norm(values))

        # Convert RGBA values to tuples
        color_tuples = [(int(r * 255), int(g * 255), int(b * 255)) for r, g, b, _ in colors]

        return color_tuples

    def get(self, colour_index=None, flip=False):
        # depending what the index is look-up:
        # print("Colour.get> INFO :", colour_index )
        if isinstance(colour_index, (int, float)):
            if flip:
                i = min(self.num_colours, (max(0, int(self.num_colours-colour_index))))
            else:
                i = min(self.num_colours, (max(0, int(colour_index))))
            # print("Screen.get_colour ", i, index)
            return self.colours[int(i)]
        elif colour_index in COLOUR_THEME[self.theme]:
            return COLOUR_THEME[self.theme][colour_index]
        else:
            print("Colour.get> WARN : index not known - look for purple ", colour_index)
            return purple


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
    def __init__(self, parent, scale=(1.0,1.0), align=('centre', 'bottom'), \
                 box_size=(100,100), led_h=10, led_gap=4, peak_h=1, right_offset=0, \
                 theme='std', flip=False, radius=0, tip=False, orient='vert', col_mode=None):

        self.right_offset = right_offset

        Frame.__init__(self, parent, align=align)
        self.resize( box_size )

        self.led_h      = led_h
        self.led_gap    = led_gap
        self.peak_h     = peak_h
        self.radius     = radius    # this makes rounded corners 0= Rectangle - works really as a % of the height
        if col_mode is None: col_mode = orient
        colour_range    = self.h if col_mode == 'vert' else self.w
        self.colours    = Colour(theme, colour_range)
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

            peak_w  = self.w*(1-peak)
            pcoords = self.abs_rect( offset=(peak_w, offset),  wh=[self.peak_h, w] )
            self.draw_peak(peak_w, True, pcoords)

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
    def __init__(self, parent, wh=None, align=('centre', 'middle'), path=None):

        self.image_cache = {}
        Frame.__init__(self, parent, align=align)

        if path is not None:
            wh = self.scaleInProportion(path, self.wh[1])
            self.resize( wh )

    def download_image(self, url):
        response = requests.get(url)
        return BytesIO(response.content)

    def scaleInProportion(self, image_ref, new_height):
        if image_ref not in self.image_cache:
            path = self.download_image(image_ref) if 'http' in image_ref else image_ref
            imagesurface = pygame.image.load(path).convert()
            original_width, original_height = imagesurface.get_size()
            aspect_ratio = original_width / original_height
            new_width = int(new_height * aspect_ratio)
            if new_width > self.w:
                new_width  = self.w
                new_height = int(new_width / aspect_ratio)

            wh=(new_width, new_height)
            self.image = pygame.transform.scale(imagesurface, wh)
            self.image_cache[image_ref]=self.image
            # print("Image.scaleInProportion> placed in cache", image_ref, len(self.image_cache)) #, original_width, original_height, wh)# Resize the image in proportion

        else:
            self.image = self.image_cache[image_ref]
            wh = self.image.get_rect().size
            # print("Image.scaleInProportion> used cache", wh, image_ref, len(self.image_cache))
        return wh

    def draw(self, image_data=None):
        if image_data is not None:
            self.scaleInProportion(image_data, self.h)

        self.platform.screen.blit(self.image, self.abs_origin())

class Lightback(Frame):
    # Draw the colorful arc background for the full frame
    def __init__(self, parent, wh=None):

        Frame.__init__(self, parent, align=align)
        self.resize( wh )
        dark_blue = (0, 0, 100)  # Dark blue color
        glow_color = (255, 255, 200)  # Light yellow color for the glow
        # print("Lightback.init> wh", bounds, self.geostr())

        # screen.fill(dark_blue)

        # Create a surface for the glow
        self.glow_surface = pygame.Surface((self.w//2, self.h), pygame.SRCALPHA)

        # Draw the light illumination in the center on the glow surface
        max_radius = self.h//2
        for radius in range(max_radius, 0, -1):
            alpha = int(255 * (radius / max_radius)**2)  # Adjust alpha based on radius
            pygame.draw.circle(self.glow_surface, glow_color + (255-alpha,), (640,100), radius)
            pygame.draw.ellipse(self.glow_surface, glow_color + (255-alpha,), (0,0,radius,radius))

    def draw(self):
        # Blit the glow surface onto the screen
        self.platform.screen.blit(self.glow_surface, self.abs_origin() )


class ArcsOctaves(Frame):
    """ Lines are for drawing meter needles, oscilogrammes etc """
    def __init__(self, parent, wh=None, colour=None, align=('centre', 'middle'), theme='std', NumOcts=5):

        self.NumOcts = NumOcts
        Frame.__init__(self, parent, align=align)
        self.resize( wh )

        self.scalar  = self.h/(NumOcts)/2
        self.colour  = Colour(theme,12)

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
        self.colours      = Colour(theme, self.w)
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
    def __init__( self, parent, colour_index=None, width=1, align=('centre', 'middle'), theme='std', \
                  circle=True, endstops=(PI/2, 3* PI/2), radius=100, centre_offset=0, tick_pc=1.0, amp_scale=0.9):

        self.width     = width
        self.circle    = circle
        self.radius    = radius
        self.tick_pc   = tick_pc
        self.linespace = []   # array of line circles
        self.amp_scale = amp_scale

        Frame.__init__(self, parent, align=align)
        self.anglescale(radius, endstops, centre_offset)  # True if val is 0-1, False if -1 to 1

        self.colour_index = colour_index
        self.colours      = Colour(theme, self.radius)
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


    def draw_mod_line(self, points, colour_index=None, amplitude=1.0):
        size   = len(points)
        # Linear scalars
        yscale = self.h       # scalar for the height amplitude of the line modulation
        xscale = self.w/size  # x scalar

        # Circular scalars
        line   = []

        for i, v in enumerate(points):
            if self.circle:
                line.append(self.anglexy(i/size, self.radius, gain=v,amp_scale=self.amp_scale*amplitude,  xyscale=self.xyscale) )
            else:
                line.append(self.abs_origin(  offset=(xscale*i, yscale*(0.5+v)*amplitude) ))

        colour_index = self.radius*(self.amp_scale*amplitude) if colour_index is None else 'alert' # Add a get col
        colour = self.colours.get(colour_index)
        pygame.draw.lines(self.platform.screen, colour, self.circle, line)
        return line

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
    TYPEFACE = 'arial'

    def __init__(self, parent, text='Default text', fontmax=0, align=('right', 'middle'), reset=False, \
                 endstops=(PI/2, 3* PI/2), radius=100, centre_offset=0, theme='std', colour_index=None):  #Create a font to fit a rectangle

        self.text     = text
        self.fontmax  = int(fontmax) # if this is zero then the largest possible is calculated
        self.reset    = reset
        self.radius   = radius
        self.theme    = theme
        self.colours  = Colour(theme, 100)
        self.colour_index = colour_index
        Frame.__init__(self, parent, align=align)
        self.anglescale(radius, endstops, centre_offset)  # True if val is 0-1, False if -1 to 1
        self.update()

    def update(self, text=''):
        if text!='': self.text=text
        # if self.reset: self.fontsize = 0
        self.font, self.fontwh = self.scalefont(self.boundswh, self.text)  # You can specify a font
        if self.reset: self.resize( self.fontwh )
        self.align()
        # print("Text.update>  wh %s, font size %d, fontwh %s, text<%s> " % (self.wh, self.fontsize, self.fontwh, self.text ))

    def scalefont(self, wh, text, min=3):  #scale the font to fit the rect, with a min fontsize
        self.fontsize = wh[1] if self.fontmax == 0 else self.fontmax
        font        = pygame.font.SysFont(Text.TYPEFACE, self.fontsize)
        fontwh      = self.textsize(text, font)  #[wh[0]+1, wh[1]+1]   # to ensure at least one cycle runs
        while fontwh[0] > wh[0] or fontwh[1] > wh[1]:
            font   = pygame.font.SysFont(Text.TYPEFACE, self.fontsize)
            fontwh = self.textsize(text, font)
            self.fontsize -= 1
            if self.fontsize < min: break
        # print("Text.scalefont> target wh %s, font size %d, fontwh %s, text<%s>" % (wh, self.fontsize, fontwh, text))
        return font, fontwh

    def draw(self, text='', offset=(0,0), coords=None, colour_index=None):  #Draw the text in the corner of the frame
        if text   == ''    : text   = self.text
        if coords == None  : coords = self.abs_rect()
        if self.reset      : self.update(text)
        if colour_index is None: colour_index = self.colour_index
        colour = self.colours.get(colour_index)

        info = self.font.render(text, True, colour)
        self.platform.screen.blit(info,coords)  # position the text upper left

        # print("Text.draw > ", self.reset, text, offset, coords, colour, colour_index, self.anglestr())
        return coords

    def drawVectoredText(self, text='', val=0, offset=(0,0), coords=None, colour_index=0):
        xy  = self.anglexy(val, self.radius)
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
    def __init__( self, parent, colour_index=None, width=1, align=('centre', 'middle'), theme='std', \
                  circle=True, endstops=(PI/2, 3* PI/2), radius=100, centre_offset=0, amp_scale=0.2, dotcount=1000):

        self.width      = width
        self.circle     = circle
        self.radius     = radius*0.5
        self.dotspace   = []
        self.dotcount   = dotcount
        self.amp_scale  = amp_scale
        Frame.__init__(self, parent, align=align)
        self.anglescale(radius, endstops, centre_offset)  # True if val is 0-1, False if -1 to 1

        self.colour_index = colour_index
        self.colours      = Colour(theme, radius)
        # print("Dots.init> ", bounds, self.geostr(), self.anglestr())

    def draw_circle(self, offset, colour_index=0):   #(x,y) offset
        if colour_index is None: colour_index = self.colour_index
        coords = self.abs_rect()
        colour = self.colours.get(colour_index)
        pygame.draw.ellipse(self.platform.screen, colour, coords, self.width)
        # print("Dots.draw> offset", self.platform.h, offset, "coords", coords, "top", self.top, self.geostr())

    def draw_mod_dots(self, points, trigger={}, colour_index=None, amplitude=1.0):
        size         = len(points)
        xc, yc       = self.centre[0], self.centre[1]
        col          = self.radius*(self.amp_scale*amplitude) if colour_index is None else col # Add a get col
        gain         = 1.1

        if 'bass' in trigger:
            gain = 1.1  # velocity the dots move outward
            col = 'alert'

        if 'treble' in trigger:
            gain = 1.01
            col  = 'foreground'  # velocity the dots move outward

        # For all the dot space, calculate the velocities and move
        for dot in self.dotspace:
            self.dotspace.remove(dot)
            x1 = int(gain*(dot[0]-xc)+ xc)
            y1 = int(gain*(dot[1]-yc)+ yc)
            # check dot is still on the screen
            if x1>=0 and x1<=self.w and y1>0 and y1<self.h and len(self.dotspace)<self.dotcount:
                self.dotspace.append([x1,y1, dot[2]])

        colour = self.colours.get(col)
        # if 'bass' in trigger:

        for i, v in enumerate(points):
            # xy = self.anglexy(i/size, self.radius, gain=1.5, amp_scale=abs(v), xyscale=(xscale,1.0))
            xy = self.anglexy(i/size, self.radius, gain=v,amp_scale=self.amp_scale*amplitude,  xyscale=self.xyscale)
            if v>0.00: self.dotspace.append([ int(xy[0]),int(xy[1]),colour])

            # Draw the dot space and calculate the velocities
        for dot in self.dotspace:
            # print("Dots.draw_mod_dots", (dot[0], dot[1]), dot[2], size)
            self.platform.screen.set_at( (dot[0], dot[1]), dot[2] )


class GraphicsDriver:
    """ Pygame based platform """
    H       = 400
    W       = 1280
    PANEL   = [W, H]   # h x w

    """
    Base class to manage all the graphics i/o functions
    """
    def __init__(self, events, FPS):
        pygame.init()   #create the drawing canvas
        self.events         = events
        self.clock          = pygame.time.Clock()
        self.screen         = pygame.display.set_mode(GraphicsDriver.PANEL)
        self.FPS            = FPS
        pygame.display.set_caption('Visualiser')
        self.my_font        = pygame.font.SysFont('helvetica', 16)
        self.dotspace       = []

    def draw_start(self, text=None):
        self.screen.fill((0,0,0))       # erase whole screen
        if text is not None: pygame.display.set_caption(text)

    def draw_end(self):
        # print("Screen.draw [END]")
        pygame.display.flip()
        self.clock.tick(self.FPS)

    def refresh(self, rect=None):
        # if rect is None: rect = [0,0]+self.wh
        pygame.display.update(pygame.Rect(rect))

    def fill(self, rect=None, colour=black):
        if rect is None: rect = [0,0]+self.wh
        self.screen.fill(colour, pygame.Rect(rect))

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
