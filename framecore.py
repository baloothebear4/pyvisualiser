#!/usr/bin/env python
"""
 Base classes for generic Frame management
    - Geometry:  manages the coordinate system used for enclosing rectangles
    - Frame: hierarchical frames, managed for overlap and alignment

 v1.0 Baloothebear4 May 2022
 v2.0 baloothebear4 Dec 2023 - generalised and refactored as part of pyvisualiser

"""

""" a data type for coordinates - converts lists to dicts and back
    - initialise from a 4 point list
    - read as 4 point list
    - write to the coordinates via setters to check legimacy

"""


import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

from colour_palette import COLOUR_THEMES, purple


PI = np.pi
# from oleddriver import internalOLED     # used for Test purposes
# from platform   import Platform         # used for Test purposes

class Geometry():
    def __init__(self, bounds=None, screen_wh=(1280,400), scalers=(1.0,1.0), align=('centre', 'middle')):
        self._abcd          = [0,0,0,0]
        self._bounds        = [0,0, screen_wh[0]-1, screen_wh[1]-1] if bounds is None else bounds
        self.screen_wh      = screen_wh
        self.alignment      = align
        self.scalers        = scalers
        self.min_offset     = 0
        self.circle_scale   = 1
        self.centre_offset  = 0  #PC of the height offsets the centre of a circle eg -0.5 moves to the bottom
        self.endstops       = (0, 2*PI)
        self.scale(self.scalers)
        # print("Geometry.init> abcd %s, scalers %s, boundswh %s, size %s, coords %s" % ( self.abcd, scalers, self.boundswh, self.wh, self.coords))


    """ test if this will return a from the syntax Frame.a """
    @property
    def a(self):
        return self._abcd[0]

    @a.setter
    def a(self, val):
        if val >= 0 and val <= self.boundswh[0]:
            self._abcd[0] = int(val)
        else:
            raise ValueError('set.a > value exceed bounds ', val, self.geostr())

    @property
    def b(self):
        return self._abcd[1]

    @b.setter
    def b(self, val):
        if val >= 0 and val <= self.boundswh[1]:
            self._abcd[1] = int(val)
        else:
            raise ValueError('set.b > value exceed bounds ', val, self.geostr())

    @property
    def c(self):
        return self._abcd[2]

    @c.setter
    def c(self, val):
        if val >= 0 and val <= self.boundswh[0]:
            self._abcd[2] = int(val)
        else:
            raise ValueError('set.c > value exceed bounds ', val, self.boundswh[0], self.geostr())

    @property
    def d(self):
        return self._abcd[3]

    @d.setter
    def d(self, val):
        if val >= 0 and val <= self.boundswh[1]:
            self._abcd[3] = int(val)
        else:
            raise ValueError('set.d > value exceed bounds ', val, self.geostr())

    @property
    def w(self):
        return self.size(self._abcd)[0]

    @property
    def h(self):
        return self.size(self._abcd)[1]

    @property
    def abcd(self):
        return self._abcd

    @property
    def coords(self):
        return self.norm()

    @property
    def wh(self):
        return self.size(self._abcd)

    @property
    def xy(self):
        return (self.a, self.b)

    @property
    def centre(self):
        return self.normxy( ( (self.c+self.a)/2, (self.d+self.b)/2) )

    @property
    def top(self):
        return self.boundswh[1]

    @property
    def right(self):
        return self.boundswh[0]

    @property
    def x0(self):
        return self.norm()[0]

    @property
    def y0(self):
        return self.norm()[1]

    @property
    def x1(self):
        return self.norm()[2]

    @property
    def y1(self):
        return self.norm()[3]

    @property
    def boundswh(self):
        return self.size(self._bounds)

    def resize(self, wh):
        # print("Geometry.resize to", wh, self.geostr())
        self.a = 0 #self._bounds[0]
        self.b = 0 #self._bounds[1]
        try:
            self.c = wh[0] -1 if wh[0] > 0 else 0
        except ValueError:
            self.c = self.boundswh[0] -1
            self.align()
            # print("!!! Geometry.resize> outside bounds w %f, set to bounds, %s" % (wh[0], self.geostr()) )
        try:
            self.d = wh[1] -1 if wh[1] > 0 else 0
        except ValueError:
            self.d = self.boundswh[1] -1
            self.align()
            # print("!!! Geometry.resize> outside bounds h %f, set to bounds, %s" % (wh[1], self.geostr()) )
        self.align()
        # print("Geometry.resize to ", wh, self.geostr())

    @property
    def bounds(self):  #resize the boundary to the size of the frame
        return(self._bounds)

    @property
    def xyscale(self):
        aspect_ratio = self.w/self.h
        xyscale      = (aspect_ratio, 1.0) if self.w > self.h else (1.0, aspect_ratio)
        return xyscale

    def size(self, abcd):
        w = abcd[2] - abcd[0] + 1
        h = abcd[3] - abcd[1] + 1
        return [w,h]

    """ scale the geometry according the given boundary and w, h scaling factors
        leave the bottom, left as is and change the top, right accordingly
    """
    def scale(self, scalers):
        # print("Geometry.scale> by", scalers," using ", self.boundswh,", to, ",[ int(self.boundswh[0] * scalers[0]), int(scalers[1] * self.boundswh[1]) ], self.geostr() )
        if scalers[0]>0 and scalers[1]>0:
            # self.scalers = scalers
            self.resize( [ int(self.boundswh[0] * scalers[0]), int(scalers[1] * self.boundswh[1])] )
        else:
            raise ValueError('Geometry.scale > scale is zero ', scalers, self.geostr())

    def rescale(self):
        self.scale(self.scalers)

    """ move the frame relative to the top/right or bottom/left corners """
    def move_ab(self, xy):
        w = self.w-1
        h = self.h-1
        self.a = xy[0]
        self.b = xy[1]
        self.c = xy[0]+w
        self.d = xy[1]+h

    def move_cd(self, xy):
        w = self.w-1
        h = self.h-1
        self.a = xy[0]-w
        self.b = xy[1]-h
        self.c = xy[0]
        self.d = xy[1]

    def move_middle(self, y):
        #y coordinate
        h = self.h-1
        # self.b = int(y-h/2)
        # print("Geometry.move_middle> y", y, "h", h)
        self.b = int(y-h/2)
        self.d = int(y+h/2)

    def move_centre(self, x):
        #x coordinate
        w = self.w-1
        # print("Geometry.move_centre> x", x, w, w/2)
        self.a = int(x-w/2)
        self.c = int(x+w/2)

    def go_top(self, offset=0):
        self.move_cd( (self.c, self.top-offset) )

    def go_middle(self):
        self.move_middle( int(self.top/2) )

    def go_bottom(self):
        self.move_ab( (self.a, 0) )
        # print("Geometry.go_bottom>", self.geostr())

    def go_left(self, offset=0):
        self.move_ab( (0+offset, self.b) )
        # print("Geometry.go_left>", self.geostr())

    def go_centre(self):
        self.move_centre( int(self.right/2) )

    def go_right(self):
        self.move_cd( (self.right, self.d) )

    """
        normalise the coordinate system to that of the actual display
        this assumes that the given boundary are actual coordinates on the screen
        so the relative coordinates of the geometry are added to the bounds x,y
        this is to give an absolute coordinate for drawing
    """
    def norm(self):
        # return self._abcd
        return [self._bounds[0]+self.a, self._bounds[1]+self.b, self._bounds[0]+self.c, self._bounds[1]+self.d]
        # return [self._bounds[0]+self.a, self._bounds[1]+self.b, self._bounds[0]+self.w, self._bounds[1]+self.h]

    """ return the absolute coordinates for drawing on screen, using TopLeft ordinates """
    def abs_origin(self, offset=(0, 0)): # Return (x, y)
        # origin = (self.x0+offset[0], (1+self.top+ (self.boundswh[1] - self.h) - self.y0-offset[1]) )
        origin = (int(self.x0+offset[0]), int(self.screen_wh[1]- (self.y0-offset[1]+self.h-1)) )
        return origin

    def abs_centre(self, offset=(0, 0)): # Return (x, y)
        # origin = (self.x0+offset[0], (1+self.top+ (self.boundswh[1] - self.h) - self.y0-offset[1]) )
        origin = [self.centre[0]+offset[0], self.screen_wh[1]- (self.centre[1]+self.h*(self.centre_offset)-offset[1]-1) ]  
        # print("Geometry.abs_centre>", self.centre, origin)
        return origin

    def abs_rect(self, offset=(0, 0), wh=None):  # Return (x, y, w, h)
        wh = [self.wh[0], self.wh[1]] if wh is None else wh
        rect = [int(self.x0+offset[0]), int(self.screen_wh[1]- (self.y0+self.h-offset[1])) ] + wh
        # print(self.screen_wh[1], self.y0, self.h, offset[1],"rect", rect)
        return rect

    def theta(self, val):    # return an angle in radians from a value range -1 to +1
        return (PI*(val))-PI/2

    def arctheta(self, angle): # return a value range -1 to +1 from an angle in radians
        return (angle-PI/2)/PI

    def anglexy(self, val_pc, radius, gain=0, amp_scale=1, xyscale=(1,1) ):
        # Assume that 0 (abs) val_pc is 0600, PI is 0600, by default 0 val angle = first end stop
        # xscale is to create eliptical shapes
        theta = self.theta(self.min_offset+self.circle_scale*val_pc) #to make sure this aligns at 0 = 0600
        xy = [self.centre[0]+xyscale[0]*radius*(amp_scale+gain)*np.sin(theta), (self.screen_wh[1])-(self.centre[1]+self.h*(self.centre_offset)+xyscale[1]*radius*(amp_scale+gain)*np.cos(theta) )]
        # print("Geometry.anglexy>theta %2.2f xy %s, radius %f, gain %2.2f, val_pc %2.2f, amp_scale %f, centre %s, centre_offset %f, self.screen_wh[1] %d" % (theta, xy, radius, gain, val_pc, amp_scale, self.centre, self.centre_offset, self.screen_wh[1]))
        return xy

    def anglescale(self, radius, endstops=[0,2*PI], centre_offset=0):
        """
            if abs value range in anglexy is 0-1, else -1 to +1,
            scale factor is the muliplier for val_pc to move between end Points
            min offset is the factor that ensures that the min val_pc is on the end stop
        """

        self.centre_offset = centre_offset
        self.endstops      = [0,2*PI] if endstops is None else list(endstops)
        minmax= [self.arctheta(self.endstops[0]), self.arctheta(self.endstops[1])]

        for val in range(int(self.arctheta(self.endstops[0])*100), int(self.arctheta(self.endstops[1])*100)):
            xy = self.anglexy(val/100, radius)

            if xy[0]< self.x0 and val/100>minmax[0]:
                # print("min", xy, minmax, val/100, self.x0, self.x1, self.endstops)
                minmax[0], self.endstops[0] = val/100, self.theta(val/100)+PI/2

            if xy[0]> self.x1 and val/100<minmax[1]:
                minmax[1], self.endstops[1] = val/100, self.theta(val/100)+PI/2
                # print("max", xy, minmax, val/100, self.x0, self.x1, self.endstops)

        # print("Geometry.anglescale>", minmax, (minmax[1]-minmax[0]))
        # print("Geometry.anglescale> start endstops", endstops, "after", self.endstops, "minmax", minmax, "scale", (minmax[1]-minmax[0]), )
        # scale factor, minimum offset
        self.min_offset   = minmax[0]
        self.circle_scale = minmax[1]-minmax[0]

    def anglestr(self):
        return("Geometry.anglestr> centre_offset", self.centre_offset, "min_offset", self.min_offset, "circle_scale", self.circle_scale, "endstops", self.endstops)

    #
    # def anglerange(self, len, val_pc=0):
    #     w = self.w
    #     if len-w/2<0:
    #         angle_min = 0
    #     else:
    #         xmin=w/2
    #         angle_min = np.arccos(xmin/len)
    #
    #     angle = (PI-angle_min) * val_pc
    #     print("Geometry.anglerange> len %d, val_pc %2.4f, angle %2.2f, angle_min %2.2f" % (len, val_pc, angle, angle_min))
    #     return angle


    def normxy(self, xy):
        return (self._bounds[0]+xy[0], self._bounds[1]+xy[1])

    def check(self):
        # check that the enclosed rectangle fits within the given boundary. Properties to test
        # 1. the area should not be greater (not needed)
        # 2. the coordinates do not exceed the boundary space
        if self.a < self._bounds[0] or self.c > self._bounds[2] or \
           self.b < self._bounds[1] or self.d > self._bounds[3]:
           raise ValueError('Geometry.check > out of bounds')
           return False
        else:
           return True

    def __str__(self):
        return( "name %s, abcd %s, bounds %s, boundswh %s, size %s, coords %s" % (type(self).__name__, self.abcd, self._bounds, self.boundswh, self.wh, self.coords))

    def geostr(self, s=0):
        return( "name %s, abcd %s, bounds %s, boundswh %s, size %s, coords %s, abs org %s, abs rect %s" % (type(self).__name__, self.abcd, self._bounds, self.boundswh, self.wh, self.coords, self.abs_origin(), self.abs_rect()))

    def align(self, align=None, offset=0):
        """
            align will use the anchors: 'top, middle, bottom', 'left, centre, right' to set the
            coordinates of the Frame within the boundary
        """
        # parse V and H alignment anchors
        # check that the frame is still in bounds
        # this is where the frame coordiantes are setup
        if align is not None: self.alignment = align

        # print("Geometry.align> top %d, right %d, abcd %s, wh %s, V=%s, H=%s" % (self.top, self.right, self.abcd, self.wh, self.V, self.H))

        if self.alignment[1]   == 'top':
            self.go_top( )
            # move so that self.d = self.bounds.d
        elif self.alignment[1] == 'middle':
            self.go_middle()
            # move so that middle(self) = middle(self.bounds) : middle =
        elif self.alignment[1] == 'row':
            self.go_top(offset)
            # move so its packs from the top - the offset ie downwards
        elif self.alignment[1] == 'bottom':
            self.go_bottom()
        else:
            raise ValueError('Frame.align: expected vertical anchor (top, middle, bottom) found->', self.alignment[1])

        if self.alignment[0]   == 'left':
            self.go_left()
            # move so that self.a = self.bounds.a
        elif self.alignment[0] == 'centre':
            self.move_centre( int(self.right/2))
            # move so that centre(self) = centre(self.bounds)
        elif self.alignment[0] == 'right':
            self.move_cd( (self.right, self.d) )
            # move so that self.c = self.bounds.c
        elif self.alignment[0] == 'col':
            self.go_left(offset)
            # move so its packs from the top - the offset ie downwards    
        else:
            raise ValueError('Frame.align: expected horz anchor (left, centre, right) found->', self.alignment[0])
        # print("Geometry.align> to", self.geostr())

