#!/usr/bin/env python
"""
 All top level screens.  Screens are comprised of Frames

 Part of mVista preDAC2 project

 v1.0 Baloothebear4 Nov 20220253


"""


from pyvisualiser import *
PI = 3.14159265358979323846

"""
Screen classes - these are top level frames comprising frames of frames at full display size
"""

class Screen1(Frame):   # comprises volume on the left, spectrum on the right
    @property
    def title(self): return 'Horizontal VUs with full meta data'

    @property
    def type(self): return 'Visualiser and metadata'

    def __init__(self, platform):
        Frame.__init__(self, platform, theme= 'hifi', padding=0)

        BACK = {'image':'particles.jpg', 'opacity':50, 'glow':True}
        colframe = ColFramer(self, padpc=0.05, col_ratios=(2,3,1.8), outline={'width':0,'colour':'light'}, padding=0,background=BACK)

        colframe += MetaImages(colframe, art_type='album', background=None, outline={'colour':'light', 'width':5, 'opacity': 255, 'radius': 20})
        colframe += MetaDataFrame(colframe, background=None )
        colframe += Diamondiser(colframe,  'mono', background=None)

class Screen2(Frame):   # comprises volume on the left, spectrum on the right
    @property
    def title(self): return 'Base spectrum screen with al'

    @property
    def type(self): return 'Visualiser and metadata'

    def __init__(self, platform):
        BACK = {'image':'artist', 'opacity':100,'per_frame_update':False}
        Frame.__init__(self, platform, theme= 'std', background='background')

        colframe = ColFramer(self,background={'image':'artist','opacity':100}) # for album art with padding
        BACK2=None
        colframe += StereoSpectrumFrame(colframe, background=BACK2)
        colframe += MetaDataFrame(colframe, background=BACK2,justify='right')  #, scalers=(1.0,1.0), align=('centre','top'))


        # colframe += MetaImages(colframe, art_type='artist')  #, outline={'colour':'light', 'width':5, 'opacity': 200, 'radius': 20})


class Screen3(Frame):   # comprises volume on the left, spectrum on the right
    @property
    def title(self): return 'Base spectrum screen with al'

    @property
    def type(self): return 'Visualiser and metadata'

    def __init__(self, platform):
        Frame.__init__(self, platform, theme= 'space',padding=5)

        colframe  = ColFramer(self, col_ratios=(1,2,1), padding=10,padpc=0.1)

        row1  = RowFramer(colframe, row_ratios=(5,1))
        row1 += MetaImages(row1, outline={'colour':'light', 'width':5, 'opacity': 200, 'radius': 10})
        row1 += MetaData(row1, 'album', justify='centre', colour='mid')

        row2  = RowFramer(colframe, row_ratios=(5,0.3,1), padding=0.0)
        # col2  = ColFramer(row2,col_ratios=(1,6))
        # col2 += VUFlipFrame(row2, orient='vert', flip=True, led_gap=3, background='background')
        row2 += SpectrumFrame(row2, 'mono', bar_style=BarStyle(led_gap=5, peak_h=3, radius=4, tip=True), spectrum_style=SpectrumStyle(barw_min=3, bar_space=1))

        row2 += PlayProgressFrame(row2)
        row2 += MetaData(row2, 'track', justify='centre')
        # rowframe += SpectrumFrame(rowframe,  'mono', flip=False, bar_style=BarStyle(led_gap=5, peak_h=3, radius=4, tip=True), spectrum_style=SpectrumStyle(barw_min=3, bar_space=1) )
        # subframe += MetaDataFrame(subframe, scalers=(1.0, 1.0))
        row3  = RowFramer(colframe, row_ratios=(5,1), padding=0.0)
        row3 += MetaImages(row3, art_type='artist',outline={'colour':'light', 'width':5, 'opacity': 200, 'radius': 10})
        row3 += MetaData(row3, 'artist', justify='centre',colour='mid')


