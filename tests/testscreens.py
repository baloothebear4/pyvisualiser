from pyvisualiser import *
from pyvisualiser.styles.presets import *





""" Spectrum Analyser based Screens """


# class SpectrumScreen(Frame):
#     """ Volume/Source on left - Spectrum on left - one channel """
#     def __init__(self, platform):
#         Frame.__init__(self, platform)
#         self += VolumeSourceFrame(self  , 0.2, 'right')
#         self += SpectrumFrame(self  , 'left', scalers=(0.8,1.0), align=('centre','middle'))
# 

class StereoSpectrumLRScreen(Frame):
    """ Volume/Source on left - Spectrum on left - one channel """
    def __init__(self, platform):
        Frame.__init__(self, platform, theme='hifi', background='background')
        self += Spectrum2chFrame(self, padding=30)


class FullSpectrumOffsetScreen(Frame):
    """ Volume/Source on left - Spectrum on left - one channel """
    def __init__(self, platform):
        Frame.__init__(self, platform, background=None)
        self += SpectrumStereoOffsetFrame(self  , scalers=(1.0,1.0), align=('centre','middle'))


class StereoSpectrumScreen(Frame):
    """ Volume/Source on left - Stereo Spectrum overlaid """
    def __init__(self, platform):
        Frame.__init__(self, platform)
        # self += VolumeSourceFrame(self  , 0.3, 'right')
        self += SpectrumStereoFrame(self  , scalers=(1.0,1.0), align=('centre','middle'))


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
        self.always_draw_background()

class MonoSpectrumLEDScreen(Frame):
    """ Volume/Source on left - Stereo Spectrum overlaid """
    def __init__(self, platform):
        Frame.__init__(self, platform, outline={'width':5,'colour':'alert'}, theme='hifi', padding=30, background='background')
        # def __init__(self, platform, bounds, channel, scale, align=('left','bottom'), right_offset=0, colour='white'):
        col = ColFramer(self)
        col += SpectrumFrame(col  , 'mono', scalers=(1.0, 1.0), peak_h=2, led_gap=3, led_h=4, barw_min=6, bar_space=0.2, background='dark')
        self.always_draw_background()


class MixedLEDScreen(Frame):
    """ Volume/Source on left - Stereo Spectrum overlaid """
    def __init__(self, platform):
        Frame.__init__(self, platform, padding=50, background='dark', outline={'width':2,'colour':'alert'}, theme='hifi')
        # def __init__(self, platform, bounds, channel, scale, align=('left','bottom'), right_offset=0, colour='white'):
        cols = ColFramer(self, col_ratios=(4,1), background={'colour':'dark','opacity':20}, padding=0, outline={'width':4,'colour':'mid'})
        cols += SpectrumFrame(cols, 'mono', peak_h=2, led_gap=3, led_h=5, barw_min=6, bar_space=0.2, theme='leds')
        cols += VU2chFrame(cols, orient='vert', flip=False, led_gap=3, led_h=5, background=None)
        self.always_draw_background()


""" Horizontal VU bar meter """
class VUScreen(Frame):   # comprises volume on the left, spectrum on the right
    def __init__(self, platform):
        background={'image':'stream.png','opacity':150, 'per_frame_update':True}
        Frame.__init__(self, platform,background='background')
        # self += VolumeSourceFrame(self  , 0.4, 'right')
        self += VU2chHorzFrame(self,background=background,     # --- Add these extreme values ---
            bloom_threshold=0.6,      # Bloom will start almost immediately
            bloom_intensity=3.0,     # Bloom will be 10x the size of the LED
            bloom_softness=0.9        # Bloom will be very diffuse)
        )

class VUVScreen(Frame):   # comprises volume on the left, spectrum on the right
    def __init__(self, platform):
        back = {'colour':'background', 'per_frame_update':True}
        Frame.__init__(self, platform, background=back)

        # self += dbVolumeSourceFrame(self  , 0.5, 'right')
        # self += SpectrumFrame(self  , 'right', (0.7, 1.0), align=('right','middle'), led_gap=0, barw_min=2, tip=True)

        #  segment_size=5, segment_gap=1, corner_radius=0, edge_softness=0.05, \
        #  intensity_threshold=0.8, intensity_scale=2.0, intensity_blur=0.7, intensity_alpha=20, \

        cols = ColFramer(self)
        rows = RowFramer(cols)
        rows += VU2chFrame(rows, orient='horz', flip=True)
        rows += VU2chFrame(rows, orient='horz', flip=False)
        row1 = RowFramer(cols)
        row1 += VU2chFrame(row1, orient='vert', flip=True, segment_size=5, segment_gap=4, corner_radius=4, edge_softness=0.05)
        row1 += VU2chFrame(row1, orient='vert', flip=False,segment_size=5, segment_gap=4, corner_radius=4, edge_softness=0.05)
        row2 = RowFramer(cols)
        row2 += VUFlipFrame(row2, orient='horz', flip=True,led_h=5, led_gap=5,barsize_pc=0.7,intensity_threshold=0.6, intensity_scale=2.0, intensity_blur=0.7, intensity_alpha=80)
        row2 += VUFlipFrame(row2, orient='horz', flip=False,led_h=5, led_gap=5,barsize_pc=0.7,intensity_threshold=0.6, intensity_scale=2.0, intensity_blur=0.7, intensity_alpha=80)
        row3 = RowFramer(cols)
        row3 += VUFlipFrame(row3, orient='vert', flip=True,led_h=5, segment_size=10, segment_gap=1, corner_radius=0, edge_softness=0.05)
        row3 += VUFlipFrame(row3, orient='vert', flip=False,led_h=5, segment_size=10, segment_gap=1, corner_radius=0, edge_softness=0.05)        


