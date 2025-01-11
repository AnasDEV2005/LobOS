import os
import time
import psutil
import operator
from collections.abc import Iterator
from loguru import logger
from fabric import Application
from fabric.widgets.box import Box
from fabric.widgets.label import Label
from fabric.widgets.overlay import Overlay
from fabric.widgets.datetime import DateTime
from fabric.widgets.circularprogressbar import CircularProgressBar
from fabric.widgets.wayland import WaylandWindow as Window
from fabric.widgets.webview import WebView
from fabric.widgets.stack import Stack
from fabric.widgets.button import Button
from fabric.widgets.image import Image
from fabric.widgets.entry import Entry
from fabric.widgets.scrolledwindow import ScrolledWindow
from fabric.utils import DesktopApp, get_desktop_applications, idle_add, remove_handler, get_relative_path
from fabric.utils import invoke_repeater, get_relative_path

def get_profile_picture_path() -> str | None:
    path = os.path.expanduser("~/.config/hypr/antman.png")
    if not os.path.exists(path):
        path = os.path.expanduser("~/.face")
    if not os.path.exists(path):
        logger.warning(
            "can't fetch a user profile picture, add a profile picture image at ~/.face or at ~/Pictures/Other/profile.jpg"
        )
        path = None
    return path

class Overview(Window):
    @staticmethod
    def bake_progress_bar(name: str = "progress-bar", size: int = 64, **kwargs):
        return CircularProgressBar(
            name=name, min_value=0, max_value=100, line_width=3, size=size, **kwargs
        )
    def bake_bat_bar(name: str = "bat-bar", size: int = 64, **kwargs):
        return CircularProgressBar(
            name="progress-bar", min_value=0, max_value=100, line_style='butt', size=size, **kwargs
        )
    def bake_disk_bar(name: str = "disk-bar", size: int = 64, **kwargs):
        return CircularProgressBar(
            name="progress-bar", min_value=0, max_value=100, pie=True, size=size, **kwargs
        )

    @staticmethod
    def bake_progress_icon(**kwargs):
        return Label(**kwargs).build().add_style_class("progress-icon").unwrap()
    def hideall(self):
        self.hide()
    def is_visibl(self):
        return self.is_visible()
    def __init__(self, **kwargs):
        super().__init__(
            layer="overlay",
            pass_through=True,
            title="fabric-overlay",
            anchor="top",
            margin="16px 0px 0px 16px",
            exclusivity="normal",
            visible=False,
            all_visible=False,
            **kwargs,
        )

## HEADER
#########################################################################################################
        self.profile_pic = Box(
            name="profile-pic",
            size=300,
            style=f"background-image: url(\"file://{get_profile_picture_path() or ''}\")",
        )
        self.uptime_label = Label(label=f"{self.get_current_uptime()}")
        self.greet = Box(
            orientation="v",
            name = "greet",
            children= [
                Label(
                    name = "big-greet",
                    label = "Welcome, to my Soul Society",
                    ),
                Label(
                    name = "small-greet",
                    label = "I wanna dunk.",
                )
            ],
        )
        self.header = Box(
            spacing=14,
            name="header-inner",
            orientation="h",
            children=[
                self.profile_pic,
                Box(
                    orientation="v",
                    children=[
                        self.greet,
                    ],
                ),
            ],
        )
        self.close_butt = Button(
            name="close-header",
            child= Label(name ="x", label='X'),
            on_clicked = lambda *_: self.close(),
        )
        self.bottom = Box(
            orientation="h",
            children = [
                Box(
                    orientation="v",
                    children= [
                        DateTime(
                            name="date-time",
                            style="margin-top: 4px; min-width: 180px;",
                        ),
                    self.uptime_label]),
                self.close_butt
            ]
        )
        self.add(
            Box(
                orientation="v",
                name="header",
                children=[self.header, self.bottom],
            ),
        )
        self.show_all()


## some more functions
    def close_widget(self):
        self.close()
    def update_status(self):
        self.disk_progress.value = psutil.disk_usage('/home').percent
        self.ram_progress.value = psutil.virtual_memory().percent
        if not (bat_sen := psutil.sensors_battery()):
            self.bat_circular.value = 42
        else:
            self.bat_circular.value = bat_sen.percent

        return True

    def get_current_uptime(self):
        uptime = time.time() - psutil.boot_time()
        uptime_days, remainder = divmod(uptime, 86400)
        uptime_hours, remainder = divmod(remainder, 3600)
        # uptime_minutes, _ = divmod(remainder, 60)
        return f"{int(uptime_days)} {'days' if uptime_days > 1 else 'day'}, {int(uptime_hours)} {'hours' if uptime_hours > 1 else 'hour'}"


if __name__ == "__main__":
    overview = Overview()
    app = Application("header", overview)
    app.set_stylesheet_from_file(get_relative_path("side_panel.css"))

    app.run()

