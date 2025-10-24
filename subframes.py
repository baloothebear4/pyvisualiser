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
from frames     import VUFrame, TextFrame, MetaData, PlayProgressFrame, SpectrumFrame, OscilogrammeBar, ArtistArtFrame, AlbumArtFrame


class VU2chFrame(Frame):
    def __init__(self, parent, scalers=None, align=None, orient='vert', flip=False, led_h=5, led_gap=1,barsize_pc=0.7, theme=None, outline=None,background=None):
        Frame.__init__(self, parent, scalers=scalers, align=align, theme=theme,outline=outline,background=background)
        # def VUVFrame(self, platform, bounds, channel, scalers=None, align=('left','bottom'), barsize_pc=0.7, theme='std', flip=False, \
        #                 led_h=5, led_gap=1, peak_h=1, col_mode='h', radius=0, barw_min=10, barw_max=200, tip=False, decay=DECAY):
        self.orient     = orient
        self.flip       = flip 
        self.led_h      = led_h
        self.led_gap    = led_gap
        self.barsize_pc = barsize_pc
        self.create()

    def create(self):
        if self.orient=='horz':
            self += VUFrame(self, 'left',  align=('centre','top'), scalers=(1.0, 0.5), orient=self.orient,flip=self.flip)
            self += VUFrame(self, 'right', align=('left','bottom'), scalers=(1.0, 0.5), orient=self.orient,flip=self.flip)
        else:     # Vertical
            self += VUFrame(self, 'left', align=('left','middle'), scalers=(0.5, 1.0), orient='vert',flip=self.flip,led_h=self.led_h, led_gap=self.led_gap,barsize_pc=self.barsize_pc)
            self += VUFrame(self, 'right', align=('right','bottom'), scalers=(0.5, 1.0), orient='vert',flip=self.flip,led_h=self.led_h, led_gap=self.led_gap,barsize_pc=self.barsize_pc)
        # self += OutlineFrame(self, display)

class VUFlipFrame(Frame):
    def __init__(self, parent, scalers=None, align=None, orient='vert', flip=False,theme=None, outline=None,background=None):
        Frame.__init__(self, parent, scalers=scalers, align=align, outline=outline,background=background, theme=theme)
        self.orient = orient
        self.create()

    def create(self):
        # def VUVFrame(self, platform, bounds, channel, scalers=None, align=('left','bottom'), barsize_pc=0.7, theme='std', flip=False, \
        #                 led_h=5, led_gap=1, peak_h=1, col_mode='h', radius=0, barw_min=10, barw_max=200, tip=False, decay=DECAY):
        if self.orient=='horz':
            self += VUFrame(self, 'left',  align=('left','middle'), scalers=(1.0, 0.5), orient=self.orient,flip=True, tip=False)
            self += VUFrame(self, 'right', align=('right','middle'), scalers=(1.0,0.5), orient=self.orient,flip=False, tip=False)
        else:     # Vertical
            self += VUFrame(self, 'left', align=('left','top'), scalers=(1.0, 0.5), orient='vert',flip=False,theme=self.theme )
            self += VUFrame(self, 'right', align=('left','bottom'), scalers=(1.0, 0.5), orient='vert',flip=True,theme=self.theme )



class VUHorzFrame(Frame):
    def __init__(self, parent, channel, scalers=None, align=None, tip=False,theme=None):
        Frame.__init__(self, parent, scalers=scalers, align=align, theme=theme)
        self.channel = channel
        self.tip     = tip
        self.create()

    def create(self):
        # def VUVFrame(self, platform, bounds, channel, scalers=None, align=('left','bottom'), barsize_pc=0.7, theme='std', flip=False, \
        #                 led_h=5, led_gap=1, peak_h=1, col_mode='h', radius=0, barw_min=10, barw_max=200, tip=False, decay=DECAY):
        self += VUFrame(self, self.channel, align=('right','middle'), scalers=(0.90, 0.8), orient='horz', barsize_pc=0.8, led_gap=0,tip=self.tip)
        # def __init__(self, parent, V, Y, text='Default Text', X=1.0, H='centre', fontmax=0):
        channel_text = ' L' if self.channel=='left' else ' R'
      # def __init__(self, parent, align=('centre', 'top'), scalers=None, text='Default Text', fontmax=0):
        self += TextFrame(self, align=('left', 'middle'), scalers=(0.1, 0.8), text=channel_text)


