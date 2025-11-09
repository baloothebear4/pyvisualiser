#!/usr/bin/env python
"""
 All top level screens.  Screens are comprised of Frames

 Part of mVista preDAC2 project

 v3.0 Baloothebear4 Dec 2023
 v3.1 Baloothebear4 Oct 2025

Subframes are combinations of base frames that come together for easier formatting eg:
- Stereo VU meters
- Stereo Spectrum analysers
- Metadata layouts

"""
from framecore  import Frame, RowFramer, ColFramer
from frames     import VUFrame, TextFrame, MetaData, PlayProgressFrame, SpectrumFrame, OscilogrammeBar, MetaImages, VUMeter

PI = 3.14152
class VU2chFrame(Frame):
    def __init__(self, parent, scalers=None, align=None, orient='vert', flip=False, led_h=5, led_gap=1,barsize_pc=0.7, theme=None, outline=None,background={'colour':'background', 'per_frame_update':True}):
        Frame.__init__(self, parent, scalers=scalers, align=align, theme=theme,outline=outline,background=background)
        # def VUVFrame(self, platform, bounds, channel, scalers=None, align=('left','bottom'), barsize_pc=0.7, theme='std', flip=False, \
        #                 led_h=5, led_gap=1, peak_h=1, col_mode='h', radius=0, barw_min=10, barw_max=200, tip=False, decay=DECAY):
        self.orient     = orient
        self.flip       = flip 
        self.led_h      = led_h
        self.led_gap    = led_gap
        self.barsize_pc = barsize_pc
        self.background = background

        if self.orient=='horz':
            self += VUFrame(self, 'left',  align=('centre','top'), scalers=(1.0, 0.5), orient=self.orient,flip=self.flip, background=self.background)
            self += VUFrame(self, 'right', align=('left','bottom'), scalers=(1.0, 0.5), orient=self.orient,flip=self.flip, background=self.background)
        else:     # Vertical
            self += VUFrame(self, 'left', align=('left','middle'), scalers=(0.5, 1.0), orient='vert',flip=self.flip,led_h=self.led_h, led_gap=self.led_gap,barsize_pc=self.barsize_pc, background=self.background)
            self += VUFrame(self, 'right', align=('right','bottom'), scalers=(0.5, 1.0), orient='vert',flip=self.flip,led_h=self.led_h, led_gap=self.led_gap,barsize_pc=self.barsize_pc, background=self.background)
        self.always_draw_background()

class VUFlipFrame(Frame):
    def __init__(self, parent, scalers=None, align=None, orient='vert', flip=False,theme=None, outline=None,background={'colour':'background', 'per_frame_update':True}):
        Frame.__init__(self, parent, scalers=scalers, align=align, outline=outline,background=background, theme=theme)
        self.orient = orient

        # def VUVFrame(self, platform, bounds, channel, scalers=None, align=('left','bottom'), barsize_pc=0.7, theme='std', flip=False, \
        #                 led_h=5, led_gap=1, peak_h=1, col_mode='h', radius=0, barw_min=10, barw_max=200, tip=False, decay=DECAY):
        flip = (False, True) if flip else (True,False)
        if self.orient=='horz':
            cols = ColFramer(self)
            cols += VUFrame(cols, 'left', orient=self.orient,flip=flip[0], tip=False)
            cols += VUFrame(cols, 'right', orient=self.orient,flip=flip[1], tip=False)

        else:     # Vertical
            rows = RowFramer(self)
            rows += VUFrame(rows, 'left', orient='vert',flip=flip[0],theme=self.theme )
            rows += VUFrame(rows, 'right',orient='vert', flip=flip[1],theme=self.theme )
        self.always_draw_background()


class VUHorzFrame(Frame):
    def __init__(self, parent, channel, tip=False, **kwargs):
        self.kwargs  = kwargs
        self.parent  = parent
        self.channel = channel
        self.tip     = tip

        Frame.__init__(self, self.parent, background={'colour':'background', 'per_frame_update':False}, **self.kwargs)
        cols = ColFramer(self, col_ratios=(1,3))
        # cols = self
        channel_text = ' L' if self.channel=='left' else ' R'
        cols += TextFrame(cols, text=channel_text)
        cols += VUFrame(cols, channel=channel, orient='horz', barsize_pc=0.8, led_gap=0,tip=self.tip)



