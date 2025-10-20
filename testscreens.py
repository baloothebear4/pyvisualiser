from framecore import Frame, ColFramer, RowFramer
from frames import  VUMeterImageFrame, Spectrum2chFrame, SpectrumStereoOffsetFrame, SpectrumStereoFrame, SpectrumStereoSplitFrame, SpectrumFrame, TextFrame
import time


""" VU Meters """
VUMETERS = ['blueVU', 'goldVU', 'blackVU', 'rainVU', 'redVU', 'vintVU', 'whiteVU', 'greenVU']

class VUImageScreen(Frame):
    """ VU meters left and right - based on an image background"""
    @property
    def title(self): return 'VU meters with image background'

    @property
    def type(self): return 'VU Image'

    def __init__(self, platform, type='blueVU'):

        Frame.__init__(self, platform)
        self += VUMeterImageFrame(self  , type=type, scalers=(0.5,0.5), align=('left','top'))



""" Spectrum Analyser based Screens """


# class SpectrumScreen(Frame):
#     """ Volume/Source on left - Spectrum on left - one channel """
#     def __init__(self, platform):
#         Frame.__init__(self, platform)
#         self += VolumeSourceFrame(self  , 0.2, 'right')
#         self += SpectrumFrame(self  , 'left', scalers=(0.8,1.0), align=('centre','middle'))
#         self.check()

class StereoSpectrumLRScreen(Frame):
    """ Volume/Source on left - Spectrum on left - one channel """
    def __init__(self, platform):
        Frame.__init__(self, platform)
        self += Spectrum2chFrame(self  , scalers=(1.0,1.0), align=('centre','middle'))
        self.check()

class FullSpectrumOffsetScreen(Frame):
    """ Volume/Source on left - Spectrum on left - one channel """
    def __init__(self, platform):
        Frame.__init__(self, platform)
        self += SpectrumStereoOffsetFrame(self  , scalers=(1.0,1.0), align=('centre','middle'))
        self.check()

class StereoSpectrumScreen(Frame):
    """ Volume/Source on left - Stereo Spectrum overlaid """
    def __init__(self, platform):
        Frame.__init__(self, platform)
        # self += VolumeSourceFrame(self  , 0.3, 'right')
        self += SpectrumStereoFrame(self  , scalers=(1.0,1.0), align=('centre','middle'))
        self.check()

class StereoSpectrumSplitScreen(Frame):
    """ Volume/Source on left - Stereo Spectrum overlaid """
    @property
    def title(self): return 'Full Spectrum Analyser, Roon Album Art, Metadata and progress bar'

    @property
    def type(self): return 'Test'
    
    def __init__(self, platform):
        Frame.__init__(self, platform)
        # self += VolumeSourceFrame(self  , 0.3, 'right')
        self += SpectrumStereoSplitFrame(self  , scalers=(1.0,1.0), align=('centre','middle'))
        self.check()

"""
    SpectrumFrame API:
    # def __init__(self, platform, bounds, channel, scale, align=('left','bottom'), right_offset=0, theme='std', flip=False, \
    #                 led_h=5, led_gap=1, peak_h=1, col_mode='h', radius=0, bar_space=0.5, barw_min=12, barw_max=20, tip=False, decay=DECAY):
"""
class MonoSpectrumScreen(Frame):
    """ Volume/Source on left - Stereo Spectrum overlaid """
    def __init__(self, platform):
        Frame.__init__(self, platform)
        # def __init__(self, platform, bounds, channel, scale, align=('left','bottom'), right_offset=0, colour='white'):
        self += SpectrumFrame(self  , 'left', scalers=(1.0, 1.0), led_gap=0, barw_min=2, tip=True)
        self.check()

class MonoSpectrumLEDScreen(Frame):
    """ Volume/Source on left - Stereo Spectrum overlaid """
    def __init__(self, platform):
        Frame.__init__(self, platform)
        # def __init__(self, platform, bounds, channel, scale, align=('left','bottom'), right_offset=0, colour='white'):
        self += SpectrumFrame(self  , 'left', scalers=(1.0, 1.0), peak_h=2, led_gap=2, led_h=4, barw_min=6, bar_space=0.2, theme='leds')
        self.check()