class VU2chHorzFrame(Frame):
    def __init__(self, parent, scalers=None, align=None,tip=False, theme=None):
        # def __init__(self, bounds, platform=None, display=None, scalers=[1.0,1.0], align=('left', 'bottom')):
        Frame.__init__(self, parent, scalers=scalers, align=align)
        self.tip =tip
        self.create()

    def create(self):
        # def VUVFrame(self, platform, bounds, channel, scalers=None, align=('left','bottom'), barsize_pc=0.7, theme='std', flip=False, \
        #                 led_h=5, led_gap=1, peak_h=1, col_mode='h', radius=0, barw_min=10, barw_max=200, tip=False, decay=DECAY):
        # self += VUHorzFrame(self, 'left',  scalers=(0.5,1.0), V='middle' , align=('left','middle'), flip=True )
        self += VUHorzFrame(self, 'left',  scalers=(1.0, 0.5), align=('left','top') ,tip=self.tip)
        self += VUHorzFrame(self, 'right', scalers=(1.0, 0.5), align=('left','bottom') ,tip=self.tip)
        # self += VUHorzFrame(self, 'right', scalers=(0.5,1.0), V='middle' , align=('left','middle') )


class MetaDataFrame(Frame):
    SHOW = { 'artist': {'colour' : 'foreground', 'align': ('centre','top'),    'scalers': (1.0, 1.0) }, \
             'track' : {'colour' : 'mid',        'align': ('centre','bottom'), 'scalers': (1.0, 0.8)}, \
             'album' : {'colour' : 'mid',        'align': ('centre','middle'), 'scalers': (1.0, 0.8)} }
    OUTLINE = { 'width' : 1, 'radius' : 0, 'colour_index' : 'dark'}

    def __init__(self, parent, scalers=None, align=None,tip=False, theme=None, justify='centre', outline=None):
        super().__init__(parent, scalers=scalers, align=align, theme=theme, outline=outline)
        self.justify = justify
        self.create()

    def create(self):  #reentrant so scaling works properly when sizing columns & rows
        # self.frames = []
        rows = RowFramer(self, padding=0.00)

        for meta, attributes in MetaDataFrame.SHOW.items():

            align = attributes['align'] if self.justify is None else (self.justify, attributes['align'][1])
            rows += MetaData(rows, meta, align = align, scalers = attributes['scalers'],colour  = attributes['colour'], theme=self.theme)

        rows += PlayProgressFrame(rows  , scalers=(1.0, 0.3), align=('centre','bottom'))

class ArtistMetaDataFrame(Frame):
    def __init__(self, parent, scalers=None, align=None,tip=False, theme=None, justify='centre'):
        super().__init__(parent, scalers=scalers, align=align, theme=theme)
        self.justify = justify
        self.create()

    def create(self):  #reentrant so scaling works properly when sizing columns & rows
        rows = RowFramer(self)
        rows += ArtistArtFrame(rows)
        rows += MetaDataFrame(rows)


class StereoSpectrumFrame(Frame):
    def __init__(self, parent, scalers=None, align=None,tip=False, theme=None):
        super().__init__(parent, scalers=scalers, align=align, theme=theme)
        self.create()

    def create(self):  #reentrant so scaling works properly when sizing columns & rows
        self += SpectrumFrame(self,  'right', scalers=(1.0, 0.5), align=('left','bottom'), flip=True, led_gap=5, peak_h=3, radius=0, tip=False, barw_min=15, bar_space=0.5)
        self += SpectrumFrame(self,  'left', scalers=(1.0, 0.5), align=('left','top'), flip=False, led_gap=5, peak_h=3,radius=0, tip=False, barw_min=15, bar_space=0.5 )


class MetaMiniSpectrumFrame(Frame):
    def __init__(self, parent, scalers=None, align=None,tip=False, theme=None, justify='centre'):
        super().__init__(parent, scalers=scalers, align=align, theme=theme)
        self.create()

    def create(self):  #reentrant so scaling works properly when sizing columns & rows
        rowframe    = RowFramer(self)
        rowframe   += MetaDataFrame(rowframe, scalers=(1.0, 1.0))
        rowframe   += SpectrumFrame(rowframe,'mono', scalers=(1.0, 0.3), align=('centre','bottom'), flip=False, led_gap=0, peak_h=1,radius=0, tip=False, barw_min=1, bar_space=2, col_mode='horz' )


class SamplesFrame(Frame):
    """ Volume/Source on left - Spectrum on left - one channel """
    def __init__(self, parent, scalers=(1.0, 1.0), align=('centre','middle'), theme='std'):
        Frame.__init__(self, parent, scalers=scalers, align=align)
        self.create()
        
    def create(self):
        self += OscilogrammeBar(self  ,  'left', scalers=(1.0,0.5), align=('left','top'), barsize_pc=0.5, led_gap=0,barw_min=2)
        self += OscilogrammeBar(self  ,  'right', scalers=(1.0,0.5), align=('left','bottom'), flip=True, barsize_pc=0.5, led_gap=0, barw_min=2)


