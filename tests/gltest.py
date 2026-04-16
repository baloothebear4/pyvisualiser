'''
Test file for glsl based visualisers


'''

import pygame

from pyvisualiser.visualisers.glvisualisers import *
from pyvisualiser.styles.presets import *
from pyvisualiser.styles.styles  import *
from pyvisualiser.core.framecore  import Frame, RowFramer, ColFramer
from pyvisualiser.visualisers.metadata import MetaDataFrame, PlayProgressFrame, TextFrame, MetaImages, MetaData
from pyvisualiser.visualisers.spectrum import *

class GLmeshScreen(Frame):
    @property
    def title(self): return 'GLSL Shader Test - Kaleidoscope & SpectrumMesh'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        # Use the new 'meter2' theme which has the cream background
        super().__init__(platform, theme='hifi', padding=0)

        
        # Add SpectrumMesh on the right
        self.spectrum_mesh = SpectrumMesh(self)
        self += self.spectrum_mesh

    def handle_key(self, key):
        """ Handle UP/DOWN keys to adjust mesh strength. """
        if not hasattr(self, 'spectrum_mesh'): return

        if key == pygame.K_UP:
            # Access the strength_multiplier on the mesh instance
            self.spectrum_mesh.strength_multiplier += 0.1
            print(f"SpectrumMesh Strength: {self.spectrum_mesh.strength_multiplier:.2f}")
        elif key == pygame.K_DOWN:
            self.spectrum_mesh.strength_multiplier -= 0.1
            # Clamp at a minimum of 0
            self.spectrum_mesh.strength_multiplier = max(0.0, self.spectrum_mesh.strength_multiplier)
            print(f"SpectrumMesh Strength: {self.spectrum_mesh.strength_multiplier:.2f}")


SHADERS1 = ["supernova", "milkdrop","starvis","liquidorb"]#,"discosun"]# , "pinkball", "spiralclouds", "warping"]
SHADERS2 = [ "pinkball","kalidoscope","warping", "balatro"]# "spiralclouds", "",cloudflight]

class GLTestScreen1(Frame):
    @property
    def title(self): return 'GLSL Shader Test - Kaleidoscope & SpectrumMesh'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        # Use the new 'meter2' theme which has the cream background
        super().__init__(platform, theme='hifi', padding=0)    

        col = ColFramer(self)
        for shader in SHADERS1:
            col += GLshader(col, shader=shader)


class GLTestScreen2(Frame):
    @property
    def title(self): return 'GLSL Shader Test - Kaleidoscope & SpectrumMesh'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        # Use the new 'meter2' theme which has the cream background
        super().__init__(platform, theme='hifi', padding=0)

        col = ColFramer(self)
        for shader in SHADERS2:
            col += GLshader(col, shader=shader)

class GLTestScreen3(Frame):
    @property
    def title(self): return 'GLSL Shader Test - as a background'

    @property
    def type(self): return 'Test'

    def __init__(self, platform):
        # Use the new 'meter2' theme which has the cream background
        super().__init__(platform, theme='hifi', padding=0, background=BackgroundStyle(colour='background', shader='milkdrop'))       


        SpectrumGlow          = None
        SpectrumReact         = None
        edge = EdgeLightStyle(enabled=True, intensity=0.7, width=0.2, softness=1.2,audio_reactivity=0.0)
        SpectrumBackground    = BackgroundStyle(colour='background', ambient_glow=SpectrumGlow, edge_light=edge,\
                                                texture_path='particles.jpg', texture_opacity=0.6 )
        SimpleOutline         = OutlineStyle(colour='mid', width=1, radius=10, opacity=1.0, glow_intensity=0.0, softness=0.0)
        # Frame.__init__(self, platform, theme= 'hifi', background=SpectrumBackground)

        cols = ColFramer(self,col_ratios=(1,2.2,0.3), padding=0, padpc=0.05)

        artoutline       = OutlineStyle(colour='mid', width=5, radius=10, opacity=1.0, glow_intensity=0.7, softness=0.3)
        cols            += MetaImages(cols, padding=10, art_type='album', background=None, outline=artoutline, opacity=1.0)
 
        centre            = RowFramer(cols, row_ratios=(1.5,3,1), padding=0, padpc=0.0)

        metadata         = RowFramer(centre,padpc=0.0)
        metadata        += MetaData(metadata, metadata_type='track',justify=('left'), colour='foreground')
        metadata        += MetaData(metadata, metadata_type='artist',justify=('left'), colour='light')

        reflection_style = ReflectionStyle(size=0.5, opacity=0.05)
        effects_style    = BarEffects(reflection=reflection_style, threshold=0.6, scale=2.0, alpha=200, blur=1.5)
        bar_style        = BarStyle(led_gap=0, peak_h=2, radius=3, tip=True,flip=False,effects=effects_style)
        spectrum_style   = SpectrumStyle(barw_min=3, barsize_pc=1, barw_max=10, decay=0.2)



        centre           += SpectrumFrame(centre, 'mono', padding=0,bar_style=bar_style, spectrum_style=spectrum_style) 
        # empty Frame to ensure space for the reflection
        centre           += Frame(centre)

        # Add the source and Volume
        volsource        = RowFramer(cols, row_ratios=(1,2), padding=0,padpc=0.0)
        volsource += MetaData(volsource, metadata_type='source', colour='light')
        volsource += MetaData(volsource, metadata_type='volume', colour='foreground')
