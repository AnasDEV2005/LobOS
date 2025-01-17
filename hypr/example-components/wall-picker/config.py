# yeah so this is here cuz i havent set the side bar one
# to update, so it might not have the new apps until 
# u kill and rerun it, so this is still useful

import operator
from collections.abc import Iterator
from fabric import Application
from fabric.widgets.box import Box
from fabric.widgets.label import Label
from fabric.widgets.button import Button
from fabric.widgets.image import Image
from fabric.widgets.entry import Entry
from fabric.widgets.scrolledwindow import ScrolledWindow
from fabric.widgets.wayland import WaylandWindow as Window
from fabric.utils import DesktopApp, get_desktop_applications, idle_add, remove_handler, get_relative_path, exec_shell_command
from os import listdir
from os.path import isfile, join, expanduser
import sys

wallpapers_dir = expanduser("~/.config/hypr/wallpapers")
onlyfiles = [f for f in listdir(wallpapers_dir) if isfile(join(wallpapers_dir, f))]

class Wallpicker(Window):
    def __init__(self, **kwargs):
        super().__init__(
            name="appwindow",
            layer="overlay",
            anchor="top",
            exclusivity="none",
            keyboard_mode="on-demand",
            visible=True,
            orientation = "v",
            all_visible=True,
            **kwargs,
        )
        
        onlyfiles = [f for f in listdir(wallpapers_dir) if isfile(join(wallpapers_dir, f))]

        self.viewport = self.make_viewport(onlyfiles)
        self.scrolled_window = ScrolledWindow(
            kinetic_scroll=True,
            name = "scrolled-viewport",
            min_content_size=(900, 500),
            max_content_size=(900, 500),
            child=self.viewport,
        )


        self.add(self.scrolled_window)
        self.show_all()


    
    def make_wallpaper_button(self, filepath):
        button = Button(
            name = "wallbutton",
            child = Image(
                image_file=filepath,
                size=250,
            ),
            on_clicked = lambda *_: exec_shell_command(f"swww img {filepath} --transition-type center"),
        )
        return button
    
    def make_viewport(self, onlyfiles):
        viewport = Box(name="viewport", orientation="v")
        box = Box(orientation="h")
        n = 0
        for filepath in onlyfiles:
            button = self.make_wallpaper_button(wallpapers_dir + "/" + filepath)
            box.add(button)
            n += 1
            if n == 3:  # Reset after two buttons in a row
                viewport.add(box)
                box = Box(orientation="h")
                n = 0
        if len(box.get_children()) > 0:  # Add any remaining buttons
            viewport.add(box)
        return viewport
            


if __name__ == "__main__":
    wallpicker = Wallpicker()
    app = Application("wallpicker", wallpicker)
    app.set_stylesheet_from_file(get_relative_path('wallpicker.css'))
    app.run()
