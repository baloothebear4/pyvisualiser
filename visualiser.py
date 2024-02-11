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
from    framecore import ListNext
import  time
from    pygame.locals import *   # this pulls down all the K_* constants



FPS    = 60

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


""" Event processor """
class Controller:
    def __init__(self):

        self.events         = Events(( 'Audio', 'KeyPress', 'Roon'))
        self.platform       = Platform(self.events)

        """ Setup the event callbacks """
        self.events.KeyPress  += self.KeyAction    # when the remote controller is pressed
        self.events.Audio     += self.AudioAction     # respond to a new sample, or audio silence
        self.events.Roon      += self.RoonAction     # respond to a new sample, or audio silence

        """Set up the screen for inital Mode"""
        self.baseScreen     = 'TrackOscScreen'
        self.preScreenSaver = self.baseScreen
        self.status         = 'running'

        """ Set up the screen objects to be used """
        self.screens    = {}  # dict for the screen objects
        self.screenList = { TrackOscScreen, TrackScreen, TrackVUMeterScreen, TrackSpectrumScreen2, TrackSpectrumScreen, TrackVisScreen3, TrackVisScreen2, TrackVisScreen, TrackScreen, TrackSpectrumScreen, TrackVUMeterScreen, \
            TrackVUMeterScreen2, TestVUMetersScreen, TestVUScreen, TrackSpectrumScreen3, TrackVUMeterScreen2 }

            # TestScreen, TestVUImageScreen1, TestVisualiserScreen, TestVUMetersScreen, TestVUScreen, TestSpectrumScreen, TestScreen}#, TestVUScreen, TestVUImageScreen1, TestVUImageScreen2, TestVUMetersScreen, TestSpectrumScreen }

        """ Screen types are:   Control for utility messages like vol change,  Test to exercise functionality, Base for mixed visual displays """

        """ Menu functionality """
        self.menuMode = False
        menuSequence  = []

        for screen in self.screenList:
            self.screens.update( {screen.__name__ : screen(self.platform) })
            if screen.type != 'Control':  #ie create a menu from Test & Base screens
                menuSequence.append(screen.__name__)
        self.screenmenu = ListNext(menuSequence, self.baseScreen)
        print("Controller.__init__> menus intialised", self.screenmenu)

    def setScreen(self, s):
        self.activeScreen = s
        print("Controller.setScreen> active screen is ", s)

    def startAction(self):
        self.setScreen(self.baseScreen)
        self.platform.start_capture()

    def stopAction(self):
        self.platform.stop()


    def AudioAction(self, e):
        if e == 'capture':
            if self.audioready>0:
                print("Controller.AudioAction> %d sample buffer underrun, dump old data " % self.audioready)
            self.platform.process()
            self.audioready +=1

        else:
            print("Controller.AudioAction> unprocessed event ",e)

    def KeyAction(self, key):
        if self.status == 'stopped':
            if key == K_RETURN:
                self.platform.start_capture()
                self.status = 'running'
            elif key == K_SPACE:
                self.status = 'exit'
            else:
                print("KeyAction ", key)
        elif self.status == 'running':
            if key == K_RETURN:
                self.platform.stop_capture()
                self.status = 'stopped'
            elif key == K_SPACE:
                self.status = 'exit'

            elif key == K_LEFT:
                self.baseScreen   = self.screenmenu.next
                self.setScreen(self.baseScreen)

            elif key == K_RIGHT:
                self.baseScreen   = self.screenmenu.prev
                self.setScreen(self.baseScreen)

            elif key == K_UP:
                print("Controller.KeyAction> UP: screen variant scrolling not implemented")
            elif key == K_DOWN:
                print("Controller.KeyAction> DOWN: screen variant scrolling not implemented")
            else:
                print("Key Press ", key)
        else:
            print("Controller.KeyAction> unknown event ",key)

    def RoonAction(self, key):
        print("Controller.RoonAction> event ", key)
        if key == 'new_track' or key == 'start':
            print("Controller.RoonAction> new track - pop up display ", key)
            # self.trackChangeTimer.start()
            # self.activeScreen= 'trackChange'

        elif key == 'stop':
            print("Controller.RoonAction> track stopped - display nothing new")
            # self.platform.clear_track()

        elif key =='trackNotified':
            print("Controller.RoonAction> track notification timeout")
            # self.activeScreen= self.baseScreen

        else:
            print("Controller.RoonAction> unknown event ", key)


    """ Main execution loop """
    def run(self):
        self.startAction()
        self.audioready = 0
        print("Controller.run> startup configured")
        t = time.time()

        # main loop
        while(self.status != 'exit'):
            self.platform.checkKeys()

            if self.audioready>0:

                self.platform.draw_start(self.screens[self.activeScreen].title)
                self.screens[self.activeScreen].draw()
                self.platform.draw_end()

                self.audioready = 0

                # print("run> waited for audio: waited", 1000*(time.time()-t))
                t = time.time()
            else:
                # print("run> waiting for audio: waited", 1000*(time.time()-t))
                time.sleep(1/FPS)

        self.stopAction()



if __name__ == "__main__":
    viz = Controller()
    try:
        viz.run()
    except KeyboardInterrupt:
        pass
