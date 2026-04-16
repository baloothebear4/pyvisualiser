#!/usr/bin/env python
"""
 Visualiser classes for MetaData
    - album/track/artist 
    - source
    - volume
    - data rate

 Part of pyvisualiser

 v1.0 Baloothebear4 Apr 2026
   - refactored from frames.py
   -added source & volume classes
   
"""



"""
Visualiser Frames create complex responses to the audio:
- concentric octaves
- oscilogrammes
- modulated lines and circles
- dots that move in accordance with bass and treble
- blended lines and circles moving in sympathy with music

"""

from    pyvisualiser.core.framecore  import Frame, Smoother
from    pyvisualiser.core.components import Bar, Text, Line, Box, Image, ArcsOctaves, Dots, BarEffects, BarStyle, SpectrumStyle
from    pyvisualiser.styles.presets  import PI, Centred
from    pyvisualiser.styles.styles   import OscillogrammeStyle, BarStyle


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


    def __init__(self, parent, channel, scalers=None, align=None, theme=None, background=None, outline=None,
                 oscillograme = OscillogrammeStyle(), bar=BarStyle(), square=False, z_order=0):

        Frame.__init__(self, parent, scalers=scalers, align=align, theme=theme, outline=outline,square=square,\
                       background=background, z_order=z_order)
        self.channel        = channel
        self.parent         = parent
        self.oscillograme   = oscillograme
        self.bar_style      = bar

        self.configure()

    def configure(self):
        # print("OscilogrammeBar.__init__> theme %s, parent.theme %s" % (self.theme, self.parent.theme))

        # Calculate how many bars can be drawn in the width available
        # Go down the bar widths to see what will fit
        for barw in range(self.oscillograme.barw_min, self.oscillograme.barw_max):
            self.bar_gap    = int(barw * self.oscillograme.barsize_pc)
            self.bars       = int(self.w/(self.bar_gap+barw))
            if  self.bars <= self.oscillograme.samplesperframe: break

        self.barw           = barw
        self.reduce_by      = 2*self.oscillograme.samplesperframe//self.bars

        # Pack out the gaps to make sure the bars + gaps fill the whole width
        oscillograme_width = self.bars * (self.bar_gap+self.barw)
        if oscillograme_width < self.width:
            gaptofill = self.width-oscillograme_width
            self.bar_gap = self.bar_gap+ gaptofill/self.bars

        self.current  = [ Smoother(1.0) for i in range(self.bars)]    #array of smoothers
        # bar_style = BarStyle(led_h=led_h, led_gap=led_gap, flip=flip, radius=radius, tip=tip, colour_mode='horz')
        self.bar      = Bar(self, box_size=(self.width, self.h), style=self.bar_style)
        self.decay    = self.oscillograme.decay

        # print("OscilogrammeBar.__init__> width=%s, reduce_by=%d, bars %s, bar_gap %d, barw %d, frame> %s" % (self.width, self.reduce_by, self.bars, self.bar_gap, self.barw, self.geostr()))




    @property
    def width(self):
        return self.bars * (self.bar_gap+self.barw)

    def update_screen(self):
        samples =  self.platform.reduceSamples( self.channel, self.reduce_by )
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
    def __init__(self, parent, channel, scalers=None, align=('left', 'bottom'), theme=None, background=None, z_order=0, **kwargs):
        self.channel = channel
        Frame.__init__(self, parent, scalers=scalers, align=align, theme=theme, background=background, z_order=z_order)
        self.configure()

    def configure(self):
        self.lines   = Line(self, circle=False, amp_scale=0.6)
        self.resolution = 256 # Limit resolution for performance
        

    def update_screen(self):
        # Limit resolution to avoid excessive draw calls (e.g. max 256 segments)
        reduceby = max(1, self.platform.framesize // self.resolution)
        samples =  self.platform.reduceSamples( self.channel, reduceby, rms=False )
        # self.draw_background(True)
        self.lines.draw_mod_line(samples, colour='foreground')
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

    def update_screen(self):
        hpf_freq = 1000
        lpf_freq = 1500
        # self.draw_background(True)

        height, peaks = self.VU.read()
        samples = self.platform.reduceSamples( self.channel, self.platform.framesize//(self.w//2), rms=False )  # reduce the dataset quite a bit
        # high_samples = self.platform.filter( samples, hpf_freq, type='highpass' )
        low_samples = self.platform.filter( samples, lpf_freq, type='lowpass' )
        self.lines.draw_mod_line(low_samples, amplitude=0.5, gain=0.1, colour=height*self.h/2)
        self.dots.draw_mod_dots(low_samples, trigger=self.platform.trigger_detected, amplitude=0.1, gain=0.1, colour='alert')
        # self.ripples.draw_mod_ripples(low_samples, trigger=self.platform.trigger_detected, amplitude=height)
        return True
        

# Subframe to drawn two spectrums flipped on top        
class SamplesFrame(Frame):
    """ Volume/Source on left - Spectrum on left - one channel """
    def __init__(self, parent, scalers=(1.0, 1.0), align=('centre','middle'), theme='std'):
        Frame.__init__(self, parent, scalers=scalers, align=align)
        self.create()
        
    def create(self):
        self += OscilogrammeBar(self,  'left', scalers=(1.0,0.5), align=('left','top'), oscillograme=OscillogrammeStyle(barsize_pc=0.5, barw_min=2), bar=BarStyle(led_gap=0))
        self += OscilogrammeBar(self,  'right', scalers=(1.0,0.5), align=('left','bottom'), oscillograme=OscillogrammeStyle(barsize_pc=0.5, barw_min=2), bar=BarStyle(led_gap=0,flip=True, colour_mode='horz'))