class Screen4(Frame):

    def __init__(self, parent, scalers=None, align=None, theme='std'):
        particles = {'count': 80, 'colour': 'light', 'speed': 0.2, 'size': 1, 'softness': 0.1}
        Frame.__init__(self, parent, scalers=scalers, align=align, background={'colour':'background', 'particles':particles, 'opacity':0}, theme='tea')

        # SHOW = { 'artist': {'colour': 'foreground', 'align': ('centre','top'),   'scalers': (1.0, 0.33) }, \
        #          'track': {'colour' : 'light',      'align': ('centre','bottom'), 'scalers': (1.0, 0.33)}, \
        #          'album': {'colour' : 'mid',        'align': ('centre','middle'), 'scalers': (1.0, 0.33)} }
        ARTIST = {'artist': {'colour':'foreground', 'align': ('right', 'middle'), 'scalers': (1.0, 1.0)}}
        TRACK  = {'track' : {'colour':'light', 'align': ('right', 'middle'), 'scalers': (1.0, 1.0)}}
        ALBUM  = {'album' : {'colour':'mid',   'align': ('right','middle'), 'scalers': (1.0, 1.0)} }

        back  = {'colour':'background', 'opacity':0, 'per_frame_update':True}
        cols  = ColFramer(self, col_ratios=(1,2), padding=5)
        cols += MetaImages(cols,  'album', outline={'colour':'mid','width':3, 'radius':10},padding=10,background={'opacity':0})
        rows  = RowFramer(cols, row_ratios=(3,1), padpc=0)
        rows += MetaDataFrame(rows, justify='left', background=back)
        rows += SpectrumFrame(cols,channel='mono', bar_style=BarStyle(led_gap=0), spectrum_style=SpectrumStyle(bar_space=4), background=back)


class Screen5(Frame):   # comprises volume on the left, spectrum on the right
    @property
    def title(self): return 'Analogue VU Meters, Roon Album Art, Metadata and progress bar'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        back = {'image':'carbonfibre.jpg', 'per_frame_update':False, 'opacity': 255}
        Frame.__init__(self, platform, background=back, theme= 'meter1', padding=30)
  
        NEEDLE    = { 'width':4, 'colour': 'foreground', 'length': 0.8, 'radius_pc': 1.0 }
        ENDSTOPS  = (3*PI/4, 5*PI/4)  #Position of endstop if not the edge of the frame
        PIVOT     = -0.5
        OUTLINE   = {'colour':'foreground', 'width':5, 'opacity': 255, 'radius': 10}
        BACK      = {'colour':'dark', 'opacity':10, 'glow':True}
        # self += MetaImages(self  , (0.25, 0.93),align=('right','middle'))
        # self += MetaImages(self  , (0.3, 0.3),align=('centre','top'))
        # self += MetaDataFrame(self  , scalers=(0.3, 1.0), align=('centre','middle'))
        # # self += MetaImages(self  , scalers=(1.0,1.0),align=('centre','middle'), opacity=40)
        # # self += PlayProgressFrame(self  , scalers=(0.3, 0.05), align=('centre','bottom'))
        # self += VUMeter(self  ,  'left', scalers=(0.3, 0.9), align=('left','top'), style=VUMeterStyle(pivot=PIVOT, scale=VUMeterScale(arcs={}), endstops=ENDSTOPS, needle=NEEDLE),outline=OUTLINE) #, background='mid')
        # self += VUMeter(self  ,  'right', scalers=(0.3, 0.9), align=('right','top'), style=VUMeterStyle(pivot=PIVOT, scale=VUMeterScale(arcs={}), endstops=ENDSTOPS, needle=NEEDLE),outline=OUTLINE) #,background='mid')
        cols = ColFramer(self, padpc=0.05)
        cols += VUMeter(cols  ,  'left', square=False, style=VUMeterStyle(pivot=PIVOT, scale=VUMeterScale(arcs={}), endstops=ENDSTOPS, needle=NEEDLE),outline=OUTLINE, background=BACK)
        cols += MetaDataFrame(cols,padding=0, background=None)#,outline=OUTLINE)
        cols += VUMeter(cols  ,  'right', square=False, style=VUMeterStyle(pivot=PIVOT, scale=VUMeterScale(arcs={}), endstops=ENDSTOPS, needle=NEEDLE),outline=OUTLINE, background=BACK)

