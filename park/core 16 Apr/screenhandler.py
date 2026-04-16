"""
    Audio Visualiser programme based on preDAC recorder
    this is a sandpit environment to create ideas for use on preDAC
    but using pygame as a renderer to test on Mac OS

    This module manages the events and screen changes
"""
from    pyvisualiser.core.processaudio import AudioProcessor
from    pyvisualiser.endpoints.roon import Roon
from    pyvisualiser.core.displaydriver import GraphicsDriver

from    pyvisualiser.core.framecore import ListNext
from    pygame.locals import *   # this pulls down all the K_* constants
import  time
from    events import Events
import  numpy as np

# from    screens import *


EVENTS  =  ( 'Control', 'Audio', 'KeyPress', 'Metadata', 'Screen' )   
# for an api - this needs to have inbuilt events and additional events with a binder

""" Use this sub class the either stub out or setup the metadata source """
class MetaData(Roon):
    pass

class HWInterface():
    """ Base class for Hardware Interface """
    def __init__(self):
        self._volume_pc        = 40.0
        self.audio_source     = "Roon"
        self.audio_sample_rate    = "44.1kHz 16bit"
        self.audio_format     = "flac"
        

    def volume(self, format='percent'):
        if format == 'db':
            return "%.1fdB" % self.volume_db
        else:
            return "%d" % self.volume_pc
        
    @property
    def volume_pc(self):
        #in time a call to the base HW is needed to read the actual volume setting
        return self._volume_pc

    @volume_pc.setter
    def a(self, val):
        if val >= 0 and val <= 100:
            self.volume_pc = int(val)
        else:
            raise ValueError('set.volume_pc > value exceed bounds ', val)        

    @property
    def volume_db(self):
        return 20*np.log10(self.volume_pc)


    def source(self):
        #in time a call to the base HW is needed to read the actual volume setting
        return self.audio_source
    
    def sample_rate(self):
        #in time a call to the base HW is needed to read the actual volume setting
        return self.audio_sample_rate
    
    def format(self):
        #in time a call to the base HW is needed to read the actual volume setting
        return self.audio_format    

