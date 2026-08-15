from fabric import Application
from fabric.utils import DesktopApp, get_desktop_applications, idle_add, remove_handler, get_relative_path
from collections.abc import Iterator
import operator
from fabric.widgets.image import Image
from fabric.widgets.scrolledwindow import ScrolledWindow
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


        self.cmd_reg = []


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


## SUGGESTIONS
##############################################################
        self._arranger_handler: int = 0
        self._all_apps = get_desktop_applications()

        self.selected_app = 0


        self.viewport = Box(name='viewport', spacing=0, orientation="v", v_align="end", size=(700, 1000))
        self.search_entry = ""

        self.scrolled_window = ScrolledWindow(
            min_content_size=(1200, 24),
            max_content_size=(1200, 400),
            child=self.viewport,
            v_align="end"
        )
        self.appbox = Box(
            name="appbox",
            orientation="v",
            v_align="baseline",
            size = (320, 1000),
            children=[
                    self.scrolled_window,
                ],
        )
        self.window_apps = Window(
                name="suggestion-view",
                layer="overlay",
                title="fabric-overlay",
                anchor="bottom left",
                margin="100px 0px 0px 170px",
                keyboard_mode='"none',
                exclusivity="none",
                v_align="end",
                visible=False,
                all_visible=False,
                size=(400, 1000),
                child=self.appbox,
            )

        self.add_keybinding("Up", lambda *_: self.up())
        self.add_keybinding("Down", lambda *_: self.down())
        



        # self.window_apps.show()
############################################################3

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

        s = self.entry.get_text()
        run = s[:4]
        if run == "run ":
            if not self.window_apps.is_visible():
                self.window_apps.show()

            if len(self.viewport.get_children())>0: self.selected_app = 0;
            self.search_entry = s[4:]
            self.arrange_viewport(self.search_entry)
            # self.viewport.get_children()[0].add_style_class("selected")
        else:
            if self.window_apps.is_visible():
                self.window_apps.hide()


    def up(self):
        if self.selected_app>0:
            self.selected_app -= 1 
        print(self.selected_app)
        if len(self.viewport.get_children())>0: self.viewport.get_children()[self.selected_app+1].remove_style_class("selected");
        
        self.viewport.get_children()[self.selected_app].add_style_class("selected")

    def down(self):
        length = len(self.viewport.get_children())
        if self.selected_app<length-1:
            self.selected_app += 1 
        print(self.selected_app)
        if self.selected_app+1: self.viewport.get_children()[self.selected_app-1].remove_style_class("selected");
        self.viewport.get_children()[self.selected_app].add_style_class("selected")




    def lock(self):
        self.entry.set_position(len(self.entry.get_text() ))
     # app launcher methods
    def arrange_viewport(self, query: str = ""):
        # reset everything so we can filter current viewport's slots...
        # remove the old handler so we can avoid race conditions
        remove_handler(self._arranger_handler) if self._arranger_handler else None

        # remove all children from the viewport
        self.viewport.children = []

        # make a new iterator containing the filtered apps
        filtered_apps_iter = iter(
            [
                app
                for app in self._all_apps
                if query.casefold()
                in (
                    (app.display_name or "")
                    + (" " + app.name + " ")
                    + (app.generic_name or "")
                ).casefold()
            ]
        )
        should_resize = operator.length_hint(filtered_apps_iter) == len(self._all_apps)

        # all aboard...
        # start the process of adding slots with a lazy executor
        # using this method makes the process of adding slots way more less
        # resource expensive without blocking the main thread and resulting in a lock
        self._arranger_handler = idle_add(
            lambda *args: self.add_next_application(*args)
            or (self.resize_viewport() if should_resize else False),
            filtered_apps_iter,
            pin=True,
        )

        return False

    def add_next_application(self, apps_iter: Iterator[DesktopApp]):
        if not (app := next(apps_iter, None)):
            return False

        self.viewport.add(self.bake_application_slot(app))
        return True

    def resize_viewport(self):
        self.scrolled_window.set_min_content_width(
            self.viewport.get_allocation().width  # type: ignore
        )
        return False

    def bake_application_slot(self, app: DesktopApp, **kwargs) -> Button:
        return Button(
            name='appslot',
            child=Box(
                orientation="h",
                spacing=4,
                children=[
                    Label(
                        label=app.display_name or "Unknown",
                        v_align="center",
                        h_align="center",
                    ),
                ],
            ),
            tooltip_text=app.description,
            on_clicked=lambda *_: (app.launch(), self.window_apps.hide()),
            **kwargs,
        )                







if __name__ == "__main__":
    window = InputMode()
    app = Application("command-input", window)
    app.set_stylesheet_from_file(get_relative_path("./bar.css"))

    app.run()
