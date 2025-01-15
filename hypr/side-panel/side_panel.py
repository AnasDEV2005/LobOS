"""
side panel, edited version of the side panel in fabric examples
contains info about the system and a few tools, in webviews
"""
import gi
import subprocess
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
from fabric.utils import invoke_repeater, get_relative_path, exec_shell_command
from gi.repository import Gtk
from wallpicker import Wallpicker    
from os import listdir
from os.path import isfile, join, expanduser
import NetworkManager
from NetworkManager import *
wallpapers_dir = expanduser("~/.config/hypr/wallpapers")

onlyfiles = [f for f in listdir(wallpapers_dir) if isfile(join(wallpapers_dir, f))]

def get_profile_picture_path() -> str | None:
    path = os.path.expanduser("~/.config/hypr/pfp.jpg")
    if not os.path.exists(path):
        path = os.path.expanduser("~/.face")
    if not os.path.exists(path):
        logger.warning(
    "can't fetch a user profile picture, add a profile picture image at ~/.face or at ~/Pictures/Other/profile.jpg"
        )
        path = None
    return path



def run_overview_widget():
    subprocess.run(["chmod", "+x", "/home/geronimo/.config/hypr/toggle_overview.sh"], check=True)
    subprocess.run(["/home/geronimo/.config/hypr/toggle_overview.sh"], check=True)



#### S I D E   P A N E L ####
# i mean its more like a bar but we ball 

