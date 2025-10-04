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
from    displaydriver import Bar, Text, Line, Box, Lightback, Image, ArcsOctaves, Dots

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
    def __init__(self, parent, scalers=None, align=None, text='Default Text', reset=True, theme=None, wrap=False, colour_index='foreground'):
        Frame.__init__(self, parent, scalers=scalers, align=align, theme=theme)
        self.text     = Text(self, text=text, reset=reset, align=align, scalers=scalers, theme=theme, colour_index=colour_index, wrap=wrap)
        self.parent   = parent
        # print("TextFrame.__init__>", text, self.text.fontwh, scalers, self.alignment, self.geostr())

    def update(self, full, text=None, colour_index=None, fontmax=None):
        # print("TextFrame.draw ", text, colour_index, self.geostr())
        if full or self.text.new_content_available(text):
            self.draw_background() # clear whats there -- not needed for
            self.text.draw(text=text, colour_index=colour_index, fontmax=fontmax)
        else:
            pass # no need to redraw
        

        

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
        Frame.__init__(self, parent, scalers=scalers, align=align, theme=theme)
        self.barw           = self.w * barsize_pc if orient == 'vert' else self.h * barsize_pc   # width of the bar
        self.parent         = parent

        text = " 22:22 "
        self.elapsed     = Text(self, fontmax=self.barw, text=text, reset=True, align=('left', 'middle'), theme=theme, colour_index='mid')
        self.remaining   = Text(self, fontmax=self.barw, text=text, reset=True, align=('right', 'middle'), theme=theme, colour_index='mid')
        text_width = self.elapsed.fontwh[0] + self.remaining.fontwh[0]

        box = (self.barw, self.h) if orient == 'vert' else (self.w-text_width, self.barw)
        self.boxbar      = Box(self, align=('centre', 'middle'), theme=theme, box=box, radius=10)

    def update(self, full):
        elapsed   = f"  {int( self.platform.elapsed//60)}:{int( self.platform.elapsed %60):02d}"
        remaining = f"{int( self.platform.remaining//60)}:{int(  self.platform.remaining%60):02d}  "

        if full or self.elapsed.new_content_available(elapsed):
            self.draw_background()
            hide_backline = -self.h/2 if self.platform.elapsedpc*self.w > self.h/2 else 0 # offset by the radius, makes sure the very start is OK too
            self.boxbar.drawH(self.platform.elapsedpc, flip=True, colour_index='dark', offset=(hide_backline,0))
            self.boxbar.drawH(self.platform.elapsedpc, colour_index='light')
            # Create the string representation

            self.elapsed.draw(elapsed, colour_index='light')
            self.remaining.draw(remaining, colour_index='light')
            # print("PlayProgressFrame>", elapsed, remaining)
        else:
            pass # no need to redraw


        

class AlbumArtFrame(Frame):
    # OUTLINE = { 'width' : 3, 'radius' : 0, 'colour_index' : 'foreground'}
    def __init__(self, parent, scalers=None, align=None, opacity=None, outline=None):
        Frame.__init__(self, parent, scalers=scalers, align=align, square=True)
        self.image_container = Image(self, outline=outline, opacity=opacity)  # make square
        self.parent          = parent

    def update(self, full):
        # print("AlbumArtFrame.draw> new album art")
        if full or self.image_container.new_content_available(self.platform.album_art):
            self.draw_background()
            self.image_container.draw(self.platform.album_art)
        else:
            pass # no need to redraw
             


class ArtistArtFrame(Frame):
    def __init__(self, parent, scalers=None, align=None, opacity=None, outline=None):
        Frame.__init__(self, parent, scalers=scalers, align=align)
        self.image_container = Image(self, align=None, scalers=(1.0,1.0), opacity=opacity, outline=outline)  
        self.parent         = parent
        # print("ArtistArtFrame.__init__>", opacity)

    def update(self, full):
        if full or self.image_container.new_content_available(self.platform.artist_art):
            self.draw_background()
            self.image_container.draw(self.platform.artist_art)
        else:
            pass # no need to redraw



