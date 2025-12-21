from fabric import Application
from fabric.widgets.box import Box
from fabric.widgets.button import Button
from fabric.widgets.entry import Entry
from fabric.widgets.label import Label
from fabric.widgets.circularprogressbar import CircularProgressBar
from fabric.widgets.wayland import WaylandWindow as Window
from fabric.utils import get_relative_path
from gi.repository import Gdk
import sys
import socket
import os

from gi.repository import GLib


class InputMode(Window):

    def __init__(self, **kwargs):
        super().__init__(
            layer="overlay",
            title="fabric-overlay",
            anchor="left top right bottom",
            keyboard_mode="exclusive",
            visible=True,
            all_visible=False,
            **kwargs,
        )
        
        self.input_mask = Box(
            size = (2000,2000),
            spacing=14,
            name="header",
            orientation="v",
        )


        self.cmd_reg = ""
        
        
        self.entry = Entry(
                name="invisible",
                size=(2000, 2000),
                anchor="left top right bottom",
                visible=False,
                notify_text=lambda entry, *_: self.update_cmd(entry.get_text()),
        )
        self.input_mask.add(self.entry)
       

        self.command_input = Label(
            h_align = "start",
            name='command-prompt',
            label="Enter command...",
            style_classes=[".active", ".inactive"],
            h_expand=True,
        )
        self.command_box = Box(
            orientation = "h",
            # h_expand=True,
            h_align = "fill",
            name='command-box',
            children=self.command_input,
        )

        self.connect("key-press-event", self.lock)
        self.command_box.add_style_class("inactive")

        self.add(
            Box(
                name="window-inner",
                orientation="v",
                spacing=24,
                children=[self.input_mask],
            ),
        )
        self.show_all()
        self.entry.grab_focus()

    def update_cmd(self, string):
        self.entry.set_position(len(string))
        self.command_input.set_label(f"{string}█")
        self.command_box.add_style_class("active")
        self.command_box.remove_style_class("inactive")
    def lock(self):
        self.entry.set_position(len(self.entry.get_text() ))
 



if __name__ == "__main__":
    window = InputMode()
    app = Application("command-input", window)
    app.set_stylesheet_from_file(get_relative_path("./bar.css"))

    app.run()
