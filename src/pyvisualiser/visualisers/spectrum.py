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
from    pyvisualiser.core.framecore  import Frame, Smoother, RowFramer, ColFramer
from    pyvisualiser.core.components import Bar, Text, Line, Box, Image, ArcsOctaves, Dots, Effects, BarStyle, SpectrumStyle
from    pyvisualiser.styles.presets  import PI, Centred


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
        # print("Spectrum.__init__> Selected spectrum: octave spacing=1/%d, num octaves %d, bar width %d" % (self.spacing, len(self.octaves),self.barw))



    def read(self, channel='left'):
        smoothedpeak = 0
        fft = self.platform.packFFT(self.bar_freqs, channel)
        # print("Spectrum.read> fft", fft)

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

            # print("Spectrum.read> ", self.current[i].__str__())

class SpectrumFrame(Frame, Spectrum):
    """
    Creates a spectrum analyser of the width and octave interval specified.
    - scale is used to determine how wide the frame is as a % of the parent frame
    - channel 'left' or 'right' selects the audio channel and screen alignment
    """

    def __init__(self, parent, channel, scalers=None, align=None, theme=None, flip=False, outline=None, square=False, \
                background=None, padding=0,\
                bar_style=None, spectrum_style=None, effects=None, \
                # # OLd API
                led_h=5, led_gap=1, peak_h=1, radius=0, tip=False, decay=Spectrum.DECAY, col_mode='vert', \
                bar_space=0.5, barw_min=1, barw_max=20, right_offset=0, \
                intensity_threshold=0.5, intensity_scale=2.5, intensity_blur=1.0, intensity_alpha=200):

        if effects is None:
            effects = Effects(threshold=intensity_threshold, scale=intensity_scale, blur=intensity_blur, alpha=intensity_alpha)

        if bar_style is None:
            bar_style = BarStyle(led_h=led_h, led_gap=led_gap, peak_h=peak_h, radius=radius, tip=tip, colour_mode=col_mode, flip=flip, right_offset=right_offset)

        if spectrum_style is None:
            spectrum_style = SpectrumStyle(bar_space=bar_space, barw_min=barw_min, barw_max=barw_max)

        # 1. Capture all configuration parameters into self.config
        self.config = {
            'channel': channel,
            'scalers': scalers,
            'align': align,
            'theme': theme,
            'bar_style': bar_style,
            'spectrum_style': spectrum_style,
            'effects': effects,
            # Legacy args captured in style/spectrum_style now
            # 'peak_h': peak_h,
            # 'radius': radius,
            # 'bar_space': bar_space,
            # 'barw_min': barw_min,
            # 'barw_max': barw_max,
            # 'decay': decay

        }
        # self.config.update(kwargs)
        
        # Assign primary attributes used outside of Frame's geometry calculation
        self.channel        = self.config['channel']
        # self.col_mode       = self.config['bar_style'].col_mode

        # 2. Call the parent Frame.__init__. This establishes self.w and self.h.
        Frame.__init__(self, parent, 
                         scalers=self.config['scalers'], 
                         align=self.config['align'], 
                         theme=self.config['theme'],
                         outline=outline,
                         background=background,
                         square=square,
                         padding=padding)
        
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
        Spectrum.__init__(self, self.w, 
                          bar_space=cfg['spectrum_style'].bar_space, 
                          barw_min=cfg['spectrum_style'].barw_min, 
                          barw_max=cfg['spectrum_style'].barw_max, 
                          decay=cfg['spectrum_style'].decay)
        # The Spectrum init populates self.bars, self.barw, etc.
        
        # 3. Create the Bar object using the newly calculated dimensions
        # self.width, self.h are from Frame, self.barw is from Spectrum
        self.bar = Bar(self, align=('left', 'bottom'),
                       box_size=(self.width, self.h), # Ensure width/h are correct
                       style=cfg['bar_style'],
                       effects=cfg['effects'])

        # print("SpectrumFrame.configure> w %s Spectrum setup: bars=%d, bar width=%d, gap=%d \n    Frame> %s" % (self.width, self.bars, self.barw, self.bar_gap, self.framestr()))
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

        if self.config['spectrum_style'].flip:
 # reversed(list(enumerate(self.current))) gives you pairs of (original_index, value) 
    # starting from the end of the array.
            for i, item in enumerate(reversed(self.current)):
                x = i * (self.barw + self.bar_gap)
                
                # We use 'i' for the x position and colour, 
                # but 'item.smoothed()' and 'self.peaks' logic must align.
                colour_index = x if self.config['bar_style'].colour_mode == 'horz' else None
                
                # Note: If self.peaks also needs to be flipped, use len(self.current) - 1 - i
                peak_val = self.peaks[len(self.current) - 1 - i]
                
                self.bar.draw(
                    x + self.config['bar_style'].right_offset, 
                    item.smoothed(), 
                    self.barw, 
                    peak_val, 
                    colour_index=colour_index
                )
                # print("SpectrumFrame.update backwards> ", colour_index, self.config['bar_style'].colour_mode)
        else:
            for i in range(len(self.current)):
                x = i * (self.barw + self.bar_gap)
                colour_index = x if self.config['bar_style'].colour_mode == 'horz' else None
                self.bar.draw( x+self.config['bar_style'].right_offset, self.current[i].smoothed(), self.barw, self.peaks[i], colour_index=colour_index)
                # print("SpectrumFrame.update forwards> ", colour_index, self.config['bar_style'].colour_mode)

        

    @property
    def width(self):
        return self.bars * (self.bar_gap+self.barw)