# class PlayerScreen(Frame):   # comprises volume on the left, spectrum on the right
#     def __init__(self, platform):
#         Frame.__init__(self, platform)
#         self += VolumeSourceFrame(self  , 0.2, 'right')
#         self += MetaDataFrame(self  , 0.8, 'left')
# 



"""
Test Code
"""


class TestVisualiserScreen(Frame):   # comprises volume on the left, spectrum on the right
    @property
    def title(self): return 'Test multiple configurations of Visualisers'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        back = {'colour':'background', 'per_frame_update':True}
        Frame.__init__(self, platform,background=back)

        self += OscilogrammeBar(self  , 'left', scalers=(1.0,0.5), align=('right','top') )
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
        Frame.__init__(self, platform, background={'colour':'background', 'per_frame_update':True})
        self += SpectrumStereoSplitFrame(self  , scalers=(0.5,0.5), align=('left','top'))
        # self += Spectrum2chFrame(self  , (0.5,0.5), align=('left','top'))
        self += SpectrumStereoOffsetFrame(self  , scalers=(0.5,0.5), align=('left','bottom'))
        back = {'colour':'background', 'per_frame_update':False}
        self += SpectrumFrame(self  , 'left', scalers=(0.5,0.5), align=('right','top'), peak_h=2, led_gap=2, led_h=4, barw_min=6, bar_space=0.2, theme='leds', background=back)
        # #mono
        self += SpectrumFrame(self  , 'left', scalers=(0.5,0.5), align=('right','bottom'), led_gap=0, barw_min=2, tip=True, background=back)


class TestVUScreen(Frame):   # comprises volume on the left, spectrum on the right
    @property
    def title(self): return 'Tests out Bar VU meters of all types'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        back = {'colour':'background', 'per_frame_update':True}
        Frame.__init__(self, platform, background=back)
        # self += VU2chFrame(self  , scalers=(0.2, 0.5), align=('left','top'), orient='vert')
        # self += VU2chFrame(self  , scalers=(0.2, 1.0), align=('left','bottom'), orient='vert', flip=False)
        self += VU2chFrame(self  ,  scalers=(0.25, 1.0), align=('left','top'), orient='vert', flip=False)
        self += VUFlipFrame(self  ,  scalers=(0.25, 1.0), align=('right','bottom'), orient='vert', flip=True)
        self += VU2chHorzFrame(self  ,  scalers=(0.5, 0.5), align=('centre','top'),tip=True)
        self += VUFlipFrame(self  ,  scalers=(0.5, 0.5), align=('centre','bottom'), orient='horz', flip=False)

class TrackVUMeterScreen2(Frame):   # comprises volume on the left, spectrum on the right
    @property
    def title(self): return 'Analogue VU Meters, Roon Album Art, Metadata and progress bar'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        back = {'image':'artist', 'per_frame_update':False, 'opacity': 100}
        Frame.__init__(self, platform, background=back, theme= 'meter1', padding=30)
  
        NEEDLE    = { 'width':4, 'colour': 'foreground', 'length': 0.8, 'radius_pc': 1.0 }
        ENDSTOPS  = (3*PI/4, 5*PI/4)  #Position of endstop if not the edge of the frame
        PIVOT     = -0.5
        OUTLINE   = {'colour':'foreground', 'width':5, 'opacity': 255, 'radius': 10}
        BACK      = {'colour':'background', 'opacity':150, 'per_frame_update':True}
        # self += MetaImages(self  , (0.25, 0.93),align=('right','middle'))
        # self += MetaImages(self  , (0.3, 0.3),align=('centre','top'))
        # self += MetaDataFrame(self  , scalers=(0.3, 1.0), align=('centre','middle'))
        # # self += MetaImages(self  , scalers=(1.0,1.0),align=('centre','middle'), opacity=40)
        # # self += PlayProgressFrame(self  , scalers=(0.3, 0.05), align=('centre','bottom'))
        # self += VUMeter(self  ,  'left', scalers=(0.3, 0.9), align=('left','top'), pivot=PIVOT, arcs={}, endstops=ENDSTOPS, needle=NEEDLE,outline=OUTLINE) #, background='mid')
        # self += VUMeter(self  ,  'right', scalers=(0.3, 0.9), align=('right','top'), pivot=PIVOT, arcs={}, endstops=ENDSTOPS, needle=NEEDLE,outline=OUTLINE) #,background='mid')
        cols = ColFramer(self, background={'colour':None,'per_frame_update':True})
        cols += VUMeter(cols  ,  'left', square=False, pivot=PIVOT, arcs={}, endstops=ENDSTOPS, needle=NEEDLE,outline=OUTLINE, background=BACK)
        cols += MetaDataFrame(cols,padding=2, background=BACK)#,outline=OUTLINE)
        cols += VUMeter(cols  ,  'right', square=False, pivot=PIVOT, arcs={}, endstops=ENDSTOPS, needle=NEEDLE,outline=OUTLINE, background=BACK)



