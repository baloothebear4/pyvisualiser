import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.config import Config
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Rotate, PushMatrix, PopMatrix, Translate
from kivy.core.text import Label as CoreLabel

# Set environment variables for display to match your setup
os.environ['KIVY_BCM_DISPMANX_ID'] = '4' # or '3' for HDMI, check your setup
os.environ['KIVY_FULLSCREEN'] = '1'

class RotationTestApp(App):
    def build(self):
        # We will not set the window size directly, but get the size reported by the OS.
        # This will be the 400x1280 portrait dimension.
        
        # Use a FloatLayout for precise positioning of the rotated content.
        root_layout = FloatLayout()
        
        # This is our virtual canvas, with the correct landscape dimensions.
        # This BoxLayout is where all our content will go.
        content_box = BoxLayout(orientation='horizontal', padding=50, size=(1280, 400))
        
        # A label to show the expected size.
        self.expected_size_label = Label(text="Expected Size: 1280 x 400", font_size='32sp')
        content_box.add_widget(self.expected_size_label)

        # A label to show the current window size
        self.size_label = Label(text=self.get_size_text(), font_size='32sp')
        content_box.add_widget(self.size_label)

        # A label to show the current orientation (landscape or portrait)
        self.orientation_label = Label(text=self.get_orientation_text(), font_size='32sp')
        content_box.add_widget(self.orientation_label)

        # Bind the window size to a method so the labels update automatically
        Window.bind(size=self.on_window_size)
        
        # Add the content box to the root layout
        root_layout.add_widget(content_box)
        
        # Use a transform to rotate the content_box.
        # This will "undo" the system's rotation.
        # We need to do this after the content_box is added to its parent.
        with content_box.canvas.before:
            PushMatrix()
            # Rotate by -90 degrees to make content appear landscape
            self.rot = Rotate(angle=-90, axis=(0, 0, 1))
            # Center the rotated widget on the screen
            self.trans = Translate(x=Window.width / 2, y=Window.height / 2)
            
        with content_box.canvas.after:
            PopMatrix()
        
        # Set the origin of the rotation
        self.rot.origin = (content_box.center_x, content_box.center_y)
        
        # This is where the magic happens. We'll set the initial position of the box
        # and then bind a function to the window size to keep it centered.
        content_box.pos = (Window.width / 2 - content_box.width / 2, Window.height / 2 - content_box.height / 2)
        
        return root_layout
    
    def on_window_size(self, window, size):
        # Update the labels
        self.size_label.text = self.get_size_text()
        self.orientation_label.text = self.get_orientation_text()
        
        # Update the rotation origin and translation to keep it centered.
        self.rot.origin = (Window.width / 2, Window.height / 2)
        self.trans.x = Window.width / 2
        self.trans.y = Window.height / 2

        # Update the position of the content box.
        self.root.children[0].pos = (Window.width / 2 - self.root.children[0].width / 2, Window.height / 2 - self.root.children[0].height / 2)
        
    def get_size_text(self):
        # We get the window size from Kivy's window object.
        return f"Window Size: {Window.width} x {Window.height}"

    def get_orientation_text(self):
        # We determine the orientation based on the window size.
        if Window.width > Window.height:
            return "Orientation: Landscape"
        else:
            return "Orientation: Portrait"

if __name__ == '__main__':
    RotationTestApp().run()
