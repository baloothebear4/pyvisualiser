# kivy_landscape_touch_sliderfix4.py
from kivy.config import Config

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
from kivy.core.window import Window

# hide mouse cursor explicitly
Window.show_cursor = False


class RotatedRoot(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = TestLayout()
        self.add_widget(self.layout)
        self.bind(size=self._update_transform)

    def _update_transform(self, *args):
        self.layout.size = (self.height, self.width)
        self.canvas.before.clear()
        self.canvas.after.clear()
        with self.canvas.before:
            PushMatrix()
            Translate(0, self.height)
            Rotate(origin=(0, 0), angle=-90)
        with self.canvas.after:
            PopMatrix()

    def _rotate_point(self, x, y):
        """Portrait → landscape mapping. Works for buttons."""
        w, h = self.width, self.height
        return h - y, x

    def on_touch_down(self, touch):
        touch.x, touch.y = self._rotate_point(touch.x, touch.y)
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        touch.x, touch.y = self._rotate_point(touch.x, touch.y)
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        touch.x, touch.y = self._rotate_point(touch.x, touch.y)
        return super().on_touch_up(touch)


class FixedSlider(Slider):
    """Slider that directly maps touch.x to slider value in rotated layout."""

    def _update_value_from_touch(self, touch):
        # Map touch.x relative to slider's left→right range
        if self.collide_point(*touch.pos):
            rel_x = (touch.x - self.x) / float(self.width)
            rel_x = min(max(rel_x, 0.0), 1.0)
            self.value = self.min + rel_x * (self.max - self.min)
            return True
        return False

    def on_touch_down(self, touch):
        if self._update_value_from_touch(touch):
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if self._update_value_from_touch(touch):
            return True
        return super().on_touch_move(touch)


class TestLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.padding = 20
        self.spacing = 20

        left_box = BoxLayout(orientation='vertical', spacing=10)
        left_box.add_widget(Label(text="Landscape (rotated)", font_size=32))
        left_box.add_widget(Button(text="Press Me", size_hint=(1, 0.3)))

        # Use fixed slider
        self.slider = FixedSlider(min=0, max=100, value=50, orientation='horizontal')
        left_box.add_widget(self.slider)

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
