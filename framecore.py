#!/usr/bin/env python
"""
 Base classes for generic Frame management
    - Geometry:  manages the coordinate system used for enclosing rectangles
    - Frame: hierarchical frames, managed for overlap and alignment


 Part of mVista preDAC2 project

 v1.0 Baloothebear4 May 202

"""

""" a data type for coordinates - converts lists to dicts and back
    - initialise from a 4 point list
    - read as 4 point list
    - write to the coordinates via setters to check legimacy

"""


import os, time
import numpy as np
PI = 3.14152
# from oleddriver import internalOLED     # used for Test purposes
# from platform   import Platform         # used for Test purposes

class Geometry():
    def __init__(self, bounds=[0,0,0,0]):
        self._abcd          = [0,0,0,0]
        self._bounds        = bounds
        self.min_offset     = 0
        self.circle_scale   = 1
        self.centre_offset  = 0  #PC of the height offsets the centre of a circle eg -0.5 moves to the bottom
        self.endstops       = (0, 2*PI)
        # print("Geometry.init> abcd %s, bounds %s, boundswh %s, size %s, coords %s" % ( self.abcd, self._bounds, self._boundswh, self.wh, self.coords))


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
            raise ValueError('set.c > value exceed bounds ', val, self.geostr())

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
            self.c = wh[0] -1
        except ValueError:
            self.c = self.boundswh[0] -1
            print("!!! Geometry.resize> outside bounds w %f, set to bounds, %s" % (wh[0], self.geostr()) )
        try:
            self.d = wh[1] -1
        except ValueError:
            self.d = self.boundswh[1] -1
            print("!!! Geometry.resize> outside bounds h %f, set to bounds, %s" % (wh[1], self.geostr()) )
        # print("Geometry.resize to ", wh, self.geostr())

    @property
    def bounds(self):  #resize the boundary to the size of the frame
        return(self._bounds)

    @property
    def xyscale(self):
        aspect_ratio = self.w/self.h
        xyscale      = (aspect_ratio, 1.0) if self.w > self.h else (1.0, aspect_ratio)
        return xyscale

    """ calculating the size will need to be more dynamic if the drawing could exceed the bounds """
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
            self.resize( [ int(self.boundswh[0] * scalers[0]), int(scalers[1] * self.boundswh[1])] )
        else:
            raise ValueError('Geometry.scale > scale is zero ', scalers, self.geostr())

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

    def go_top(self):
        self.move_cd( (self.c, self.top) )

    def go_middle(self):
        self.move_middle( self.top/2 )

    def go_bottom(self):
        self.move_ab( (self.a, 0) )
        # print("Geometry.go_bottom>", self.geostr())

    def go_left(self):
        self.move_ab( (0, self.b) )
        # print("Geometry.go_left>", self.geostr())

    def go_centre(self):
        self.move_centre( self.right/2 )

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
    def abs_origin(self, screen_h=0, offset=(0, 0)): # Return (x, y)
        # origin = (self.x0+offset[0], (1+self.top+ (self.boundswh[1] - self.h) - self.y0-offset[1]) )
        origin = (int(self.x0+offset[0]), int(screen_h- (self.y0-offset[1]+self.h-1)) )
        return origin

    def abs_centre(self, screen_h=0, offset=(0, 0)): # Return (x, y)
        # origin = (self.x0+offset[0], (1+self.top+ (self.boundswh[1] - self.h) - self.y0-offset[1]) )
        origin = [self.centre[0]+offset[0], screen_h- (self.centre[1]+self.h*(self.centre_offset)-offset[1]-1) ]  #-self.h deleted from this
        # print("Geometry.abs_centre>", self.centre, origin)
        return origin

    def abs_rect(self, screen_h=0, offset=(0, 0), wh=None):  # Return (x, y, w, h)
        wh = [self.wh[0], self.wh[1]] if wh is None else wh
        rect = [int(self.x0+offset[0]), int(screen_h- (self.y0+self.h-offset[1]-1)) ] + wh
        return rect

    def theta(self, val):    # return an angle in radians from a value range -1 to +1
        return (PI*(val))-PI/2

    def arctheta(self, angle): # return a value range -1 to +1 from an angle in radians
        return (angle-PI/2)/PI

    def anglexy(self, val_pc, radius, gain=0, amp_scale=1, screen_h=0, xyscale=(1,1) ):
        # Assume that 0 (abs) val_pc is 0600, PI is 0600, by default 0 val angle = first end stop
        # xscale is to create eliptical shapes
        theta = self.theta(self.min_offset+self.circle_scale*val_pc) #to make sure this aligns at 0 = 0600
        xy = [self.centre[0]+xyscale[0]*radius*(amp_scale+gain)*np.sin(theta), (screen_h)-(self.centre[1]+self.h*(self.centre_offset)+xyscale[1]*radius*(amp_scale+gain)*np.cos(theta) )]
        # print("Geometry.anglexy>theta %2.2f xy %s, radius %f, gain %2.2f, val_pc %2.2f, amp_scale %f, centre %s, centre_offset %f, screen_h %d" % (theta, xy, radius, gain, val_pc, amp_scale, self.centre, self.centre_offset, screen_h))
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
        return( "name %s, abcd %s, bounds %s, boundswh %s, size %s, coords %s, abs org %s, abs rect %s" % (type(self).__name__, self.abcd, self._bounds, self.boundswh, self.wh, self.coords, self.abs_origin(s), self.abs_rect(s)))

    def align(self, Halign='left', Valign='top'):
        """
            align will use the anchors: 'top, middle, bottom', 'left, centre, right' to set the
            coordinates of the Frame within the boundary
        """
        # parse V and H alignment anchors
        # check that the frame is still in bounds
        # this is where the frame coordiantes are setup
        self.V          = Valign
        self.H          = Halign
        # print("Geometry.align> top %d, right %d, abcd %s, wh %s, V=%s, H=%s" % (self.top, self.right, self.abcd, self.wh, self.V, self.H))

        if self.V   == 'top':
            self.move_cd( (self.c, self.top) )
            # move so that self.d = self.bounds.d
        elif self.V == 'middle':
            self.move_middle( int(self.top/2) )
            # move so that middle(self) = middle(self.bounds) : middle =
        elif self.V == 'bottom':
            self.go_bottom()
            # move so that self.b = self.bounds.b
        else:
            raise ValueError('Frame.align: unknown vertical anchor (top, middle, bottom)->', self.V)

        if self.H   == 'left':
            self.go_left()
            # move so that self.a = self.bounds.a
        elif self.H == 'centre':
            self.move_centre( int(self.right/2))
            # move so that centre(self) = centre(self.bounds)
        elif self.H == 'right':
            self.move_cd( (self.right, self.d) )
            # move so that self.c = self.bounds.c
        else:
            raise ValueError('Frame.align: unknown horz anchor (left, centre, right)->', self.H)
        # print("Frame.align> to", self.geostr())


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
    """

    def __init__(self, bounds=[0,0,0,0], platform=None, display=None, scalers=[1.0,1.0], Valign='bottom', Halign='left', square=False):
        """
            scalars is a tuple (w%, h%) where % is of the bounds eg (0,0,64,32) is half the width, full height
            bounds is list of the bottom left and upper right corners eg (64,32)
        """
        Geometry.__init__(self, bounds)
        self.platform   = platform    #only needed by the top Frame or Screen, as is passed on draw()
        self.frames     = []         #Holds the stack of containing frames
        self.display    = display
        # xy = (scalers[0] * self.xyscale[0], scalers[1] * self.xyscale[1]) if square else scalers
        self.scale(scalers)
        self.align(Halign, Valign)

        if square:
            xy = (scalers[0] * self.xyscale[0], scalers[1] * self.xyscale[1])
            if self.w>self.h:
                xy=(self.h+1, self.h)
            else:
                xy=(self.w+1, self.w)
            # print("Frame.__init__> square", square, self.xyscale, xy, self, self.geostr())
            self.resize(xy)
            self.align(Halign, Valign)
        # print("Frame.__init__> square", square, self.xyscale, scalers, self, self.geostr())


    def __iadd__(self, frame):
        self.frames.append(frame)
        return self

    def draw(self):
        # print("Framecore.draw. #frames=", len(self.frames))
        for f in self.frames:
            # print("Frame.draw> ", type(f).__name__, "has draw ", hasattr(f, 'draw'), "has undraw ", hasattr(f, 'undraw'))
            # if hasattr(f, 'undraw'):  f.undraw()

            not_changed = f.draw()
            # if not_changed is None: self.display.refresh(self.abs_rect(screen_h=self.display.h))
    # 
    # def undraw(self):
    #     # print("Frame.undraw> generic", type(self).__name__)
    #     self.display.fill(self.abs_rect(screen_h=self.display.h))

    def frametext(self, f):
        return "%-10s > %s" % (type(f).__name__, super(Frame, f).__str__())

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