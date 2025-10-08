import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.config import Config
from kivy.core.window import Window

# Set environment variables for display to match your setup
os.environ['KIVY_BCM_DISPMANX_ID'] = '4' # or '3' for HDMI, check your setup
os.environ['KIVY_FULLSCREEN'] = '1'

# To test Kivy's rotation ability, you can uncomment this line.
# A value of 90, -90, or 180 will rotate the display.
# Config.set('graphics', 'rotation', '90')

class RotationTestApp(App):
    def build(self):
        # Manually set the window size to our desired landscape dimensions.
        Window.size = (1280, 400)

        # The root widget will be a BoxLayout which automatically manages
        # the layout of its children based on window size.
        # We set the orientation to 'horizontal' for our landscape view.
        layout = BoxLayout(orientation='horizontal', padding=50)

        # A label to show the window size we forced.
        self.expected_size_label = Label(text=self.get_expected_size_text(), font_size='32sp')
        layout.add_widget(self.expected_size_label)

        # A label to show the current window size
        self.size_label = Label(text=self.get_size_text(), font_size='32sp')
        layout.add_widget(self.size_label)

        # A label to show the current orientation (landscape or portrait)
        self.orientation_label = Label(text=self.get_orientation_text(), font_size='32sp')
        layout.add_widget(self.orientation_label)

        # Bind the window size to a method so the labels update automatically
        Window.bind(size=self.on_window_size)
        
        return layout
    
    def get_expected_size_text(self):
        return f"Expected Size: 1280 x 400"

    def on_window_size(self, window, size):
        # This method is called whenever the window size changes (e.g., on rotation)
        self.size_label.text = self.get_size_text()
        self.orientation_label.text = self.get_orientation_text()
        
    def get_size_text(self):
        return f"Window Size: {Window.width} x {Window.height}"

    def get_orientation_text(self):
        if Window.width > Window.height:
            return "Orientation: Landscape"
        else:
            return "Orientation: Portrait"

if __name__ == '__main__':
    RotationTestApp().run()
