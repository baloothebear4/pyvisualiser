import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.label import Label
from kivy.graphics import Rotate, PushMatrix, PopMatrix, Translate
from kivy.core.window import Window

# Set environment variables for a full-screen application
os.environ['KIVY_BCM_DISPMANX_ID'] = '4'
os.environ['KIVY_FULLSCREEN'] = '1'

class RotatedScreen(RelativeLayout):
    """
    A custom widget that handles all the rotation logic for its children.
    It expects the physical screen to be 400x1280 and rotates the content
    to a landscape 1280x400 view.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_rotated = False

        # Create the graphics instructions once, so we can modify them later
        with self.canvas.before:
            PushMatrix()
            self.rot = Rotate(angle=0, axis=(0, 0, 1), origin=(0, 0))
            self.trans = Translate(x=0, y=0)

        with self.canvas.after:
            PopMatrix()

        # Bind the window size event and key press event
        Window.bind(size=self.update_transformation)
        Window.bind(on_key_down=self.on_key_down)

    def on_key_down(self, window, key, scancode, codepoint, modifier):
        """Handles key presses. When 'r' is pressed, it toggles the rotation."""
        if codepoint == 'r':
            self.is_rotated = not self.is_rotated
            self.update_transformation(None, Window.size)

    def update_transformation(self, instance, size):
        """Recalculates the translation and rotation based on the screen size."""
        window_width, window_height = size

        if self.is_rotated:
            # We want to rotate the content to landscape
            self.rot.angle = -90
            self.rot.origin = (0, 0) # Rotate around the top-left corner
            
            # Translate to compensate for the rotation and keep the content on-screen
            self.trans.x = 0
            self.trans.y = window_width
            
            print(f"Applying -90 degree rotation. Window size: {size}")
            print(f"Translation: ({self.trans.x}, {self.trans.y})")
        else:
            # When not rotated, reset to normal portrait view
            self.rot.angle = 0
            self.trans.x = 0
            self.trans.y = 0
            
            print(f"Resetting to 0 degree rotation. Window size: {size}")
            print(f"Translation: ({self.trans.x}, {self.trans.y})")


class RotatedApp(App):
    def build(self):
        """Builds the root widget and the content."""
        self.rotated_screen = RotatedScreen()

        # This is the content that will be rotated. Its size is what we want
        # for our final landscape view.
        self.content_box = BoxLayout(orientation='horizontal', padding=100, spacing=20)
        self.content_box.size_hint = (None, None)
        self.content_box.size = (1280, 400)
        self.content_box.pos_hint = {'center_x': 0.5, 'center_y': 0.5}

        # Add a diagnostic label
        self.status_label = Label(text="Initial State: No Rotation", font_size='24sp')
        self.content_box.add_widget(self.status_label)
        
        # This is the test content that we will rotate
        self.content_label = Label(text="Press 'r' to rotate", font_size='32sp')
        self.content_box.add_widget(self.content_label)

        # Add the content to our custom container
        self.rotated_screen.add_widget(self.content_box)
        
        # Call the initial update to set the state
        self.rotated_screen.update_transformation(None, Window.size)

        print("--- Initial Diagnostic ---")
        print(f"Kivy Window Size: {Window.size}")
        print("--------------------------")

        return self.rotated_screen

if __name__ == '__main__':
    RotatedApp().run()
