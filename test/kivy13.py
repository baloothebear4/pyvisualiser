import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
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
        self.is_rotated = False

        self.root_box = BoxLayout(orientation='vertical', padding=100, spacing=20)
        
        # Add a diagnostic label
        self.status_label = Label(text="Initial State: No Rotation", font_size='24sp',
                                  size_hint_y=None, height=50)
        self.root_box.add_widget(self.status_label)
        
        # This is the test content that we will rotate
        self.content_label = Label(text="Press 'r' to rotate", font_size='32sp')
        self.root_box.add_widget(self.content_label)

        # Bind the keyboard and window size events
        Window.bind(on_key_down=self.on_key_down)

        # Update the display to its initial state
        self.update_display()

        print("--- Initial Diagnostic ---")
        print(f"Kivy Window Size: {Window.size}")
        print("--------------------------")

        return self.root_box

    def on_key_down(self, window, key, scancode, codepoint, modifier):
        """
        Handles key presses. When 'r' is pressed, it toggles the rotation.
        """
        # Check if the 'r' key was pressed
        if codepoint == 'r':
            print("--- Toggling Rotation ---")
            self.is_rotated = not self.is_rotated
            self.update_display()

    def update_display(self):
        """
        Handles updating the display based on the rotation state and window size.
        """
        if self.is_rotated:
            # Set the window and box to landscape dimensions
            Window.size = (1280, 400)
            self.root_box.orientation = 'horizontal'
            
            # Update diagnostic labels
            self.status_label.text = "State: Rotated"
            self.content_label.text = "This should be a wide box!"

            print(f"Applying -90 degree rotation. Expect wide, short box.")
            print(f"New Kivy Window Size: {Window.size}")
        else:
            # Set the window and box to portrait dimensions
            Window.size = (400, 1280)
            self.root_box.orientation = 'vertical'
            
            # Update diagnostic labels
            self.status_label.text = "Initial State: No Rotation"
            self.content_label.text = "Press 'r' to rotate"
            
            print(f"Resetting to original state. Expect tall, thin box.")
            print(f"New Kivy Window Size: {Window.size}")
        
        print("-------------------------")

if __name__ == '__main__':
    RotatedApp().run()