#------------ Image Test screens --------------
class ImageTestScreen(Frame):
    @property
    def title(self): return 'ArtTestScreen> aligns Album art and Artist Art'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        super().__init__(platform, theme='hifi', outline={'width':20,'colour':'alert'}, padding=2)

        rows = RowFramer(self, row_ratios=(1,1), padding=20)
        colframe = ColFramer(rows, col_ratios =(1,1,2), background='mid', padpc=0, padding=0, outline={'colour':'alert','width':5}) #, align=('centre','middle'))

        colframe += MetaImages(colframe,  art_type='album',  opacity=255, outline={'colour':'alert','width':1}, reflection=True)
        colframe += TextFrame(colframe  , text='Test Art', background='light', outline={'colour':'alert','width':2})
        colframe += MetaImages(colframe,  art_type='artist',  opacity=190, outline={'colour':'alert','width':1},reflection={'size': 0.4, 'opacity': 0.3})

class ReflectionTestScreen(Frame):
    @property
    def title(self): return 'Reflection Test Screen'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        super().__init__(platform, theme='hifi', background={'image': 'particles.jpg', 'opacity': 100})
        
        cols = ColFramer(self, col_ratios=(1, 1, 1), padding=20)
        
        # Column 1: Default Reflection
        col1 = RowFramer(cols, row_ratios=(5, 1))
        col1 += MetaImages(col1, art_type='album', reflection=True, outline={'colour':'light', 'width':2}, z_order=1)
        col1 += TextFrame(col1, text="Default", align=('centre', 'middle'))

        # Column 2: Strong Reflection
        col2 = RowFramer(cols, row_ratios=(5, 1))
        col2 += MetaImages(col2, art_type='artist', reflection={'size': 0.5, 'opacity': 0.7}, outline={'colour':'alert', 'width':2}, z_order=1)
        col2 += TextFrame(col2, text="Strong", align=('centre', 'middle'))

        # Column 3: Subtle Reflection
        col3 = RowFramer(cols, row_ratios=(5, 1))
        col3 += MetaImages(col3, art_type='album', reflection={'size': 0.2, 'opacity': 0.2}, outline={'colour':'mid', 'width':2}, z_order=1)
        col3 += TextFrame(col3, text="Subtle", align=('centre', 'middle'))

class IntensityTestScreen(Frame):
    @property
    def title(self): return 'Intensity Test Screen'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        super().__init__(platform, theme='hifi', background={'image': 'particles.jpg', 'opacity': 100})
        
        rows = RowFramer(self, padding=20, padpc=0.3)
        
        # 1. Default
        r1 = ColFramer(rows, col_ratios=(1, 3))
        r1 += TextFrame(r1, text="Default", align=('right', 'middle'))
        r1 += VU2chHorzFrame(r1)

        # 2. High Sensitivity (Threshold 0.1)
        r2 = ColFramer(rows, col_ratios=(1, 3))
        r2 += TextFrame(r2, text="High Sensitivity", align=('right', 'middle'))
        r2 += VU2chHorzFrame(r2, intensity_threshold=0.1)

        # 3. High Intensity (Scale 4.0, Alpha 100)
        r3 = ColFramer(rows, col_ratios=(1, 3))
        r3 += TextFrame(r3, text="High Intensity", align=('right', 'middle'))
        r3 += VU2chHorzFrame(r3, intensity_threshold=0.5, intensity_scale=4.0, intensity_alpha=100,intensity_blur=100.0)

        # 4. Sharp Glow (Blur 0.0)
        r4 = ColFramer(rows, col_ratios=(1, 3))
        r4 += TextFrame(r4, text="Sharp Glow", align=('right', 'middle'))
        r4 += VU2chHorzFrame(r4, intensity_threshold=0.5, intensity_blur=10.0, intensity_alpha=130)

class BarParametersTestScreen(Frame):
    @property
    def title(self): return 'Bar Parameters Test Screen'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        super().__init__(platform, theme='hifi', background={'image': 'particles.jpg', 'opacity': 100})
        
        rows = RowFramer(self, row_ratios=(1, 1, 1, 1), padding=20)
        
        # 1. Default
        r1 = ColFramer(rows, col_ratios=(1, 3))
        r1 += TextFrame(r1, text="Default", align=('right', 'middle'))
        r1 += VU2chHorzFrame(r1)

        # 2. Blocky (Retro)
        r2 = ColFramer(rows, col_ratios=(1, 3))
        r2 += TextFrame(r2, text="Blocky (Retro)", align=('right', 'middle'))
        r2 += VU2chHorzFrame(r2, segment_size=15, segment_gap=2, corner_radius=0, edge_softness=0.0)

        # 3. Round & Soft (Modern)
        r3 = ColFramer(rows, col_ratios=(1, 3))
        r3 += TextFrame(r3, text="Round & Soft", align=('right', 'middle'))
        r3 += VU2chHorzFrame(r3, segment_size=8, segment_gap=4, corner_radius=4, edge_softness=0.1)

        # 4. Solid Bar (Analog)
        r4 = ColFramer(rows, col_ratios=(1, 3))
        r4 += TextFrame(r4, text="Solid (Analog)", align=('right', 'middle'))
        r4 += VU2chHorzFrame(r4, segment_size=10, segment_gap=0, corner_radius=5, edge_softness=0.02)