class SidePanel(Window):
    @staticmethod
    def bake_progress_bar(name: str = "progress-bar", size: int = 64, **kwargs):
        return CircularProgressBar(
            name=name, min_value=0, max_value=100, line_style='butt', line_width=3, size=size, **kwargs
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

    def __init__(self, **kwargs):
        super().__init__(
            layer="top",
            title="fabric-overlay",
            anchor="top left bottom",
            margin="10px 0px 10px 0px",
            keyboard_mode='on-demand',
            exclusivity="auto",
            size=(500, 800),
            visible=False,
            all_visible=False,
            **kwargs,
        )


        self.add_keybinding("Ctrl s", self.save_notes)


## STATUS CIRCLES
#############################################################################################################################
        self.disk_progress = self.bake_disk_bar()
        self.ram_progress = self.bake_progress_bar()
        self.bat_circular = self.bake_bat_bar().build().set_value(42).unwrap()
            
        self.progress_container = Box(
            name="progress-bar-container",
            spacing=25,
            orientation="v",
            children=[
                Box(
                    children=[
                        Overlay(
                            child=self.disk_progress,
                            overlays=[
                                self.bake_progress_icon(
                                    label="",
                                ),
                                Image(
                                    name="close-svg",
                                    image_file="/home/geronimo/.config/hypr/icon/database.png",
                                    size=27,
                                ),
                            ],
                        ),
                    ],
                ),
                Box(
                    children=[
                        Overlay(
                            child=self.ram_progress,
                            overlays=[
                                self.bake_progress_icon(
                                    label="",
                                    style="margin-right: 4px; text-shadow: 0 0 10px #fff;",
                                ),
                                Image(
                                    name="close-svg",
                                    image_file="/home/geronimo/.config/hypr/icon/cpu.png",
                                    size=27,
                                ),
                            ],
                        )
                    ]
                ),
                Box(
                    children=[
                        Overlay(
                            child=self.bat_circular,
                            overlays=[
                                self.bake_progress_icon(
                                    label="",
                                    style="margin-right: 0px; text-shadow: 0 0 10px #fff, 0 0 18px #fff;",
                                ),
                                Image(
                                    name="close-svg",
                                    image_file="/home/geronimo/.config/hypr/icon/bat.png",
                                    size=27,
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        )

##################### TOOLS  ########################################################################

## NOTES
############################################################

        self.textview = Gtk.TextView()
        self.textview.set_size_request(300, 800)
 
        self.note = Box(
            name='notes',
            spacing = 15,
            orientation = "v",
            children = [
                Label(label="NOTES", name="note-title", style="font-size: 50px;"),
                Box(
                    style = "padding: 28px;",
                    children = [ self.textview,],
                ),
                Button(
                    name = "save-button",
                    label = "SAVE",
                    on_clicked = lambda *_: self.save_notes(),
                )
            ],
        )

        self.load_notes()

        self.window_note = Window(
                name="window-inner",
                layer="overlay",
                title="fabric-overlay",
                anchor="top left bottom",
                margin="10px 0px 10px 0px",
                keyboard_mode='on-demand',
                exclusivity="none",
                visible=True,
                all_visible=True,
                size=(300, 800),
                child=self.note,
            )

        self.window_note.add_keybinding("Ctrl s", self.save_notes)

        self.window_note.hide()

## POWER MENU
#############################################################
        self.powermenu = Box(
            orientation='v',
            name='powermenu',
            spacing= 10,
            children=[
            Button(name='shutdown',
                   style='padding:10px ; border-radius: 5px;',
                    child=Image(
                        name="apps",
                        image_file="/home/geronimo/.config/hypr/icon/power.png",
                        size=38,
                    ),

                    on_clicked=lambda *_: exec_shell_command('systemctl poweroff'),
                ),                
            Button(name='reboot',
                   style='padding:10px ; border-radius: 5px;',
                    child=Image(
                        name="apps",
                        image_file="/home/geronimo/.config/hypr/icon/reboot.png",
                        size=30,
                    ),

                    on_clicked=lambda *_: exec_shell_command('systemctl soft-reboot'),
                ),                
            Button(name='sleep',
                   style='padding:10px ; border-radius: 5px;',
                    child=Image(
                        name="apps",
                        image_file="/home/geronimo/.config/hypr/icon/moon.png",
                        size=38,
                    ),

                    on_clicked=lambda *_: exec_shell_command('systemctl sleep'),
                ),                               
            ],
        )
        self.window_power = Window(
                name="powermenu",
                layer="overlay",
                title="fabric-overlay",
                anchor="left bottom",
                margin="10px 0px 10px 0px",
                keyboard_mode='on-demand',
                exclusivity="normal",
                visible=False,
                all_visible=False,
                size=(400, 800),
                child=self.powermenu,
            )
## APP LAUNCHER
##############################################################
        self._arranger_handler: int = 0
        self._all_apps = get_desktop_applications()

        self.viewport = Box(name='viewport', spacing=15, orientation="v")
        self.search_entry = Entry(
            name='search',
            placeholder="Search Apps...",
            h_expand=True,
            notify_text=lambda entry, *_: self.arrange_viewport(entry.get_text()),
            on_button_press_event=print,
        )
        self.scrolled_window = ScrolledWindow(
            min_content_size=(400, 320),
            max_content_size=(400, 1000),
            child=self.viewport,
        )
        self.appbox = Box(
            name="appbox",
            orientation="v",
            size = (320, 1000),
            children=[
                    Box(
                        spacing=2,
                        orientation="h",
                        children=[
                            self.search_entry,
                        ],
                    ),
                    # the actual slots holder
                    self.scrolled_window,
                ],
        )
        self.window_apps = Window(
                name="window-inner",
                layer="overlay",
                title="fabric-overlay",
                anchor="top left bottom",
                margin="10px 0px 10px 0px",
                keyboard_mode='on-demand',
                exclusivity="none",
                visible=False,
                all_visible=False,
                size=(400, 1000),
                child=self.appbox,
            )

## WIFI MANAGER
#############################################################################


## WALLPAPER PICKER
#############################################################################
        onlyfiles = [f for f in listdir(wallpapers_dir) if isfile(join(wallpapers_dir, f))]

        self.w_viewport = self.make_viewport(onlyfiles)

        self.w_scrolled_window = ScrolledWindow(
            kinetic_scroll=True,
            name = "scrolled-viewport",
            min_content_size=(900, 500),
            max_content_size=(900, 500),
            child=self.w_viewport,
        )

        self.window_wallpicker = Window(
            name="appwindow",
            layer="overlay",
            anchor="top left",
            exclusivity="none",
            keyboard_mode="on-demand",
            visible=False,
            orientation = "v",
            all_visible=False,
            child=self.w_scrolled_window,
            )




##################### TOOLS BUTTONS ########################################################################3        

        self.buttons = Box(
            orientation='v',
            style="margin-top:30px;",
            spacing=42,
            children=[
            Box(name="pfp", size = (40, 60), style=f"background-image: url(\"file://{get_profile_picture_path() or ''}\")",),
            self.progress_container,

            Button(name='apps',
                   style='padding-top:7px ; padding-bottom:7px ;',
                    child=Image(
                        name="apps",
                        image_file="/home/geronimo/.config/hypr/icon/squares-four.png",
                        size=38,
                    ),

                    on_clicked=lambda *_: self.toggle_window_app(),
                ),
            Button(name='note',
                   style='padding-top:7px ; padding-bottom:7px ;',
                    child=Image(
                        name="apps",
                        image_file="/home/geronimo/.config/hypr/icon/notepad.png",
                        size=38,
                    ),

                    on_clicked=lambda *_: self.toggle_window_note(),
                ),
            Button(name='browser',
                   style='padding-top:7px ; padding-bottom:7px ;',
                    child=Image(
                        name="apps",
                        image_file="/home/geronimo/.config/hypr/icon/browser.png",
                        size=38,
                    ),

                    on_clicked=lambda *_: subprocess.Popen(["xdg-open", "https://www.google.com"]),
                ),
            Button(name='wallpicker',
                   style='padding-top:7px ; padding-bottom:7px ;',
                    child=Image(
                        name="apps",
                        image_file="/home/geronimo/.config/hypr/icon/image.png",
                        size=38,
                    ),

                    on_clicked=lambda *_: self.toggle_window_wallpicker(),
                ),
            Button(name='wifi',
                   style='padding-top:7px ; padding-bottom:7px ;',
                    child=Image(
                        name="apps",
                        image_file="/home/geronimo/.config/hypr/icon/wifi.png",
                        size=38,
                    ),

                    on_clicked=lambda *_: subprocess.Popen(["iwgtk"]),
                ),
            Button(name='powermenubutton',
                   style='padding-top:7px ; padding-bottom:7px ;',
                    child=Image(
                        name="apps",
                        image_file="/home/geronimo/.config/hypr/icon/power.png",
                        size=38,
                    ),

                    on_clicked=lambda *_: self.toggle_window_power(),
                ),
            ]
        )
         


        self.sidebar = Box(
            name="window-inner",
            orientation="v",
            spacing=15,
            children=[self.buttons],
        )
        self.sidepanel = Box(
                name="maaan",
                orientation='h',
                children=[self.sidebar],
            )
        self.add(
            self.sidepanel
        )

        invoke_repeater(1000, self.update_status)
        self.show_all()




## methods
    
    # wallpaper picker methods
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

    # progress bars methods
    def update_status(self):
        self.disk_progress.value = psutil.disk_usage('/home').percent
        self.ram_progress.value = psutil.virtual_memory().percent
        if not (bat_sen := psutil.sensors_battery()):
            self.bat_circular.value = 42
        else:
            self.bat_circular.value = bat_sen.percent

        return True

    # notes methods
    def save_notes(self, *args):
        buffer = self.textview.get_buffer()
        
        start_iter = buffer.get_start_iter()
        end_iter = buffer.get_end_iter()
        
        text = buffer.get_text(start_iter, end_iter, True)
        home_dir = os.path.expanduser("~")
        file_path = os.path.join(home_dir, "fabric-notes.txt")
        with open(file_path, 'w') as file:
            file.write(text)

    def load_notes(self):
        home_dir = os.path.expanduser("~")
        file_path = os.path.join(home_dir, "fabric-notes.txt")
        try:
            with open(file_path, 'r') as file:
                file_content = file.read()
            buffer = self.textview.get_buffer()
            buffer.set_text(file_content)

        except Exception as e:
            print(f"Error reading file: {e}")

    # tool toggling methods
    def toggle_window_note(self):
        if self.window_note.is_visible(): self.window_note.hide()
        elif self.window_apps.is_visible(): 
            self.window_apps.hide()
            self.window_note.show()
        else: self.window_note.show()

    def toggle_window_app(self):
        if self.window_apps.is_visible(): self.window_apps.hide()
        elif self.window_note.is_visible(): 
            self.window_note.hide()
            self.window_apps.show()
        else: self.window_apps.show()

    def toggle_window_power(self):
        if self.window_power.is_visible(): self.window_power.hide()
        else: self.window_power.show()

    def toggle_window_wallpicker(self):
        if self.window_wallpicker.is_visible():
            self.window_wallpicker.hide()
        else:
            self.window_wallpicker.show()

    def toggle_window_wifi(self):
        if self.network_window.is_visible():
            self.network_window.hide()
        else:
            self.network_window.show()

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
                spacing=12,
                children=[
                    Image(pixbuf=app.get_icon_pixbuf(), h_align="start", size=32),
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
        
# run app
if __name__ == "__main__":
    side_panel = SidePanel()
    app = Application("side-panel", side_panel)
    app.set_stylesheet_from_file(get_relative_path("side_panel.css"))

    app.run()