class MetaDataFrame(Frame):
    SHOW = {'artist': {'colour':'foreground', 'align': ('centre','top'), 'scalers': (1.0, 0.33) }, \
            'track': {'colour':'light', 'align': ('centre','middle'), 'scalers' : (1.0, 0.33) }, \
            'album': {'colour':'mid', 'align': ('centre','bottom'), 'scalers' : (1.0, 0.33) } }

    def __init__(self, parent, scalers=None, align=None,theme=None,show=SHOW, same_size=True):
        Frame.__init__(self, parent, scalers=scalers, align=align, outline=None)
        self.show       = show
        self.same_size  = same_size
        self.metadata   = {}
        self.parent     = parent

        for meta, attributes in self.show.items():
            scalers = attributes['scalers'] if 'scalers' in attributes else MetaDataFrame.SHOW[meta]['scalers']
            align   = attributes['align']   if 'align'   in attributes else MetaDataFrame.SHOW[meta]['align']
            colour  = attributes['colour']  if 'colour'  in attributes else MetaDataFrame.SHOW[meta]['colour']
            self.metadata[meta] = TextFrame(self, scalers=scalers, align=align, colour_index=colour, reset=True, theme=theme, wrap=True)
            # self.metadata[meta] = TextFrame(self, scalers=self.show[meta]['scalers'], align=self.show[meta]['align'], reset=True, theme=theme, wrap=True)

            # print("MetaDataFrame.__init__>", meta, attributes, self.wh, self.show )

    def update(self, full, fontsize=None):
        # fontsize = self.h//2
        for meta, container in self.metadata.items():
            if 'track'  in meta: container.update(full, text=self.platform.track, fontmax=fontsize) #, colour_index=self.show['track']['colour'])
            if 'album'  in meta: container.update(full, text=self.platform.album, fontmax=fontsize) #, colour_index=self.show['album']['colour'])
            if 'artist' in meta: container.update(full, text=self.platform.artist, fontmax=fontsize) #, colour_index=self.show['artist']['colour'])
        
            



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

    def __init__(self, parent, channel, scalers=None, align=('centre','middle'), peakmeter=False, outline=None,\
                 endstops=ENDSTOPS, tick_w=TICK_W, tick_pc=TICK_PC,fonth=FONTH, pivot=PIVOT, decay=DECAY, smooth=SMOOTH, bgdimage=None, \
                 needle=NEEDLE, ticklen=TICKLEN, scaleslen=SCALESLEN, theme=None, marks=MARKS, annotate=ANNOTATE, arcs=ARCS):

        self.channel = channel
        self.marks   = marks
        channel      = channel if channel == 'left' or channel == 'right' else align[0]
        Frame.__init__(self, parent, scalers=scalers, align=(channel, align[1] ), theme=theme)
        self.parent = parent

        # if endstops is None: endstops = self.needle.endstops   # using endstops = None automatically calculates the endsstops based on the arc the needle to the edge of the sssssframe
        # METERS      = { 'blueVU' : {'file': 'blue-bgr.png', 'needle':NEEDLE, 'endstops':ENDSTOPS, 'pivot':0}
        # Setup the background

        if bgdimage is not None:
            self.path       = VUMeter.VUIMAGEPATH +'/'+ bgdimage
            self.bgdimage   = Image(self, align=('centre', 'middle'), path=self.path,outline=outline )
            # print("VUeter.__init__> setup background images", self.framestr())
        else:
            self.path        = None
            radius           = self.h*(0.5-pivot)
            self.scales      = { mark : Text(self, text=marks[mark]['text'], colour_index=marks[mark]['colour'], fontmax=self.h*fonth, endstops=endstops, scalers=(1.0,1.0),centre_offset=pivot, radius=radius*scaleslen, reset=False, theme=theme ) for mark in marks }
            self.dB          = Text(self, fontmax=self.h*fonth*2, text=annotate['text'], align=('centre', annotate['Valign']), colour_index=annotate['colour'], reset=True, theme=theme, scalers=(1.0,1.0))
            self.ticks       = Line(self, width=tick_w, endstops=endstops, tick_pc=tick_pc, centre_offset=pivot, radius=radius*ticklen, theme=theme )
            self.arclines    = []
            for rad_pc, arc in arcs.items():
                self.arclines.append(Line(self, width=arc['width'], colour_index=arc['colour'], endstops=endstops, tick_pc=tick_pc, centre_offset=pivot, radius=radius*rad_pc, theme=theme ))

        # setup the needle
        radius           = self.h*(0.5-pivot)
        self.VU          = VU(self.platform, self.channel, decay=decay, smooth=smooth)
        self.needle      = Line(self, width=needle['width'], tick_pc=needle['radius_pc'], centre_offset=pivot, endstops=endstops, radius=radius*needle['length'], theme=theme, colour_index=needle['colour'])
        self.peak        = Line(self, width=needle['width'], tick_pc=needle['radius_pc'], centre_offset=pivot, endstops=endstops, radius=radius*needle['length'], theme=theme, colour_index='alert')
        self.peakmeter   = peakmeter

    def update(self, full):
        if self.path is None:
            self.drawVUBackground()
        else:
            self.bgdimage.draw()
        self.drawNeedle()
        

    def drawVUBackground(self):
        self.draw_background()
        for val, mark in self.marks.items():
            self.scales[val].drawVectoredText(val, colour_index=mark['colour'])
            self.ticks.drawFrameCentredVector(val, colour_index=mark['colour'], width=mark['width'])

        for arc in self.arclines:
            arc.drawFrameCentredArc(0)

        self.dB.draw()

    def drawNeedle(self):
        vu, peaks   = self.VU.read()
        self.needle.drawFrameCentredVector(vu)
        if self.peakmeter and peaks > 0: self.peak.drawFrameCentredVector(peaks)