class ArtistScreen(Frame):   # comprises volume on the left, spectrum on the right
    @property
    def title(self): return 'Artist art front and centre'

    @property
    def type(self): return 'Visualiser and metadata'

    def __init__(self, platform):
        Frame.__init__(self, platform, theme= 'zomp')
        """
            Central panel of artist with horz VUs below, progress below
            Album art top right
            Split out meta data
        
        """

        ARTIST = {'artist': {'colour':'light', 'align': ('centre', 'middle'), 'scalers': (1.0, 1.0)}}
        TRACK  = {'track' : {'colour':'light', 'align': ('centre', 'middle'), 'scalers': (0.6, 1.0)}}
        ALBUM  = {'album' : {'colour':'mid',   'align': ('centre','middle'), 'scalers': (0.6, 1.0)} }
 
        META = {'track' : {'colour':'light', 'align': ('centre', 'bottom'), 'scalers': (1.0, 1.0)},
                'artist' : {'colour':'mid',   'align': ('centre','top'), 'scalers': (1.0, 1.0)} }
 
        cols = ColFramer(self, background='dark')
        cols += MetaImages(cols, art_type='album', outline={'colour':'mid', 'width':7, 'opacity': 100, 'radius': 0})
        cols += MetaDataFrame(cols, background='dark')
        # cols += VUFlipFrame(cols, background='dark',orient='horz',outline={'colour':'mid', 'width':50, 'opacity': 100, 'radius': 0})
        cols += VUFlipFrame(cols, background='dark',orient='vert',outline={'colour':'mid', 'width':20, 'opacity': 100, 'radius': 0})
        # cols.always_draw_background()
        print(self)

class BloomImageTestScreen(Frame):
    @property
    def title(self): return 'Bloom Effect over Image Background'
    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        # Screen background
        Frame.__init__(self, platform, background={'image': 'particles.jpg', 'opacity': 255})
        
        # Add a column framer
        cols = ColFramer(self, col_ratios=(1, 2), padding=20)
        
        # Left: Album Art with some opacity
        cols += MetaImages(cols, art_type='album', opacity=200, outline={'colour':'light', 'width':2})
        
        # Right: VU Meters with Bloom over a semi-transparent background
        # We want the VU frame itself to have a semi-transparent dark background so the main background shows through slightly
        vu_bg = {'colour': 'dark', 'opacity': 100} 
        
        cols += VU2chHorzFrame(cols, 
            background=vu_bg,
            bloom_threshold=0.5,
            bloom_intensity=2.0,
            bloom_softness=0.8,
            bloom_alpha=80, # Visible bloom
            softness=0.1
        )

class ShadowTestScreen(Frame):
    @property
    def title(self): return 'Drop Shadow Test'
    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        # Screen background
        Frame.__init__(self, platform, background={'image': 'particles.jpg', 'opacity': 50})
        
        # Add a column framer
        cols = ColFramer(self, col_ratios=(1, 1, 1), padding=40)
        
        # Frame 1: Hard Shadow
        shadow1 = {
            'color': (0, 0, 0),
            'opacity': 255,
            'offset': (15, 15),
            'softness': 0.0
        }
        cols += TextFrame(cols, text="Hard Shadow", 
                          background={'colour': 'light', 'shadow': shadow1, 'opacity': 255},
                          outline={'colour': 'foreground', 'width': 2, 'radius': 10})

        # Frame 2: Soft Shadow
        shadow2 = {
            'color': (0, 0, 0),
            'opacity': 200,
            'offset': (20, 20),
            'softness': 0.8
        }
        cols += TextFrame(cols, text="Soft Shadow", 
                          background={'colour': 'mid', 'shadow': shadow2, 'opacity': 255},
                          outline={'colour': 'foreground', 'width': 2, 'radius': 20})

        # Frame 3: Colored Glow (Centered Shadow)
        shadow3 = {
            'color': (255, 50, 50), # Red glow
            'opacity': 255,
            'offset': (0, 0), # Centered
            'softness': 0.9
        }
        cols += TextFrame(cols, text="Red Glow", 
                          background={'colour': 'dark', 'shadow': shadow3, 'opacity': 255},
                          outline={'colour': 'foreground', 'width': 2, 'radius': 30})

#----------- PlayProgress Test screens ---------------------------
"""
    def __init__(self, parent, scalers=None, align=None, barsize_pc=0.5, theme=None, flip=False, \
                    led_h=1, led_gap=0, radius=0, barw_min=10, barw_max=400, tip=True, orient='horz', background='background'): 
"""
class ProgressScreen(Frame):
    @property
    def title(self): return 'Progress> checks the API for PlayProgressFrame'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        back = {'colour':'background', 'opacity':255, 'per_frame_update':False}
        super().__init__(platform, theme='hifi', outline={'width':20,'colour':'alert'}, padding=0)

        cols = ColFramer(self)
        cols += PlayProgressFrame(cols, scalers=(1.0,0.2), background=back)
        cols += MetaData(cols,  'track', colour='foreground', scalers=(1.0,1.0), outline={'colour':'alert','width':0})
        rows = RowFramer(cols, row_ratios=(4,1,1),background='mid', padpc=0, padding=0, outline={'colour':'alert','width':0}) #, align=('centre','middle'))

        rows += MetaData(rows,  'track', colour='foreground', scalers=(1.0,1.0), outline={'colour':'alert','width':0})
        rows += PlayProgressFrame(rows, led_h=3, led_gap=3)

        rows += PlayProgressFrame(rows, orient='horz')





#----------- Test screens ---------------------------

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



