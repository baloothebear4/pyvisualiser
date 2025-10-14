from framecore import Frame, RowFramer, ColFramer
from frames import VUFrame, TextFrame, MetaData,PlayProgressFrame, SpectrumFrame


class VU2chFrame(Frame):
    def __init__(self, parent, scalers=None, align=None, orient='vert', flip=False, led_h=5, led_gap=1,barsize_pc=0.7, theme=None):
        Frame.__init__(self, parent, scalers=scalers, align=align, theme='std')
        # def VUVFrame(self, platform, bounds, channel, scalers=None, align=('left','bottom'), barsize_pc=0.7, theme='std', flip=False, \
        #                 led_h=5, led_gap=1, peak_h=1, col_mode='h', radius=0, barw_min=10, barw_max=200, tip=False, decay=DECAY):
        if orient=='horz':
            self += VUFrame(self, 'left',  align=('centre','top'), scalers=(1.0, 0.5), orient=orient,flip=flip,  )
            self += VUFrame(self, 'right', align=('left','bottom'), scalers=(1.0, 0.5), orient=orient,flip=flip )
        else:     # Vertical
            self += VUFrame(self, 'left', align=('left','middle'), scalers=(0.5, 1.0), orient='vert',flip=flip,led_h=led_h, led_gap=led_gap,barsize_pc=barsize_pc, theme=theme )
            self += VUFrame(self, 'right', align=('right','bottom'), scalers=(0.5, 1.0), orient='vert',flip=flip,led_h=led_h, led_gap=led_gap,barsize_pc=barsize_pc, theme=theme )
        # self += OutlineFrame(self, display)
        self.check()

class VUFlipFrame(Frame):
    def __init__(self, parent, scalers=None, align=None, orient='vert', flip=False,theme=None):
        Frame.__init__(self, parent, scalers=scalers, align=align)
        # def VUVFrame(self, platform, bounds, channel, scalers=None, align=('left','bottom'), barsize_pc=0.7, theme='std', flip=False, \
        #                 led_h=5, led_gap=1, peak_h=1, col_mode='h', radius=0, barw_min=10, barw_max=200, tip=False, decay=DECAY):
        if orient=='horz':
            self += VUFrame(self, 'left',  align=('left','middle'), scalers=(0.5, 0.5), orient=orient,flip=True, tip=False,theme=theme )
            self += VUFrame(self, 'right', align=('right','middle'), scalers=(0.5,0.5), orient=orient,flip=False, tip=False,theme=theme )
        else:     # Vertical
            self += VUFrame(self, 'left', align=('left','top'), scalers=(0.5, 0.5), orient='vert',flip=False,theme=theme )
            self += VUFrame(self, 'right', align=('left','bottom'), scalers=(0.5, 0.5), orient='vert',flip=True,theme=theme )
        # self += OutlineFrame(self, display)
        self.check()


class VUHorzFrame(Frame):
    def __init__(self, parent, channel, scalers=None, align=None, tip=False,theme=None):
        Frame.__init__(self, parent, scalers=scalers, align=align, theme=theme)
        # def VUVFrame(self, platform, bounds, channel, scalers=None, align=('left','bottom'), barsize_pc=0.7, theme='std', flip=False, \
        #                 led_h=5, led_gap=1, peak_h=1, col_mode='h', radius=0, barw_min=10, barw_max=200, tip=False, decay=DECAY):
        self += VUFrame(self, channel, align=('right','middle'), scalers=(0.90, 0.8), orient='horz', barsize_pc=0.8, led_gap=0,tip=tip, theme=theme )
        # def __init__(self, parent, V, Y, text='Default Text', X=1.0, H='centre', fontmax=0):
        channel_text = ' L' if channel=='left' else ' R'
      # def __init__(self, parent, align=('centre', 'top'), scalers=None, text='Default Text', fontmax=0):
        self += TextFrame(self, align=('left', 'middle'), scalers=(0.1, 0.8), text=channel_text, theme=theme)

