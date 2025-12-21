
import time
from gi.repository import GLib, Gtk
from fabric import App
from fabric.widgets.box import Box
from fabric.widgets.label import Label
from fabric.widgets.button import Button


class Stopwatch(App):
    def __init__(self):
        super().__init__("Stopwatch")

        # Load CSS
        self.load_css("style.css")

        # UI Layout
        self.time_label = Label("00:00:00")
        self.time_label.add_css_class("time-display")

        self.start_button = Button("Start", on_click=self.start)
        self.stop_button = Button("Stop", on_click=self.stop)
        self.reset_button = Button("Reset", on_click=self.reset)

        for b in [self.start_button, self.stop_button, self.reset_button]:
            b.add_css_class("control-button")

        self.button_box = Box(
            orientation="h",
            spacing=10,
            children=[self.start_button, self.stop_button, self.reset_button],
            halign="center",
        )

        self.box = Box(
            orientation="v",
            spacing=20,
            children=[self.time_label, self.button_box],
            halign="center",
            valign="center",
        )

        self.set_content(self.box)

        # Timer State
        self.running = False
        self.start_time = 0
        self.elapsed = 0
        self.timer_id = None

    def load_css(self, path):
        """Load a CSS stylesheet into GTK."""
        css_provider = Gtk.CssProvider()
        css_provider.load_from_path(path)
        display = Gtk.StyleContext()
        Gtk.StyleContext.add_provider_for_display(
            display.get_display(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

    def start(self, *_):
        if not self.running:
            self.running = True
            self.start_time = time.time() - self.elapsed
            self.timer_id = GLib.timeout_add(1000, self.update_time)

    def stop(self, *_):
        if self.running:
            self.running = False
            if self.timer_id:
                GLib.source_remove(self.timer_id)
            self.timer_id = None

    def reset(self, *_):
        self.stop()
        self.elapsed = 0
        self.time_label.label = "00:00:00"

    def update_time(self):
        if not self.running:
            return False  # stop timeout
        self.elapsed = time.time() - self.start_time
        self.time_label.label = self.format_time(self.elapsed)
        return True  # continue timeout

    @staticmethod
    def format_time(seconds):
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        return f"{h:02}:{m:02}:{s:02}"


if __name__ == "__main__":
    Stopwatch().run()
