#!/usr/bin/env python
"""
 Display classes:
    - base screens
    - screen frames
    - sub-frames

 Part of mVista preDAC

 v1.0 Baloothebear4 Sept 17 - Original
 v2.0 Baloothebear4  May 20 - Re-factored to use Frame class, simplifying & cleaning up
 v3.0 Baloothebear4 Dec 23 - Refactored for MacOS & DSI Display usage

"""

# from    displaydriver import make_font, scaleImage, scalefont
from    framecore import Frame
from    displaydriver import Bar, Text, Line, Box, Image, ArcsOctaves, Dots

PI = 3.14152

class Smoother:
    """
    Collects 5 points then performs a triangle smoothing
    """
    def __init__(self, maximum, ave_size=5):
        self.size = ave_size
        self.FrameHeight = maximum
        self.smoother = [0.0]* self.size

    def add(self, data):
        self.smoother.insert(0, data)
        del self.smoother[-1]

    def smoothed(self):
        if self.size==5: #Triange smoother
            return min(self.FrameHeight, (sum(self.smoother)+2*self.smoother[2]+self.smoother[1] +self.smoother[3])/8)
        else:           #Rectangle smoother, can reduce size to 3 as well
            ave = 0
            tot = 0
            for i, v in enumerate(self.smoother):
                inc  = len(self.smoother) - i
                tot += inc
                ave += v * inc
            return ave / (tot*0.9)  # this increased teh amplitude as the smoothing damps the range for VUs

class TextFrame(Frame):
    """
        Display a simple centred set of text
        - text is the largest imaginable width of text
        - V is the vertical alignment
        - Y is the y scaler
    """
    def __init__(self, parent, scalers=None, align=None, text='Default Text', reset=True, theme=None, wrap=False, \
                 colour='foreground', justify='centre', background=None, outline=None, padding=0, update_fn=None):
        Frame.__init__(self, parent, scalers=scalers, align=align, theme=theme, background=background, outline=outline,padding=padding)
        self.colour         = colour
        self.wrap           = wrap
        self.reset          = reset
        self.text           = text
        self.justify        = justify
        self.update_fn      = update_fn
        self.configure()

    def configure(self):
        print("TextFrame.configure>", self.text, self.background_frame.background, self.geostr())
        self.textcomp      = Text(self, text=self.text, fontmax=self.h, reset=self.reset, colour=self.colour, wrap=self.wrap, justify=self.justify)
        # self.textcomp      = Text(self, text=self.text, fontmax=self.h, reset=self.reset, colour_index=self.colour_index, wrap=self.wrap)

    def update_screen(self, full, text=None, colour=None, fontmax=None):

        if self.update_fn is not None: text = self.update_fn()

        # print("TextFrame.update ", text, self.geostr())
        if full or self.textcomp.new_content_available(text) or self.background_frame.is_per_frame_update():
            # print("TextFrame.draw ", full, text, colour, full, self.geostr())
            self.draw_background(True) # clear whats there -- not needed for
            self.textcomp.draw(text=text, colour=colour, fontmax=fontmax)
            return self.abs_rect()
        else:
            # print("TextFrame.draw > NO DRAW", text, colour, self.geostr())
            return False # no need to redraw
        
    @property
    def width(self):
        return self.w
    
    @property
    def fontsize(self):
        return self.text.fontsize


"""
MetaData Frames
"""

class PlayProgressFrame(Frame):
    """ This creates a propgress bar that moves according to play progress with time elapsd and time to go calc """
    def __init__(self, parent, scalers=None, align=None, barsize_pc=0.5, theme=None, flip=False, \
                    led_h=1, led_gap=0, radius=0, barw_min=10, barw_max=400, tip=True, orient='horz'):

        self.barsize_pc     = barsize_pc      # min widths
        self.barw_max       = barw_max      # max width
        self.orient         = orient   # Horz or vert bars
        self.theme          = theme
        Frame.__init__(self, parent, scalers=scalers, align=align, theme=theme)
        self.configure()


    def configure(self):
        self.barw           = self.w * self.barsize_pc if self.orient == 'vert' else self.h * self.barsize_pc   # width of the bar

        text = " 22:22 "
        self.elapsed     = Text(self, fontmax=self.barw, text=text, reset=True, justify=('left', 'middle'), colour='mid')
        self.remaining   = Text(self, fontmax=self.barw, text=text, reset=True, justify=('right', 'middle'), colour='mid')
        self.text_width  = self.elapsed.fontwh[0] + self.remaining.fontwh[0]

        box = (self.barw, self.h) if self.orient == 'vert' else (self.w-self.text_width, self.barw)
        self.boxbar      = Box(self, align=('centre', 'middle'), theme=self.theme, box=box, radius=10)

    def update_screen(self, full):
        # check is parent has resized
        box = (self.barw, self.h) if self.orient == 'vert' else (self.w-self.text_width, self.barw)
        if self.boxbar.wh != box:
            self.boxbar.resize(box)

        elapsed   = f"  {int( self.platform.elapsed//60)}:{int( self.platform.elapsed %60):02d}"
        remaining = f"{int( self.platform.remaining//60)}:{int(  self.platform.remaining%60):02d}  "

        if full or self.elapsed.new_content_available(elapsed) or self.background_frame.is_per_frame_update():
            self.draw_background(True)
            hide_backline = -self.h/2 if self.platform.elapsedpc*self.w > self.h/2 else 0 # offset by the radius, makes sure the very start is OK too
            self.boxbar.drawH(self.platform.elapsedpc, flip=True, colour_index='dark', offset=(hide_backline,0))
            self.boxbar.drawH(self.platform.elapsedpc, colour_index='light')
            # Create the string representation

            self.elapsed.draw(elapsed, colour='light')
            self.remaining.draw(remaining, colour='light')
            # print("PlayProgressFrame>", elapsed, remaining)
            return True
        else:
            return False
            # no need to redraw

