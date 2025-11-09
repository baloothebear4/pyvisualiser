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
    def __init__(self, bounds=None, screen_wh=(1280,400), scalers=(1.0,1.0), align=('centre', 'middle'), square=False, outline_w=0, padding=0):
        """
            bounds is list of the bottom left and upper right corners eg (0,0,64,32)
            screen_wh is the size of the actual display screen - needed for absolute coordinates
            scalers is a tuple (w%, h%) where % is of the bounds eg (0,0,64,32) is half the width, full height
            align is a tuple (horizontal, vertical) - where horz is one of 'left', 'right', 'centre', vertical 'top', 'middle', 'bottom'
            square is to force the shape to have w=h
            outline_w is pixels to reduce the size of the frame to allow for an outline border
            padding is pixels to the frame size to allow a blank space round the frame
        """
        self._abcd          = [0,0,0,0]
        self._bounds        = [0,0, screen_wh[0]-1, screen_wh[1]-1] if bounds is None else bounds
        self.screen_wh      = screen_wh
        self.alignment      = align
        self.scalers        = scalers
        self.square         = square
        self.outline_w      = outline_w
        self.padding        = padding

        self.min_offset     = 0
        self.align_offset   = 0
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
            raise ValueError('set.a > value exceed bounds ', val, self.boundswh[0], self.geostr())


    @property
    def b(self):
        return self._abcd[1]

    @b.setter
    def b(self, val):
        if val >= 0 and val <= self.boundswh[1]:
            self._abcd[1] = int(val)
        else:
            raise ValueError('set.b > value exceed bounds ', val, self.boundswh[1], self.geostr())

    @property
    def c(self):
        return self._abcd[2]

    @c.setter
    def c(self, val):
        if val < self.a:
            raise ValueError(f'set.c < set.a: {val} < {self.a}. Cannot invert coordinates.', self.geostr())
            
        if val >= 0 and val <= self.boundswh[0]:
            self._abcd[2] = int(val)
        else:
            raise ValueError('set.c > value exceed bounds ', val, self.boundswh[0], self.geostr())


    @property
    def d(self):
        return self._abcd[3]

    @d.setter
    def d(self, val):
        # if val >= 0 and val <= self.boundswh[1]:
        #     self._abcd[3] = int(val)
        # else:
        #     raise ValueError('set.d > value exceed bounds ', val, self.geostr())
        if val < self.b:
            raise ValueError(f'set.d < set.b: {val} < {self.b}. Cannot invert coordinates.', self.geostr())
            
        if val >= 0 and val <= self.boundswh[1]:
            self._abcd[3] = int(val)
        else:
            raise ValueError('set.d > value exceed bounds ', val, self.boundswh[1], self.geostr())

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
    def abs_wh(self):
        return self.abs_rect()[-2:]

    @property
    def abs_h(self):
        return self.abs_wh[1]
    
    @property
    def abs_w(self):
        return self.abs_wh[0]
    
    @property
    def xy(self):
        return (self.a, self.b)

    @property
    def centre(self):
        return self.normxy( ( (self.c+self.a)/2, (self.d+self.b)/2) )

    @property
    def top(self):
        return self.boundswh[1]-1

    @property
    def right(self):
        return self.boundswh[0]-1

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
    
    def change_bounds(self, coords):
        self._bounds = coords

    def resize(self, wh):
        # print("Geometry.resize start to", wh, self.geostr())
        # Square means that the aspect ration is 1:1, so resize according to the largest of w or h
        if self.square:
            self.scalers = (self.scalers[0] * self.xyscale[0], self.scalers[1] * self.xyscale[1])
            if wh[0]>wh[1]:
                wh=(wh[1]+1, wh[1])
            else:
                wh=(wh[0]+1, wh[0])
            print("Geometry.resize> square", wh, self.xyscale, self, self.geostr())

        # reduce the sw & h to allow for outline width

        self.a = 0
        self.b = 0
        try:
            self.c = wh[0] -1 if wh[0] > 0 else 0
        except ValueError:
            self.c = self.boundswh[0] -1
            # self.align()
            print("!!! Geometry.resize> outside bounds w %f, set to bounds, %s" % (wh[0], self.geostr()) )
        try:
            self.d = wh[1] -1 if wh[1] > 0 else 0
        except ValueError:
            self.d = self.boundswh[1] -1
            # self.align()
            print("!!! Geometry.resize> outside bounds h %f, set to bounds, %s" % (wh[1], self.geostr()) )

        # print("Geometry.resize end to ", wh, self.geostr())
        self.align()

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
        if scalers is None: scalers = self.scalers
        if scalers[0]>0 and scalers[1]>0:
            self.scalers = scalers
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
        self.move_middle( int((self.top+1)/2) ) # fix rounding error

    def go_bottom(self):
        self.move_ab( (self.a, 0) )
        # print("Geometry.go_bottom>", self.geostr())

    def go_left(self, offset=0):
        self.move_ab( (0+offset, self.b) )
        # print("Geometry.go_left>", self.geostr())

    def go_centre(self):
        self.move_centre( int((self.right+1)/2) ) # fix rounding error

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

    # the drawing canvas is the space inside the perimeter of the Frame, inside the outline and the padding
    # this is also the bounds coordiantes of a child frame
    def canvas_coords(self):
        canvas_a, canvas_b, canvas_c, canvas_d = self.norm()
        shrink=self.outline_w+self.padding
        return [canvas_a+shrink, canvas_b+shrink, canvas_c-shrink, canvas_d-shrink]


    """ return the absolute coordinates for drawing on screen with pygame, using Top Left ordinates """
    # centre does not change regardless of borders and padding
    def abs_centre(self, offset=(0, 0)): # Return (x, y)
        # origin = (self.x0+offset[0], (1+self.top+ (self.boundswh[1] - self.h) - self.y0-offset[1]) )
        origin = [self.centre[0]+offset[0], self.screen_wh[1]- (self.centre[1]+self.h*(self.centre_offset)-offset[1]) ]  # -1????
        # print("Geometry.abs_centre>", self.centre, origin)
        return origin
    
    # def abs_origin(self, offset=(0, 0)): # Return (x, y)
    #     # origin = (self.x0+offset[0], (1+self.top+ (self.boundswh[1] - self.h) - self.y0-offset[1]) )
    #     origin = (int(self.x0+self.outline_w+self.padding+offset[0]), int(self.screen_wh[1]- (self.y0-self.outline_w-self.padding-offset[1]+self.h+1)) ) # -1????
    #     return origin

    def abs(self, offset=(0, 0), wh=None, xy_shrink=0, wh_shrink=0):  # Return (x, y, w, h)
        wh      = [int(self.w-wh_shrink), int(self.h-wh_shrink)] if wh is None else wh
        rect    = [int(self.x0+xy_shrink+offset[0]), int(self.screen_wh[1]- (self.y0+self.h-xy_shrink-offset[1])) ] + wh
        # print("Geometry.abs>",type(self).__name__, self.coords, self.bounds, self.screen_wh[1], self.wh, self.h, "offset", offset, xy_shrink, wh_shrink, "rect", rect)
        return rect

    def abs_rect(self,offset=(0, 0), wh=None):
        return self.abs(offset,wh,xy_shrink=int(self.outline_w+self.padding), wh_shrink=(self.outline_w+self.padding)*2)
    
    def abs_background(self, offset=(0, 0), wh=None):
        return self.abs(offset, wh, xy_shrink=int(self.outline_w), wh_shrink=self.outline_w*2)
    
    def abs_outline(self, offset=(0, 0), wh=None):
        return self.abs(offset, wh) # pygame >v2.1 Outline width draws within the perimiter of the rect ###xy_shrink=int(self.outline_w/2), wh_shrink=self.outline_w)
    
    def abs_perimeter(self, offset=(0, 0), wh=None):
        return self.abs(offset, wh)
    
    def abs_origin(self, offset=(0, 0)):
        xy = self.abs_rect(offset)
        return (xy[0], xy[1])

    def abs_coords(self,offset=(0, 0), wh=None):
        # coords= self.abs(offset,wh,xy_shrink=int(self.outline_w+self.padding), wh_shrink=(self.outline_w+self.padding))    
        rect = self.abs_rect()   
        coords = (rect[0], rect[1], rect[0]+rect[2]-1, rect[1]+rect[3]-1)
        # print("Geometry.abs_coords>",coords)
        return coords
    
    # updates the coordinates the align accordingly in the frame
    def align_coords(self, coords, wh, align=('centre','middle')):
        new_coords    = list(coords)

        if align[1]   == 'top':
            # new_coords[1] = coords[1] + int(self.h)
            pass

        elif align[1] == 'middle':
            new_coords[1] = coords[1] + int((self.abs_rect()[3] - wh[1])/2)

        elif align[1] == 'bottom':
            new_coords[1] = coords[1] + int((self.abs_rect()[3] - wh[1])) #- int(self.coords[3] + wh[1])

        else:
            raise ValueError('Geometry.align_coords>: expected vertical anchor (top, middle, bottom) found->', align)

        if align[0]   == 'left':
            pass    #leave as is

        elif align[0] == 'centre':
            new_coords[0] = coords[0] + int((self.abs_rect()[2] - wh[0])/2)

        elif align[0] == 'right':
            new_coords[0] = coords[0] + int((self.abs_rect()[2] - wh[0]))

        else:
            raise ValueError('Geometry.align_coords: expected horz anchor (left, centre, right) found->', align)
        
        # print("Geometry.align_coords >", type(self).__name__, self.h, self.w, coords, new_coords, align, wh)
        return new_coords


    """ Circular coordiante calculations"""
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
        print("Geometry.anglescale> start endstops", endstops, "after", self.endstops, "minmax", minmax, "scale", (minmax[1]-minmax[0]), )
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
        return( "name %s, outline_w %d, abcd %s, bounds %s, boundswh %s, size %s, coords %s, abs org %s, offset %s\n         abs rect %s, abs outline %s, abs_perimeter %s, abs_background %s, abs_centre %s, wh %s, padding %s" \
            % (type(self).__name__, self.outline_w, self.abcd, self._bounds, self.boundswh, self.wh, self.coords, self.abs_origin(), self.align_offset, self.abs_rect(), self.abs_outline(),self.abs_perimeter(), self.abs_background(), self.abs_centre(), self.wh, self.padding))

    # alignment offset is the % of the parent wh to offset
    def align(self, align=None, offset=None):
        """
            align will use the anchors: 'top, middle, bottom', 'left, centre, right' to set the
            coordinates of the Frame within the boundary
        """
        # parse V and H alignment anchors
        # check that the frame is still in bounds
        # this is where the frame coordiantes are setup
        if align  is not None: self.alignment    = align
        if offset is not None: self.align_offset = offset

        # print("Geometry.align start> top %d, right %d, abcd %s, wh %s >> %s" % (self.top, self.right, self.abcd, self.wh, self.geostr()))

        if self.alignment[1]   == 'top':
            self.go_top( )
            # move so that self.d = self.bounds.d
        elif self.alignment[1] == 'middle':
            self.go_middle()
            # move so that middle(self) = middle(self.bounds) : middle =
        elif self.alignment[1] == 'row':
            self.go_top(int(self.boundswh[1]*self.align_offset))
            # move so its packs from the top - the offset ie downwards
        elif self.alignment[1] == 'bottom':
            self.go_bottom()
        else:
            raise ValueError('Frame.align: expected vertical anchor (top, middle, bottom) found->', self.alignment[1])

        if self.alignment[0]   == 'left':
            self.go_left()
            # move so that self.a = self.bounds.a
        elif self.alignment[0] == 'centre':
            self.move_centre( int((1+self.right)/2))
            # move so that centre(self) = centre(self.bounds)
        elif self.alignment[0] == 'right':
            self.move_cd( (self.right, self.d) )
            # move so that self.c = self.bounds.c
        elif self.alignment[0] == 'col':
            self.go_left(int(self.boundswh[0]*self.align_offset))
            # move so its packs from the top - the offset ie downwards    
        else:
            raise ValueError('Frame.align: expected horz anchor (left, centre, right) found->', self.alignment[0])
        # print("Geometry.align end > to", self.alignment, self.geostr())

