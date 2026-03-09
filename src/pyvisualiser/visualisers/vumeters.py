'''
Analogue VU meters have image based background and scale based background.  The rendering and light effects are  cruicial to get 
a good simulation of Analogue VU meters

Mar 2026 Baloothebear4. v1.0
- refectored from frames.py and subframes.py

'''

from    pyvisualiser.core.framecore  import Frame, get_asset_path, Smoother, RowFramer, ColFramer
from    pyvisualiser.core.components import Text, Line, Image, VUNeedleStyle, VUMeterStyle, VUMeterScale
from    pyvisualiser.styles.presets  import Centred, PI
from    pyvisualiser.styles.styles   import OutlineStyle, Effects


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
 
    def __init__(self, parent, channel, scalers=None, align=Centred, outline=None, square=False, background=None,
                 style: VUMeterStyle = None, z_order=0, **kwargs):
        
        # 1. Capture all non-style configuration parameters into self.config
        self.config = {
            'channel': channel,
            'scalers': scalers,
            'align': align,
            'outline':outline,
            'outline': outline,
            'background': background,
            'square': square,
            'z_order': z_order
        }

        # 2. Resolve Style (VUMeterStyle)
        # if style is None:
        #     # Fallback to legacy arguments or class defaults
        #     _endstops = endstops if endstops is not None else self.ENDSTOPS
        #     _pivot = pivot if pivot is not None else self.PIVOT
        #     _needle = needle if needle is not None else self.NEEDLE
        #     _theme = theme # VUMeterStyle handles None by defaulting to 'meter1'
        #     _marks = marks if marks is not None else self.MARKS
        #     _arcs = arcs if arcs is not None else self.ARCS
        #     _annotate = annotate if annotate is not None else self.ANNOTATE
        if style is None:
            # If no style object is passed, build one from kwargs for backward compatibility.
            peakmeter = kwargs.get('peakmeter', False)
            endstops = kwargs.get('endstops', (3 * PI / 4, 5 * PI / 4))
            pivot = kwargs.get('pivot', -0.5)
            bgdimage = kwargs.get('bgdimage')
            needle = kwargs.get('needle')
            theme = kwargs.get('theme', 'meter1')
            decay = kwargs.get('decay', 0.3)
            smooth = kwargs.get('smooth', 15)

            # Scale-related legacy arguments
            marks = kwargs.get('marks')
            arcs = kwargs.get('arcs')
            annotate = kwargs.get('annotate')
            tick_w = kwargs.get('tick_w', 3)
            ticklen = kwargs.get('ticklen', 0.8)
            tick_pc = kwargs.get('tick_pc', 0.1)
            scaleslen = kwargs.get('scaleslen', 0.9)
            fonth = kwargs.get('fonth', 0.05)

            # Ensure needle is a Style object
            if isinstance(needle, dict):
                _needle = VUNeedleStyle(**needle)
            elif isinstance(needle, VUNeedleStyle):
                _needle = needle
            else:
                _needle = VUNeedleStyle()

            _scale = VUMeterScale(marks=marks, arcs=arcs, annotate=annotate,
                                  tick_width=tick_w, tick_length=ticklen, tick_radius_pc=tick_pc,
                                  scale_radius=scaleslen, font_height=fonth)

            style = VUMeterStyle(endstops=endstops, pivot=pivot, needle=_needle, scale=_scale,
                                 texture_path=bgdimage, theme=theme, show_peak=peakmeter,
                                 decay=decay, smooth=smooth)

        elif isinstance(style, dict):
            # Allow passing style as a dictionary
            style = VUMeterStyle(**style)

        # Ensure scale is present if style was passed but scale was missing
        if style.scale is None:
            style.scale = VUMeterScale()
            
        self.style = style

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
                         z_order=z_order,
                         **kwargs)

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

    def update_screen(self, full):
        self.draw_background(True)
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
                 # New API
                 style=None, \
                 segment_size=5, segment_gap=1, corner_radius=0, edge_softness=0.05, \
                 effects=None, \
                 intensity_threshold=0.8, intensity_scale=2.0, intensity_blur=0.7, intensity_alpha=20, \
                 # Legacy args (for compatibility)
                 led_h=None, led_gap=None, radius=None, softness=None, \
                 bloom_threshold=None, bloom_intensity=None, bloom_softness=None, bloom_alpha=None, **kwargs):

        # Map legacy arguments to new API if present
        if led_h is not None: segment_size = led_h
        if led_gap is not None: segment_gap = led_gap
        if radius is not None: corner_radius = radius
        if softness is not None: edge_softness = softness
        if bloom_threshold is not None: intensity_threshold = bloom_threshold
        if bloom_intensity is not None: intensity_scale = bloom_intensity
        if bloom_softness is not None: intensity_blur = bloom_softness
        if bloom_alpha is not None: intensity_alpha = bloom_alpha

        if effects is None:
            effects = Effects(threshold=intensity_threshold, scale=intensity_scale, blur=intensity_blur, alpha=intensity_alpha)

        if style is None:
            style = BarStyle(led_h=led_h, led_gap=led_gap, peak_h=peak_h, flip=flip, orient=orient, 
                             segment_size=segment_size, segment_gap=segment_gap, corner_radius=corner_radius, edge_softness=edge_softness)

        # 1. Capture all configuration parameters into self.config
        self.config = {
            'channel': channel, 'barsize_pc':barsize_pc, 'flip':flip, \
            'peak_h':peak_h, 'barw_min':barw_min, 'barw_max':barw_max, \
            'tip':tip, 'decay':decay, 'orient':orient, \
            'style': style, \
            'effects': effects
        }
        # Add any remaining keyword arguments
        self.config.update(kwargs)

        Frame.__init__(self, parent, scalers=scalers, align=align,theme=theme,background=background, outline=outline,square=square)
        self.configure()

    def configure(self):
        self.barw   = self.abs_w * self.config['barsize_pc'] if self.config['orient'] == 'vert' else self.abs_h * self.config['barsize_pc']   # width of the bar
        box         = (self.barw, self.h) if self.config['orient'] == 'vert' else (self.w, self.barw)
        self.bar    = Bar(self, align=('centre', 'middle'), box_size=box, \
                        style=self.config['style'], \
                        effects=self.config['effects'])
        # self += self.bar
        self.VU     = VU(self.platform, self.config['channel'], self.config['decay'])
        # print("VUFrame._configure> box=%s, flip=%d, orient %s, frame> %s" % (box, self.config['flip'], self.config['orient'], self.geostr()))

    def update_screen(self, full):
        # barw   = self.w * self.config['barsize_pc'] if self.config['orient'] == 'vert' else self.h * self.config['barsize_pc']  
        # if barw != self.barw:
        #     self.bar.resize( (self.barw, self.h) if self.config['orient'] == 'vert' else (self.w, self.barw))
        #     self.barw = barw

        height, peaks = self.VU.read()
        self.draw_background(True)
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