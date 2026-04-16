'''
Analogue VU meters have image based background and scale based background.  The rendering and light effects are  cruicial to get 
a good simulation of Analogue VU meters

Mar 2026 Baloothebear4. v1.0
- refectored from frames.py and subframes.py

'''

from    pyvisualiser.core.framecore  import Frame, get_asset_path, Smoother, RowFramer, ColFramer
from    pyvisualiser.core.components import Text, Line, Image, Bar
from    pyvisualiser.styles.presets  import Centred, PI
from    pyvisualiser.styles.styles   import *
from    pyvisualiser.styles.profiles import ProfileManager
from    pyvisualiser.visualisers.metadata   import TextFrame


class VU:
    """ A place for all the moving elements of a VU bar or meter """
    DECAY     = 0.3   # Lower is longer delay - This is the amount that a bar reduces each period
    PEAKDECAY = 0.01  # pc of Decay to use for peak bars

    def __init__(self, platform, channel, decay=DECAY, smooth=8):
        self.peaks          = 0.0            # This is used to hold the values and implement a smoothing factor
        self.current        = Smoother(1.0, smooth)    # array of smoothers
        self.decay          = decay
        self.peak_decay     = decay * VU.PEAKDECAY
        self.platform       = platform
        self.channel        = channel

    def read(self):
        """
        Decay work by assuming that all bars naturally decay at a fixed rate and manner (eg lin /log)
        Use the same method as spectrum analyser
        """
        target_height      = self.platform.vu[self.channel]
        smoothedpeak = 0

        if target_height > self.current.smoothed():
            self.current.add(target_height)

        if self.current.smoothed() > self.peaks:
            self.peaks = self.current.smoothed()

        height = self.current.smoothed()
        if height > smoothedpeak: smoothedpeak = height

        if self.current.smoothed() < self.decay/100.0:
            self.current.add(0.0)
        else:
            self.current.add(height* (1- self.decay))

        if self.current.smoothed() < self.decay/3.0:  #Look for when its gone quiet to clear the peak bars
            self.peaks = 0.0

        self.peaks *= (1- self.peak_decay)

        return height, self.peaks