FULLSCALE = (1.0,1.0)
CENTRED   = ('centre', 'middle')

class Frame(Geometry):
    """
        - manages the alignment of a Frame within a Screen
        - a Screen is defined at the top most Frame
        - Frames can be nested within frames
        - the base coordinate system has (0,0) as bottom, left -> hence requires normalisation to actual screen coord system
        - Each Frame is a rectangle of given size (w,h)
        - each frame uses Geometry to resize within the bounds of the parent Frame
        - the geometry of a Frame is always relative to the parent
        - a Frame itself can contain other frames that can be positioned with the frame
        - checks are performed to see the coordinates given do not take the Frame outside the bounds

        bounds      is the physical coordinates of the Frame (bottom left), (top right)
        platform    is the set of objects that enable access to data sets, screen drivers and graphics
        scalers     is how the frame is scaled vs the boundary
        square      is to force the shape to have w=h
        padding     is a % additional scaling added to the absolute size is a smaller than the scaled size
        
    """
    OUTLINE = { 'width' : 3, 'radius' : 0, 'colour_index' : 'foreground'}

    def __init__(self, parent, scalers=FULLSCALE, align=CENTRED, square=False, theme=None, background=None, outline=None):
        """
            scalars is a tuple (w%, h%) where % is of the bounds eg (0,0,64,32) is half the width, full height
            align is a tuple (horizontal, vertical) - where horz is one of 'left', 'right', 'centre', vertical 'top', 'middle', 'bottom'
            bounds is list of the bottom left and upper right corners eg (64,32)

            NB: making outline = '' will draw frame outlines around all frames that do not have their own draw functions - useful for tweaking screen design
        """
        self.frames     = []         #Holds the stack of containing frames
        self.outline    = outline
        scalers         = FULLSCALE   if scalers  is None else scalers
        alignment       = CENTRED     if align    is None else align      
        # print("Frame.__init__> startup>>>", type(self).__name__, align, scalers, theme, background)
        if isinstance(parent, Frame):
            """ Sub-frame, so scale to the size of the parent Frame """
            bounds          = parent.coords
            # scalers         = parent.scalers    if scalers  is None else scalers
            self.theme      = parent.theme      if theme    is None else theme
            # alignment       = parent.alignment  if align    is None else align            
            self.platform   = parent.platform
            # print("Frame.__init__>", type(self).__name__, scalers, alignment, theme, self.theme, "parent", parent.scalers, parent.alignment, parent.theme)
        else:
            """ Screen (aka top-level Frame), so scale to the boundary """
            bounds          = parent.boundary
            self.platform   = parent    #only needed by the top Frame or Screen, as is passed on draw()
            scalers         = FULLSCALE              if scalers  is None else scalers
            self.theme      = 'std'                  if theme    is None else theme
            alignment       = CENTRED                if align    is None else align         

        Geometry.__init__(self, bounds, self.platform.wh, scalers, alignment)

        self.background     = 'background' if background is None else background
        self.colour         = Colour(self.theme, self.w)

        if outline is not None: 
            self.outline    = self.platform.create_outline(self.theme, outline, self.w)
            # print("create outline ", type(self).__name__)

        if square:
            xy = (scalers[0] * self.xyscale[0], scalers[1] * self.xyscale[1])
            if self.w>self.h:
                xy=(self.h+1, self.h)
            else:
                xy=(self.w+1, self.w)
            # print("Frame.__init__> square", square, self.xyscale, xy, self, self.geostr())
            self.resize(xy)

        # print("Frame.__init__> done", self.geostr())

    def scale_scalers(self, scalers, padding):
        return (scalers[0]*padding, scalers[1]*padding)

    def __iadd__(self, frame):
        self.frames.append(frame)
        return self

    # A full update drawns all frames, components and backgrounds regardless is the content is new
    #

    def realign(self, align=None, offset=None):
        if align is not None or offset is not None:
            # Only run self.align if new alignment/offset is provided
            self.align(align, offset) 
            
        if hasattr(self, 'create'):
            self.frames=[]
            self.create()
            
        # Always realign children based on their own *stored* alignment.
        # for f in self.frames:
        #     f.align(f.alignment) # Use the child's stored alignment, relative to its new parent size/position.
            # if hasattr(f, 'create'): f.create() # Assuming create() is needed to redraw internal components
        # print("Frame.realign> ", hasattr(self, 'create'), align, offset, self.framestr())

    def update(self, full=False):
        drawn = False
        if full: 
            self.draw_background()
            drawn = True
            # print("Frame.update> #frames=%d, full update %s" % (len(self.frames), full))

        for f in self.frames:
            # print("Frame.draw> ", f._need_to_redraw, type(f).__name__, "has draw ", hasattr(f, 'draw'), "has undraw ", hasattr(f, 'undraw'))
            # if hasattr(f, 'undraw'):  f.undraw()

            # print("Frame.draw> full", full, f._need_to_redraw, type(f).__name__, f.abs_rect(), "has draw ", hasattr(f, 'draw') )
            if f.update(full) or f.draw_outline(full): 
                self.platform.dirty_mgr.add(tuple(f.abs_rect()))
                drawn = True
            
            # print("Frame.update> rect", full, type(f).__name__, f.abs_rect())
        if drawn: 
            self.platform.dirty_mgr.add(tuple(self.abs_rect()))
            return True
        else:
            return False

    def draw_background(self):
        # print("Frame.draw_background", type(self).__name__, self.abs_rect())
        self.platform.fill(self.abs_rect(), colour=self.colour, colour_index=self.background)
        self.platform.dirty_mgr.add(tuple(self.abs_rect()))

    def draw_outline(self, full):
        if self.outline is not None and full: 
            self.outline.draw(self.abs_rect())
            # print("Frame.draw_outline>", self.abs_rect())
            self.platform.dirty_mgr.add(tuple(self.abs_rect()))
            return True
        else:
            return False
            
    def framestr(self):
        return "%-10s > wh %s, abs %s, parent %s, %s, %s, %s" % (type(self).__name__, self.wh, self.abs_rect(), self.bounds, self.scalers, self.alignment, self.theme)

    def frametext(self, f):
        return "%-10s > %s" % (type().__name__, super(Frame, f).__str__())

    def __str__(self):
        text = '%s Frame stack>' % type(self).__name__
        for f in self.frames:
            text += "\n  " + self.frametext( f ) + self.geostr()
        return text

    """ goes through the frames to see if they overlap  """
    """ test if the frame overlaps the one given        """
    def overlaps(self, f):
        # print("Frame.overlap> SRC algorithm")
        if   self.c >= f.a and f.c>= self.a and self.d >= f.b and f.d >= self.b:
            # print('Frame.overlap> detected')
            return True
        else:
            return False


    def check(self):
        # print("%s Frame overlap check for...>" % type(self).__name__)
        ok = True
        for index, f1 in enumerate(self.frames):
            if f1 == self: continue
            if index+1 == len(self.frames): break
            f2 = self.frames[index+1]
            if f1.overlaps(f2):
                print('Frame.check> frame %s overlaps %s' % (type(f1).__name__, type(f2).__name__) )
                ok = False
        return ok

