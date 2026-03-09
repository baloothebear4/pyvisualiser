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
from pyvisualiser.core.framecore            import Frame, RowFramer, ColFramer
from pyvisualiser.visualisers.frames        import TextFrame, MetaDataFrame, PlayProgressFrame, SpectrumFrame, OscilogrammeBar, MetaImages
from pyvisualiser.visualisers.vumeters      import VUFrame, VUMeter, VUMeterImageFrame
from pyvisualiser.styles.styles             import VUNeedleStyle, VUMeterStyle, VUMeterScale, OutlineStyle

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