class VU2chHorzFrame(Frame):
    def __init__(self, parent, tip=False, **kwargs):
        self.tip =tip
        Frame.__init__(self, parent, **kwargs)
        # def VUVFrame(self, platform, bounds, channel, scalers=None, align=('left','bottom'), barsize_pc=0.7, theme='std', flip=False, \
        #                 led_h=5, led_gap=1, peak_h=1, col_mode='h', radius=0, barw_min=10, barw_max=200, tip=False, decay=DECAY):
        # self += VUHorzFrame(self, 'left',  scalers=(0.5,1.0), V='middle' , align=('left','middle'), flip=True )
        rows = RowFramer(self)
        rows += VUHorzFrame(rows, 'left' ,tip=self.tip)
        rows += VUHorzFrame(rows, 'right',tip=self.tip)
        # self += VUHorzFrame(self, 'right', scalers=(0.5,1.0), V='middle' , align=('left','middle') )
        # self.always_draw_background()

class MetaDataFrame(Frame):
    SHOW = { 'track' : {'colour' : 'foreground', 'align': ('left','middle'), 'scalers': (1.0, 1.0)}, \
             'album' : {'colour' : 'mid',        'align': ('left','middle'), 'scalers': (1.0, 0.8)},  \
             'artist': {'colour' : 'mid',        'align': ('left','middle'), 'scalers': (1.0, 0.8) } }
             

    
    OUTLINE = { 'width' : 1, 'radius' : 0, 'colour_index' : 'dark'}

    def __init__(self, parent, scalers=None, align=None,tip=False, theme=None, justify=('centre','top'), outline=None, background=None):
        super().__init__(parent, scalers=scalers, align=align, theme=theme, outline=outline, background=background)
        self.justify = justify

        rows  = RowFramer(self, padding=0.00, background=background) #row_ratios=(1.5,1,1,0.5)
        print("Metadata Frame RowFramer>", rows.geostr(), rows._scalers)
        rows += MetaData(rows, 'track', justify=self.justify,  colour  = 'foreground', background=background)
        rows += MetaData(rows, 'album', justify=self.justify,  colour  = 'mid', background=background)
        rows += MetaData(rows, 'artist', justify=self.justify, colour  = 'mid', background=background) 

        # for meta, attributes in MetaDataFrame.SHOW.items():
        #     print("**ad meta**", meta)
        #     rows += MetaData(rows, meta, justify=self.justify, colour  = attributes['colour'], theme=self.theme)

        # rows += PlayProgressFrame(rows)

class ArtistMetaDataFrame(Frame):
    def __init__(self, parent, scalers=None, align=None,tip=False, theme=None, justify='centre'):
        super().__init__(parent, scalers=scalers, align=align, theme=theme)
        self.justify = justify
        self.create()

    def create(self):  #reentrant so scaling works properly when sizing columns & rows
        rows = RowFramer(self)
        rows += MetaImages(rows)
        rows += MetaDataFrame(rows)