#End of Frame class

"""
Is an alignment device to equally align all the subframes in columns, with a padding (ie spacing), that is even.
Works by scaling the scalars of each subframe accordingly.  Works iteratively, each time a subframe is added

These Framer classes will override the positional alignments for their axis
"""
class ColFramer(Frame):
    def __init__(self, parent, *args, **kwargs):
        padding=kwargs.pop('padding', 0.0)
        super().__init__(parent, *args, **kwargs)
        self.padding =  1-padding
        parent += self #make sure this frame is in the update() stack
        # print("ColFramer.__init__>", self.framestr())

    def __iadd__(self, frame):
        # super().__iadd__(self)
        self.frames.append(frame)
        columns = len(self.frames)
        summed_frame_w = 0
        for f in self.frames:
            f.scale((f.scalers[0]*self.padding*1/columns,f.scalers[1]*self.padding))
            summed_frame_w += f.w

        # Now work out how much space there is evenly between the frames, and align them
        frame_padding = (self.w - summed_frame_w)/(columns + 1)
        offset = frame_padding
        for f in self.frames:  
            f.realign( align=('col',f.alignment[1]), offset=offset)

            # for child in f.frames:
            #     child.realign(child.alignment) # Re-align child based on its *original* alignment
            
            offset += frame_padding + f.w
            # print("ColFrame.__iadd__> sum of frames" , summed_frame_w, f.framestr())
        return self

