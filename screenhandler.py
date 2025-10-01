"""
    Audio Visualiser programme based on preDAC recorder
    this is a sandpit environment to create ideas for use on preDAC
    but using pygame as a renderer to test on Mac OS

    This module manages the events and screen changes
"""
from    processaudio import AudioProcessor
from    roon import Roon
from    displaydriver import GraphicsDriver
from    screens import *
from    events import Events
from    framecore import ListNext
from    pygame.locals import *   # this pulls down all the K_* constants

EVENTS  =  ( 'Control', 'Audio', 'KeyPress', 'Metadata', 'Screen' )   
# for an api - this needs to have inbuilt events and additional events with a binder

""" Use this sub class the either stub out or setup the metadata source """
class MetaData(Roon):
    pass

""" HW Platform providing display, audio and physical controls """
class Platform(AudioProcessor, MetaData, GraphicsDriver):
    def __init__(self, events, hw_platform):
        GraphicsDriver.__init__(self, events, gfx=hw_platform['gfx'])
        AudioProcessor.__init__(self, events, device=hw_platform['loopback'])
        MetaData.__init__(self, events, maxwh=self.wh, target_name=hw_platform['roon_zone'])


    def stop(self):
        print("Platform.stop> shutting down...")
        self.stop_capture()
        print("Platform.stop> shutting down audio")
        self.metadata_stop()
        print("Platform.stop> shutting down metadata")
        self.graphics_end()
        print("Platform.stop> shutting down graphics")




class ScreenController:
    def __init__(self, screens, hw_platform):

        """ Set up the HW platform inc GFS driver, key handling and audio loopback """
        self.events         = Events(EVENTS)
        self.platform       = Platform(self.events, hw_platform)

        """ Setup the event callbacks """
        EventHandler(self.events, self.platform, self.screenEvents)


        """Set up the screen for inital Mode"""
        self.startScreen    = screens[0].__name__
        self.preScreenSaver = self.startScreen
        self.activeScreen   = self.startScreen
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
        self.events.Screen('set', self.startScreen)
        self.events.Control('start')
        loop_count = 0
        CRITICAL_LOOPTIME = (1024000/44100)
        FPS = 50
        print("ScreenController.run> startup configured")

        # main loop
        while(self.activeScreen != 'exit'):
            self.events.Control('check_keys')
            
            if self.activeScreen != 'exit' and self.platform.audio_available:  # The code is reentrant, hence multiple test for exit condition  

                # instument the real-time audio processing to see where the time bottlenecks are
                start_time = time.perf_counter()

                # perform the audio processing
                self.platform.process() 
                self.platform.data_available = False # Reset the flag
                self.audioready = 0
                processing_time_ms = (time.perf_counter() - start_time) * 1000

                # build and update the display
                screen    = self.screens[self.activeScreen]
                self.events.Control('loop_start', text=screen.title + " > " + type(screen).__name__)
                screen.draw()
                drawing_time_ms = ((time.perf_counter() - start_time) * 1000) - processing_time_ms
                self.events.Control('loop_end')
                render_time_ms = ((time.perf_counter() - start_time ) * 1000 ) - drawing_time_ms
                
                self.platform.regulate_fps()

                # analyse the loop time, only display every 2 seconds       
                if loop_count % 20 == 0:
                    loop_time = processing_time_ms + drawing_time_ms + render_time_ms
                    
                    if loop_time > CRITICAL_LOOPTIME: 
                        print("Controller.run> **WARNING** loop time %.2fms exceeds capture time %.2fms, audio processing %.2fms, draw %.2fms, render %.2fms, %.2ffps" % (loop_time, CRITICAL_LOOPTIME, processing_time_ms, drawing_time_ms, render_time_ms, self.platform.clock.get_fps()) )
                    else:    
                        print("Controller.run> loop time: %.2fms, audio processing %.2fms, draw %.2fms, render %.2fms, %.2ffps" % (loop_time, processing_time_ms, drawing_time_ms, render_time_ms, self.platform.clock.get_fps()) )

                    loop_count = 0
                loop_count += 1

        self.events.Control('exit')   

    
 
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

        elif e == 'check_keys':
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
            print("EventHandler.KeyAction> Exiting....")
            self.events.Screen('exit')

        elif key == K_LEFT:
            self.platform.clear_screen()
            self.events.Screen('previous')

        elif key == K_RIGHT:
            self.platform.clear_screen()
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
            self.events.Screen('exit')
        else:
            print("EventHandler.KeyAction> unknown event ",key)
        

    def MetadataAction(self, key):
        # print("EventHandler.MetadataAction> event ", key)
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

       