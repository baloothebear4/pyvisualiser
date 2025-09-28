"""
    Audio Visualiser programme based on preDAC recorder
    this is a sandpit environment to create ideas for use on preDAC
    but using pygame as a renderer to test on Mac OS

    This module manages the events and screen changes
"""
from    processaudio import AudioProcessor
from    roon import Roon
from    displaydriver import GraphicsDriverMac
from    screens import *
from    events import Events
from    framecore import ListNext
from    screenhandler import ScreenController, EventHandler
from    pygame.locals import *   # this pulls down all the K_* constants

FPS = 30 #Frames per second


""" Use this sub class the either stub out or setup the metadata source """
class MetaData(Roon):
    pass

""" HW Platform providing display, audio and physical controls """
class Platform(AudioProcessor, MetaData, GraphicsDriverMac):
    def __init__(self, events):
        GraphicsDriverMac.__init__(self, events, FPS)
        AudioProcessor.__init__(self, events, device='BlackHole 2ch')
        MetaData.__init__(self, events, maxwh=self.wh, target_name='MacViz')


    def stop(self):
        self.graphics_end()
        self.stop_capture()
        self.stop_roon()


class ScreenController:
    def __init__(self, screens, hw_platform):

        """Set up the screen for inital Mode"""
        self.startScreen    = screens[0].__name__
        self.preScreenSaver = self.startScreen
        self.activeScreen   = self.startScreen
        self.events         = events
        self.platform       = platform

        """ Setup the event callbacks """
        events          = Events(EVENTS)
        platform        = Platform(events)

        EventHandler(events, platform, visualiser.screenEvents)

        """ Set up the screen objects to be used """
        self.screens    = {}  # dict for the screen objects

        """ Menu functionality - sort out Control (temporary) from main (base) screens"""
        menuSequence  = []
        for screen in screens:
            self.screens.update( {screen.__name__ : screen(self.platform) })
            if screen.type != 'Control':  #ie create a menu from Test & Base screens
                menuSequence.append(screen.__name__)
        self.screenmenu = ListNext(menuSequence, self.startScreen)
        print("ScreenController.__init__> menus intialised", self.screenmenu)

 

    def screenEvents(self, e, option=None):
        if e == 'set':
            self.activeScreen = option
            print("ScreenController.self.events.Control('set',> active screen is ", option)

        elif e == 'next':
            self.baseScreen   = self.screenmenu.next
            self.activeScreen = self.baseScreen

        elif e == 'previous':
            self.baseScreen   = self.screenmenu.prev
            self.activeScreen = self.baseScreen

        elif e == 'exit':
            self.activeScreen = 'exit'

        else: 
            print("ScreenController.screenEvents: unknown event", e)

    """ Main execution loop """
    def run(self):
        self.exit = False
        self.events.Control('set', self.startScreen)
        self.events.Control('start')
        print("ScreenController.run> startup configured")

        # main loop
        while(self.activeScreen != 'exit'):
            self.events.Control('check')
            if self.activeScreen != 'exit':  # The code is reentrant, hence multiple test for exit condition  
                screen    = self.screens[self.activeScreen]
                self.events.Control('loop_start', text=screen.title + " > " + type(screen).__name__)
                screen.draw()
                self.events.Control('loop_end')

        self.events.Control('exit')   

 
 """ Event processing - this is configured according to the platform/enviroment"""

EVENTS  =  ( 'Control', 'Audio', 'KeyPress', 'Metadata', 'Screen' )   
# for an api - this needs to have inbuilt events and additional events with a binder
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
        elif key == 'exit':
            print("EventHandler.KeyAction> quit")
            exit()
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

       