class Screen6(Frame):
    """ Volume/Source on left - Spectrum on left - one channel """
    def __init__(self, platform):
        Frame.__init__(self, platform, theme='hifi',background='waves.png', padding=20)

        rows = RowFramer(self, row_ratios=(1,7), padpc=0.1)
        rows += MetaData(rows, metadata_type='track',background=None)
        rows += SpectrumFrame(rows, channel='mono', outline={'width':0},background={'colour':'background','opacity':150, 'glow':True})


class Screen7(Frame):   # comprises volume on the left, spectrum on the right
    @property
    def title(self): return 'Oscillogram, Roon Album Art, Metadata and progress bar'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        Frame.__init__(self, platform, theme= 'red')

        rows = RowFramer(self, row_ratios=(3,1), background={'image':'stream.png', 'opacity':100})

        subframe = ColFramer(rows, col_ratios=(1.5, 4,0.1), padpc=0.1)

        subframe += MetaImages(subframe, art_type='album', background=None)
        subframe += MetaDataFrame(subframe, scalers=(1.0, 1.0), justify='left', background=None)
        subframe += VU2chFrame(subframe, bar_style=BarStyle(led_h=7, led_gap=2),barsize_pc=0.2, outline={'colour':'foreground', 'width':0},background=None, effects=DreamEffect)

        rows += Oscilogramme(rows, 'mono',background=None)


class ProfileTestScreen(Frame):
    @property
    def title(self): return 'Profile Controls Tuning'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        # A dark background makes bloom and vignette most obvious
        Frame.__init__(self, platform, theme='std', background=None, padding=20)

        rows = RowFramer(self, row_ratios=(1, 4), padding=10)

        text = "PROFILE CONTROLS TEST MENU\nPress 1(Luxury), 2(Neon), 3(Minimal). Press 'L' for HUD."
        rows += TextFrame(rows, text=text, colour='light', align=('centre', 'middle'))

        cols = ColFramer(rows, padding=10)
        # Spectrum Frame with thick bars and reflections to test Bloom / Softness
        bar_style = BarStyle(led_gap=2, peak_h=3, radius=1, tip=True, flip=False, colour_mode='vert')
        spectrum_style = SpectrumStyle(barw_min=8, bar_space=0.5, barw_max=25)
        effects = Effects(reflection=ReflectionStyle(size=0.4, opacity=0.3))
        
        spectrum_wrapper = RowFramer(cols, padding=10)
        spectrum_wrapper += SpectrumFrame(spectrum_wrapper, 'mono', bar_style=bar_style, spectrum_style=spectrum_style, effects=effects)
        
        # Meta Images to show album art interactions with Depth, Sharpness, Vignette
        cols += MetaImages(cols, art_type='album', align=('centre','middle'), outline=OutlineStyle(colour='light', width=4, glow_intensity=1.0, softness=0.5))

        # Bottom VU Meter for bright static elements
        meter_style = VUMeterStyle(pivot=-0.5, endstops=(3*PI/4, 5*PI/4), needle=VUNeedleStyle(width=4, colour='light', length=0.8, radius_pc=1.0))
        cols += VUMeter(cols, 'left', square=False, style=meter_style, background=None)
# @dataclass(frozen=True)
# class VUMeterStyle:
#     endstops: tuple = (3*PI/4, 5*PI/4)
#     pivot: float = -0.5
#     needle: VUNeedleStyle = field(default_factory=VUNeedleStyle)
#     scale: VUMeterScale = field(default_factory=VUMeterScale)
#     texture_path: Optional[str] = None
#     texture_opacity: float = 1.0
#     theme: str = 'meter1'
#     show_peak: bool = False
#     decay: float = DECAY
#     smooth: int = SMOOTH