# end Geometry class


FULLSCALE = (1.0,1.0)
CENTRED   = ('centre', 'middle')
OUTLINE   = None #{ 'width' : 1, 'radius' : 0, 'colour_index' : 'foreground'}

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


    def __init__(self, parent, scalers=FULLSCALE, align=CENTRED, square=False, theme=None, background=None, outline=None, padding=0):
        """
            scalars is a tuple (w%, h%) where % is of the bounds eg (0,0,64,32) is half the width, full height
            align is a tuple (horizontal, vertical) - where horz is one of 'left', 'right', 'centre', vertical 'top', 'middle', 'bottom'
            bounds is list of the bottom left and upper right corners eg (64,32)

            NB: making outline = '' will draw frame outlines around all frames that do not have their own draw functions - useful for tweaking screen design
        """
        # print("Frame.__init__> startup>>>", type(self).__name__, align, scalers, theme, background)

        scalers         = FULLSCALE   if scalers  is None else scalers
        alignment       = CENTRED     if align    is None else align      
        outline         = OUTLINE     if outline  is None else outline

        if isinstance(parent, Frame):
            """ Sub-frame, so scale to the size of the parent Frame """
            bounds          = parent.canvas_coords()
            self.theme      = parent.theme      if theme    is None else theme           
            self.platform   = parent.platform
            # background      = parent.background_frame.background if parent.background_frame is not None and background is None else background
            # print("Frame.__init__ subframe>", type(self).__name__, scalers, alignment, theme, bounds, "parent", type(parent).__name__, parent.geostr())
        else:
            """ Screen (aka top-level Frame), so scale to the boundary """
            bounds          = parent.boundary
            self.platform   = parent    #only needed by the top Frame or Screen, as is passed on draw()
            self.theme      = 'std'                  if theme    is None else theme  
            background      = 'background'           if background is None else background

        self.frames         = []         #Holds the stack of containing frames
        self.outline_frame  = self.platform.create_outline(self, outline)

        Geometry.__init__(self, bounds, self.platform.wh, scalers, alignment, square, self.outline_frame.w, padding)

        self.colours                  = Colour(self.theme, self.w)
        self.background_frame         = self.platform.create_background(self, background)

        # print("Frame.__init__> done", self.background_frame.background, self.framestr())

    def __iadd__(self, frame):
        self.frames.append(frame)
        return self


    # to dynamically change the geometry:
    # 1. scale and realign the current frame
    # 2. update the geometry of the children frames recusively (the scaling & alignment remains, its the change in parent bounds that causes the update)
    def update_geometry(self, bounds, scalers=None, align=None, offset=None):
        print("Frame.update_geometry> ", bounds, scalers, align, offset, self.framestr())
        self.change_bounds(bounds)
        self.scale(scalers)
        self.align(align, offset)
        if hasattr(self, 'configure'): self.configure()

    # 3. If I am an AxisFramer, I need to tell my children their FINAL bounds.
        # if isinstance(self, AxisFramer): # <-- Check for the new base class
        #     self.refactor_bounds()
        #     #results in a new set of bounds
        # # else:
        for f in self.frames:
            print("Frame.update_geometry> child from ", f.bounds, "to new parent", f.abs_coords(), f.scalers, f.align_offset,"has config", hasattr(f, 'configure'), f.framestr())
            f.update_geometry(self.canvas_coords())

            # some base classes have complex configurations that need to be updated once the parent geometry changes
            if hasattr(f, 'configure'): f.configure()


    # update the screen with the frame contents
    # whether the background and outline is drawn depends on whether the frame update is per frame or per metadata change
    #
    def update_screen(self, full=False, **kwargs):
        self.draw_background(full)
        self.draw_outline(True)
        # print("Frame.update> #frames=%d, full update %s" % (len(self.frames), full))

        for f in self.frames:
            # print("Frame.draw> ", f._need_to_redraw, type(f).__name__, "has draw ", hasattr(f, 'draw'), "has undraw ", hasattr(f, 'undraw'))
            # f.draw_background(full)
            if f.update_screen(full, **kwargs): self.platform.dirty_mgr.add(tuple(f.abs_rect()))   #<---- fix this in due course
            f.draw_outline(full)


    def draw_background(self, full=True):
        # print("Frame.draw_background", type(self).__name__, full, self.abs_background())
        self.background_frame.draw(full)

    def always_draw_background(self, full=True):
        # print("Frame.draw_background", type(self).__name__, full, self.abs_background())
        self.background_frame.per_frame_update(full)

    def draw_outline(self, full=True):
        if self.outline_frame is not None and full: # --> need to draw it everytime else the background erases it
            self.outline_frame.draw()
            # print("Frame.draw_outline> ", full, type(self).__name__, self.abs_background())
            
    def framestr(self):
        return "%-10s > wh %s, abs %s, parent %s, %s, %s, %s %s" % (type(self).__name__, self.wh, self.abs_rect(), self.bounds, self.scalers, self.alignment, self.theme, self.align_offset)

    def frametext(self, f):
        return "%-10s > %s" % (type(f).__name__, f.geostr())

    def __str__(self):
        text = '%s Frame stack>' % (type(self).__name__)
        text += "\n  " + self.geostr( self )
        # text += "\n  " + self.__str__()
        for f in self.frames:
            text += "\n  " + f.geostr( f )
            text += "\n  >>" + f.__str__()
        text += "\n  "
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