class MixedLEDScreen(Frame):
    """ Volume/Source on left - Stereo Spectrum overlaid """
    def __init__(self, platform):
        Frame.__init__(self, platform)
        # def __init__(self, platform, bounds, channel, scale, align=('left','bottom'), right_offset=0, colour='white'):
        self += SpectrumFrame(self  , 'right', scalers=(0.8, 1.0), align=('right','middle'), peak_h=2, led_gap=3, led_h=5, barw_min=6, bar_space=0.2, theme='leds')
        self += VU2chFrame(self  , scalers=(0.2, 1.0), align=('left','top'), orient='vert', flip=False, theme='leds', led_gap=3, led_h=5)






""" Horizontal VU bar meter """
class VUScreen(Frame):   # comprises volume on the left, spectrum on the right
    def __init__(self, platform):
        Frame.__init__(self, platform)
        # self += VolumeSourceFrame(self  , 0.4, 'right')
        # def __init__(self, platform, bounds, scalers, align=('left','bottom')):
        self += VU2chHorzFrame(self  , scalers=(1.0, 1.0), align=('centre', 'top'))
        self.check()

class VUVScreen(Frame):   # comprises volume on the left, spectrum on the right
    def __init__(self, platform):
        Frame.__init__(self, platform)
        # self += dbVolumeSourceFrame(self  , 0.5, 'right')
        # self += SpectrumFrame(self  , 'right', (0.7, 1.0), align=('right','middle'), led_gap=0, barw_min=2, tip=True)
        self += VU2chFrame(self  , scalers=(0.3, 0.5), align=('left','top'), orient='vert', flip=True)
        self += VUFlipFrame(self  , scalers=(0.5, 0.5), align=('right','bottom'), orient='vert', flip=True)
        self.check()

# class PlayerScreen(Frame):   # comprises volume on the left, spectrum on the right
#     def __init__(self, platform):
#         Frame.__init__(self, platform)
#         self += VolumeSourceFrame(self  , 0.2, 'right')
#         self += MetaDataFrame(self  , 0.8, 'left')
#         self.check()



"""
Test Code
"""

VUMETERS = ['blueVU', 'goldVU', 'blackVU', 'rainVU', 'redVU', 'vintVU', 'whiteVU', 'greenVU']
class TestVUImageScreen1(Frame):
    """ VU meters left and right - based on an image background"""
    @property
    def title(self): return 'Test multiple VU meters with image backgrounds'

    @property
    def type(self): return 'Test'

    def __init__(self, platform, type=None):

        Frame.__init__(self, platform)

        self += VUMeterImageFrame(self  , type='blueVU', scalers=(0.5,0.5), align=('left','top'))
        self += VUMeterImageFrame(self  , type='goldVU', scalers=(0.5,0.5), align=('left','bottom'))
        self += VUMeterImageFrame(self  , type='blackVU', scalers=(0.5,0.5), align=('right','top'))
        self += VUMeterImageFrame(self  , type='rainVU', scalers=(0.5,0.5), align=('right','bottom'))
        # self += VUMeterImageFrame(self  , type='redVU', scalers=(0.5,0.5), align=('left','top'))
        # self += VUMeterImageFrame(self  , type='vintVU', scalers=(0.5,0.5), align=('left','bottom'))
        # self += VUMeterImageFrame(self  , type='whiteVU', scalers=(0.5,0.5), align=('right','top'))
        # self += VUMeterImageFrame(self  , type='greenVU', scalers=(0.5,0.5), align=('right','bottom'))

class TestVUImageScreen2(Frame):
    """ VU meters left and right - based on an image background"""
    @property
    def title(self): return 'Test multiple VU meters with image backgrounds'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        # METERS = ['blueVU', 'goldVU', 'blackVU', 'rainVU', 'redVU', 'vintVU', 'whiteVU', 'greenVU']
        Frame.__init__(self, platform)

        # self += VUMeterImageFrame(self  , type='blueVU', scalers=(0.5,0.5), align=('left','top'))
        # self += VUMeterImageFrame(self  , type='goldVU', scalers=(0.5,0.5), align=('left','bottom'))
        # self += VUMeterImageFrame(self  , type='blackVU', scalers=(0.5,0.5), align=('right','top'))
        # self += VUMeterImageFrame(self  , type='rainVU', scalers=(0.5,0.5), align=('right','bottom'))
        self += VUMeterImageFrame(self  , type='redVU', scalers=(0.5,0.5), align=('left','top'))
        self += VUMeterImageFrame(self  , type='vintVU', scalers=(0.5,0.5), align=('left','bottom'))
        self += VUMeterImageFrame(self  , type='whiteVU', scalers=(0.5,0.5), align=('right','top'))
        self += VUMeterImageFrame(self  , type='greenVU', scalers=(0.5,0.5), align=('right','bottom'))