class VU2chHorzFrame(Frame):
    def __init__(self, parent, scalers=None, align=None,tip=False, theme=None):
        # def __init__(self, bounds, platform=None, display=None, scalers=[1.0,1.0], align=('left', 'bottom')):
        Frame.__init__(self, parent, scalers=scalers, align=align)
        # def VUVFrame(self, platform, bounds, channel, scalers=None, align=('left','bottom'), barsize_pc=0.7, theme='std', flip=False, \
        #                 led_h=5, led_gap=1, peak_h=1, col_mode='h', radius=0, barw_min=10, barw_max=200, tip=False, decay=DECAY):
        # self += VUHorzFrame(self, 'left',  scalers=(0.5,1.0), V='middle' , align=('left','middle'), flip=True )
        self += VUHorzFrame(self, 'left',  scalers=(1.0, 0.5), align=('left','top') ,tip=tip, theme=theme )
        self += VUHorzFrame(self, 'right', scalers=(1.0, 0.5), align=('left','bottom') ,tip=tip, theme=theme )
        # self += VUHorzFrame(self, 'right', scalers=(0.5,1.0), V='middle' , align=('left','middle') )

class MetaDataFrame(Frame):
    SHOW = {'track': {'colour':'foreground', 'align': ('centre','middle'), 'scalers': (1.0, 1.0) }, \
            'artist': {'colour':'mid', 'align': ('centre','middle'), 'scalers' : (1.0, 0.7) }, \
            'album': {'colour':'mid', 'align': ('centre','middle'), 'scalers' : (1.0, 0.7) } }    

    def __init__(self, parent, scalers=None, align=None,tip=False, theme=None, justify='centre'):
        super().__init__(parent, scalers=scalers, align=align, theme=theme)
        self.justify = justify
        self.create()

    def create(self):  #reentrant so scaling works properly when sizing columns & rows
        # self.frames = []
        rows = RowFramer(self, padding=0.00)

        for meta, attributes in MetaDataFrame.SHOW.items():

            align = attributes['align'] if self.justify is None else (self.justify, attributes['align'][1])
            # print(meta, attributes, align)
            rows += MetaData(rows, meta, align = align, scalers = attributes['scalers'],colour  = attributes['colour'], theme=self.theme)

        # rows += SpectrumFrame(rows,'mono', scalers=(1.0, 0.5), align=('centre','bottom'), flip=False, led_gap=0, peak_h=1,radius=0, tip=False, barw_min=1, bar_space=2, col_mode='horz' )
        rows += PlayProgressFrame(rows  , scalers=(1.0, 0.3), align=('centre','bottom'))

class StereoSpectrumFrame(Frame):
    def __init__(self, parent, scalers=None, align=None,tip=False, theme=None, justify='centre'):
        super().__init__(parent, scalers=scalers, align=align, theme=theme)
        self.create()

    def create(self):  #reentrant so scaling works properly when sizing columns & rows
        # self.frames = []
 
        self += SpectrumFrame(self,  'right', scalers=(1.0, 0.5), align=('left','bottom'), flip=True, led_gap=5, peak_h=3, radius=0, tip=False, barw_min=15, bar_space=0.5)
        self += SpectrumFrame(self,  'left', scalers=(1.0, 0.5), align=('left','top'), flip=False, led_gap=5, peak_h=3,radius=0, tip=False, barw_min=15, bar_space=0.5 )

class MetaMiniSpectrumFrame(Frame):
    def __init__(self, parent, scalers=None, align=None,tip=False, theme=None, justify='centre'):
        super().__init__(parent, scalers=scalers, align=align, theme=theme)
        self.create()

    def create(self):  #reentrant so scaling works properly when sizing columns & rows
        # self.frames = []

        rowframe    = RowFramer(self)
        rowframe   += MetaDataFrame(rowframe, scalers=(1.0, 1.0))
        rowframe   += SpectrumFrame(rowframe,'mono', scalers=(1.0, 0.3), align=('centre','bottom'), flip=False, led_gap=0, peak_h=1,radius=0, tip=False, barw_min=1, bar_space=2, col_mode='horz' )