class ArtFrame(Frame):
    # OUTLINE = { 'width' : 3, 'radius' : 0, 'colour_index' : 'foreground'}
    # def __init__(self, parent, update_fn=None, square=False, scalers=None, align=None, opacity=None, outline=None, padding=0, background=None):
    def __init__(self, parent, update_fn=None, opacity=None, **kwargs):

        # Frame.__init__(self, parent, scalers=scalers, align=align, outline=outline, padding=padding, background=background, square=square)
        self.kwargs    = kwargs
        self.parent    = parent
        self.update_fn = update_fn
        self.opacity   = opacity 
        Frame.__init__(self, parent, **kwargs)
        # print("ArtFrame", square, opacity)
        self.configure()

    def configure(self):    
        self.frames = []
        self.image_container = Image(self, opacity=self.opacity)  

    def update_screen(self, full):
        # Check if parent Frame has changed size
        # if self.wh != self.image_container.target_wh:
        #     self.configure()
        #     print("ArtFrame.update> re-create Image size", self.image_container.target_wh, self.wh)

        if full or self.image_container.new_content_available(self.update_fn()):
            self.draw_background(True)
            self.image_container.draw(self.update_fn())
            return True
        else:
            return False

class MetaImages(ArtFrame):
    def __init__(self, parent, art_type='album', opacity=None, **kwargs): #colour='foreground', scalers=(1.0, 1.0), align=('centre','middle'),theme=None, same_size=True, outline=None,justify='centre'):

        METAART_UPDATE = {  'album':  { 'update_fn': parent.platform.album_art,  'square' : False},
                            'artist': { 'update_fn': parent.platform.artist_art, 'square' : False} }

        if  art_type  in METAART_UPDATE: 

            update_fn = METAART_UPDATE[art_type]['update_fn']
            ArtFrame.__init__(self, parent, update_fn= update_fn, opacity=opacity, square=METAART_UPDATE[art_type]['square'],  **kwargs) 

            # print("MetaImages.__init__>", art_type, self.wh, self.framestr() )
        else:
            raise ValueError("MetaImages.__init__> Meta art type not known", self.art_type )   
    

class MetaData(TextFrame):
    def __init__(self, parent, metadata_type='artist', **kwargs): #colour='foreground', scalers=(1.0, 1.0), align=('centre','middle'),theme=None, same_size=True, outline=None,justify='centre'):

        METADATA_UPDATE = { 'track': parent.platform.track,
                            'album' :parent.platform.album,
                            'artist': parent.platform.artist}

        if  metadata_type  in METADATA_UPDATE: 

            update_fn = METADATA_UPDATE[metadata_type]
            TextFrame.__init__(self, parent, update_fn= update_fn, **kwargs) 

            # print("MetaDataFrame.configure>", self.metadata_type, self.wh, self.framestr() )
        else:
            raise ValueError("MetaDataFrame.update> Metadata type not known", self.metadata_type )   
    