class TestVUMetersScreen(Frame):
    """ Vol/source in centre - VU meters left and right """
    @property
    def title(self): return 'Tests out multiple configurations of Stereo VU Meters'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        Frame.__init__(self, platform)

        self += VUMeterFrame1(self  , scalers=(0.5,0.5), align=('left','top'))
        self += VUMeterFrame2(self  , scalers=(0.5,0.5), align=('left','bottom'))
        self += VUMeterFrame3(self  ,  scalers=(0.5,0.5), align=('right','top'))
        self += VUMeterFrame4(self  ,  scalers=(0.5,0.5), align=('right','bottom'))

        # self += VolumeSourceFrame(self  , 0.2, 'centre'

class TestVisualiserScreen(Frame):   # comprises volume on the left, spectrum on the right
    @property
    def title(self): return 'Test multiple configurations of Visualisers'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        Frame.__init__(self, platform)
        self += OscilogrammeBar(self  , 'left', scalers=(1.0,0.5), align=('right','top'))
        self += OscilogrammeBar(self  , 'right', scalers=(1.0,0.5), align=('right','bottom'), flip=True)
        # self += Diamondiser(self  , 'right', (0.5,0.5), align=('left','top'))
        # # self += Octaviser(self  , 'right', (0.5,0.5), align=('left','bottom'))
        # self += CircleModulator(self  , 'left', (0.5,0.5), align=('right','top'))


class TestSpectrumScreen(Frame):   # comprises volume on the left, spectrum on the right
    @property
    def title(self): return 'Tests out multiple configurations of spectrum analysers'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        Frame.__init__(self, platform)
        self += SpectrumStereoSplitFrame(self  , scalers=(0.5,0.5), align=('left','top'))
        # self += Spectrum2chFrame(self  , (0.5,0.5), align=('left','top'))
        self += SpectrumStereoOffsetFrame(self  , scalers=(0.5,0.5), align=('left','bottom'))
        #
        self += SpectrumFrame(self  , 'left', scalers=(0.5,0.5), align=('right','top'), peak_h=2, led_gap=2, led_h=4, barw_min=6, bar_space=0.2, theme='leds')
        # #mono
        self += SpectrumFrame(self  , 'left', scalers=(0.5,0.5), align=('right','bottom'), led_gap=0, barw_min=2, tip=True)


class TestVUScreen(Frame):   # comprises volume on the left, spectrum on the right
    @property
    def title(self): return 'Tests out Bar VU meters of all types'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        Frame.__init__(self, platform)
        # self += VU2chFrame(self  , scalers=(0.2, 0.5), align=('left','top'), orient='vert')
        # self += VU2chFrame(self  , scalers=(0.2, 1.0), align=('left','bottom'), orient='vert', flip=False)
        self += VU2chFrame(self  ,  scalers=(0.25, 1.0), align=('left','top'), orient='vert', flip=False)
        self += VUFlipFrame(self  ,  scalers=(0.25, 1.0), align=('right','bottom'), orient='vert', flip=True)
        self += VU2chHorzFrame(self  ,  scalers=(0.5, 0.5), align=('centre','top'),tip=True)
        self += VUFlipFrame(self  ,  scalers=(0.5, 0.5), align=('centre','bottom'), orient='horz', flip=True)


class TestScreen(Frame):
    @property
    def title(self): return 'Tests out Frames, nesting and components'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        Frame.__init__(self, platform)
        subframe = Frame(self, scalers=(1.0,0.5), align=('centre','top'))
        self += SubFrame(self  , scalers=(0.5,0.3), align=('left','top'))
        self += SubFrame(self  , scalers=(0.5,0.3), align=('right','bottom'))
        self += TestFrame(self, scalers=(1.0, 0.25), align=('centre','middle'))
        self += TestFrame(self, scalers=(0.5, 0.3), align=('left','bottom'), run=True)
        # self += TextFrame(self,  scalers=(1.0,0.3), align=('centre','middle'), text='TextFrame')
        # self.box     += Box(self  , box=self.wh, width=0, align=('right','top'))
        # self += TextFrame(subframe,  scalers=(1.0,0.2), align=('centre','middle'), text='Very very very very very very very very very ery very very very very very very very very very very very very very very very very very very very very ery very very very very very very very very very very very very very very veryvery ery very very very very very very very very very long piece of text that really needs to wrap into multiple lines')

        
