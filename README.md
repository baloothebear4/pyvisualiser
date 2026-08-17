# pyvisualiser

> Transform your hardware project or desktop playback into a stunning visual experience. **`pyvisualiser`** is a high-performance, GPU-accelerated Python framework designed to render real-time audio visualisations. Whether you are building an eye-catching desktop visualiser or designing an embedded front-panel UI for Hi-Fi preamplifiers, custom Linux streamers (e.g., Raspberry Pi with Volumio/Moode), or smart audio equipment, `pyvisualiser` gives you total creative control.

---

## ✨ Features & Capabilities

* **Real-Time Audio Analysis**: Multi-band FFT spectrum analysers, responsive segmented or solid LED VU meters, classic skeuomorphic analogue needle meters, oscillograms, and concentric radial display engines ("Diamondiser").
* **Shader & Background FX**: GPU-accelerated GLSL shader passes featuring starfields, vapor clouds, film grain, vignette, ambient glow, and audio-reactive peak flashes.
* **Rich Media & Metadata Integration**: Render album artwork, artist portraits, dynamic track properties, and playback progress indicators with hardware-like segmented LED bars (supports audio engines like Roon and MPD).
* **Flexible Layout Architecture**: Hierarchical layout system using declarative column/row framers (`ColFramer`, `RowFramer`) with relative coordinate scaling, automatic aspect ratio preservation, and customizable themes.
* **Cross-Platform Rendering**: Support for OpenGL compositing on macOS/Windows/Linux as well as direct Raspberry Pi native KMS framebuffer pipelines (`pi_kms`).
* **Endpoint integration**: Roon, [TBC- UPNP, Airplay2, Spotify]

---

## ⚡ Quick Start Code Example

Building a multi-panel studio dashboard requires only a few lines of declarative Python code to create this



### python

    class ArtMetadataScreen(Frame):

        def __init__(self, parent):
            Frame.__init__(self, parent, theme='hifi', background=ScreenBackground)

            ''' 2 Cols: 
                    Reflected album art on left, 
                    5 rows: Full MetaData, Playprogress, Spectrum. 
                VolumeSource overlaid on right '''

            cols  = ColFramer(self, col_ratios=(4,7,1), padding=10, padpc=0.0)

            image = RowFramer(cols,row_ratios=(4,1), outline=None)
            image += MetaImages(image,  'album',padding=0, reflection=True,\            
                        background=BackgroundStyle(colour='background', colour_opacity=1.0), \
                        outline=OutlineStyle(width=0, softness=1.8, glow_intensity=0.2,\
                        glow_colour='foreground'))
            image += Frame(image) # blank padding space for the reflection

            rows  = RowFramer(cols, row_ratios=(3,1), padpc=0.05,padding=5)
            rows += MetaDataFrame(rows, justify='left')
            rows  += SpectrumFrame(rows,channel='mono', \
                        bar_style=BarStyle(led_gap=0), \
                        spectrum_style=SpectrumStyle(barsize_pc=4))

            cols += Frame(cols) # blank frame to pad the volume source on the right
            self += VolumeSource(self)
## 📖 API Reference & Documentation
For detailed architecture breakdowns, class constructors, parameters, and style configuration references, see the comprehensive API Reference Guide included in this repository.

## 🛠️ Installation Instructions

1. Create a home for the project
   
`cd path/to/your/project`

3. Create a virtual environment to protect your wider config

`python3 -m venv .venv`

`source venv/bin/activate`

4. Clone the package
   
`git clone https://github.com/baloothebear4/pyvisualiser.git`
   
6. Setup the dependencies
   
`pip install -r requirements.txt`
   
8. Execute the example visualiser (NB: this is configured for roon metadata, which will require authentication in the roon display/Extensions settings)

`python 3.11 tests/vis.py`
  
9. The left and right arrow keys will allow you to scroll across a number of test screens,  virtually all parameters are configurable.  Spacebar will exit


Roon Integration: If using Roon metadata, ensure your Roon core is running and authorize pyvisualiser under Roon Settings -> Extensions.


## 🤝 Contributing & Acknowledgments
Collaborators are welcome! Feel free to open issues or submit pull requests for new layout widgets, audio DSP drivers, or GLSL background shaders.

Special thanks to the PeppyMeter project for analogue meter image assets incorporated into this package.