"""
VU Meter frames
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
    FONTH     = 0.05        # as a percentage of the overall frame height
    PIVOT     = -0.5        # % of the frame height the pivot is below
    NEEDLELEN = 0.8         # length of the needle as pc of height
    TICKLEN   = 0.8         # length marks
    SCALESLEN = 0.9
    ARCLEN    = TICKLEN
    TICK_PC   = 0.1         # lenth of the ticks as PC of the needle
    TICK_W    = 3           # width of the ticks in pixels
    DECAY     = 0.3         # decay factor
    SMOOTH    = 15          # samples to smooth

    # MARKS     = {'-40':0.1, '-20':0.3, '-10':0.4, '-3':0.6, '0':0.7, '+3':0.8, '+6':0.9}
    # Key is the value (0-1) where the mark is drawn, with colour, width & text
    MARKS     = {0.1: {'text':'-40', 'width': TICK_W, 'colour': 'light'},
                 0.3: {'text':'-20', 'width': TICK_W, 'colour': 'light'},
                #  0.4: {'text':'-10', 'width': TICK_W, 'colour': 'light'},
                 0.5: {'text':'-5', 'width': TICK_W, 'colour': 'light'},
                 0.6: {'text':'-3', 'width': TICK_W, 'colour': 'light'},
                 0.7: {'text':'+0', 'width': TICK_W, 'colour': 'alert'},
                 0.8: {'text':'+3', 'width': TICK_W*2, 'colour': 'alert'},
                 0.9: {'text':'+6', 'width': TICK_W*3, 'colour': 'alert'} }
    # Key is the radius, attributes width & colour
    ARCS      = {ARCLEN    : {'width': TICK_W//2, 'colour': 'mid'},
                 ARCLEN*0.9: {'width': TICK_W//2, 'colour': 'mid'} }
    # Key is the Valign=None, attributes Words, Colour
    ANNOTATE  = { 'Valign':'middle', 'text':'dB', 'colour':'mid' }
    ENDSTOPS  = (3*PI/4, 5*PI/4)  #Position of endstop if not the edge of the frame
    NEEDLE    = { 'width':4, 'colour': 'foreground', 'length': NEEDLELEN, 'radius_pc': 1.0 }
    VUIMAGEPATH = 'VU Images'
 
    def __init__(self, parent, channel, scalers=None, align=('centre','middle'), peakmeter=False, outline=None, square=False,\
                endstops=ENDSTOPS, tick_w=TICK_W, tick_pc=TICK_PC, fonth=FONTH, pivot=PIVOT, decay=DECAY, smooth=SMOOTH, bgdimage=None, \
                needle=NEEDLE, ticklen=TICKLEN, scaleslen=SCALESLEN, theme=None, marks=MARKS, annotate=ANNOTATE, arcs=ARCS, \
                background=None, **kwargs):
        
        # 1. Capture all configuration parameters into self.config
        self.config = {
            'channel': channel,
            'scalers': scalers,
            'align': align,
            'peakmeter': peakmeter,
            'outline': outline,
            'endstops': endstops,
            'tick_w': tick_w,
            'tick_pc': tick_pc,
            'fonth': fonth,
            'pivot': pivot,
            'decay': decay,
            'smooth': smooth,
            'bgdimage': bgdimage,
            'needle': needle,
            'ticklen': ticklen,
            'scaleslen': scaleslen,
            'theme': theme,
            'marks': marks,
            'annotate': annotate,
            'arcs': arcs,
            'background': background,
            'square': square
        }
        # Add any remaining keyword arguments
        self.config.update(kwargs)

        # 2. Determine the channel/alignment for the parent Frame.__init__
        align_channel = channel if channel in ('left', 'right') else align[0]
        
        # 3. Call the parent's __init__ using the stored values
        super().__init__(parent, 
                         scalers=self.config['scalers'], 
                         align=(align_channel, self.config['align'][1]),
                         theme=self.config['theme'], 
                         background=self.config['background'],
                         square=self.config['square'],
                         outline=self.config['outline'])

        # 4. Initialize the frame layout using the configure() method
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
        
        # --- Background Setup (Image or Vector) ---
        if cfg['bgdimage'] is not None:
            self.path     = VUMeter.VUIMAGEPATH + '/' + cfg['bgdimage']
            self.bgdimage = Image(self, align=('centre', 'middle'), path=self.path, outline=cfg['outline'])
            # Image.__init__ should add the Image to self.frames, so VUMeter is a parent
        
        else:
            # Vector Background Setup
            self.path = None
            radius = self.abs_h * (0.5 - cfg['pivot'])
            self.anglescale(radius, cfg['endstops'], cfg['pivot'])


            # Add Text objects for scales (marks)
            self.scales = {
                mark: Text(self, text=cfg['marks'][mark]['text'], 
                           colour=cfg['marks'][mark]['colour'], 
                           fontmax=self.abs_h * cfg['fonth'], 
                           endstops=cfg['endstops'], 
                           centre_offset=cfg['pivot'], 
                           radius=radius * cfg['scaleslen'], 
                           reset=False)
                for mark in cfg['marks']
            }
            
            # Add dB Annotation
            self.dB = Text(self, fontmax=self.abs_h * cfg['fonth'] * 2, 
                           text=cfg['annotate']['text'], 
                           justify=('centre', cfg['annotate']['Valign']), 
                           colour=cfg['annotate']['colour'], 
                           reset=True)
            
            # Add Ticks (Line)
            self.ticks = Line(self, width=cfg['tick_w'], endstops=cfg['endstops'], 
                              tick_pc=cfg['tick_pc'], centre_offset=cfg['pivot'], 
                              radius=radius * cfg['ticklen'], theme=cfg['theme'])
            
            # Add Arcs (Line objects)
            self.arclines = []
            for rad_pc, arc in cfg['arcs'].items():
                self.arclines.append(
                    Line(self, width=arc['width'], colour=arc['colour'], 
                         endstops=cfg['endstops'], tick_pc=cfg['tick_pc'], 
                         centre_offset=cfg['pivot'], radius=radius * rad_pc, theme=cfg['theme'])
                )
            
            # NOTE: Text and Line objects must add themselves to self.frames in their __init__

        # --- Needle Setup (common to both background types) ---
        radius = self.abs_h * (0.5 - cfg['pivot'])
        self.VU = VU(self.platform, cfg['channel'], decay=cfg['decay'], smooth=cfg['smooth'])
        
        # Needle Line
        self.needle = Line(self, width=cfg['needle']['width'], tick_pc=cfg['needle']['radius_pc'], 
                           centre_offset=cfg['pivot'], endstops=cfg['endstops'], 
                           radius=radius * cfg['needle']['length'], theme=cfg['theme'], 
                           colour=cfg['needle']['colour'])
        
        # Peak Line
        self.peak  = Line(self, width=cfg['needle']['width'], tick_pc=cfg['needle']['radius_pc'], 
                         centre_offset=cfg['pivot'], endstops=cfg['endstops'], 
                         radius=radius * cfg['needle']['length'], theme=cfg['theme'], 
                         colour='alert')
        
        self.peakmeter = cfg['peakmeter']
        # The Line objects should also add themselves to self.frames.    

    def update_screen(self, full):
        self.draw_background(True)
        if self.path is None:
            self.drawVUBackground()
        else:
            self.bgdimage.draw()
        self.drawNeedle()
        return True
        

    def drawVUBackground(self):
        for val, mark in self.config['marks'].items():
            self.scales[val].drawVectoredText(val, colour=mark['colour'])
            self.ticks.drawFrameCentredVector(val, colour=mark['colour'], width=mark['width'])

        for arc in self.arclines:
            arc.drawFrameCentredArc(0)

        self.dB.draw()

    def drawNeedle(self):
        # print("VUeter._drawNeedle", self.framestr(), "\n", self.needle.framestr())
        vu, peaks   = self.VU.read()
        self.needle.drawFrameCentredVector(vu)
        if self.peakmeter and peaks > 0: self.peak.drawFrameCentredVector(peaks)



"""
VU Bar Frames
"""
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
                 led_h=5, led_gap=1, peak_h=1, radius=0, barw_min=10, barw_max=400, tip=False, decay=VU.DECAY, orient='vert',**kwargs):

        # 1. Capture all configuration parameters into self.config
        self.config = {
            'channel': channel, 'barsize_pc':barsize_pc, 'flip':flip, \
            'led_h':led_h, 'led_gap':led_gap, 'peak_h':peak_h, 'radius':radius, 'barw_min':barw_min, 'barw_max':barw_max, \
            'tip':tip, 'decay':decay, 'orient':orient }
        # Add any remaining keyword arguments
        self.config.update(kwargs)

        Frame.__init__(self, parent, scalers=scalers, align=align,theme=theme,background=background, outline=outline,square=square)
        self.configure()

    def configure(self):
        self.barw   = self.abs_w * self.config['barsize_pc'] if self.config['orient'] == 'vert' else self.abs_h * self.config['barsize_pc']   # width of the bar
        box         = (self.barw, self.h) if self.config['orient'] == 'vert' else (self.w, self.barw)
        self.bar    = Bar(self, align=('centre', 'middle'), box_size=box, led_h=self.config['led_h'], \
                        led_gap=self.config['led_gap'], peak_h=self.config['peak_h'], flip=self.config['flip'], \
                        radius=self.config['radius'], tip=self.config['tip'], orient=self.config['orient'])
        # self += self.bar
        self.VU     = VU(self.platform, self.config['channel'], self.config['decay'])
        print("VUFrame._configure> box=%s, flip=%d, orient %s, frame> %s" % (box, self.config['flip'], self.config['orient'], self.geostr()))

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
        


"""
Outline Frame - alternative is to use to the outline function within Frame
"""
# class OutlineFrame(Frame):
#     def __init__(self, parent, scalers=None, align=None, theme=None, width=4):
#         Frame.__init__(self, parent, scalers=scalers, align=align)
#         self.out     = Box(self, self.wh, width=width, theme=theme)
#         self.parent  = parent
#     # def __init__( self, platform, bounds, colour_index=0, theme='std', box=None, width=None, radius=5, align=('centre', 'middle') ):
#     def update_screen(self, full):
#         self.out.draw( colour_index='foreground' )
#         return True
        


"""
Spectrum Analyser Frames
"""
class Spectrum:
    DECAY     = 0.4   # Lower is longer delay - This is the amount that a bar reduces each period
    PEAKDECAY = 0.01  # pc of Decay to use for peak bars


    def __init__(self, width, bar_space=0.5, barw_min=1, barw_max=20, bandwidth=None, decay=DECAY):
        self.bar_space      = bar_space     # pc of barwidth
        self.barw_min       = barw_min      # min widths
        self.barw_max       = barw_max      # max width
        self.decay          = decay
        self.peak_decay     = decay * Spectrum.PEAKDECAY
        # Calculate how many bars can be drawn in the width available
        # Go down the bar widths to see what will fit
        # Determine the max octave fraction that can be accomodated
        # Set up the number function to pack the samples

        for self.spacing in (48, 24, 12, 6, 3, 2, 1):   # 48th is the finest, go down from the finest to the coarsest to find one that fits
            self.bar_freqs = self.platform.createBands(self.spacing, flast=bandwidth)
            self.bars      = len(self.bar_freqs)
            for barw in range(self.barw_max, self.barw_min, -1):
                self.bar_gap    = int(barw * self.bar_space)
                self.max_bars   = int(width/(self.bar_gap+barw))
                if  self.bars <= self.max_bars: break
            if  self.bars <= self.max_bars: break

        self.barw           = barw
        spectrum_width = self.bars * (self.bar_gap+self.barw)
        if spectrum_width < width:
            gaptofill = width-spectrum_width
            # print("gap to fill")
            self.bar_gap = self.bar_gap+ gaptofill/self.bars

        self.peaks          = [0.0] * self.bars  #This is used to hold the values and implement a smoothing factor
        self.current        = [ Smoother(1.0) for i in range(self.bars)]    #array of smoothers

        #count num_octaves, as an Octave is a doubling of frequency
        self.octaves = [0]
        for freq_bin in range(1, len(self.bar_freqs)):
            if self.bar_freqs[freq_bin] >= 2 * self.bar_freqs[self.octaves[-1]]:
                if freq_bin - self.octaves[-1] < 12:
                    continue
                else:
                    self.octaves.append(freq_bin)
                    continue
        print("Spectrum.__init__> Selected spectrum: octave spacing=1/%d, num octaves %d" % (self.spacing, len(self.octaves)))



    def read(self, channel='left'):
        smoothedpeak = 0
        fft = self.platform.packFFT(self.bar_freqs, self.channel)

        for i, target_height in enumerate(fft):
            if target_height > self.current[i].smoothed():
                self.current[i].add(target_height)

            if self.current[i].smoothed() > self.peaks[i]:
                self.peaks[i] = self.current[i].smoothed()

            height = self.current[i].smoothed()
            if height > smoothedpeak: smoothedpeak = height

            if self.current[i].smoothed() < self.decay/100.0:
                self.current[i].add(0.0)
            else:
                self.current[i].add(height* (1- self.decay))

            if self.current[i].smoothed() < self.decay/3.0:  #Look for when its gone quiet to clear the peak bars
                self.peaks[i] = 0.0

            self.peaks[i] *= (1- self.peak_decay)


# class SpectrumFrame(Frame, Spectrum):
#     """
#     Creates a spectrum analyser of the width and octave interval specified
#     intervals are 1, 3 or 6
#     widths    are really half or whole screen
#     - scale is used to determine how wide the frame is as a % of the parent frame
#     - channel 'left' or 'right' selects the audio channel and screen alignment
#     """

    # def __init__(self, parent, channel, scalers=None, align=('left','bottom'), right_offset=0, theme=None, flip=False, \
    #                 led_h=5, led_gap=1, peak_h=1, radius=0, bar_space=0.5, barw_min=1, barw_max=20, tip=False, decay=Spectrum.DECAY, col_mode='vert'):

    #     self.channel        = channel
    #     self.right_offset   = right_offset
    #     self.parent         = parent
    #     self.col_mode       = col_mode

    #     Frame.__init__(self, parent, scalers=scalers, align=align, theme=theme)

    #     Spectrum.__init__(self, self.w, bar_space, barw_min, barw_max, decay=decay)
    #     self.bar = Bar(self, box_size=(self.width, self.h), led_h=led_h, led_gap=led_gap, peak_h=peak_h, flip=flip, radius=radius, tip=tip, col_mode=col_mode)

    #     # print("SpectrumFrame.__init__> Selected spectrum: max bars=%d, octave spacing=1/%d, num bars=%d, width=%d, gap=%d, flip=%d" % (self.max_bars, self.spacing, self.bars, self.barw, self.bar_gap, flip))

