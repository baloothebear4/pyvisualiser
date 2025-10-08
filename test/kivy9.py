import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.graphics import Rotate, PushMatrix, PopMatrix, Translate
from kivy.core.window import Window

# Set environment variables for a full-screen application
os.environ['KIVY_BCM_DISPMANX_ID'] = '4'
os.environ['KIVY_FULLSCREEN'] = '1'

class RotatedApp(App):
    def build(self):
        """
        Initial build method. This creates a simple, non-rotated layout.
        The initial screen will be tall and thin.
        """
        self.root_box = BoxLayout(orientation='vertical', padding=100, spacing=20,
                                 size_hint=(None, None), size=(400, 1280),
                                 pos=(0, 0))

        # Add a diagnostic label
        self.status_label = Label(text="Initial State: No Rotation", font_size='24sp',
                                  size_hint_y=None, height=50)
        self.root_box.add_widget(self.status_label)
        
        # This is the test content that we will rotate
        self.content_label = Label(text="Press 'r' to rotate", font_size='32sp')
        self.root_box.add_widget(self.content_label)

        # Bind the keyboard event to our method
        Window.bind(on_key_down=self.on_key_down)

        print("--- Initial Diagnostic ---")
        print(f"Kivy Window Size: {Window.size}")
        print(f"Content Box Size: {self.root_box.size}")
        print("--------------------------")

        return self.root_box

    def on_key_down(self, window, key, scancode, codepoint, modifier):
        """
        Handles key presses. When 'r' is pressed, it applies the rotation.
        """
        # Check if the 'r' key was pressed
        if codepoint == 'r':
            print("--- Applying Rotation ---")
            print(f"Key '{codepoint}' pressed. Applying -90 degree rotation.")

            # This is the key part: applying graphics instructions to the canvas
            with self.root_box.canvas.before:
                PushMatrix()
                self.trans = Translate(x=0, y=0)
                self.rot = Rotate(angle=-90, axis=(0, 0, 1), origin=(0, 0))

            with self.root_box.canvas.after:
                PopMatrix()

            # Update the widget's properties to handle the new rotated state
            self.root_box.size = (1280, 400)
            self.root_box.orientation = 'horizontal'

            # Update the diagnostic label
            self.status_label.text = "State: Rotated"
            self.content_label.text = "This should be a wide box!"

            # Re-center the widget on the new window
            self.on_window_size(None, Window.size)

            print(f"New Content Box Size: {self.root_box.size}")
            print("Rotation applied. Expect a wide, short box.")
            print("-------------------------")

    def on_window_size(self, instance, size):
        """
        Handles centering the box based on the window size.
        """
        # We must center the translated and rotated content.
        # This calculation accounts for the width/height swap after rotation.
        self.root_box.pos = (Window.width / 2 - self.root_box.width / 2, 
                             Window.height / 2 - self.root_box.height / 2)


if __name__ == '__main__':
    RotatedApp().run()