""" A visualiser based on a circle display of spectrum lines """
class Diamondiser(Frame, Spectrum):
    BARSPACE = 1
    def __init__(self, parent, channel, scalers=None, theme=None, align=None, bar_space=BARSPACE,background=None, z_order=0, **kwargs):
        Frame.__init__(self, parent, scalers=scalers, align=align, square=True, theme=theme,background=background, z_order=z_order)
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

    def update_screen(self, full):
        self.read(self.channel)
        radius  = self.centre_pc

        for ray_index, ray in enumerate(self.rays):
            col = self.max_radius*(ray_index/self.bars)
            amp = radius*self.current[ray_index].smoothed() if self.current[ray_index].smoothed() > 0 else 0
            ray.drawFrameCentredVector(ray_index*self.ray_angle, amplitude=amp, gain=1-radius, colour=col)


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
        fft = self.read(self.channel)

        for octave in range(1, self.num_octaves):
            self.arcs.draw(octave, fft[self.octaves[octave-1]:self.octaves[octave]])
            # print(bin, self.octaves[octave]) #, fft[bin:self.octaves[octave]])

        


"""
Spectrum Analyser Frames - variants on
    1. Full frame - mono
    2. Horz Split screen
    3. Horz Split screen - right flipped
    4. Vert split - L/R
    5. Full frame, right channel offset

    SpectrumFrame API:
    # def __init__(self, parent, channel, scale, align=('left','bottom'), right_offset=0, theme='std', flip=False, \
    #                 led_h=5, led_gap=1, peak_h=1, radius=0, bar_space=0.5, barw_min=12, barw_max=20, tip=False, decay=DECAY):
"""

class Spectrum2chFrame(Frame): #""" Vert split - L/R """
    def __init__(self, parent, **kwargs) :
        Frame.__init__(self, parent, outline={'width':4,'colour':'light'}, **kwargs)

        rows = ColFramer(self, scalers=(0.7, 0.7), padding=10, outline={'width':4,'colour':'light'})
        rows += SpectrumFrame(rows, 'left'  )
        rows += SpectrumFrame(rows, 'right' )
        

class SpectrumStereoFrame(Frame): #""" Horz Split screen - right flipped 'Apple Style' """
    # THis is vertically aligned, with one flipped
    def __init__(self, parent, scalers, align) :
        Frame.__init__(self, parent, scalers=scalers, align=align, background=None)

        self += SpectrumFrame(self, 'right', scalers=(0.5, 1.0), align=('right','top'), bar_style=BarStyle(flip=False, led_gap=2, peak_h=0, radius=2,colour_mode='horz'), spectrum_style=SpectrumStyle(barw_min=10, bar_space=0.4), theme='rainbow', background=None)
        self += SpectrumFrame(self, 'left', scalers=(0.5, 1.0), align=('left','top'), bar_style=BarStyle(flip=False, led_gap=2, peak_h=0, radius=2, colour_mode='horz'),spectrum_style=SpectrumStyle(barw_min=10, bar_space=0.4,flip=True), theme='rainbow', background=None)
        

class SpectrumStereoLRFrame(Frame): #""" Horz Split screen - LED Style right flipped  """
    # THis is vertically aligned, with one flipped
    def __init__(self, parent, scalers, align) :
        Frame.__init__(self, parent, scalers=scalers, align=align)

        self += SpectrumFrame(self, 'right', scalers=(1.0, 0.5), align=('left','top'), bar_style=BarStyle(flip=True, led_gap=1, peak_h=1, radius=2), spectrum_style=SpectrumStyle(barw_min=12), theme='white' )
        self += SpectrumFrame(self, 'left', scalers=(1.0, 0.5), align=('left','bottom'), bar_style=BarStyle(flip=False, led_gap=1, peak_h=1, radius=2), spectrum_style=SpectrumStyle(barw_min=12), theme='red' )
        

class SpectrumStereoSplitFrame(Frame): #""" Horz Split screen - right flipped """
    # This is vertically aligned
    def __init__(self, parent, scalers, align) :
        Frame.__init__(self, parent, scalers=scalers, align=align, background={'colour':'background', 'per_frame_update':True})
        self += SpectrumFrame(self, 'right', scalers=(1.0, 0.5), align=('left','bottom'), bar_style=BarStyle(led_gap=0, flip=True, tip=True), spectrum_style=SpectrumStyle(barw_min=5, bar_space=0.5) )
        self += SpectrumFrame(self, 'left', scalers=(1.0, 0.5), align=('left','top'), bar_style=BarStyle(led_gap=0, tip=True), spectrum_style=SpectrumStyle(barw_min=5, bar_space=0.5) )
        

class SpectrumStereoOffsetFrame(Frame):
    def __init__(self, parent, scalers, align) :
        Frame.__init__(self, parent, scalers=scalers, align=align,background={'colour':'background', 'per_frame_update':True})
        self += SpectrumFrame(self, 'right', scalers=(1.0, 1.0), align=('left','top'), right_offset=2, bar_style=BarStyle(led_gap=0, tip=True), spectrum_style=SpectrumStyle(barw_min=8, bar_space=1.5), theme='red', background=None)
        self += SpectrumFrame(self, 'left', scalers=(1.0, 1.0), align=('left','bottom'), right_offset=0, bar_style=BarStyle(led_gap=0, tip=True), spectrum_style=SpectrumStyle(barw_min=8, bar_space=1.5), theme='blue',background=None )


class StereoSpectrumFrame(Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        self += SpectrumFrame(self,  'right', scalers=(1.0, 0.5), align=('left','top'), flip=False, led_gap=5, peak_h=3, radius=0, tip=False, barw_min=15, bar_space=0.5, **kwargs)
        self += SpectrumFrame(self,  'left', scalers=(1.0, 0.5), align=('left','bottom'), flip=True, led_gap=5, peak_h=3,radius=0, tip=False, barw_min=15, bar_space=0.5, **kwargs )