This is dynamic and can rescale Frames dynamically using the col_ratios attribute.  If this is not use then Frames simply are sized equal
"""
#
"""--Row and Col Framers to arrange frames intuitively--------------------------"""
class AxisFramer(Frame):
    """
    Generic axis-based framer.  
    Handles layout along a single axis (x for columns, y for rows).
    """
    def __init__(self, parent, ratios=None, axis='x', padpc=0, **kwargs):
        super().__init__(parent, **kwargs)
        self.axis = axis  # 'x' for ColFramer, 'y' for RowFramer
        self.padpc = 1 - padpc
        self.ratios = ratios
        self._scalers = self._normalize(ratios) if ratios is not None else []
        self.dynamic_scalers = []
        self.frames = []
        parent += self  # ensure parent tracks updates
        print(f"{self.__class__.__name__}.__init__> {self.axis}-axis ratios={self.ratios} {self.framestr()}")

    def _normalize(self, values):
        """Normalize ratios to sum to 1.0"""
        if isinstance(values, int):
            values = [1.0] * values
        values = list(map(float, values))
        total = sum(values)
        if total <= 0:
            raise ValueError("Cannot normalize zero or negative ratios", values)
        normalized = [v / total for v in values]
        print(f"{self.__class__.__name__}.normalize> {values} → {normalized}")
        return normalized

    def __iadd__(self, frame):
        """Add frame to this framer and assign it proportional geometry."""
        self.frames.append(frame)

        # If no predefined ratios, infer dynamically from child scalers
        if self.ratios is None:
            self.dynamic_scalers.append(frame.scalers[0 if self.axis == 'x' else 1])
            self._scalers = self._normalize(self.dynamic_scalers)

        count = len(self.frames)
        if count > len(self._scalers):
            raise ValueError(f"{self.__class__.__name__}.__iadd__> Too many frames ({count}) for {len(self._scalers)} ratios")

        # Apply scaling and alignment
        self._apply_layout()

        return self
    
    #When Framers are nested the children Frames will be aligned first, these need to 
    #locked in place through updating the parent boundary and offset set back at zero
    #hence recalu
    def refactor_bounds(self):
        print("\nAxisFramer.refactor_bounds> bounds %s, offset %s, scalers %s" %(self.bounds, self.align_offset, self.scalers))
        print(self)

    def _apply_layout(self):
        """Compute frame sizes and positions along this axis."""
        frames = self.frames
        count = len(frames)
        if count == 0:
            return

        # Padding calculation
        frame_padding = (self.w if self.axis == 'x' else self.h) * (1 - self.padpc) / (count + 1)
        offset = frame_padding

        for i, f in enumerate(frames):
            # scale width or height depending on axis
            if self.axis == 'x':

                print("AxisFramer._apply_layout> W offset %3f" % (offset/self.boundswh[0]))
                allocated_w = int(self.boundswh[0] * self._scalers[i])
                f.update_geometry(self.canvas_coords(), 
                                  scalers = (self.padpc * self._scalers[i], f.scalers[1]),
                                  align   = ('col', f.alignment[1]), 
                                  offset  = offset/self.boundswh[0])
                offset += frame_padding + f.w #<-----a square Frame will not use all its allocated space, which means there is a gap - what shall we do with this?
                if f.w < allocated_w: 
                    print("\nAxisFramer._apply_layout> child frame has not used allocated space - w", f.w, allocated_w)
                    offset += int(allocated_w- f.w) #assume the gap is due to rounding errors so add half the gap back

            else:

                print("AxisFramer._apply_layout> H offset %3f" % (offset/self.boundswh[1]))
                allocated_h = int(self.boundswh[1] * self._scalers[i])
                f.update_geometry(self.canvas_coords(),
                                  scalers= (f.scalers[0], self.padpc * self._scalers[i]),
                                  align  = (f.alignment[0],'row'), 
                                  offset = offset/self.boundswh[1])
                offset += frame_padding + f.h
                if f.h < allocated_h: 
                    print("\nAxisFramer._apply_layout> child frame has not used allocated space - h", f.h, allocated_h)
                    offset += int(allocated_h- f.h) #assume the gap is due to rounding errors so add half the gap back




    # def _apply_layout(self):
    #     """Compute frame sizes and positions along this axis."""
    #     frames = self.frames
    #     count = len(frames)
    #     if count == 0:
    #         return

    #     # 1. Calculate running variables
    #     total_axis_length = self.w if self.axis == 'x' else self.h
    #     frame_padding = int(total_axis_length * (1 - self.padpc) / (count + 1))
    #     offset = frame_padding # offset is the starting position RELATIVE to parent's X0/Y0

    #     # Parent's absolute origin for convenience
    #     parent_x0, parent_y0, _, parent_y1 = self.abs_coords()
        
    #     for i, f in enumerate(frames):
            
    #         # 2. Calculate ALLOCATED size based on parent's size and the child's scaler
    #         allocated_w = int(self.boundswh[0] * self._scalers[i]) if self.axis == 'x' else self.boundswh[0]
    #         allocated_h = self.boundswh[1] if self.axis == 'x' else int(self.boundswh[1] * self._scalers[i])
            
    #         # 3. Determine the CHILD'S ABSOLUTE BOUNDING BOX (X0, Y0, X1, Y1)
    #         if self.axis == 'x':
    #             x0 = parent_x0 + offset                  # Absolute X start = Parent X0 + running relative offset
    #             y0 = parent_y0                           # Y start is the parent's Y0
    #             x1 = x0 + allocated_w - 1                # Absolute X end = X0 + Allocated Width - 1
    #             y1 = parent_y1                           # Y end is the parent's Y1 (full height)
                
    #             # Use 1.0 scalers since the bounds are the precise allocated size
    #             child_scalers = (self.padpc * self._scalers[i], f.scalers[1])
    #             child_align = ('col', f.alignment[1])
                
    #             # Update offset for NEXT frame
    #             offset += allocated_w + frame_padding
                
    #         else: # axis == 'y' (Vertical/RowFramer)
    #             x0 = parent_x0
    #             y0 = parent_y0 + offset                  # Absolute Y start = Parent Y0 + running relative offset
    #             x1 = self.x1 # Parent's absolute right coordinate
    #             y1 = y0 + allocated_h - 1                # Absolute Y end = Y0 + Allocated Height - 1
                
    #             # Use 1.0 scalers since the bounds are the precise allocated size
    #             child_scalers = (f.scalers[0], self.padpc * self._scalers[i])
    #             child_align = (f.alignment[0], 'row')

    #             # Update offset for NEXT frame
    #             offset += allocated_h + frame_padding 

    #         # 4. Final update_geometry call with the precisely calculated bounds
    #         f.update_geometry(bounds= (x0, y0, x1, y1), 
    #                           scalers=child_scalers,
    #                           align=child_align, 
    #                           offset=0) # Safe now that align_offset is disabled!


class ColFramer(AxisFramer):
    def __init__(self, parent, col_ratios=None, padpc=0, **kwargs):
        super().__init__(parent, ratios=col_ratios, axis='x', padpc=padpc, **kwargs)


class RowFramer(AxisFramer):
    def __init__(self, parent, row_ratios=None, padpc=0, **kwargs):
        super().__init__(parent, ratios=row_ratios, axis='y', padpc=padpc, **kwargs)

#------------------- End Framers -----------------------------------------------------

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
        
    def is_colour(self, colour):
        if isinstance(colour, str):
            return colour in COLOUR_THEMES[self.theme]
        else:
            return False


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
