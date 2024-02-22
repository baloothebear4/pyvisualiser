"""
    Audio Visualiser programme based on preDAC recorder
    this is a sandpit environment to create ideas for use on preDAC
    but using pygame as a renderer to test on Mac OS

    This version aims to simulate the new display and create a range of visually appealing spectrum
    analysers:  Variables to experiment:
        - smoothing
        - decay profiles
        - peak profiles
        - bars made of rectangles

"""
from    processaudio import AudioProcessor
from    roon import Roon
from    displaydriver import GraphicsDriver
from    screens import *
from    events import Events
from    framecore import ListNext, ScreenController
from    pygame.locals import *   # this pulls down all the K_* constants

FPS = 60 #Frames per second

""" Use this sub class the either stub out or setup the metadata source """
class MetaData(Roon):
    pass

""" HW Platform providing display, audio and physical controls """
class Platform(AudioProcessor, MetaData, GraphicsDriver):
    def __init__(self, events):
        GraphicsDriver.__init__(self, events, FPS)
        AudioProcessor.__init__(self, events)
        MetaData.__init__(self, events, maxwh=self.wh, target_name='MacViz')


    def stop(self):
        self.graphics_end()
        self.stop_capture()
        self.stop_roon()



""" Event processing - this is configured according to the platform/enviroment"""
class EventHandler:        
    def __init__(self, events, platform, screen_handler):

        self.platform          = platform
        self.track_rotate      = False
        """ Setup the event callbacks """
        self.events            = events
        self.events.KeyPress  += self.KeyAction        # when the remote controller is pressed
        self.events.Audio     += self.AudioAction      # respond to a new sample, or audio silence
        self.events.Metadata  += self.MetadataAction   # respond to a changes to meta data
        self.events.Control   += self.ControlAction    # respond controls, start, stop, check, end loop 
        self.events.Screen    += screen_handler        # change screens


    def ControlAction(self, e, text=None):
        if e == 'start':
            self.platform.start_capture()

        elif e =='exit':
            self.platform.stop()

        elif e == 'check':
            self.platform.checkKeys()

        elif e == 'loop_start':
            self.platform.draw_start(text)

        elif e == 'loop_end':
            self.platform.draw_end()

        else:
            print("EventHandler.ControlAction> unknown event ",e)


    def AudioAction(self, e):
        if e == 'capture':
            # print("EventHandler.AudioAction> %d sample buffer underrun, dump old data " % self.audioready)
            self.platform.process()

        else:
            print("EventHandler.AudioAction> unprocessed event ",e)

    def KeyAction(self, key):
        if key == K_SPACE:
            self.events.Screen('exit')

        elif key == K_LEFT:
            self.events.Screen('previous')

        elif key == K_RIGHT:
            self.events.Screen('next')

        elif key == 114:  #R key pressed
            self.track_rotate = not self.track_rotate
            print("EventHandler.KeyAction> R: track screen rotate", self.track_rotate)

        elif key == K_UP:
            print("EventHandler.KeyAction> UP: screen variant scrolling not implemented")

        elif key == K_DOWN:
            print("EventHandler.KeyAction> DOWN: screen variant scrolling not implemented")

        else:
            print("EventHandler.KeyAction> unknown event ",key)
        

    def MetadataAction(self, key):
        print("EventHandler.MetadataAction> event ", key)
        if key == 'start':
            print("EventHandler.MetadataAction> track started")

        elif key == 'new_track':
            print("EventHandler.MetadataAction> new track - pop up display ", key)
            if self.track_rotate: self.events.Screen('next')

        elif key == 'stop':
            print("EventHandler.MetadataAction> track stopped - display nothing new")

        elif key =='trackNotified':
            print("EventHandler.MetadataAction> track notification timeout")

        else:
            print("EventHandler.MetadataAction> unknown event ", key)





""" Screen types are:   Control for utility messages like vol change,  Test to exercise functionality, Base for mixed visual displays """
# TestVUMetersScreen, TestVUScreen,  
# TestScreen, TestVUImageScreen1, TestVisualiserScreen, TestVUMetersScreen, TestVUScreen, TestSpectrumScreen, TestScreen,\
# TestVUScreen, TestVUImageScreen1, TestVUImageScreen2, TestVUMetersScreen, TestSpectrumScreen 

SCREENS = ( ArtistScreen, MetaVUScreen, BigDialsScreen, TrackScreen, TrackSpectrumScreen, TrackSpectrumScreen2, TrackSpectrumScreen3, TrackSpectrumScreen4, \
            TrackOscScreen, TrackVisScreen, TrackVisScreen2, TrackVisScreen3, TrackVUMeterScreen, TrackVUMeterScreen2,  )
    
EVENTS  =  ( 'Control', 'Audio', 'KeyPress', 'Metadata', 'Screen' )   

if __name__ == "__main__":
    events          = Events(EVENTS)
    platform        = Platform(events)
    visualiser      = ScreenController(SCREENS, events, platform)
    EventHandler(events, platform, visualiser.screenEvents)

    try:
        visualiser.run()
    except KeyboardInterrupt:
        pass
