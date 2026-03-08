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
from pyvisualiser.core.framecore  import Frame, RowFramer, ColFramer
from pyvisualiser.visualisers.frames     import VUFrame, TextFrame, MetaData, PlayProgressFrame, SpectrumFrame, OscilogrammeBar, MetaImages, VUMeter
from pyvisualiser.styles.styles  import VUNeedleStyle, VUMeterStyle, VUMeterScale, OutlineStyle

PI = 3.14152
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
            self += VUFrame(self, 'left',  align=('centre','top'), scalers=(1.0, 0.5), orient=self.orient,flip=self.flip, background=self.background, **kwargs)
            self += VUFrame(self, 'right', align=('left','bottom'), scalers=(1.0, 0.5), orient=self.orient,flip=self.flip, background=self.background, **kwargs)
        else:     # Vertical
            self += VUFrame(self, 'left', align=('left','middle'), scalers=(0.5, 1.0), orient='vert',flip=self.flip,led_h=self.led_h, led_gap=self.led_gap,barsize_pc=self.barsize_pc, background=None, **kwargs)
            self += VUFrame(self, 'right', align=('right','bottom'), scalers=(0.5, 1.0), orient='vert',flip=self.flip,led_h=self.led_h, led_gap=self.led_gap,barsize_pc=self.barsize_pc, background=None, **kwargs)
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
            cols += VUFrame(cols, 'left', orient=self.orient,flip=flip[0], tip=False,led_h=led_h, **kwargs)
            cols += VUFrame(cols, 'right', orient=self.orient,flip=flip[1], tip=False,led_h=led_h, **kwargs)

        else:     # Vertical
            rows = RowFramer(self)
            rows += VUFrame(rows, 'left', orient='vert',flip=flip[0],theme=self.theme,led_h=led_h, **kwargs )
            rows += VUFrame(rows, 'right',orient='vert', flip=flip[1],theme=self.theme ,led_h=led_h, **kwargs)
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
            
        cols += VUFrame(cols, channel=channel, orient='horz', barsize_pc=0.8, tip=tip, **vu_kwargs)



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

class MetaDataFrame(Frame):
    SHOW = { 'track' : {'colour' : 'foreground', 'align': ('left','middle'), 'scalers': (1.0, 1.0)}, \
             'album' : {'colour' : 'mid',        'align': ('left','middle'), 'scalers': (1.0, 0.8)},  \
             'artist': {'colour' : 'mid',        'align': ('left','middle'), 'scalers': (1.0, 0.8) } }
             

    
    OUTLINE = { 'width' : 1, 'radius' : 0, 'colour' : 'dark'}

    def __init__(self, parent, tip=False, justify=('centre','middle'), background='background', **kwargs):
        super().__init__(parent, **kwargs)
        self.justify = justify

        OUT = None
        rows  = RowFramer(self, padding=0.00, background=background, row_ratios=(1.5,1,1,0.5),padpc=0.3     )
        rows += MetaData(rows, 'track', justify=self.justify,  colour  = 'foreground', background=None, outline=OUT)
        rows += MetaData(rows, 'album', justify=self.justify,  colour  = 'mid',background=None, outline=OUT)
        rows += MetaData(rows, 'artist', justify=self.justify, colour  = 'mid',background=None, outline=OUT) 
        rows += PlayProgressFrame(rows,background=None, outline=OUT)
        # rows.always_draw_background()

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

        self += SpectrumFrame(self,  'right', scalers=(1.0, 0.5), align=('left','top'), flip=False, led_gap=5, peak_h=3, radius=0, tip=False, barw_min=15, bar_space=0.5, **kwargs)
        self += SpectrumFrame(self,  'left', scalers=(1.0, 0.5), align=('left','bottom'), flip=True, led_gap=5, peak_h=3,radius=0, tip=False, barw_min=15, bar_space=0.5, **kwargs )


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
        Frame.__init__(self, parent, outline={'width':4,'colour':'light'}, **kwargs)

        rows = ColFramer(self, background='background', scalers=(0.7, 0.7), padding=10, outline={'width':4,'colour':'light'})
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



