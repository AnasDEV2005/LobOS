
import gi, pam, fabric
from fabric import Application
import time
gi.require_version("GtkSessionLock", "0.1")
from gi.repository import Gdk, GtkSessionLock, GLib
from fabric.widgets.window import Window
from fabric.widgets.entry import Entry
from fabric.utils import DesktopApp, get_desktop_applications, idle_add, remove_handler, get_relative_path
import os
from loguru import logger
import sys
from datetime import datetime
from fabric.widgets.label import Label
from fabric.widgets.overlay import Overlay
from fabric.widgets.box import Box
from fabric.widgets.image import Image
from random import randint
from fabric.utils import invoke_repeater, get_relative_path, exec_shell_command




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


def get_bg_picture_path() -> str | None:
    path = os.path.expanduser("~/wallpapers/Wallpaper.png")
    if not os.path.exists(path):
        path = os.path.expanduser("~/.face")
    if not os.path.exists(path):
        logger.warning(
            "can't fetch a user profile picture, add a profile picture image at ~/.face or at ~/Pictures/Other/profile.jpg"
        )
        path = None
    return path


class LockScreen(Window):
    def __init__(self, lock: GtkSessionLock.Lock):
        self.lock = lock
        super().__init__(
            name="main-window",
            visible=False,
            all_visible=False,
        )




        
       # self.add_keybinding("Ctrl w", self.quit_window)



        self.set_events(Gdk.EventMask.KEY_PRESS_MASK | Gdk.EventMask.KEY_RELEASE_MASK)
        self.connect("key-press-event", self.on_key_press)
        self.connect("key-release-event", self.on_key_release)

        self.label = Label(name="lbl_title", label="LOGIN")
        self.entry = Entry(name="pass_entry", size=(2000, 2000), on_activate=self.on_activate)
        self.pfp = Box(name="pfp", size = (250, 250), style=f"background-image: url(\"file://{get_profile_picture_path() or ''}\")",)
        self.pam_service = pam.pam()

        self.signals = Box(
            orientation="h",
            spacing=13,
            name="signals",
            children=[
                Box(name="signal", size=80),
                Box(name="signal", size=80),
                Box(name="signal", size=80),
                Box(name="signal", size=80),
                Box(name="signal", size=80),
            ],
        )


        self.is_unlocked = False
        
        self.opened = False



        self.box = Box(
            name="container",
            orientation="v",
            spacing=50,
            children=[self.pfp, self.label, self.signals],
            style=f"background-image: url(\"file://{get_bg_picture_path() or ''}\")",
        )

         
        self.add(Overlay(overlays=[self.box, self.entry]))
        invoke_repeater(3000, self.check_nd_quit)  
        invoke_repeater(300, self.fade_in)

    def check_nd_quit(self, *args):
        print(f"Checking is_unlocked: {self.is_unlocked}")      
        if self.is_unlocked:
            self.quit_window()
        return True

    def on_key_press(self, widget, event):
        print("typed")
        signal = randint(0, 4)
        self.signals.children[signal].add_style_class("typing-signal")
        self.signals.children[signal].remove_style_class("no-signal")
        self.active_key = signal

    def on_key_release(self, widget, event):
        print("released")
        for i in range(0, 5):
            self.signals.children[i].remove_style_class("typing-signal")
            self.signals.children[i].add_style_class("no-signal")

    def make_signals_red(self):
        for i in range(0, 5):
            self.signals.children[i].add_style_class("incorrect-signal")
            self.signals.children[i].remove_style_class("no-signal")

    def remove_red_signals(self):
        for i in range(0, 5):
            self.signals.children[i].remove_style_class("incorrect-signal")
            self.signals.children[i].add_style_class("no-signal")

    def authenticate(self, password):
        return password == "Anas2005"  # placeholder dammit

    def fade_out(self):
        self.add_style_class("fade-out")
        self.remove_style_class("visible")
    
    def fade_in(self):
        if self.opened:
            self.add_style_class("visible")
        else:
            self.opened = True

    def on_activate(self, entry: Entry, *args):
        password = entry.get_text()
        if self.authenticate(password):
            self.fade_out()
            self.is_unlocked = True
            print(is_unlocked)
        else:
            self.make_signals_red()
            self.entry.set_text("")
            GLib.timeout_add_seconds(1, lambda: self.remove_red_signals() or False)
    
    def quit_window(self, *args):
        self.lock.unlock_and_destroy()
        self.destroy()
is_unlocked = False

if __name__ == "__main__":
    unique_name = f"pylock_{os.getpid()}_{datetime.now().timestamp()}"
    app_instance_name = unique_name.replace(".", "")
    app_name = app_instance_name.replace("_", "-")

    lock = GtkSessionLock.prepare_lock()
    lock.lock_lock()
    lockscreen = LockScreen(lock)
    lock.new_surface(lockscreen, Gdk.Display.get_default().get_monitor(0))
    lockscreen.show_all()

    app = Application(app_name, lockscreen)
    app.set_stylesheet_from_file(get_relative_path("fablock.css"))
    app.run()