""" HW Platform providing display, audio and physical controls """
class Platform(AudioProcessor, MetaData, GraphicsDriver, HWInterface):
    def __init__(self, events, hw_platform):
        GraphicsDriver.__init__(self, events, gfx=hw_platform['gfx'])
        AudioProcessor.__init__(self, events, device=hw_platform['loopback'])
        MetaData.__init__(self, events, maxwh=self.wh, target_name=hw_platform['roon_zone'])
        HWInterface.__init__(self)

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
        EventHandler(self.events, self.platform, self.screenEvents, self.keyEvents)


        """Set up the screen for inital Mode"""
        self.startScreen    = screens[0].__name__
        self.preScreenSaver = self.startScreen
        self.activeScreen   = self.startScreen
        self.screens        = {}    # dict for the screen objects
        self.full_update    = True  # force everything to be drawn, else only draw what has changed

        """ Menu functionality - sort out Control (temporary) from main (base) screens"""
        menuSequence  = []
        for screen in screens:
            self.screens.update( {screen.__name__ : screen(self.platform) })
            is_not_control_screen = hasattr(screen, 'type') and screen.type != 'Control' 
            # if is_not_control_screen:  #ie create a menu from Test & Base screens
            menuSequence.append(screen.__name__)
            print("ScreenController.__init__> intialised screen --> FIX TO EXCLUDE TEST & CONTROL SCREENS", screen.__name__)

        self.screenmenu = ListNext(menuSequence, self.startScreen)


 

    def screenEvents(self, e, option=None):
        if e == 'set':
            self.activeScreen = option
            self.full_update  = True  # force everything to be drawn, else only draw what has changed
            print("ScreenController.self.events.Control('set',> active screen is ", option)

        elif e == 'next':
            self.baseScreen   = self.screenmenu.next
            self.activeScreen = self.baseScreen
            self.full_update  = True  # force everything to be drawn, else only draw what has changed
            print("\nScreenController.self.events.Control('next',> active screen is ", self.activeScreen)

        elif e == 'previous':
            self.baseScreen   = self.screenmenu.prev
            self.activeScreen = self.baseScreen
            self.full_update  = True  # force everything to be drawn, else only draw what has changed
            print("\nScreenController.self.events.Control('previous',> active screen is ", self.activeScreen)

        elif e == 'new_track':
            self.full_update  = True  # force everything to be drawn

        elif e == 'exit':
            self.activeScreen = 'exit'

    def keyEvents(self, key):
        from pyvisualiser.styles.profiles import ProfileManager
        from pyvisualiser.styles.presets import LUXURY_PROFILE, NEON_PROFILE, MINIMAL_PROFILE

        controller = ProfileManager.get_controller()
        # print(f"ScreenController.keyEvents> key={key} id(controller)={id(controller)}")

        # Keyboard Render Stage Debugging (1-4)
        if key == K_1: 
            self.platform.compositor.debug_view = None
            print("RenderStage> FULL SCENE")
        elif key == K_2: 
            self.platform.compositor.debug_view = 'bg'
            print("RenderStage> BACKGROUNDS ONLY (Check alpha mask)")
        elif key == K_3: 
            self.platform.compositor.debug_view = 'ui'
            print("RenderStage> UI GEOMETRY ONLY")
        elif key == K_4: 
            self.platform.compositor.debug_view = 'glow'
            print("RenderStage> EXTRACTED GLOW BUFFER")

        # --- HUD Navigation and Adjustment (New) ---
        elif key == K_UP:    controller.select_prev()
        elif key == K_DOWN:  controller.select_next()
        elif key == K_LEFT:  controller.adjust(None, -0.1)
        elif key == K_RIGHT: controller.adjust(None, 0.1)

        # --- Standard Mappings (Using constants for robustness) ---
        elif key == K_q: controller.adjust('intensity', 0.1)
        elif key == K_a: controller.adjust('intensity', -0.1)
        elif key == K_w: controller.adjust('softness', 0.1)
        elif key == K_s: controller.adjust('softness', -0.1)
        elif key == K_e: controller.adjust('energy', 0.1)
        elif key == K_d: controller.adjust('energy', -0.1)
        elif key == K_r: controller.adjust('depth', 0.1)
        elif key == K_f: controller.adjust('depth', -0.1)
        elif key == K_t: controller.adjust('vignette', 0.1)
        elif key == K_g: controller.adjust('vignette', -0.1)
        elif key == K_y: controller.adjust('sharpness', 0.1)
        elif key == K_h: controller.adjust('sharpness', -0.1)
        elif key == K_z: controller.adjust('threshold', 0.1)
        elif key == K_x: controller.adjust('threshold', -0.1)
        elif key == K_c: controller.adjust('warmth', 0.1)
        elif key == K_v: controller.adjust('warmth', -0.1)
        elif key == K_b: controller.adjust('saturation', 0.1)
        elif key == K_n: controller.adjust('saturation', -0.1)
        elif key == K_l: self.platform.toggle_debug_hud()

        elif self.activeScreen in self.screens:
            self.screens[self.activeScreen].handle_key(key)

        else: 
            print("ScreenController.keyEvents: unknown event", key)

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
            
            if self.activeScreen != 'exit':  

                # 1. Drain all pending audio frames from the queue (non-blocking)
                #    If there's multiple chunks, process them to catch up.
                audio_processed_ms = 0.0
                start_audio = time.perf_counter()
                
                # is_audio_available() grabs one chunk off the queue and updates mono/left/right structures
                # Because audio buffer comes in chunks like 2048 at 44.1kHz (21 FPS),
                # we only want to process what has arrived, but draw regardless to preserve smooth 60fps UI decay
                did_audio_update = False
                while self.platform.is_audio_available():
                    self.platform.process() 
                    self.platform.data_available = False # Reset the flag
                    self.audioready = 0
                    did_audio_update = True
                    
                processing_time_ms = (time.perf_counter() - start_audio) * 1000

                # 2. Draw and Render the Frame
                start_draw = time.perf_counter()
                
                # build and update the display
                screen = self.screens[self.activeScreen]
                title = screen.title + " > " + type(screen).__name__ if hasattr(screen, 'title') else type(screen).__name__
                self.events.Control('loop_start', text=title)

                screen.update_screen()
                drawing_time_ms = (time.perf_counter() - start_draw) * 1000

                self.events.Control('loop_end')
                render_time_ms = ((time.perf_counter() - start_draw) * 1000) - drawing_time_ms
                
                # 3. Rest to maintain target lock FPS (e.g 60Hz)
                self.platform.regulate_fps()
                self.full_update = False  # Only draw what has changed

                # 4. Telemetry
                if loop_count % self.platform.FPS == 0:
                    loop_time = processing_time_ms + drawing_time_ms + render_time_ms
                    
                    if loop_time > CRITICAL_LOOPTIME: 
                        print("Controller.run> **WARNING** loop time %.2fms exceeds capture time %.2fms, audio %.2fms, draw %.2fms, render %.2fms, %.2ffps, %.2f%%" % 
                              (loop_time, CRITICAL_LOOPTIME, processing_time_ms, drawing_time_ms, render_time_ms, self.platform.clock.get_fps(), self.platform.area_drawn()) )
                    elif self.platform.clock.get_fps() < self.platform.FPS * 0.9:
                        print("Controller.run> loop time: %.2fms, audio %.2fms, draw %.2fms, render %.2fms, %.2ffps, %.1f%%" % 
                              (loop_time, processing_time_ms, drawing_time_ms, render_time_ms, self.platform.clock.get_fps(), self.platform.area_drawn()) )
                    loop_count = 0
                loop_count += 1

        self.events.Control('exit')   

    def stop(self):
        self.platform.stop()
    
 