"""
Analogue VU Meter frames
"""
class VUMeter(Frame):
    """
        Background for the VU Meter comprising
        - a horiziontal line
        - calibrated dB level markers
        - a needle base
        - optional arc
        - optional background image
    """
 
    def __init__(self, parent, channel, scalers=None, align=Centred, outline=None, square=False, background=None, padding=0,
                 style: VUMeterStyle = None, z_order=0):
        
        # 1. Capture all non-style configuration parameters into self.config
        self.config = {
            'channel': channel,
            'scalers': scalers,
            'align': align,
            'outline': outline,
            'background': background,
            'square': square,
            'padding': padding,
            'z_order': z_order
        }

        # 2. Resolve Style (VUMeterStyle)
        profile = ProfileManager.get_profile()
        self.style = style if style is not None else profile.get_style('vu_meter')
        if self.style is None:
            self.style = VUMeterStyle()

        # 3. Determine the channel/alignment for the parent Frame.__init__
        align_channel = channel if channel in ('left', 'right') else align[0]
        
        # 4. Call the parent's __init__ using the stored values
        super().__init__(parent, 
                         scalers=self.config['scalers'], 
                         align=(align_channel, self.config['align'][1]),
                         theme=self.style.theme, 
                         background=self.config['background'],
                         square=self.config['square'],
                         outline=self.config['outline'],
                         padding=self.config['padding'],
                         z_order=z_order)

        # 5. Initialize the frame layout using the configure() method
        self.configure()

    def configure(self):
        """
        Re-entrant method to generate all visual components based on the 
        current frame canvas geometry (self.abs_wh).
        """
        # 1. CRITICAL: Clear all previous components to prevent drawing overlap
        # VUMeter is a container, so we must clear its contents.
        # self.frames = [] 
        self.shape  = self.abs_wh
        
        # Pull required configs locally for cleaner code
        cfg = self.config
        style = self.style
        
        # --- Background Setup (Image or Vector) ---
        if style.texture_path is not None:
            self.path     = get_asset_path('VU Images', style.texture_path)
            self.bgdimage = Image(self, align=('centre', 'middle'), path=self.path, outline=cfg['outline'], opacity=int(style.texture_opacity*255))
            # Image.__init__ should add the Image to self.frames, so VUMeter is a parent
        
        else:
            # Vector Background Setup
            self.path = None
            radius = self.abs_h * (0.5 - style.pivot)
            self.anglescale(radius, style.endstops, style.pivot)

            # Resolve scale components
            current_marks = style.scale.marks if style.scale and style.scale.marks is not None else {}
            current_arcs = style.scale.arcs if style.scale and style.scale.arcs is not None else {}
            current_annotate = style.scale.annotate if style.scale and style.scale.annotate is not None else {}

            # Add Text objects for scales (marks)
            self.scales = {
                mark: Text(self, text=current_marks[mark]['text'], 
                               colour=current_marks[mark]['colour'],
                               fontmax=self.abs_h * style.scale.font_height,
                               endstops=style.endstops,
                               centre_offset=style.pivot,
                               radius=radius * style.scale.scale_radius,
                               reset=False)
                    for mark in current_marks
            }
            
            # Add dB Annotation
            if current_annotate and current_annotate.get('text'):
                self.dB = Text(self, fontmax=self.abs_h * style.scale.font_height * 2,
                               text=current_annotate.get('text', ''),
                               justify=('centre', current_annotate.get('Valign', 'middle')),
                               colour=current_annotate.get('colour', 'mid'),
                               reset=True)
            else:
                self.dB = None
            
            # Add Ticks (Line)
            self.ticks = Line(self, width=style.scale.tick_width, endstops=style.endstops, 
                              tick_pc=style.scale.tick_radius_pc, centre_offset=style.pivot, 
                              radius=radius * style.scale.tick_length, theme=style.theme)
            
            # Add Arcs (Line objects)
            self.arclines = []
            if current_arcs:
                for rad_pc, arc in current_arcs.items():
                    self.arclines.append(
                        Line(self, width=arc['width'], colour=arc['colour'],
                             endstops=style.endstops, tick_pc=style.scale.tick_radius_pc,
                             centre_offset=style.pivot, radius=radius * rad_pc, theme=style.theme)
                    )
            
            # NOTE: Text and Line objects must add themselves to self.frames in their __init__

        # --- Needle Setup (common to both background types) ---
        radius = self.abs_h * (0.5 - style.pivot)
        self.VU = VU(self.platform, cfg['channel'], decay=style.decay, smooth=style.smooth)
        
        # Needle Line
        self.needle = Line(self, width=style.needle.width, tick_pc=style.needle.radius_pc, 
                           centre_offset=style.pivot, endstops=style.endstops, 
                           radius=radius * style.needle.length, theme=style.theme, 
                           colour=style.needle.colour)
        
        # Peak Line
        self.peak  = Line(self, width=style.needle.width, tick_pc=style.needle.radius_pc, 
                         centre_offset=style.pivot, endstops=style.endstops, 
                         radius=radius * style.needle.length, theme=style.theme, 
                         colour='alert')
        
        # The Line objects should also add themselves to self.frames.    
        # print("VUMeter.configure>", self.__str__())

    def update_screen(self):
        # self.draw_background(True)
        if self.path is None:
            self.drawVUBackground()
        else:
            self.bgdimage.draw()
        self.drawNeedle()
        return True
        

    def drawVUBackground(self):
        # Optimization: Group draw calls to batch geometry and reduce GPU flushes
        # 1. Draw all Lines (Ticks and Arcs) first
        current_marks = self.style.scale.marks if self.style.scale and self.style.scale.marks is not None else {}
        
        for val, mark in current_marks.items():
            self.ticks.drawFrameCentredVector(val, colour=mark['colour'], width=mark['width'])

        for arc in self.arclines:
            arc.drawFrameCentredArc(0)

        # 2. Draw all Text (Scales and dB) second
        if self.scales:
            for val, mark in current_marks.items():
                if val in self.scales:
                    self.scales[val].drawVectoredText(val, colour=mark['colour'])

        if self.dB:
            self.dB.draw()

    def drawNeedle(self):
        # print("VUeter._drawNeedle", self.framestr(), "\n", self.needle.framestr())
        vu, peaks   = self.VU.read()
        
        # 0. Draw Shadow
        if self.style.needle.shadow:
            xy = self.needle.anglexy(vu, self.needle.radius)
            ab = self.needle.anglexy(vu, self.needle.radius*(1-self.needle.tick_pc))
            
            # Offset shadow by 4 pixels
            offset = 5
            shadow_xy = (xy[0] + offset, xy[1] + offset)
            shadow_ab = (ab[0] + offset, ab[1] + offset)
            
            self.platform.renderer.draw_line((0, 0, 0, 100), shadow_ab, shadow_xy, width=self.style.needle.width, softness=1.0)

        # 1. Draw Glow (Behind)
        if self.style.needle.glow_intensity > 0:
            # Draw a tighter, controlled glow
            glow_opacity = int(255 * self.style.needle.glow_intensity)
            self.needle.drawFrameCentredVector(vu, colour=self.style.needle.glow_colour, 
                                               width=self.style.needle.width * 3, 
                                               softness=1.0, additive=True, opacity=glow_opacity)

        # 2. Draw Main Needle
        self.needle.drawFrameCentredVector(vu, softness=0.1)
        
        # 3. Draw Peak Needle
        if self.style.show_peak and peaks > 0: self.peak.drawFrameCentredVector(peaks)

        # 4. Draw Tip Glow (High Level)
        if self.style.needle.tip_glow and vu > 0.8:
            tip_xy = self.needle.anglexy(vu, self.needle.radius)
            col = self.colours.get(self.style.needle.glow_colour)
            # Draw a small glowing dot at the tip
            self.platform.renderer.draw_rect(col, (tip_xy[0]-6, tip_xy[1]-6, 12, 12), border_radius=6, softness=1.0, additive=True)