class ColAlignedScreen(Frame):
    @property
    def title(self): return 'ColAlignedScreen> Creates 3 box frames and aligns them horizontally, evenly'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        super().__init__(platform, theme='hifi', outline={'width':20,'colour':'alert'}, padding=0)
        # print("SubFrame> ", self.geostr())
        self.create()

    def create(self):
        
        # self += TextFrame(self  , scalers=(0.6,0.6), align=('centre','middle'), text='centre', background='dark', outline={'width':10,'colour':'alert'})
        # print(self)

        # colframe = ColFramer(self, scalers=(1.0,1.0), align=('centre','middle'), background='mid', padpc=0, padding=0, outline={'colour':'alert','width':5}) #, align=('centre','middle'))
        # print("ColAlignedScreen.create> colframe", colframe.framestr())
        self += Frame(self, scalers=(0.5,0.5), align=('left','middle'), background='light', outline={'colour':'alert','width':5})
        self += Frame(self, scalers=(0.5,0.5), align=('right','bottom'), background='mid', outline={'colour':'alert','width':5})
        # self += TextFrame(self  , text='one', scalers=(1.0, 1.0), background='light') #, outline={'colour':'alert','width':20})
        # self += TextFrame(self  , text='two', scalers=(0.3, 1.0), background='mid', outline={'colour':'foreground','width':15})
        # colframe += TextFrame(colframe  , text='mid on a very long string that needs to be even longer askjdhfkjahsdlfkjhalskjdhflkajshdflkjashdflkj', wrap=True, background='mid', outline={'colour':'alert','width':1})
        # colframe += MetaData(colframe,  'track', colour='foreground', scalers=(1.0,1.0), outline={'colour':'alert','width':1})

        # rowframe = RowFramer(colframe  ,  scalers=(1.0,1.0), align=('right','middle'), background='dark', padding=0.0)

        # rowframe += Frame(rowframe  ,   scalers=(1.0,1.0), background='mid', outline={'colour':'foreground','width':3})
        # rowframe += TextFrame(rowframe  , text='rhs', background='light', outline={'colour':'alert'})
        # rowframe += Frame(rowframe  ,  scalers=(1.0, 1.0), background='foreground')
        print(self)

class RowAlignedScreen(Frame):
    @property
    def title(self): return 'ColAlignedScreen> Creates 3 box frames and aligns them horizontally, evenly'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        super().__init__(platform, theme='hifi', outline={'width':1,'colour':'foreground'})
        # print("SubFrame> ", self.geostr())
        self.create()

    def create(self):
        
        # self += TextFrame(self  , scalers=(0.6,0.6), align=('centre','middle'), text='centre', background='dark', outline={'width':10,'colour':'alert'})
        # print(self)

        rowframe = RowFramer(self, scalers=(1.0,1.0), align=('centre','middle'), background='dark', padpc=0,outline={'colour':'alert','width':1}) #, align=('centre','middle'))
        # print("ColAlignedScreen.create> colframe", colframe.framestr())
        rowframe += TextFrame(rowframe  , text='left', scalers=(1.0, 1.0), background='light', outline={'colour':'alert','width':1})
        rowframe += TextFrame(rowframe  , text='mid on a very long string that needs to be even longer askjdhfkjahsdlfkjhalskjdhflkajshdflkjashdflkj', wrap=True, background='mid', outline={'colour':'alert','width':1})
        rowframe += MetaData(rowframe,  'track', colour='foreground', scalers=(1.0,1.0), outline={'colour':'alert','width':1})

        # rowframe = RowFramer(colframe  ,  scalers=(1.0,1.0), align=('right','middle'), background='dark', padding=0.0)

        # rowframe += Frame(rowframe  ,   scalers=(1.0,1.0), background='mid', outline={'colour':'foreground','width':3})
        # rowframe += TextFrame(rowframe  , text='rhs', background='light', outline={'colour':'alert'})
        # rowframe += Frame(rowframe  ,  scalers=(1.0, 1.0), background='foreground')        
        print(self)


# Test harness to get outline, background and frame geo correct:
class F1(Frame):
    @property
    def title(self): return 'F1> Creates 3 box frames and aligns them horizontally, evenly'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        super().__init__(platform, theme='hifi', outline={'width':10,'colour':'alert'}, padding=10, background={'image': 'stream.png', 'opacity': 255})
        # print("SubFrame> ", self.geostr())
        self.create()

    def create(self):
        self += Frame(self, scalers=(0.5,0.5), align=('left','bottom'), background=BackgroundDefault, outline={'colour':'foreground','width':10})
        self += Frame(self, scalers=(0.5,0.5), align=('right','bottom'), background=None, outline={'colour':'foreground','width':10})
        self += Frame(self, scalers=(0.5,0.5), align=('left','top'), background=None, outline={'colour':'foreground','width':10})
        self += Frame(self, scalers=(0.5,0.5), align=('right','top'), background=None, outline={'colour':'foreground','width':10})
        # self += Frame(self, scalers=(0.3,0.3), align=('left','middle'), background='light', outline={'colour':'foreground','width':5})
        # self += Frame(self, scalers=(0.3,0.3), align=('right','middle'), background='mid', outline={'colour':'foreground','width':5})
        # self += Frame(self, scalers=(0.3,0.3), align=('centre','top'), background='mid', outline={'colour':'foreground','width':5})
        # self += Frame(self, scalers=(0.3,0.3), align=('centre','middle'), background='light', outline={'colour':'foreground','width':5})
        # self += Frame(self, scalers=(0.3,0.3), align=('centre','bottom'), background='mid', outline={'colour':'foreground','width':5})

        print(self)