""" Complex VU Meters""" 

class VUMeterFrame1(Frame):
    """ Simple Meter with marks and scales  - based on frame width"""
    def __init__(self, parent, scalers=None, align=('centre', 'middle')):

        Frame.__init__(self, parent, scalers=scalers, align=align)
        style = VUMeterStyle(endstops=(3*PI/4-0.2, 5*PI/4+0.2), 
                             needle=VUNeedleStyle(width=4, colour='foreground', length=0.8, radius_pc=1.0),
                             scale=VUMeterScale(arcs={}))
        self += VUMeter(self, 'left', scalers=(0.5, 1.0), align=('left', 'bottom'), style=style)
        self += VUMeter(self, 'right', scalers=(0.5, 1.0), align=('right', 'bottom'), style=style)

class VUMeterFrame2(Frame):
    """ 180 degrees meter, centre rotate """

    def __init__(self, parent, scalers=None, align=('centre', 'middle')):
        Frame.__init__(self, parent, scalers=scalers, align=align)
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
        
        style = VUMeterStyle(endstops=(PI/2, 3*PI/2), pivot=-0.4, 
                             needle=VUNeedleStyle(width=4, colour='foreground', length=0.8, radius_pc=1.0),
                             scale=VUMeterScale(marks=MARKS, arcs=ARCS, annotate=ANNOTATE, 
                                                tick_width=TICK_W, tick_length=TICKLEN, tick_radius_pc=TICK_PC, scale_radius=SCALESLEN), 
                             show_peak=True)

        self += VUMeter(self, 'left', scalers=(0.5, 1.0), align=('left', 'bottom'), \
                        style=style)
        self += VUMeter(self, 'right', scalers=(0.5, 1.0), align=('right', 'bottom'), \
                        style=style)

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
        
        style = VUMeterStyle(pivot=0, endstops=(PI/4, 7*PI/4),
                             scale=VUMeterScale(marks=MARKS, arcs=ARCS, annotate=ANNOTATE, 
                                                tick_width=TICK_W))

        self += VUMeter(self, 'left', scalers=(0.5, 1.0), align=('left', 'bottom'), \
                        style=style)
        self += VUMeter(self, 'right', scalers=(0.5, 1.0), align=('right', 'bottom'), \
                        style=style)

class VUMeterFrame4(Frame):
    """120 degrees meter, low pivot """
    def __init__(self, parent, scalers=None, align=('centre', 'middle')):
        Frame.__init__(self, parent, scalers=scalers, align=align)
        TICK_W    = 3
        TICK_PC   = 0.2
        ARCLEN    = 0.8
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
        
        style = VUMeterStyle(pivot=-0.7, endstops=(3*PI/4, 5*PI/4), 
                             needle=VUNeedleStyle(width=4, colour='foreground', length=0.85, radius_pc=0.4),
                             scale=VUMeterScale(marks=MARKS, arcs=ARCS, annotate=ANNOTATE, 
                                                tick_width=TICK_W, tick_radius_pc=TICK_PC))

        self += VUMeter(self, 'left', scalers=(0.5, 1.0), align=('left', 'bottom'), \
                        style=style)
        self += VUMeter(self, 'right', scalers=(0.5, 1.0), align=('right', 'bottom'), \
                        style=style)

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
                        'greenVU': VUMeterStyle(texture_path='emerald-bgr.jpeg', needle=VUNeedleStyle(width=2, colour='foreground', length=0.63, radius_pc=0.60), endstops=ENDSTOPS, pivot=-0.6, theme='meter1') }

        # if the meter type does not exist then there will be a run time error
        # meter colour themes assume meter1
        style = METERS[type]
        outline = OutlineStyle(width=4, radius=10, colour='light', glow_intensity=0.1, softness=0.2)
        cols = ColFramer(self, padding=10, padpc=0.05)
        cols += VUMeter(cols, 'left', style=style, outline=outline)
        cols += VUMeter(cols, 'right', style=style, outline=outline)
