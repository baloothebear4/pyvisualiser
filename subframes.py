from framecore import Frame
from frames import VUFrame, TextFrame


class VU2chFrame(Frame):
    def __init__(self, parent, scalers=None, align=None, orient='vert', flip=False, led_h=5, led_gap=1,barsize_pc=0.7, theme=None):
        Frame.__init__(self, parent, scalers=scalers, align=align)
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