class F2(Frame):
    @property
    def title(self): return 'F2> Creates 3 box frames and aligns them horizontally, evenly'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        super().__init__(platform, theme='hifi', outline={'width':20,'colour':'alert'}, padding=20)
        # print("SubFrame> ", self.geostr())
        self.create()

    def create(self):
        self += Frame(self, scalers=(0.3,0.3), align=('centre','bottom'), background='light', outline={'colour':'foreground','width':5})
        self += Frame(self, scalers=(0.3,0.3), align=('right','bottom'), background='mid', outline={'colour':'foreground','width':5})
        self += Frame(self, scalers=(0.3,0.3), align=('left','top'), background='light', outline={'colour':'foreground','width':5})
        self += Frame(self, scalers=(0.3,0.3), align=('right','top'), background='mid', outline={'colour':'foreground','width':5})
        self += Frame(self, scalers=(0.3,0.3), align=('left','middle'), background='light', outline={'colour':'foreground','width':5})
        self += Frame(self, scalers=(0.3,0.3), align=('right','middle'), background='mid', outline={'colour':'foreground','width':5})


        print(self)

class F3(Frame):
    @property
    def title(self): return 'F3> Checks out Text Frames'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        super().__init__(platform, theme='hifi', outline={'width':20,'colour':'foreground'}, padding=30)
        # print("SubFrame> ", self.geostr())
        self.create()

    def create(self):
        # self += Frame(self, scalers=(0.5,0.333), align=('centre','middle'), background='light', outline={'colour':'alert','width':5}, padding =20)
        # self += Frame(self, scalers=(0.5,0.333), align=('centre','bottom'), background='mid', outline={'colour':'alert','width':5},padding = 10)
        self += TextFrame(self  , text='one', scalers=(0.33,1.0 ), background='mid', align=('left','middle'), outline={'colour':'alert','width':10}, padding =10)
        self += TextFrame(self  , text='two', scalers=(0.33, 1.0), background='mid', align=('centre','middle'), outline={'colour':'alert','width':10}, padding =10)
        self += TextFrame(self  , text='three', scalers=(0.33, 1.0), background='mid', align=('right','middle'), outline={'colour':'alert','width':10}, padding =10)
                # self += f


        print(self)

class F4(Frame):
    @property
    def title(self): return 'F4> Checks out Col Framer'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        super().__init__(platform, theme='hifi', outline={'width':5,'colour':'alert'}, background={'image': 'particles.jpg', 'opacity': 100}, padding=30)
        # print("SubFrame> ", self.geostr())
        
        # self += TextFrame(self  , scalers=(0.6,0.6), align=('centre','middle'), text='centre', background='dark', outline={'width':10,'colour':'alert'})
        # print(self)

        back = {'colour':'dark', 'opacity':100, 'glow':True}
        colframe = ColFramer(self,col_ratios=(1.0,1.0,1,1), align=('centre','middle'), background=None, padpc=0.1, padding=0, outline={'colour':'alert','width':0}) #, align=('centre','middle'))
        # # # print("ColAlignedScreen.create> colframe", colframe.framestr())
        # # # colframe += Frame(colframe, scalers=(1.0,1.0), background='light', outline={'colour':'alert','width':0},padding=0)
        # # # colframe += Frame(colframe, scalers=(1.0,1.0), background='foreground', outline={'colour':'alert','width':0})
        colframe += TextFrame(colframe  , text='oneRT',  background=back, justify=('right','top'), outline={'colour':'foreground','width':1}, padding =0)

        colframe += TextFrame(colframe  , text='wideC',  background='light', justify=('centre','middle'), outline={'colour':'alert','width':1})
        colframe += TextFrame(colframe  , text='threeLB',  background=back, justify=('left','bottom'), outline={'colour':'mid','width':1})
        # colframe += TextFrame(colframe  , text='mid on a very long string that needs to be even longer askjdhfkjahsdlfkjhalskjdhflkajshdflkjashdflkj', wrap=True, background='mid', outline={'colour':'alert','width':1})
        # colframe += MetaData(colframe,  'track', colour='foreground', scalers=(1.0,1.0), outline={'colour':'alert','width':1})


        rowframe = RowFramer(colframe  , padpc=0.0, align=('right','middle'), background=back, padding=0.0, outline={'colour':'foreground','width':1})
        rowframe += TextFrame(rowframe  , text="top",  scalers=(1.0,1.0), background='mid', outline={'colour':'foreground','width':0})

        rowframe += TextFrame(rowframe  , text='rhs', background='dark', justify=('left','top'),outline={'colour':'mid', 'width':0})
        rowframe += TextFrame(rowframe  , text='next', background='dark', justify=('centre','middle'),outline={'colour':'mid', 'width':0})
        rowframe += TextFrame(rowframe  ,  text='b', scalers=(1.0, 1.0), justify=('right','bottom'),background='light')
        print(self)

class F5(Frame):
    @property
    def title(self): return 'F5 Checks background images'

    @property
    def type(self): return 'Test'

