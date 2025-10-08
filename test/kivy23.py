# kivy_landscape_touch_only.py
from kivy.config import Config

# Native panel: 400x1280 portrait
Config.set('graphics', 'width', '400')
Config.set('graphics', 'height', '1280')
Config.set('graphics', 'resizable', False)
Config.set('graphics', 'fullscreen', 'auto')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.graphics import PushMatrix, PopMatrix, Rotate, Translate


class RotatedRoot(Widget):
    """Rotate the child layout into landscape and remap touch events."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = TestLayout()
        self.add_widget(self.layout)

        self.bind(size=self._update_transform)

    def _update_transform(self, *args):
        # After rotation, logical size must be swapped
        self.layout.size = (self.height, self.width)

        self.canvas.before.clear()
        self.canvas.after.clear()

        with self.canvas.before:
            PushMatrix()
            # Keep the original correct rotation (-90° CCW)
            Translate(0, self.height)
            Rotate(origin=(0, 0), angle=-90)
        with self.canvas.after:
            PopMatrix()

    # --- Touch remapping (flipped 180° vs. last time) ---
    def _rotate_point(self, x, y):
        w, h = self.width, self.height
        # Original mapping was: (new_x, new_y) = (y, w - x)
        # To flip touch 180°, invert both axes:
        return (h - y, x)

    def on_touch_down(self, touch):
        touch.x, touch.y = self._rotate_point(touch.x, touch.y)
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        touch.x, touch.y = self._rotate_point(touch.x, touch.y)
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        touch.x, touch.y = self._rotate_point(touch.x, touch.y)
        return super().on_touch_up(touch)


class TestLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.padding = 20
        self.spacing = 20

        left_box = BoxLayout(orientation='vertical', spacing=10)
        left_box.add_widget(Label(text="Landscape (rotated)", font_size=32))
        left_box.add_widget(Button(text="Press Me", size_hint=(1, 0.3)))
        left_box.add_widget(Slider(min=0, max=100, value=50))

        self.pb = ProgressBar(max=100, value=0)
        left_box.add_widget(self.pb)

        self.add_widget(left_box)

        right_box = BoxLayout(orientation='vertical', spacing=10)
        right_box.add_widget(Label(text="Right Panel", font_size=24))
        for i in range(3):
            right_box.add_widget(Button(text=f"Button {i+1}"))

        self.add_widget(right_box)

        Clock.schedule_interval(self.update_pb, 0.1)

    def update_pb(self, dt):
        self.pb.value = (self.pb.value + 1) % 100


class LandscapeApp(App):
    def build(self):
        return RotatedRoot()


if __name__ == "__main__":
    LandscapeApp().run()