class StereoSpectrumFrame(Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.create()

    def create(self):  #reentrant so scaling works properly when sizing columns & rows
        self += SpectrumFrame(self,  'right', scalers=(1.0, 0.5), align=('left','top'), flip=True, led_gap=5, peak_h=3, radius=0, tip=False, barw_min=15, bar_space=0.5)
        self += SpectrumFrame(self,  'left', scalers=(1.0, 0.5), align=('left','bottom'), flip=False, led_gap=5, peak_h=3,radius=0, tip=False, barw_min=15, bar_space=0.5 )


class MetaMiniSpectrumFrame(Frame):
    def __init__(self, parent, justify='centre', **kwargs):
        super().__init__(parent, **kwargs)
        self.justify = justify
        self.create()

    def create(self):  #reentrant so scaling works properly when sizing columns & rows
        rowframe    = RowFramer(self)
        rowframe   += MetaDataFrame(rowframe, scalers=(1.0, 1.0), justify=self.justify)
        rowframe   += SpectrumFrame(rowframe,'mono', scalers=(1.0, 0.3), align=('centre','bottom'), flip=False, led_gap=0, peak_h=1,radius=0, tip=False, barw_min=1, bar_space=2, col_mode='horz' )


class SamplesFrame(Frame):
    """ Volume/Source on left - Spectrum on left - one channel """
    def __init__(self, parent, scalers=(1.0, 1.0), align=('centre','middle'), theme='std'):
        Frame.__init__(self, parent, scalers=scalers, align=align)
        self.create()
        
    def create(self):
        self += OscilogrammeBar(self  ,  'left', scalers=(1.0,0.5), align=('left','top'), barsize_pc=0.5, led_gap=0,barw_min=2)
        self += OscilogrammeBar(self  ,  'right', scalers=(1.0,0.5), align=('left','bottom'), flip=True, barsize_pc=0.5, led_gap=0, barw_min=2)


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
        Frame.__init__(self, parent, background='dark', outline={'width':4,'colour_index':'light'}, **kwargs)

        rows = ColFramer(self, background='background', scalers=(0.7, 0.7), padding=10, outline={'width':4,'colour_index':'light'})
        rows += SpectrumFrame(rows, 'left'  )
        rows += SpectrumFrame(rows, 'right' )
        rows.always_draw_background()
        

class SpectrumStereoFrame(Frame): #""" Horz Split screen - right flipped 'Apple Style' """
    # THis is vertically aligned, with one flipped
    def __init__(self, parent, scalers, align) :
        Frame.__init__(self, parent, scalers=scalers, align=align, background={'colour':'background', 'per_frame_update':True})

        self += SpectrumFrame(self, 'right', scalers=(1.0, 0.5), align=('left','bottom'), flip=True, led_gap=2, peak_h=0, radius=2, theme='white', barw_min=10, bar_space=0.4, background=None)
        self += SpectrumFrame(self, 'left', scalers=(1.0, 0.5), align=('left','top'), flip=False, led_gap=2, peak_h=0,radius=2, theme='white', barw_min=10, bar_space=0.4, background=None)
        

class SpectrumStereoLRFrame(Frame): #""" Horz Split screen - LED Style right flipped  """
    # THis is vertically aligned, with one flipped
    def __init__(self, parent, scalers, align) :
        Frame.__init__(self, parent, scalers=scalers, align=align)

        self += SpectrumFrame(self, 'right', scalers=(1.0, 0.5), align=('left','top'), flip=True, led_gap=1, peak_h=1, radius=2, theme='white', barw_min=12 )
        self += SpectrumFrame(self, 'left', scalers=(1.0, 0.5), align=('left','bottom'), flip=False, led_gap=1, peak_h=1,radius=2, theme='red', barw_min=12 )
        

class SpectrumStereoSplitFrame(Frame): #""" Horz Split screen - right flipped """
    # This is vertically aligned
    def __init__(self, parent, scalers, align) :
        Frame.__init__(self, parent, scalers=scalers, align=align, background={'colour':'background', 'per_frame_update':True})
        self += SpectrumFrame(self, 'right', scalers=(1.0, 0.5), align=('left','bottom'), led_gap=0, flip=True, barw_min=5, bar_space=0.5, tip=True )
        self += SpectrumFrame(self, 'left', scalers=(1.0, 0.5), align=('left','top'), led_gap=0, barw_min=5, bar_space=0.5, tip=True )
        

class SpectrumStereoOffsetFrame(Frame):
    def __init__(self, parent, scalers, align) :
        Frame.__init__(self, parent, scalers=scalers, align=align,background={'colour':'background', 'per_frame_update':True})
        self += SpectrumFrame(self, 'right', scalers=(1.0, 1.0), align=('left','top'), right_offset=2, barw_min=8, bar_space=1.5, theme='red', led_gap=0, tip=True, background=None)
        self += SpectrumFrame(self, 'left', scalers=(1.0, 1.0), align=('left','bottom'), right_offset=0, barw_min=8, bar_space=1.5, theme='blue', led_gap=0, tip=True,background=None )
        print(self)



""" Complex VU Meters""" 

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
    def __init__(self, parent, type=None, scalers=None, align=('centre', 'middle'),outline=None,square=False):
        Frame.__init__(self, parent, scalers=scalers, align=align, outline =outline,square=square)

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