# , background={'path': 'blue.jpg', 'opacity': 255}
    def __init__(self, platform):
        super().__init__(platform, theme='hifi', outline={'width':0,'colour':'alert'}, padding=30, background={'image': 'particles.jpg', 'opacity': 100} )
        # print("SubFrame> ", self.geostr())
 
        # self += TextFrame(self  , scalers=(0.6,1.0), align=('left','middle'), text='a very very very big mess', background='dark', outline={'width':10,'colour':'alert'})

        # print(self)
        back={'file': 'particles.jpg', 'opacity': 255}
        # back = 'dark'


        colframe = ColFramer(self, col_ratios=(1,1,2), scalers=(1.0,1.0), background=None, outline={'colour':'foreground','width':1}, padding=0)
        # colframe += TextFrame(colframe  , text='one big oneLB', scalers=(1.0,0.2), align=('left','top'), justify=('left', 'bottom'), background='mid', outline={'colour':'foreground','width':1}, padding =10)
        colframe += TextFrame(colframe  , text='twoCM', scalers=(1.0,1.0), align=('right','top'), justify=('centre', 'middle'), background='light', outline={'colour':'alert','width':1})
        # colframe += TextFrame(colframe  , text='threeRT', scalers=(1.0, 0.2), background='mid', justify=('right', 'top'), align=('centre','bottom'), outline={'colour':'foreground','width':1}, padding =10)
        colframe += VUFrame(colframe, 'left', align=('right','middle'), scalers=(1.0,1.0), orient='horz', barsize_pc=1.0, led_gap=0,tip=True, background='dark')
        
 
        rowframe = RowFramer(colframe  , row_ratios=(1,3, 1),  scalers=(1.0,1.0), align=('right','middle'), background='dark', padding=0.0)
        # rowframe += MetaImages(rowframe, art_type='album',scalers=(1.0,1.0), outline={'colour':'foreground','width':30, 'radius':4, 'opacity':50},padding=0, background='mid')
        rowframe += TextFrame(rowframe  , text='row sub', scalers=(1.0, 1.0), background='light') #, outline={'colour':'alert','width':20})
        # rowframe = Frame(rowframe)
        # rowframe += subframe
        colframe2 = ColFramer(rowframe, scalers=(1.0,1.0), align=('centre','middle'), background='mid', padpc=0, padding=0, outline={'colour':'alert','width':0}) #, align=('centre','middle'))
        colframe2 += TextFrame(colframe2  , text='a', scalers=(1.0, 1.0), background='light') #, outline={'colour':'alert','width':20})
        colframe2 += TextFrame(colframe2  , text='two', scalers=(1.0, 1.0), background='dark', outline={'colour':'mid','width':30})
        colframe2 += TextFrame(colframe2  , text='mleftj', wrap=True, background='mid', outline={'colour':'alert','width':1})


        # rowframe += TextFrame(rowframe  , text='four', scalers=(1.0, 0.5), align=('left','top'),background='light', outline={'colour':'alert','width':60}, justify='left')
        rowframe += TextFrame(rowframe  , text='five', scalers=(1.0, 0.5), align=('left','bottom'), background='dark', outline={'colour':'mid','width':2})
        # rowframe += MetaDataFrame(rowframe, outline={'colour':'alert','width':1}, background="carbonfibre.jpg")


      
        # # print("ColAlignedScreen.create> colframe", colframe.framestr())
        # colframe = self


        # colframe += VU2chFrame(colframe, scalers=(1.0, 1.0), background='light', align=('right','middle'), led_h=7, led_gap=2,barsize_pc=0.1, outline={'colour':'foreground', 'width':1}, theme='std')
        # colframe += AlbumArtFrame(colframe, scalers=(1.0,1.0), outline={'colour':'foreground','width':30, 'radius':4, 'opacity':50},padding=0, background='mid')
        # colframe += ArtistArtFrame(colframe, scalers=(1.0,1.0), background='light', outline={'colour':'alert','width':1},padding=0)



        # colframe += Frame(colframe, scalers=(1.0,1.0), background='light', outline={'colour':'alert','width':0},padding=0)
        # colframe += Frame(colframe, scalers=(1.0,1.0), background='mid', outline={'colour':'alert','width':0},padding=0)
        # colframe += Frame(colframe, scalers=(1.0,1.0), background='light', outline={'colour':'alert','width':0},padding=0)


 
  
        # # colframe += MetaData(colframe,  'track', colour='foreground', scalers=(1.0,1.0), outline={'colour':'alert','width':1})

        # rowframe = RowFramer(self  ,  scalers=(1.0,0.5), align=('right','middle'), background='dark', padding=0.0)
        # rowframe += TextFrame(rowframe  , text='top', scalers=(1.0,1.0), background='light', outline={'colour':'alert'})
        # rowframe += TextFrame(rowframe  , text='mid', scalers=(1.0,1.0), background='light', outline={'colour':'alert'})
        # rowframe += Frame(rowframe  ,   scalers=(1.0,1.0), background='mid', outline={'colour':'mid','width':3})

        # rowframe += Frame(rowframe  ,  scalers=(1.0, 1.0), background='foreground')
        print(self)        


class F6(Frame):
    @property
    def title(self): return 'F5 Checks background images'

    @property
    def type(self): return 'Test'

