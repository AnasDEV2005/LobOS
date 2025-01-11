import os
import time
import psutil
from loguru import logger
from fabric import Application
from fabric.widgets.box import Box
from fabric.widgets.button import Button
from fabric.widgets.label import Label
from fabric.widgets.overlay import Overlay
from fabric.widgets.datetime import DateTime
from fabric.widgets.circularprogressbar import CircularProgressBar
from fabric.widgets.wayland import WaylandWindow as Window
from fabric.widgets.window import Window as NormalWindow
from fabric.utils import invoke_repeater, get_relative_path
import gi 
from gi.repository import Gdk, Gtk
from hq import Overview 



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
            layer="background",
            title="fabric-overlay",
            visible=False,
            all_visible=False,
            **kwargs,
        )

        self.set_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        
        self.button_listen_window = Button(
            size = (2000,2000),
            spacing=14,
            name="header",
            orientation="v",
        )

        self.connect("button-release-event", self.on_button_press)
        
        self.connect("button-release-event", self.on_click_outside)
        
        self.popover_container = Overview() 
        
        self.box = Box(name="popover-box", orientation="v", spacing=10)
        label = Label(label="Hello from Popover!")
        self.box.add(label)
        self.popover_container.add(self.box)
       


        self.toggle_button = Window(
            anchor = "bottom",
            layer = "overlay",
        )
        self.toggle_button.add(
            Button(
                name = "hq_button",
                label = "  ^  ",
                on_clicked = lambda *_: self.toggle_overview_widget(),
            )
        )
        self.toggle_button.show()

        

        self.add(
            Box(
                name="window-inner",
                orientation="v",
                spacing=24,
                children=[self.button_listen_window],
            ),
        )
        self.show_all()
        self.popover_container.hide()
        
# 1818, 1036

    def on_button_press(self, widget, event):
        if event.button == 3:
            self.popover_container.show()

    def on_click_outside(self, widget, event):
        if event.button != 3:
            self.popover_container.hide()
    

    def toggle_overview_widget(self):
        if self.popover_container.is_visible(): 
            self.popover_container.hide()
        else: 
            self.popover_container.show()


if __name__ == "__main__":
    side_panel = SidePanel()
    app = Application("leftclickwindow", side_panel)
    app.set_stylesheet_from_file(get_relative_path("./popup.css"))

    app.run()