class TestBacks(Frame):
    @property
    def title(self): return 'Tests out outline Frames, light backs and Dots'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        Frame.__init__(self, platform, theme='ocean')
        self += CircleModulator(self, 'mono', scalers=(1.0,1.0), align=('centre','middle'))
        self += Lightback(self, scalers=(1.0,1.0), align=('right','top'), colour_index='mid')




class SubFrame(Frame):
    def __init__(self, parent, scalers, align):
        Frame.__init__(self, parent, scalers=scalers, align=align)
        # print("SubFrame> ", self.geostr())
        self += TestFrame(self  , scalers=(0.5, 0.3), align=('left','bottom'))
        self += TestFrame(self  , scalers=(0.5, 0.3), align=('centre','middle'))
        self += TestFrame(self  ,scalers=(0.5, 0.3), align=('right','top'))
        self += OutlineFrame(self  , scalers=(1.0, 1.0), align=('right','top'))

class TestFrame(Frame):
    """ A Frame is a box with coords relative to its enclosing Frame,
        on creation this creates the create, in the orientation and positioning withing the super-Frame
        componenets or subframes are added to this Frame
    """

    # def __init__(self, platform, bounds=None, display=None, scalers=[1.0,1.0], align=('left','bottom')):
    def __init__(self, parent, scalers, align, run=False):
        Frame.__init__(self, parent, scalers=scalers, align=align)
        # self.outline = Outline(self, platform)
        self.box     = Box(self  , box=self.wh, width=0, align=align)
        self.text    = TextFrame(self,  scalers=(1.0, 1.0), align=align, text=align[0]+align[1], reset=True, wrap=True)
        self.run = run
        # print("TestFrame.__init__>",  self.geostr())
        self.start_time = time.time()
        self.t=' very very very very very ery very very very very very very very very very very very very very very veryvery ery very very veryvery very very very very very long piece of text that really needs to wrap into multiple lines'


    def draw(self):
        # print("TestFrame.draw>")
        # self.outline.draw()
        self.box.draw( (0,0) )
        if self.run:
            self.text.draw(text=self.t)
            up = True
            if time.time() - self.start_time >= 0.2:
                self.start_time = time.time()
                # if up:
                #     self.t += 'Very very very'
                #     up == len(self.t)<100
                # else:
                self.t = self.t[3:]
        else:
            self.text.draw()

class ColAlignedScreen(Frame):
    @property
    def title(self): return 'ColAlignedScreen> Creates 3 box frames and aligns them horizontally, evenly'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        super().__init__(platform, theme='hifi')
        # print("SubFrame> ", self.geostr())
        self.create()

    def create(self):
        

        colframe = ColFramer(self, scalers=(1.0,1.0), align=('left','middle'), background='dark', padding=0.0) #, align=('centre','middle'))
        # print("ColAlignedScreen.create> colframe", colframe.framestr())
        colframe += TextFrame(colframe  , text='left', scalers=(1.0, 1.0), background='light', outline={'colour_index':'alert'})
        colframe += TextFrame(colframe  , text='mid', background='mid')
        # colframe += Frame(colframe  ,  scalers=(1.0, 0.3), align=('left','top'), background='foreground')

        rowframe = RowFramer(colframe  ,  scalers=(0.5,1.0), align=('right','middle'), background='dark', padding=0.0)
        # print("ColAlignedScreen.create> rowframe", rowframe.framestr())
        rowframe += Frame(rowframe  ,   scalers=(1.0,1.0), background='mid')
        rowframe += TextFrame(rowframe  , text='rhs', background='light', outline={'colour_index':'alert'})
        rowframe += Frame(rowframe  ,  scalers=(1.0, 1.0), background='foreground')

        # self += Frame(self  ,  scalers=(0.3, 0.3), align=('right','top'), background='foreground')

        # print("ColAlignedScreen.create")

        # self += TestFrame(self  , scalers=(0.5, 0.3), align=('left','bottom'))
        # self += TestFrame(self  , scalers=(0.5, 0.3), align=('centre','middle'))
        # self += TestFrame(self  ,scalers=(0.5, 0.3), align=('right','top'))
        # self += OutlineFrame(self  , scalers=(1.0, 1.0), align=('right','top'))            