""" Event processing - this is configured according to the platform/enviroment"""
class EventHandler:        
    def __init__(self, events, platform, screen_handler,key_handler=None):

        self.platform          = platform
        self.track_rotate      = False
        """ Setup the event callbacks """
        self.events            = events
        self.events.KeyPress  += self.KeyAction        # when the remote controller is pressed
        self.events.Audio     += self.AudioAction      # respond to a new sample, or audio silence
        self.events.Metadata  += self.MetadataAction   # respond to a changes to meta data
        self.events.Control   += self.ControlAction    # respond controls, start, stop, check, end loop 
        self.events.Screen    += screen_handler        # change screens
        self.key_handler       = key_handler


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
        elif e in ('signal_detected', 'silence_detected'):
            pass

        else:
            print("EventHandler.AudioAction> unprocessed event ",e)

    def KeyAction(self, key):
        if key == K_SPACE:
            print("EventHandler.KeyAction> Exiting....")
            self.events.Screen('exit')

        elif key == K_LEFT:
            if getattr(self.platform, 'show_debug_hud', False):
                # Pass to HUD adjustment
                if self.key_handler: self.key_handler(key)
            else:
                self.platform.clear_screen()
                self.events.Screen('previous')

        elif key == K_RIGHT:
            if getattr(self.platform, 'show_debug_hud', False):
                # Pass to HUD adjustment
                if self.key_handler: self.key_handler(key)
            else:
                self.platform.clear_screen()
                self.events.Screen('next')

        elif key == 114:  #R key pressed
            self.track_rotate = not self.track_rotate
            print("EventHandler.KeyAction> R: track screen rotate", self.track_rotate)

        # elif key == K_UP:
        #     print("EventHandler.KeyAction> UP: screen variant scrolling not implemented")

        # elif key == K_DOWN:
        #     print("EventHandler.KeyAction> DOWN: screen variant scrolling not implemented")

        elif key == 'exit':
            print("EventHandler.KeyAction> quit")
            self.events.Screen('exit')
        else:
            # Pass other keys to the screen controller (and thus the active screen)
            if self.key_handler:
                self.key_handler(key)
            else:
                print("EventHandler.KeyAction> unknown event ",key)
        

    def MetadataAction(self, key):
        # print("EventHandler.MetadataAction> event ", key)
        if key == 'start':
            print("EventHandler.MetadataAction> track started")

        elif key == 'new_track':
            print("EventHandler.MetadataAction> new track - pop up display ", key)
            self.events.Screen('new_track')
            if self.track_rotate: self.events.Screen('next')

        elif key == 'stop':
            print("EventHandler.MetadataAction> track stopped - display nothing new")

        elif key =='trackNotified':
            print("EventHandler.MetadataAction> track notification timeout")

        else:
            print("EventHandler.MetadataAction> unknown event ", key)

       