class SpectrumFrame(Frame, Spectrum):
    """
    Creates a spectrum analyser of the width and octave interval specified.
    - scale is used to determine how wide the frame is as a % of the parent frame
    - channel 'left' or 'right' selects the audio channel and screen alignment
    """

    def __init__(self, parent, channel, scalers=None, align=('left','bottom'), right_offset=0, theme=None, flip=False, outline=None, square=False, \
                background=None,\
                led_h=5, led_gap=1, peak_h=1, radius=0, bar_space=0.5, barw_min=1, barw_max=20, tip=False, decay=Spectrum.DECAY, col_mode='vert', **kwargs):

        # 1. Capture all configuration parameters into self.config
        self.config = {
            'channel': channel,
            'scalers': scalers,
            'align': align,
            'right_offset': right_offset,
            'theme': theme,
            'flip': flip,
            'led_h': led_h,
            'led_gap': led_gap,
            'peak_h': peak_h,
            'radius': radius,
            'bar_space': bar_space,
            'barw_min': barw_min,
            'barw_max': barw_max,
            'tip': tip,
            'decay': decay,
            'col_mode': col_mode,
        }
        self.config.update(kwargs)
        
        # Assign primary attributes used outside of Frame's geometry calculation
        self.channel        = self.config['channel']
        self.right_offset   = self.config['right_offset']
        self.col_mode       = self.config['col_mode']

        # 2. Call the parent Frame.__init__. This establishes self.w and self.h.
        Frame.__init__(self, parent, 
                         scalers=self.config['scalers'], 
                         align=self.config['align'], 
                         theme=self.config['theme'],
                         outline=outline,
                         background=background,
                         square=square)
        
        # 3. Call Spectrum.__init__ (This only needs the initial size and bar settings)
        # Note: Spectrum.__init__ is being called here because it manages the audio processing 
        # structure, which might be stateful beyond simple frame redraws. If it relies 
        # on self.w, it must be re-called in configure() OR just the parts that depend on
        # geometry must be moved to configure(). Since it seems to set bar geometry:
        # self.spectrum_reinit()

        # 4. Initialize the scene components via configure()
        self.configure()

        
    def configure(self):
        """
        Re-entrant method to generate all visual components based on the 
        current frame geometry (self.w, self.h).
        """
        # 1. CRITICAL: Clear existing children frames
        self.frames = [] 
        cfg = self.config

        # 2. Re-initialize the Spectrum geometry (in case frame size changed)
        # Spectrum.__init__ should be safe to call multiple times if it just recalculates bar geometry
        Spectrum.__init__(self, self.w, cfg['bar_space'], cfg['barw_min'], cfg['barw_max'], decay=cfg['decay'])
        # The Spectrum init populates self.bars, self.barw, etc.
        
        # 3. Create the Bar object using the newly calculated dimensions
        # self.width, self.h are from Frame, self.barw is from Spectrum
        self.bar = Bar(self, 
                       box_size=(self.width, self.h), # Ensure width/h are correct
                       led_h=cfg['led_h'], 
                       led_gap=cfg['led_gap'], 
                       peak_h=cfg['peak_h'], 
                       flip=cfg['flip'], 
                       radius=cfg['radius'], 
                       tip=cfg['tip'], 
                       col_mode=cfg['col_mode'])

        print("SpectrumFrame.configure> w %s Spectrum setup: bars=%d, bar width=%d, gap=%d \n    Frame> %s" % (self.width, self.bars, self.barw, self.bar_gap, self.framestr()))
        # Note: Bar.__init__ must add the bar to self.frames of the SpectrumFrame parent.

    def update_screen(self, full=True):
        """
        Decay work by assuming that all bars naturally decay at a fixed rate and manner (eg lin /log)
        If the target height is less than the current height then, the decay continues
        If the target height is greater than the current, the height immediately increases - per smoothing algorithm
        This is intended to give a sharp peak response, but a slow delay
        """

        # #Check if the parent frame has been resized
        # if self.width > self.w:
        #     self.configure()

        self.read(self.channel)
        self.draw_background(True)
        for i in range(len(self.current)):
            x = i * (self.barw + self.bar_gap)
            colour_index = x if self.col_mode == 'horz' else None
            self.bar.draw( x+self.right_offset, self.current[i].smoothed(), self.barw, self.peaks[i], colour_index=colour_index)
        # print("SpectrumFrame.update> ", self.abs_rect())
        return True
        

    @property
    def width(self):
        return self.bars * (self.bar_gap+self.barw)



