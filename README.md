# pyvisualiser
A generic music visualisation package intended for use on MacOS, Windows and linux based embedded music players &amp; preamplifiers (eg Raspberry Pi and Volumio/Moode etc). Rich api for eye-catching &amp; customisable music displays inc Spectrum Analysers, VU meters, Visualisations and Metadata (eg from  Roon  or MPD).

The package is in the alpha test stage with a Roon API for use on MacOS desktop.  The first port will be to a Rasberry Pi headless display.

**Installation Instructions (MacOS)**
1. Create a home for the project
  cd path/to/your/project
2. Create a virtual environment to protect your wider config
  python3 -m venv venv
  virtualenv venv
  source venv/bin/activate
3. Clone the package
   git clone https://github.com/baloothebear4/pyvisualiser.git
4. Setup the dependencies
   pip install -r requirements.txt
5. Execute the example visualiser (NB: this is configured for roon metadata, which will require authentication in the roon display/Extensions settings)
   python 3 visualiser.py
6. The left and right arrow keys will allow you to scroll across a number of test screens,  virtually all parameters are configurable.  Spacebar will exit


**Package overview**
The package is intented to be easily portable to different hardware platforms, metadata sources and graphics drivers.  The Alpha version is based on MacOS, roon and pygame.  This can reaily be adapted.  The first port will be Raspberry PI/linux with ALSA & MPD.

The class architecture is as follows:
1. **Controller** - top level control logic.  For example in embedded preamplifers with physicall controls the events are used to drive the overall screen behaviours.  This is a simple event driven based control logic.  This runs a main loop at the Frames Per Second of the display after first instantiating all the display screens (each a Class).  The events then update the metadata used in each screen refresh.
2. **Screens** - A simple geometry class manages all the positional data associated with a Frame.  A Frame is a heirarchical class, Frames of Frames is the way to construct the overall display - with the Screen being the top level class.
3. **Frame** classes - lower down Frames comprise classes that go the conversion from realtime audio samples into graphical functions. Everything is relative which makes creating complex displays very straightforward. For example VUFrame, SpectrumFrame (based on fast fourier transforms).  This include smoothing classes that significantly improve the look of the display.
4. **Geometry** class - this is a base class used to do all coordinate, circular, resize etc functions on a frame.  For example where a drawing component (eg text) is left/top aligned within a frame
5. **Display Driver** classes - these comprise lower level components that use geometry too and are directly responsible for writing to the display via the graphics driver.  A rich set of drawing components including lines, bars, boxes and images.  Only this file needs to be changed to port to another graphics package eg pygame, tkinter, Kivy, PyQT etc.
6. **ProcessAudio** classes - these use pyaudio to capture frames and process the samples into RMS values for VU or ffts for spectrum analysers.  These are configurable for the number of octaves and frequency.  Filters are available too.
7. **Roon** classes - this is based on pyroon and creates a set of attributes for displaying metadata eg Album art, track titles etc.  An MPD version of this exists too and will be uploaded in the Beta

Here are some example test screens, some screens with multiple test screens:
<img width="1280" alt="IMG_0872" src="https://github.com/baloothebear4/pyvisualiser/assets/13680355/c34503cb-27e0-432d-b0e5-0b425baca7df">
<img width="1278" alt="IMG_4629" src="https://github.com/baloothebear4/pyvisualiser/assets/13680355/43182ad4-0f68-4404-8bc5-1a03b75bceaa">
<img width="1278" alt="IMG_9947" src="https://github.com/baloothebear4/pyvisualiser/assets/13680355/a27c28a6-7423-4110-b5d3-e0119ac36b31">
<img width="1276" alt="IMG_2570" src="https://github.com/baloothebear4/pyvisualiser/assets/13680355/baa544bc-55a1-4a7d-bc03-f84d873d10c6">
<img width="1277" alt="IMG_5514" src="https://github.com/baloothebear4/pyvisualiser/assets/13680355/c5a655c7-c769-4649-8047-7d2d8aa16d7d">
<img width="1278" alt="IMG_6812" src="https://github.com/baloothebear4/pyvisualiser/assets/13680355/37d28da0-36f0-4493-b610-f2a7ea1cdbe7">
<img width="1282" alt="IMG_4973" src="https://github.com/baloothebear4/pyvisualiser/assets/13680355/e6fc5ddf-9577-4c3c-969e-4ab48f587c77">


Collaboration welcome!

I want to give credit to https://github.com/project-owner/PeppyMeter  for use of some of the VU images.  These have been incorporated as VU meter images
