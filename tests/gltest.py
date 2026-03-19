'''
Test file for glsl based visualisers


'''

import pygame

from pyvisualiser.visualisers.glvisualisers import *
from pyvisualiser.styles.presets import *
from pyvisualiser.styles.styles  import *
from pyvisualiser.core.framecore  import Frame, RowFramer, ColFramer
from pyvisualiser.visualisers.frames import MetaDataFrame, PlayProgressFrame, TextFrame


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


SHADERS1 = ["supernova", "milkdrop","starvis"]#,"discosun"]# , "pinkball", "spiralclouds", "warping"]
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