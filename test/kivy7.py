import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.graphics import Rotate, PushMatrix, PopMatrix
from kivy.core.window import Window
from kivy.properties import ObjectProperty

# Set environment variables for a full-screen application
os.environ['KIVY_BCM_DISPMANX_ID'] = '4' # or '3' for HDMI
os.environ['KIVY_FULLSCREEN'] = '1'

class RotatedScreen(FloatLayout):
    """
    A custom layout widget that handles the rotation and centering of its content.
    This class is the key abstraction layer, ensuring the rest of the app
    code remains simple and agnostic to the screen orientation.
    """
    def __init__(self, **kwargs):
        super(RotatedScreen, self).__init__(**kwargs)

        # This will be our main content container. We give it the desired landscape size.
        self.content_box = BoxLayout(orientation='horizontal', padding=50, size=(1280, 400),
                                     size_hint=(None, None))
        
        # Add a simple label to the content box to show it's working
        self.content_box.add_widget(Label(text="Kivy Rotated Screen", font_size='32sp'))

        # Add some test content to show the horizontal layout is working
        self.content_box.add_widget(Label(text="Left side", font_size='24sp'))
        self.content_box.add_widget(Label(text="Center", font_size='24sp'))
        self.content_box.add_widget(Label(text="Right side", font_size='24sp'))
        
        # We need to bind a method to the window size so the content box can be
        # centered and the rotation updated correctly.
        Window.bind(size=self.on_window_size)
        
        # Add the rotation instructions directly to the content box's canvas.
        # This is the key fix that ensures the content is rotated, not the entire window.
        with self.content_box.canvas.before:
            PushMatrix()
            self.rot = Rotate(angle=-90, axis=(0, 0, 1))
        
        with self.content_box.canvas.after:
            PopMatrix()
            
        # Add the content box to this layout
        self.add_widget(self.content_box)
    
    def on_window_size(self, instance, size):
        """
        Called whenever the window size changes.
        This handles centering the content box and updating the rotation origin.
        """
        # Center the content box based on the current window size
        self.content_box.pos = (Window.width / 2 - self.content_box.height / 2, 
                                Window.height / 2 - self.content_box.width / 2)
        
        # We need to manually set the rotation origin to the center of the rotated content
        self.rot.origin = self.content_box.center

class VisualiserApp(App):
    def build(self):
        # The main app simply uses our custom RotatedScreen as its root widget.
        # It doesn't need to know anything about the rotation logic.
        return RotatedScreen()

if __name__ == '__main__':
    VisualiserApp().run()