"""
Digital VU Bar Frames
"""

class VUFrame(Frame):
    """
        Displays a vertical or horizontal bar with changing colours at the top
        - limits is an array of points where colour changes occur: [level (%), colour] eg [[0, 'grey'], [0.8,'red'], [0.9],'purple']
        - sits within a screen to compile two together
        - uses full screen height

        Creates a bar, centred in a Frame as a % of the Frame width
    """
    def __init__(self, parent, channel, scalers=None, align=None, theme=None, background=None, \
                 barsize_pc=0.7, flip=False, outline=None,square=False, \
                 peak_h=1, barw_min=10, barw_max=400, tip=False, decay=VU.DECAY, orient='vert', \
                 style=None):

        profile = ProfileManager.get_profile()

        if style is None:
            style = profile.get_style('bar')
            if style is None:
                style = BarStyle(peak_h=peak_h, flip=flip, orient=orient)

        # 1. Capture all configuration parameters into self.config
        self.config = {
            'channel': channel, 'barsize_pc':barsize_pc, 'flip':flip, \
            'peak_h':peak_h, 'barw_min':barw_min, 'barw_max':barw_max, \
            'tip':tip, 'decay':decay, 'orient':orient, \
            'style': style
        }

        Frame.__init__(self, parent, scalers=scalers, align=align,theme=theme,background=background, outline=outline,square=square)
        self.configure()

    def configure(self):
        self.barw   = self.abs_w * self.config['barsize_pc'] if self.config['orient'] == 'vert' else self.abs_h * self.config['barsize_pc']   # width of the bar
        box         = (self.barw, self.h) if self.config['orient'] == 'vert' else (self.w, self.barw)
        self.bar    = Bar(self, align=('centre', 'middle'), box_size=box, \
                        style=self.config['style'])
        # self += self.bar
        self.VU     = VU(self.platform, self.config['channel'], self.config['decay'])
        # print("VUFrame._configure> box=%s, flip=%d, orient %s, frame> %s" % (box, self.config['flip'], self.config['orient'], self.geostr()))

    def update_screen(self):
        # barw   = self.w * self.config['barsize_pc'] if self.config['orient'] == 'vert' else self.h * self.config['barsize_pc']  
        # if barw != self.barw:
        #     self.bar.resize( (self.barw, self.h) if self.config['orient'] == 'vert' else (self.w, self.barw))
        #     self.barw = barw

        height, peaks = self.VU.read()
        # self.draw_background(True)
        self.bar.draw( 0, height, self.barw, peaks)
        # print("VUFrame.update>")
        return True
    


""" Complex VU Meters""" 