"""
Visualiser Frames create complex responses to the audio:
- concentric octaves
- oscilogrammes
- modulated lines and circles
- dots that move in accordance with bass and treble
- blended lines and circles moving in sympathy with music

"""
class OscilogrammeBar(Frame):
    """
        Displays a vertical bars with changing colours at the top
        - limits is an array of points where colour changes occur: [level (%), colour] eg [[0, 'grey'], [0.8,'red'], [0.9],'purple']
        - sits within a screen to compile two together
        - uses full screen height

        Creates a bar, centred in a Frame as a % of the Frame width

        barsize_pc  - is the percentage of gap to barwidth
        barw_min    - is the minimum width of a bar
        led_h       - is the height of one 'LED', when a bar is comprised of lots of LEDs stacked up
        led_gap     - is the size of the gap between LEDS - 0 means the LEDs are not distinct, but enables amplitude based colours
        col_mode    - colours change either horizontally across the platform, or vertically with the amplitude of the bar
        radius      - is curved edges to each LED
        tip         - is a curved end to the bar
        decay       - is a time constant for how quickly a bar falls down
    """
    DECAY     = 0.5   # Lower is longer delay - This is the amount that a bar reduces each period
    FRAME     = 1024  # Samples
    BAR_MAX   = 20    # Max width of a Bar

    def __init__(self, parent, channel, scalers=None, align=('left', 'bottom'), barsize_pc=1, theme='std', flip=False, background=None,\
                    led_h=5, led_gap=0, col_mode='horz', radius=0, barw_min=4, tip=True, decay=DECAY,outline=None, square=False):

        Frame.__init__(self, parent, scalers=scalers, align=align, theme=theme, outline=outline,square=square,background=background)
        self.bar_space      = barsize_pc     # pc of barwidth
        self.decay          = decay
        self.channel        = channel
        self.parent         = parent

        # Calculate how many bars can be drawn in the width available
        # Go down the bar widths to see what will fit
        for barw in range(barw_min, OscilogrammeBar.BAR_MAX):
            self.bar_gap    = int(barw * self.bar_space)
            self.bars       = int(self.w/(self.bar_gap+barw))
            if  self.bars <= OscilogrammeBar.FRAME: break

        self.barw           = barw
        self.reduce_by      = 2*OscilogrammeBar.FRAME//self.bars

        # Pack out the gaps to make sure the bars + gaps fill the whole width
        oscillograme_width = self.bars * (self.bar_gap+self.barw)
        if oscillograme_width < self.width:
            gaptofill = self.width-oscillograme_width
            self.bar_gap = self.bar_gap+ gaptofill/self.bars

        self.current  = [ Smoother(1.0) for i in range(self.bars)]    #array of smoothers
        self.bar      = Bar(self, align=('centre', 'middle'), box_size=(self.width, self.h), led_h=led_h, led_gap=led_gap, theme=theme, flip=flip, radius=radius, tip=tip, col_mode='horz')

        # print("OscilogrammeBar.__init__> width=%s, reduce_by=%d, bars %s, bar_gap %d, barw %d, frame> %s" % (self.width, self.reduce_by, self.bars, self.bar_gap, self.barw, self.geostr()))

    @property
    def width(self):
        return self.bars * (self.bar_gap+self.barw)

    def update_screen(self, full):
        samples =  self.platform.reduceSamples( self.channel, self.reduce_by )
        self.draw_background()
        for i in range(self.bars):
            # add the new sample
            target_height = min(1.0, samples[i])
            # print(target_height)
            if target_height > self.current[i].smoothed():
                self.current[i].add(target_height)

            # decay the existing ones
            if self.current[i].smoothed() < self.decay/100.0:
                self.current[i].add(0.0)
            else:
                self.current[i].add(self.current[i].smoothed()* (1- self.decay))

            x = i * (self.barw + self.bar_gap)
            self.bar.draw( x, self.current[i].smoothed(), self.barw, colour_index=x)
        return True
        