class RowFramer(Frame):
    def __init__(self, parent, *args, **kwargs):
        padding=kwargs.pop('padding', 0.0)
        super().__init__(parent, *args, **kwargs)
        self.padding =  1-padding
        parent += self #make sure this frame is in the update() stack
        # print("RowFramer.__init__>", self.framestr())

    def __iadd__(self, frame):
        # super().__iadd__(self)
        self.frames.append(frame)
        rows = len(self.frames)
        summed_frame_h = 0
        for f in self.frames:
            f.scale((f.scalers[0]*self.padding,f.scalers[1]*self.padding*1/rows))
            summed_frame_h += f.h

        # Now work out how much space there is evenly between the frames, and align them
        frame_padding = (self.h - summed_frame_h)/(rows + 1)
        offset = frame_padding
        for f in self.frames:  
            f.realign( align=(f.alignment[0],'row'), offset=offset)
            offset += frame_padding + f.h
            # print("RowFrame.__iadd__> sum of frames", summed_frame_h, f.framestr())
        return self


"""
Class to manage lists eg of menu items or sources to find previous and next items
    init with a a list of keys - these key are used to index a dict
    use the prev & next methods to get the previous and nexy items in the list
    use the curr method to read the current item

"""
class ListNext:
    def __init__(self, list, startItem):
        self._list       = list
        self._curr       = startItem
        self._curr_index = self.findItemIndex(self._curr)

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
        if self._curr_index > 0:
            self._curr_index -= 1
        else:
            self._curr_index  = len(self._list)-1
        self.curr = self._list[self._curr_index]
        return self.curr

    @property
    def next(self):
        if self._curr_index < len(self._list)-1:
            self._curr_index += 1
        else:
            self._curr_index  = 0
        self.curr = self._list[self._curr_index]    
        return self.curr

    # @property
    # def prev(self):
    #     i = self.findItemIndex(self._curr)
    #     if i > 0:
    #         self.curr = self._list[i-1]
    #     else:
    #         self.curr = self._list[-1]
    #     return self.curr

    # @property
    # def next(self):
    #     i = self.findItemIndex(self._curr)
    #     if i < len(self._list)-1:
    #         self.curr =  self._list[i+1]
    #     else:
    #         self.curr =  self._list[0]
    #     return self.curr

    def __str__(self):
        return "list>%s, current>%s" % (self._list, self.curr)


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

        hex_colours = [rgb_to_hex(color) for color in COLOUR_THEMES[theme]['range']]
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

    def get(self, colour_index=None, flip=False, opacity=255):
        # depending what the index is look-up:
        # print("Colour.get> INFO :", colour_index )
        if isinstance(colour_index, (int, float)):
            if flip:
                i = min(self.num_colours, (max(0, int(self.num_colours-colour_index))))
            else:
                i = min(self.num_colours, (max(0, int(colour_index))))
            # print("Screen.get_colour ", i, index)
            return self.colours[int(i)]
        elif colour_index in COLOUR_THEMES[self.theme]:
            return list(COLOUR_THEMES[self.theme][colour_index])+[opacity]
        else:
            print("Colour.get> WARN : index not known - look for purple ", colour_index)
            return purple