class VUMeterImageFrame(Frame):
    """ Image background based class - the """
    def __init__(self, parent, type=None, scalers=None, align=('centre', 'middle'),outline=None,square=False):

        Frame.__init__(self, parent, scalers=scalers, align=align, outline =outline,square=square)

        NEEDLE      = VUNeedleStyle(colour='dark', width=4, length=0.7, radius_pc = 0.7)
                                    # { 'width':3, 'colour': 'dark', 'length': 0.7, 'radius_pc': 0.7 }
        NEEDLE2     = VUNeedleStyle(colour='mid', width=3, length=0.8, radius_pc = 0.55)
                            # { 'width':3, 'colour': 'mid', 'length': 0.8, 'radius_pc': 0.55 }
        NEEDLE3     = VUNeedleStyle(colour='foreground', width=3, length=0.7, radius_pc = 0.5)
                        # { 'width':3, 'colour': 'foreground', 'length': 0.7, 'radius_pc': 0.5 }
        NEEDLE4     = VUNeedleStyle(colour='alert', width=4, length=0.85, radius_pc = 0.75)
                        # { 'width':4, 'colour': 'alert', 'length': 0.85, 'radius_pc': 0.75 }

        ENDSTOPS    = (3*PI/4, 5*PI/4)
        METERS      = { 'blueVU' : VUMeterStyle(texture_path='blue-bgr.png', needle=NEEDLE, endstops=ENDSTOPS, pivot=-0.49, theme='blue'),
                        'goldVU' : VUMeterStyle(texture_path='gold-bgr.png', needle=NEEDLE2, endstops=ENDSTOPS, pivot=-0.35, theme='white'),
                        'blackVU': VUMeterStyle(texture_path='black-white-bgr.png', needle=NEEDLE3, endstops=ENDSTOPS, pivot=-0.65, theme='meter1'),
                        'rainVU' : VUMeterStyle(texture_path='rainbow-bgr.png', needle=NEEDLE4, endstops=ENDSTOPS, pivot=-0.75, theme='meter1'),
                        'redVU'  : VUMeterStyle(texture_path='red-bgr.jpeg', needle=VUNeedleStyle(width=3, colour='dark', length=0.8, radius_pc=0.65), endstops=ENDSTOPS, pivot=-0.76, theme='meter1'),
                        'vintVU' : VUMeterStyle(texture_path='vintage-bgr.jpeg', needle=VUNeedleStyle(width=3, colour='alert', length=0.7, radius_pc=0.8), endstops=ENDSTOPS, pivot=-0.6, theme='meter1'),
                        'whiteVU': VUMeterStyle(texture_path='white-red-bgr.png', needle=VUNeedleStyle(width=2, colour='foreground', length=0.75, radius_pc=0.65), endstops=ENDSTOPS, pivot=-0.75, theme='meter1'),
                        'OldVU': VUMeterStyle(texture_path='vintage-VU.png', needle=VUNeedleStyle(width=3, colour='foreground', length=0.75, radius_pc=0.65), endstops=ENDSTOPS, pivot =-0.75, theme='meter2'),
                        'ModVU': VUMeterStyle(texture_path='modern-VU.png', needle=VUNeedleStyle(width=2, colour='foreground', length=0.75, radius_pc=0.65), endstops=ENDSTOPS, pivot=-0.75, theme='meter1'),
                        'greenVU': VUMeterStyle(texture_path='emerald-bgr.jpeg', needle=VUNeedleStyle(width=2, colour='foreground', length=0.63, radius_pc=0.60), endstops=ENDSTOPS, pivot=-0.6, theme='meter1') }

        # if the meter type does not exist then there will be a run time error
        # meter colour themes assume meter1
        style = METERS[type]
        outline = OutlineStyle(width=4, radius=10, colour='light', glow_intensity=0.1, softness=0.2)
        cols = ColFramer(self, padding=30, padpc=0.05)
        cols += VUMeter(cols, 'left', style=style, outline=outline)
        cols += VUMeter(cols, 'right', style=style, outline=outline)    


class VU2chFrame(Frame):
    def __init__(self, parent, scalers=None, align=None, orient='vert', flip=False, led_h=5, led_gap=1,barsize_pc=0.7, theme=None, outline=None,background={'colour':'background', 'per_frame_update':True}, **kwargs):
        
        # Separate Frame args from VUFrame args to prevent TypeError in Frame.__init__
        frame_keys = ['square', 'padding', 'z_order']
        frame_kwargs = {k: kwargs.pop(k) for k in frame_keys if k in kwargs}

        Frame.__init__(self, parent, scalers=scalers, align=align, theme=theme,outline=outline,background=background,**frame_kwargs)
        # def VUVFrame(self, platform, bounds, channel, scalers=None, align=('left','bottom'), barsize_pc=0.7, theme='std', flip=False, \
        #                 led_h=5, led_gap=1, peak_h=1, col_mode='h', radius=0, barw_min=10, barw_max=200, tip=False, decay=DECAY):
        self.orient     = orient
        self.flip       = flip 
        self.led_h      = led_h
        self.led_gap    = led_gap
        self.barsize_pc = barsize_pc
        self.background = background

        if self.orient=='horz':
            self += VUFrame(self, 'left',  align=('centre','top'), scalers=(1.0, 0.5), style=BarStyle(orient=self.orient, flip=self.flip), background=self.background, **kwargs)
            self += VUFrame(self, 'right', align=('left','bottom'), scalers=(1.0, 0.5), style=BarStyle(orient=self.orient, flip=self.flip), background=self.background, **kwargs)
        else:     # Vertical
            self += VUFrame(self, 'left', align=('left','middle'), scalers=(0.5, 1.0), style=BarStyle(orient='vert', flip=self.flip, led_h=self.led_h, led_gap=self.led_gap),barsize_pc=self.barsize_pc, background=None, **kwargs)
            self += VUFrame(self, 'right', align=('right','bottom'), scalers=(0.5, 1.0), style=BarStyle(orient='vert', flip=self.flip, led_h=self.led_h, led_gap=self.led_gap),barsize_pc=self.barsize_pc, background=None, **kwargs)
        # self.always_draw_background()