class VUMeterFrame1(Frame):
    """ Simple Meter with marks and scales  - based on frame width"""
    def __init__(self, parent, scalers=None, align=('centre', 'middle')):

        Frame.__init__(self, parent, scalers=scalers, align=align)
        NEEDLE    = { 'width':4, 'colour': 'foreground', 'length': 0.8, 'radius_pc': 1.0 }
        ENDSTOPS  = (3*PI/4-0.2, 5*PI/4+0.2)  #Position of endstop if not the edge of the frame
        self += VUMeter(self, 'left', scalers=(0.5, 1.0), align=('left', 'bottom'), arcs={}, endstops=ENDSTOPS, needle=NEEDLE)
        self += VUMeter(self, 'right', scalers=(0.5, 1.0), align=('right', 'bottom'), arcs={}, endstops=ENDSTOPS, needle=NEEDLE)

class VUMeterFrame2(Frame):
    """ 180 degrees meter, centre rotate """

    def __init__(self, parent, scalers=None, align=('centre', 'middle')):
        Frame.__init__(self, parent, scalers=scalers, align=align)
        NEEDLE    = { 'width':4, 'colour': 'foreground', 'length': 0.8, 'radius_pc': 1.0 }
        ENDSTOPS  = (PI/2, 3*PI/2)
        TICK_W    = 3

        TICKLEN   = 0.8         # length marks
        TICK_PC   = 0.1         # lenth of the ticks as PC of the needle
        SCALESLEN = 0.9
        DECAY     = 0.3         # decay factor
        SMOOTH    = 10          # samples to smooth
        ARCLEN    = TICKLEN * (1-TICK_PC)

        MARKS     = {0.0: {'text':'0', 'width': TICK_W, 'colour': 'mid'},
                     0.14: {'text':'1', 'width': TICK_W, 'colour': 'mid'},
                     0.28: {'text':'2', 'width': TICK_W, 'colour': 'mid'},
                     0.42: {'text':'3', 'width': TICK_W, 'colour': 'mid'},
                     0.56: {'text':'4', 'width': TICK_W, 'colour': 'light'},
                     0.70: {'text':'5', 'width': TICK_W, 'colour': 'light'},
                     0.84: {'text':'6', 'width': TICK_W, 'colour': 'alert'},
                     1.0: {'text':'7', 'width': TICK_W, 'colour': 'alert'} }
        ARCS      = {ARCLEN    : {'width': TICK_W//2, 'colour': 'mid'} }
        ANNOTATE  = { 'Valign':'middle', 'text':'PPM', 'colour':'mid' }
        self += VUMeter(self, 'left', scalers=(0.5, 1.0), align=('left', 'bottom'), \
                        pivot=-0.4, endstops=ENDSTOPS, peakmeter=True, needle=NEEDLE, marks=MARKS, arcs=ARCS, annotate=ANNOTATE, smooth=SMOOTH)
        self += VUMeter(self, 'right', scalers=(0.5, 1.0), align=('right', 'bottom'), \
                        pivot=-0.4, endstops=ENDSTOPS, peakmeter=True, needle=NEEDLE, marks=MARKS, arcs=ARCS, annotate=ANNOTATE, smooth=SMOOTH)

class VUMeterFrame3(Frame):
    """ 270 speedo dial type VU - colourful """
    def __init__(self, parent, scalers=None, align=('left', 'bottom')):
        Frame.__init__(self, parent, scalers=scalers, align=align)
        TICK_W    = 3
        ARCLEN    = 0.70
        MARKS     = {0.0: {'text':'0', 'width': TICK_W, 'colour': 'mid'},
                     0.14: {'text':'1', 'width': TICK_W, 'colour': 'mid'},
                     0.28: {'text':'2', 'width': TICK_W, 'colour': 'mid'},
                     0.42: {'text':'3', 'width': TICK_W, 'colour': 'mid'},
                     0.56: {'text':'4', 'width': TICK_W, 'colour': 'light'},
                     0.70: {'text':'5', 'width': TICK_W, 'colour': 'light'},
                     0.84: {'text':'6', 'width': TICK_W, 'colour': 'alert'},
                     1.0: {'text':'7', 'width': TICK_W, 'colour': 'alert'} }
        ARCS      = {ARCLEN    : {'width': TICK_W//2, 'colour': 'mid'} }
        ANNOTATE  = { 'Valign':'bottom', 'text':'Peak RMS', 'colour':'mid' }
        self += VUMeter(self, 'left', scalers=(0.5, 1.0), align=('left', 'bottom'), \
                        pivot=0, endstops=(PI/4, 7*PI/4), marks=MARKS, arcs=ARCS,annotate=ANNOTATE)
        self += VUMeter(self, 'right', scalers=(0.5, 1.0), align=('right', 'bottom'), \
                        pivot=0, endstops=(PI/4, 7*PI/4), marks=MARKS, arcs=ARCS,annotate=ANNOTATE,)

class VUMeterFrame4(Frame):
    """120 degrees meter, low pivot """
    def __init__(self, parent, scalers=None, align=('centre', 'middle')):
        Frame.__init__(self, parent, scalers=scalers, align=align)
        TICK_W    = 3
        TICK_PC   = 0.2
        ARCLEN    = 0.8
        NEEDLE    = { 'width':4, 'colour': 'foreground', 'length': 0.85, 'radius_pc': 0.4 }
        MARKS     = {0.0: {'text':'-60', 'width': TICK_W, 'colour': 'mid'},
                     0.1: {'text':'-40', 'width': TICK_W, 'colour': 'mid'},
                     0.3: {'text':'-20', 'width': TICK_W, 'colour': 'mid'},
                     0.45: {'text':'-10', 'width': TICK_W, 'colour': 'mid'},
                     0.6: {'text':'-3', 'width': TICK_W, 'colour': 'mid'},
                     0.7: {'text':'+0', 'width': TICK_W, 'colour': 'alert'},
                     0.85: {'text':'+3', 'width': TICK_W*2, 'colour': 'alert'},
                     1.0: {'text':'+6', 'width': TICK_W*3, 'colour': 'alert'}
                     }
        ARCS      = {ARCLEN    : {'width': TICK_W//2, 'colour': 'mid'},
                     ARCLEN*(1-TICK_PC): {'width': TICK_W//2, 'colour': 'mid'} }
        ANNOTATE  = { 'Valign':'middle', 'text':'dB', 'colour':'mid' }
        self += VUMeter(self, 'left', scalers=(0.5, 1.0), align=('left', 'bottom'), annotate=ANNOTATE,\
                        pivot=-0.7, endstops=(3*PI/4, 5*PI/4), tick_pc=TICK_PC, peakmeter=False, needle=NEEDLE, marks=MARKS, arcs=ARCS)
        self += VUMeter(self, 'right', scalers=(0.5, 1.0), align=('right', 'bottom'), annotate=ANNOTATE,\
                        pivot=-0.7, endstops=(3*PI/4, 5*PI/4), tick_pc=TICK_PC, peakmeter=False, needle=NEEDLE, marks=MARKS, arcs=ARCS)

class VUMeterImageFrame(Frame):
    """ Image background based class - the """
    def __init__(self, parent, type=None, scalers=None, align=('centre', 'middle'),outline=None):
        Frame.__init__(self, parent, scalers=scalers, align=align)

        NEEDLE      = { 'width':3, 'colour': 'dark', 'length': 0.7, 'radius_pc': 0.7 }
        NEEDLE2     = { 'width':3, 'colour': 'mid', 'length': 0.8, 'radius_pc': 0.55 }
        NEEDLE3     = { 'width':3, 'colour': 'foreground', 'length': 0.7, 'radius_pc': 0.5 }
        NEEDLE4     = { 'width':4, 'colour': 'alert', 'length': 0.85, 'radius_pc': 0.75 }
        ENDSTOPS    = (3*PI/4, 5*PI/4)
        METERS      = { 'blueVU' : {'file': 'blue-bgr.png', 'needle':NEEDLE, 'endstops':ENDSTOPS, 'pivot':-0.49, 'theme':'blue'},
                        'goldVU' : {'file': 'gold-bgr.png', 'needle':NEEDLE2, 'endstops':ENDSTOPS, 'pivot':-0.35, 'theme':'white'},
                        'blackVU': {'file': 'black-white-bgr.png', 'needle':NEEDLE3, 'endstops':ENDSTOPS, 'pivot':-0.65, 'theme':'meter1'},
                        'rainVU' : {'file': 'rainbow-bgr.png', 'needle':NEEDLE4, 'endstops':ENDSTOPS, 'pivot':-0.75, 'theme':'meter1'},
                        'redVU'  : {'file': 'red-bgr.jpeg', 'needle':{ 'width':3, 'colour': 'dark', 'length': 0.8, 'radius_pc': 0.65 }, 'endstops':ENDSTOPS, 'pivot':-0.76, 'theme':'meter1'},
                        'vintVU' : {'file': 'vintage-bgr.jpeg', 'needle':{ 'width':3, 'colour': 'alert', 'length': 0.7, 'radius_pc': 0.8 }, 'endstops':ENDSTOPS, 'pivot':-0.6, 'theme':'meter1'},
                        'whiteVU': {'file': 'white-red-bgr.png', 'needle':{ 'width':2, 'colour': 'foreground', 'length': 0.75, 'radius_pc': 0.65 }, 'endstops':ENDSTOPS, 'pivot':-0.75, 'theme':'meter1'},
                        'greenVU': {'file': 'emerald-bgr.jpeg', 'needle':{ 'width':2, 'colour': 'foreground', 'length': 0.63, 'radius_pc': 0.60 }, 'endstops':ENDSTOPS, 'pivot':-0.6, 'theme':'meter1'} }

        # if the meter type does not exist then there will be a run time error
        # meter colour themes assume meter1
        meter = METERS[type]
        self += VUMeter(self, 'left', scalers=(0.5, 1.0), align=('left', 'bottom'), theme=meter['theme'],\
                        pivot=meter['pivot'], endstops=meter['endstops'], needle=meter['needle'], bgdimage=meter['file'],outline=outline)
        self += VUMeter(self, 'right', scalers=(0.5, 1.0), align=('left', 'bottom'), theme=meter['theme'],\
                        pivot=meter['pivot'], endstops=meter['endstops'], needle=meter['needle'], bgdimage=meter['file'],outline=outline)


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
    def __init__(self, parent, channel, scalers=None, align=None, barsize_pc=0.7, theme=None, flip=False, \
                    led_h=5, led_gap=1, peak_h=1, radius=0, barw_min=10, barw_max=400, tip=False, decay=VU.DECAY, orient='vert'):

        self.barw_min       = barw_min      # min widths
        self.barw_max       = barw_max      # max width
        self.orient         = orient   # Horz or vert bars
        self.parent         = parent

        Frame.__init__(self, parent, scalers=scalers, align=align)
        self.barw           = self.w * barsize_pc if orient == 'vert' else self.h * barsize_pc   # width of the bar
        box = (self.barw, self.h) if orient == 'vert' else (self.w, self.barw)
        self.bar = Bar(self, align=('centre', 'middle'), box_size=box, led_h=led_h, led_gap=led_gap, peak_h=peak_h, theme=theme, flip=flip, radius=radius, tip=tip, orient=orient)
        self.VU  = VU(self.platform, channel, decay)

        # print("VUFrame.__init__> box=%s, flip=%d, orient %s, frame> %s" % (box, flip, orient, self.geostr()))

    def update(self, full):
        height, peaks = self.VU.read()
        self.draw_background()
        self.bar.draw( 0, height, self.barw, peaks)
        


"""
Outline Frame - alternative is to use to the outline function within Frame
"""
class OutlineFrame(Frame):
    def __init__(self, parent, scalers=None, align=None, theme=None, width=4):
        Frame.__init__(self, parent, scalers=scalers, align=align)
        self.out     = Box(self, self.wh, width=width, theme=theme)
        self.parent  = parent
    # def __init__( self, platform, bounds, colour_index=0, theme='std', box=None, width=None, radius=5, align=('centre', 'middle') ):
    def update(self, full):
        self.out.draw( colour_index='foreground' )
        


"""
Spectrum Analyser Frames
"""
class Spectrum:
    DECAY     = 0.5   # Lower is longer delay - This is the amount that a bar reduces each period
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
        # print("Spectrum.__init__> Selected spectrum: octave spacing=1/%d, num octaves %d" % (self.spacing, len(self.octaves)))



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


class SpectrumFrame(Frame, Spectrum):
    """
    Creates a spectrum analyser of the width and octave interval specified
    intervals are 1, 3 or 6
    widths    are really half or whole screen
    - scale is used to determine how wide the frame is as a % of the parent frame
    - channel 'left' or 'right' selects the audio channel and screen alignment
    """

    def __init__(self, parent, channel, scalers=None, align=('left','bottom'), right_offset=0, theme=None, flip=False, \
                    led_h=5, led_gap=1, peak_h=1, radius=0, bar_space=0.5, barw_min=1, barw_max=20, tip=False, decay=Spectrum.DECAY, col_mode='vert'):

        self.channel        = channel
        self.right_offset   = right_offset
        self.parent         = parent
        self.col_mode       = col_mode

        Frame.__init__(self, parent, scalers=scalers, align=align, theme=theme)

        Spectrum.__init__(self, self.w, bar_space, barw_min, barw_max, decay=decay)
        self.bar = Bar(self, box_size=(self.width, self.h), led_h=led_h, led_gap=led_gap, peak_h=peak_h, flip=flip, radius=radius, tip=tip, col_mode=col_mode)

        # print("SpectrumFrame.__init__> Selected spectrum: max bars=%d, octave spacing=1/%d, num bars=%d, width=%d, gap=%d, flip=%d" % (self.max_bars, self.spacing, self.bars, self.barw, self.bar_gap, flip))

    def update(self, full):
        """
        Decay work by assuming that all bars naturally decay at a fixed rate and manner (eg lin /log)
        If the target height is less than the current height then, the decay continues
        If the target height is greater than the current, the height immediately increases - per smoothing algorithm
        This is intended to give a sharp peak response, but a slow delay
        """
        self.read(self.channel)
        self.draw_background()
        for i in range(len(self.current)):
            x = i * (self.barw + self.bar_gap)
            colour_index = x if self.col_mode == 'horz' else None
            self.bar.draw( x+self.right_offset, self.current[i].smoothed(), self.barw, self.peaks[i], colour_index=colour_index)
        

    @property
    def width(self):
        return self.bars * (self.bar_gap+self.barw)

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
    def __init__(self, parent, scalers, align) :
        Frame.__init__(self, parent, scalers=scalers, align=align)
        # def __init__(self, parent, channel, scale, V, H, right_offset=0, colour='white', noflip=1):
        self += SpectrumFrame(self, 'left', scalers=(0.5, 1.0), align=('left','bottom') )
        self += SpectrumFrame(self, 'right', scalers=(0.5, 1.0) , align=('right','bottom') )
        self.check()

class SpectrumStereoFrame(Frame): #""" Horz Split screen - right flipped 'Apple Style' """
    # THis is vertically aligned, with one flipped
    def __init__(self, parent, scalers, align) :
        Frame.__init__(self, parent, scalers=scalers, align=align)

        self += SpectrumFrame(self, 'right', scalers=(1.0, 0.5), align=('left','bottom'), flip=True, led_gap=2, peak_h=0, radius=2, theme='white', barw_min=10, bar_space=0.4)
        self += SpectrumFrame(self, 'left', scalers=(1.0, 0.5), align=('left','top'), flip=False, led_gap=2, peak_h=0,radius=2, theme='white', barw_min=10, bar_space=0.4)
        self.check()

class SpectrumStereoLRFrame(Frame): #""" Horz Split screen - LED Style right flipped  """
    # THis is vertically aligned, with one flipped
    def __init__(self, parent, scalers, align) :
        Frame.__init__(self, parent, scalers=scalers, align=align)

        self += SpectrumFrame(self, 'right', scalers=(1.0, 0.5), align=('left','bottom'), flip=True, led_gap=1, peak_h=1, radius=2, theme='white', barw_min=12 )
        self += SpectrumFrame(self, 'left', scalers=(1.0, 0.5), align=('left','top'), flip=False, led_gap=1, peak_h=1,radius=2, theme='white', barw_min=12 )
        self.check()

class SpectrumStereoSplitFrame(Frame): #""" Horz Split screen - right flipped """
    # This is vertically aligned
    def __init__(self, parent, scalers, align) :
        Frame.__init__(self, parent, scalers=scalers, align=align)
        self += SpectrumFrame(self, 'right', scalers=(1.0, 0.5), align=('left','bottom'), led_gap=0, flip=True, barw_min=5, bar_space=0.5, tip=True )
        self += SpectrumFrame(self, 'left', scalers=(1.0, 0.5), align=('left','top'), led_gap=0, barw_min=5, bar_space=0.5, tip=True )
        self.check()

class SpectrumStereoOffsetFrame(Frame):
    def __init__(self, parent, scalers, align) :
        Frame.__init__(self, parent, scalers=scalers, align=align)
        self += SpectrumFrame(self, 'right', scalers=(1.0, 1.0), align=('left','bottom'), right_offset=8, barw_min=8, bar_space=1.5, theme='red', led_gap=0, tip=True)
        self += SpectrumFrame(self, 'left', scalers=(1.0, 1.0), align=('left','bottom'), right_offset=0, barw_min=8, bar_space=1.5, theme='blue', led_gap=0, tip=True )
        self.check()

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

    def __init__(self, parent, channel, scalers=None, align=('left', 'bottom'), barsize_pc=1, theme='std', flip=False, \
                    led_h=5, led_gap=0, col_mode='horz', radius=0, barw_min=4, tip=True, decay=DECAY):

        Frame.__init__(self, parent, scalers=scalers, align=align)
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
        self.reduce_by      = OscilogrammeBar.FRAME//self.bars

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

    def update(self, full):
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
        


class Oscilogramme(Frame):
    """
    Draw a frame of samples - scaling the number of samples is the trick to align the frame rate and the sample rate
    """
    def __init__(self, parent, channel, scalers=None, align=('left', 'bottom'), theme=None):
        self.channel = channel
        Frame.__init__(self, parent, scalers=scalers, align=align, theme=theme)
        self.lines   = Line(self, circle=False, amp_scale=0.6)
        self.parent  = parent

    def update(self, full):
        samples =  self.platform.reduceSamples( self.channel, self.platform.framesize//self.w, rms=False )
        self.draw_background()
        self.lines.draw_mod_line(samples, colour_index='foreground')
        


class Octaviser(Frame, Spectrum):
    def __init__(self, parent, channel, scalers=None, align=('left', 'bottom'), theme=None):
        self.channel = channel
        Frame.__init__(self, parent, scalers=scalers, align=align)
        Spectrum.__init__(self, self.w, bar_space=5)
        self.num_octaves=len(self.octaves)
        self.arcs = ArcsOctaves(self.parent, theme='rainbow', NumOcts=self.num_octaves)
        self.parent  = parent

    def update(self, full):
        self.draw_background()
        fft = self.read(self.channel)

        for octave in range(1, self.num_octaves):
            self.arcs.draw(octave, fft[self.octaves[octave-1]:self.octaves[octave]])
            # print(bin, self.octaves[octave]) #, fft[bin:self.octaves[octave]])
        


class CircleModulator(Frame):
    def __init__(self, parent, channel, scalers=None, align=None, theme=None):
        self.channel = channel
        Frame.__init__(self, parent, scalers=scalers, align=align, theme=theme, square=False)

        self.lines   = Line(self, circle=True, radius=self.h/2, endstops=(0,2*PI), amp_scale=1.0)
        # self.ripples = Line(self, circle=True, radius=self.h/2, endstops=(0,2*PI), amp_scale=1.4)
        self.dots    = Dots(self, circle=True, radius=self.h/2, endstops=(0,2*PI), amp_scale=1.0)
        self.VU      = VU(self.platform, channel, decay=0.2)
        self.parent  = parent

        # print("VUFrame.__init__> box=%s, flip=%d, orient %s, frame> %s" % (box, flip, orient, self.geostr()))

    def update(self, full):

        hpf_freq = 1000
        lpf_freq = 1500
        self.draw_background()

        height, peaks = self.VU.read()
        samples = self.platform.reduceSamples( self.channel, self.platform.framesize//(self.w//2), rms=False )  # reduce the dataset quite a bit
        # high_samples = self.platform.filter( samples, hpf_freq, type='highpass' )
        low_samples = self.platform.filter( samples, lpf_freq, type='lowpass' )
        self.lines.draw_mod_line(low_samples, amplitude=0.5, gain=0.1, colour_index=height*self.h/2)
        self.dots.draw_mod_dots(low_samples, trigger=self.platform.trigger_detected, amplitude=0.1, gain=0.1, colour_index='alert')
        # self.ripples.draw_mod_ripples(low_samples, trigger=self.platform.trigger_detected, amplitude=height)
        


""" A visualiser based on a circle display of spectrum lines """
class Diamondiser(Frame, Spectrum):
    BARSPACE = 1
    def __init__(self, parent, channel, scalers=None, align=('left', 'bottom'), theme=None, bar_space=BARSPACE):
        Frame.__init__(self, parent, scalers=scalers, align=align, square=True, theme=theme)
        Spectrum.__init__(self, self.w, bar_space=bar_space, bandwidth=5000, decay=0.5)
        # self.VU          = VU(self.platform, channel, decay=0.2)

        self.channel     = channel
        self.max_radius  = self.h/2
        self.ray_angle   = 1/self.bars
        self.centre_pc   = 0.7
        self.parent      = parent

        self.rays        = [Line(self, endstops=(PI/2, 5*PI/2), width=bar_space*2, tick_pc=self.centre_pc, centre_offset=0, radius=self.max_radius, theme=theme, colour_index='mid') \
                             for _ in range(self.bars)]
        # print("Diamondiser.__init__>", self.bars, self.max_radius, self.geostr(), self.anglestr())

    def update(self, full, channel='left'):
        self.read(self.channel)
        radius  = self.centre_pc
        self.draw_background()
        for ray_index, ray in enumerate(self.rays):
            col = self.max_radius*(ray_index/self.bars)
            amp = radius*self.current[ray_index].smoothed() if self.current[ray_index].smoothed() > 0 else 0
            ray.drawFrameCentredVector(ray_index*self.ray_angle, amplitude=amp, gain=1-radius, colour_index=col)
        
