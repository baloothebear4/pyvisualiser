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
from pyvisualiser.styles.styles             import *

PI = 3.14152