class VUFlipFrame(Frame):
    def __init__(self, parent, scalers=None, align=None, orient='vert', flip=False,theme=None, outline=None,background={'colour':'background', 'per_frame_update':True},led_h=2, **kwargs):
        Frame.__init__(self, parent, scalers=scalers, align=align, outline=outline,background=background, theme=theme)
        self.orient = orient

        # def VUVFrame(self, platform, bounds, channel, scalers=None, align=('left','bottom'), barsize_pc=0.7, theme='std', flip=False, \
        #                 led_h=5, led_h=1, peak_h=1, col_mode='h', radius=0, barw_min=10, barw_max=200, tip=False, decay=DECAY):
        flip = (False, True) if flip else (True,False)
        if self.orient=='horz':
            cols = ColFramer(self)
            cols += VUFrame(cols, 'left', style=BarStyle(orient=self.orient, flip=flip[0], tip=False, led_h=led_h), **kwargs)
            cols += VUFrame(cols, 'right', style=BarStyle(orient=self.orient, flip=flip[1], tip=False, led_h=led_h), **kwargs)

        else:     # Vertical
            rows = RowFramer(self)
            rows += VUFrame(rows, 'left', style=BarStyle(orient='vert', flip=flip[0], led_h=led_h), theme=self.theme, **kwargs )
            rows += VUFrame(rows, 'right',style=BarStyle(orient='vert', flip=flip[1], led_h=led_h), theme=self.theme, **kwargs)
        # self.always_draw_background()


class VUHorzFrame(Frame):
    def __init__(self, parent, channel, tip=False, **kwargs):
        # Split kwargs into Frame args and VUFrame args
        frame_keys = ['scalers', 'align', 'square', 'theme', 'background', 'outline', 'padding']
        frame_kwargs = {k: kwargs[k] for k in frame_keys if k in kwargs}
        vu_kwargs = {k: v for k, v in kwargs.items() if k not in frame_keys}

        Frame.__init__(self, parent, **frame_kwargs)
        cols = ColFramer(self, col_ratios=(1,3))
        # cols = self
        channel_text = ' L' if channel=='left' else ' R'
        cols += TextFrame(cols, text=channel_text)
        
        # Default gap to 0 for horizontal bars if not specified, but allow override
        if 'led_gap' not in vu_kwargs and 'segment_gap' not in vu_kwargs:
            vu_kwargs['segment_gap'] = 0
            
        cols += VUFrame(cols, channel=channel, barsize_pc=0.8, style=BarStyle(orient='horz', tip=tip), **vu_kwargs)



class VU2chHorzFrame(Frame):
    def __init__(self, parent, tip=False, **kwargs):
        # Split kwargs into Frame args and VUFrame args
        frame_keys = ['scalers', 'align', 'square', 'theme', 'background', 'outline', 'padding']
        frame_kwargs = {k: kwargs[k] for k in frame_keys if k in kwargs}
        vu_kwargs = {k: v for k, v in kwargs.items() if k not in frame_keys}

        Frame.__init__(self, parent, **frame_kwargs)
        # def VUVFrame(self, platform, bounds, channel, scalers=None, align=('left','bottom'), barsize_pc=0.7, theme='std', flip=False, \
        #                 led_h=5, led_gap=1, peak_h=1, col_mode='h', radius=0, barw_min=10, barw_max=200, tip=False, decay=DECAY):
        # self += VUHorzFrame(self, 'left',  scalers=(0.5,1.0), V='middle' , align=('left','middle'), flip=True )
        # back = {'colour':'background', 'per_frame_update':True}
        rows = RowFramer(self)
        rows += VUHorzFrame(rows, 'left' ,tip=tip, **vu_kwargs)
        rows += VUHorzFrame(rows, 'right',tip=tip, **vu_kwargs)
        # self += VUHorzFrame(self, 'right', scalers=(0.5,1.0), V='middle' , align=('left','middle') )
        # self.always_draw_background()


        # rows.always_draw_background()        