# , background={'path': 'blue.jpg', 'opacity': 255}
    def __init__(self, platform):
        super().__init__(platform, theme='hifi', outline={'width':0,'colour':'alert'}, padding=10, background={'image': 'stream.png', 'opacity': 255} )
        # print("SubFrame> ", self.geostr())
        self.create()

    def create(self):
        
        # self += TextFrame(self  , scalers=(0.6,0.6), align=('centre','middle'), text='centre', background='dark', outline={'width':10,'colour':'alert'})
        # print(self)
        back={'file': 'particles.jpg', 'opacity': 255}
        # back = 'dark'
        # colframe = ColFramer(self, scalers=(1.0,1.0), align=('centre','middle'), background='mid', padpc=0, padding=0, outline={'colour':'alert','width':0}) #, align=('centre','middle'))
        # # print("ColAlignedScreen.create> colframe", colframe.framestr())


        colframe = ColFramer(self, col_ratios=(1,1,1), scalers=(1.0,1.0), background=None, outline={'colour':'foreground','width':1}, padding=10)
        # colframe += VU2chFrame(colframe, scalers=(0.1, 1.0), align=('right','middle'), background='background',led_h=7, led_gap=2,barsize_pc=0.1, outline={'colour':'foreground', 'width':1}, theme='std')
        colframe += MetaDataFrame(colframe)
        colframe += VUFrame(colframe, 'left', align=('right','middle'), scalers=(1.0,1.0), orient='vert', barsize_pc=1.0, led_gap=0,tip=True, background='dark')
        # colframe += MetaImages(colframe, art_type='album', scalers=(1.0,1.0), outline={'colour':'foreground','width':30, 'radius':4, 'opacity':20},padding=0, background='mid')
        # colframe += MetaImages(colframe, art_type='artist', scalers=(1.0,1.0), background='light', outline={'colour':'alert','width':5},padding=0, opacity=100)

        print(self)  


class F7(Frame):
    @property
    def title(self): return 'F7> Checks out Bars'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        super().__init__(platform, theme='std', outline={'width':20,'colour':'foreground'}, padding=30, background={'image': 'stream.png', 'opacity': 255})
        # print("SubFrame> ", self.geostr())
        self.create()

    def create(self):
        col = ColFramer(self,col_ratios=(2,1,1), background='dark')
        # self += Frame(self, scalers=(0.5,0.333), align=('centre','middle'), background='light', outline={'colour':'alert','width':5}, padding =20)
        # self += Frame(self, scalers=(0.5,0.333), align=('centre','bottom'), background='mid', outline={'colour':'alert','width':5},padding = 10)
        # self += TextFrame(self  , text='one', scalers=(0.33,1.0 ), background='mid', align=('left','middle'), outline={'colour':'alert','width':10}, padding =10)
        # self += TextFrame(self  , text='two', scalers=(0.33, 1.0), background='mid', align=('centre','middle'), outline={'colour':'alert','width':10}, padding =10)
        # self += TextFrame(self  , text='three', scalers=(0.33, 1.0), background='mid', align=('right','middle'), outline={'colour':'alert','width':10}, padding =10)
        # col += SpectrumFrame(col,  'left', scalers=(1.0, 1.0), align=('left','top'), flip=False, led_gap=5, peak_h=3,radius=0, tip=False, barw_min=15, bar_space=0.5,background='dark' )
        # self += VUHorzFrame(self, 'left',  scalers=(1.0, 0.5), align=('left','top') ,tip=False, background='mid')
        col += VUFrame(col, 'left', align=('right','middle'), scalers=(1.0,1.0), orient='horz', barsize_pc=1.0, led_gap=0,tip=True, background='dark')
        # col += VUFrame(col  , 'right', scalers=(1.0, 1.0), align=('centre', 'top'), background='stream.png')

        print(self)  


class F8(Frame):   # comprises volume on the left, spectrum on the right
    @property
    def title(self): return 'F8 > Check out Spectrum Analyser'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        Frame.__init__(self, platform, theme= 'white', background='background')

        cols = ColFramer(self, background='background')
        # spectrum = Frame(cols)
        cols += SpectrumFrame(cols  ,  'mono', flip=False, led_gap=0, peak_h=1, radius=0, tip=True, barw_min=3, bar_space=2,background='background')
        # spectrum += SpectrumFrame(spectrum  ,  'left', scalers=(1.0, 0.5), align=('left','top'), flip=False, led_gap=0, peak_h=1,radius=0, tip=True, barw_min=3, bar_space=2 )
        # cols += StereoSpectrumFrame(cols)
        # cols += MetaMiniSpectrumFrame(cols)
        artoutline = {'colour':'background', 'width':5}
        cols += MetaImages(cols  , art_type='artist', opacity=100, outline=artoutline)
        cols += MetaDataFrame(cols )
        # self += PlayProgressFrame(self  ,  scalers=(0.5, 0.05), align=('left','bottom'))        
        # cols.always_draw_background()
        # print(self)  

class F9(Frame):   # comprises volume on the left, spectrum on the right
    @property
    def title(self): return 'Background layers test'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        Frame.__init__(self, platform, theme= 'blue', background={'image':'stream.png', 'opacity':200},padding=30)

        # rows = RowFramer(self, row_ratios=(3,1), background='background')

        subframe = ColFramer(self, col_ratios=(1,1,1), padpc=0.1,padding=40, background={'image':'particles.jpg'})
        subframe += VU2chFrame(subframe, led_h=7, led_gap=2,barsize_pc=1.0, outline={'colour':'foreground', 'width':5},\
                               background={'colour':'mid','opacity':100})
        subframe += MetaImages(subframe, art_type='album', opacity=255)
        subframe += TextFrame(subframe  , text='Volume',  background={'colour':'dark','opacity':200}, \
                              justify=('right','middle'), outline={'colour':'foreground','width':1}, padding =0)
        # led_h=5, led_gap=1,barsize_pc=0.7, theme=None
        # subframe += MetaDataFrame(subframe, scalers=(1.0, 1.0), justify='left', background='background')        