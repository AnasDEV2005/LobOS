
import os
import time
import psutil
from loguru import logger
from fabric import Application
from fabric.widgets.box import Box
from fabric.widgets.label import Label
from fabric.widgets.overlay import Overlay
from fabric.widgets.datetime import DateTime
from fabric.widgets.circularprogressbar import CircularProgressBar
from fabric.widgets.wayland import WaylandWindow as Window
from fabric.utils import invoke_repeater, get_relative_path





class SidePanel(Window):
    @staticmethod
    def bake_progress_bar(name: str = "progress-bar", size: int = 64, **kwargs):
        return CircularProgressBar(
            name=name, min_value=0, max_value=100, size=size, **kwargs
        )

    @staticmethod
    def bake_progress_icon(**kwargs):
        return Label(**kwargs).build().add_style_class("progress-icon").unwrap()

    def __init__(self, **kwargs):
        super().__init__(
            layer="overlay",
            title="fabric-overlay",
            anchor="bottom right",
            pass_through=True,
            margin="10px 10px 10px 0px",
            exclusivity="none",
            visible=False,
            all_visible=False,
            **kwargs,
        )


        self.header = Box(
            spacing=14,
            name="header",
            orientation="v",
            children=[
                Box(
                    orientation="v",
                    spacing=5,
                    children=[ 
                        Label(name="big",label = "Activate Linux",),
                        Label(name = "small", label="Go to settings to activate Arch Linux."),
                    ],
                ),
            ],
        )




        self.add(
            Box(
                name="window-inner",
                orientation="v",
                spacing=24,
                children=[self.header],
            ),
        )
        self.show_all()

if __name__ == "__main__":
    side_panel = SidePanel()
    app = Application("activate-linux", side_panel)
    app.set_stylesheet_from_file(get_relative_path("./activatelinux.css"))

    app.run()