class Oscilogramme(Frame):
    """
    Draw a frame of samples - scaling the number of samples is the trick to align the frame rate and the sample rate
    """
    def __init__(self, parent, channel, scalers=None, align=('left', 'bottom'), theme=None):
        self.channel = channel
        Frame.__init__(self, parent, scalers=scalers, align=align, theme=theme)
        self.configure()

    def configure(self):
        self.lines   = Line(self, circle=False, amp_scale=0.6)
        

    def update_screen(self, full):
        samples =  self.platform.reduceSamples( self.channel, self.platform.framesize//self.w, rms=False )
        self.draw_background()
        self.lines.draw_mod_line(samples, colour='foreground')
        return True
        


class Octaviser(Frame, Spectrum):
    def __init__(self, parent, channel, scalers=None, align=('left', 'bottom'), theme=None):
        self.channel = channel
        Frame.__init__(self, parent, scalers=scalers, align=align)
        self.configure()

    def configure(self):
        Spectrum.__init__(self, self.w, bar_space=5)
        self.num_octaves=len(self.octaves)
        self.arcs = ArcsOctaves(self.parent, theme='rainbow', NumOcts=self.num_octaves)

    def update_screen(self, full):
        self.draw_background()
        fft = self.read(self.channel)

        for octave in range(1, self.num_octaves):
            self.arcs.draw(octave, fft[self.octaves[octave-1]:self.octaves[octave]])
            # print(bin, self.octaves[octave]) #, fft[bin:self.octaves[octave]])
        return True
        


class CircleModulator(Frame):
    def __init__(self, parent, channel, scalers=None, align=None, theme=None):
        self.channel = channel
        Frame.__init__(self, parent, scalers=scalers, align=align, theme=theme, square=False)
        self.configure()

    def configure(self):
        self.lines   = Line(self, circle=True, radius=self.h/2, endstops=(0,2*PI), amp_scale=1.0)
        # self.ripples = Line(self, circle=True, radius=self.h/2, endstops=(0,2*PI), amp_scale=1.4)
        self.dots    = Dots(self, circle=True, radius=self.h/2, endstops=(0,2*PI), amp_scale=1.0)
        self.VU      = VU(self.platform, self.channel, decay=0.2)

        # print("VUFrame.__init__> box=%s, flip=%d, orient %s, frame> %s" % (box, flip, orient, self.geostr()))

    def update_screen(self, full):
        hpf_freq = 1000
        lpf_freq = 1500
        self.draw_background()

        height, peaks = self.VU.read()
        samples = self.platform.reduceSamples( self.channel, self.platform.framesize//(self.w//2), rms=False )  # reduce the dataset quite a bit
        # high_samples = self.platform.filter( samples, hpf_freq, type='highpass' )
        low_samples = self.platform.filter( samples, lpf_freq, type='lowpass' )
        self.lines.draw_mod_line(low_samples, amplitude=0.5, gain=0.1, colour=height*self.h/2)
        self.dots.draw_mod_dots(low_samples, trigger=self.platform.trigger_detected, amplitude=0.1, gain=0.1, colour='alert')
        # self.ripples.draw_mod_ripples(low_samples, trigger=self.platform.trigger_detected, amplitude=height)
        return True
        


""" A visualiser based on a circle display of spectrum lines """
class Diamondiser(Frame, Spectrum):
    BARSPACE = 1
    def __init__(self, parent, channel, scalers=None, align=('left', 'bottom'), theme=None, bar_space=BARSPACE):
        Frame.__init__(self, parent, scalers=scalers, align=align, square=True, theme=theme)
        self.channel     = channel
        self.bar_space   = bar_space
        self.configure()

    def configure(self):
        Spectrum.__init__(self, self.w, bar_space=self.bar_space, bandwidth=8000, decay=0.5)
        # self.VU          = VU(self.platform, channel, decay=0.2)
        self.max_radius  = self.h/2
        self.ray_angle   = 1/self.bars
        self.centre_pc   = 0.8

        self.rays        = [Line(self, endstops=(PI/2, 5*PI/2), width=self.bar_space*2, tick_pc=self.centre_pc, centre_offset=0, \
                            radius=self.max_radius, colour='mid') \
                             for _ in range(self.bars)]
        # print("Diamondiser.__init__>", self.bars, self.max_radius, self.geostr(), self.anglestr())

    def update_screen(self, full, channel='left'):
        self.read(self.channel)
        radius  = self.centre_pc
        self.draw_background()
        for ray_index, ray in enumerate(self.rays):
            col = self.max_radius*(ray_index/self.bars)
            amp = radius*self.current[ray_index].smoothed() if self.current[ray_index].smoothed() > 0 else 0
            ray.drawFrameCentredVector(ray_index*self.ray_angle, amplitude=amp, gain=1-radius, colour=col)
        return True
        