class Cache:
    def __init__(self, maxitems=100):
        self.cache  = {}
        self.oldest = [''] * maxitems

    def add(self, key, value):
        self.cache[key] = value
        if self.oldest[0] in self.cache: del self.cache[self.oldest[0]]
        self.oldest.append(key)
        self.oldest.pop(0)

    def find(self, key):
        if key in self.cache:
            return self.cache[key]
        else:
            return None




""" test code

    Create a FRAME
    Resize the box
    Go through all the move options

    Rescale the FRAME
    Check that the move options

    Check the coordinates in the Border

    Check the absolute coordinates for drawing primitives

"""
# bounds=[0,0,0,0], platform=None, display=None, scalers=[1.0,1.0], Valign='bottom', Halign='left'

def testFrame(bounds):
    print("\ntestFrame> Bounds ", bounds)
    f = Frame( bounds, None, None, (1.0, 1.0), Valign='bottom', Halign='centre')
    print("Result>", f.geostr())

    f.scale((0.5,0.5))
    print("Result>", f.geostr(),"\n")

    f = Frame( bounds, None, None, (1.0, 1.0), Valign='bottom', Halign='left')
    H=['left', 'centre', 'right']
    V=['top', 'middle', 'bottom']

    for v in V:
        for h in H:
            f.V = v
            f.H = h
            f.align()
            print("Result> align ", f.V, f.H, f.geostr(),"\n")

def testAbs(bounds):
    print("\ntestAbs> Bounds", bounds)
    f = Frame( bounds, None, None, (0.5, 0.5), Valign='bottom', Halign='left')
    print("Result>", f.geostr())

def testScale(bounds):
    print("\ntestScale> Bounds", bounds)
    f = Frame( bounds, None, None, (1.0, 1.0), Valign='bottom', Halign='left')
    print("Result>", f.geostr(),"\n")

    for x in range(1,10,1):
        for y in range(1,10,1):
            f.scale((x/10, y/10))
            print("Result> scale ", x/10, y/10, f.geostr())


if __name__ == "__main__":
    try:
        testFrame( (0,0,999,499))
        # testFrame( (1000,500,1999,999))
        # b= [(641, 321, 1280, 400), (0,0,999,499)]
        # testScale(b[0]  )

        # testAbs( (0,0,999,499) )
        # testAbs( (1000,500,1999,999) )

        time.sleep(1)

    except KeyboardInterrupt:
        pass
