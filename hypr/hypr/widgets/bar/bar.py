import psutil
import os
from fabric.widgets.image import Image
from fabric import Application
from fabric.widgets.box import Box
from fabric.widgets.label import Label
from fabric.widgets.button import Button
from fabric.widgets.entry import Entry
from fabric.widgets.overlay import Overlay
from fabric.widgets.eventbox import EventBox
from fabric.widgets.datetime import DateTime
from fabric.widgets.centerbox import CenterBox
from fabric.system_tray.widgets import SystemTray
from fabric.widgets.circularprogressbar import CircularProgressBar
from fabric.widgets.wayland import WaylandWindow as Window
from fabric.hyprland.widgets import Language, ActiveWindow, Workspaces, WorkspaceButton
from fabric.utils import (
    FormattedString,
    bulk_replace,
    invoke_repeater,
    get_relative_path,
    exec_shell_command
)
from command_processor import process_cmd
from gi.repository import Gio, GLib
import command_layer

AUDIO_WIDGET = True

if AUDIO_WIDGET is True:
    try:
        from fabric.audio.service import Audio
    except Exception as e:
        print(e)
        AUDIO_WIDGET = False


class VolumeWidget(Box):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.audio = Audio()

        self.progress_bar = CircularProgressBar(
            name="volume-progress-bar", line_style="butt", size=24
        )

        self.event_box = EventBox(
            events="scroll",
            child=Overlay(
                child=self.progress_bar,
                overlays=Label(
                    label="",
                    style="margin: 0px 6px 0px 0px; font-size: 12px; color: #69C3FF;",  # to center the icon glyph
                ),
            ),
        )

        self.audio.connect("notify::speaker", self.on_speaker_changed)
        self.event_box.connect("scroll-event", self.on_scroll)
        self.add(self.event_box)
        self.show_all()
    def on_scroll(self, _, event):
        match event.direction:
            case 0:
                self.audio.speaker.volume += 8
            case 1:
                self.audio.speaker.volume -= 8
        return

    def on_speaker_changed(self, *_):
        if not self.audio.speaker:
            return
        self.progress_bar.value = self.audio.speaker.volume / 100
        self.audio.speaker.bind(
            "volume", "value", self.progress_bar, lambda _, v: v / 100
        )
        return
    
# the bar class


class StatusBar(Window):
    @staticmethod
    def power_menu(self):
        exec_shell_command('source ~/.config/hypr/myvenv/bin/activate && python ~/.config/hypr/power-menu/powermenu.py')
    @staticmethod
    def bake_progress_bar(name: str = "progress-bar", size: int = 24, **kwargs):
        return CircularProgressBar(
            name=name, min_value=0, max_value=100, line_style='butt', size=size, **kwargs
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


    def __init__(
        self,
    ):
        super().__init__(
            name="bar",
            layer="top",
            anchor="left bottom right",
            margin="0px 0px -2px 0px",
            exclusivity="auto",
            visible=False,
            all_visible=False,
        )
        
        self.active_window = ActiveWindow(name="hyprland-window")  # the middle title
        self.language = Language(
            formatter=FormattedString(
                " {replace_lang(language)}",
                replace_lang=lambda lang: bulk_replace(
                    lang,
                    (r".*Eng.*", r".*Ar.*"),
                    ("ENG", "ARA"),
                    regex=True,
                ),
            ),
            name="lang",
        )

        # the status info stuff + tray
        self.date_time = DateTime(name="date-time")
        self.system_tray = SystemTray(name="system-tray", spacing=4)

## STATUS CIRCLES
#############################################################################################################################
        self.disk_progress = CircularProgressBar(
            name="cpu-progress-bar", size=27, line_style='butt', line_width=3, min_value=0, max_value=100
        )
        self.ram_progress = CircularProgressBar(
            name="cpu-progress-bar", size=27, line_style='butt', line_width=3, min_value=0, max_value=100
        )
        self.bat_circular = CircularProgressBar(
            name="cpu-progress-bar", size=27, line_style='butt', line_width=3, min_value=0, max_value=100
        ).build().set_value(42).unwrap()
            
        self.progress_container = Box(
            name="progress-bar-container",
            spacing=25,
            orientation="h",
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
                                    size=15,
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
                                    size=15,
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
                                    size=15,
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        )

#########################################################################################################

        self.command_layer = command_layer.InputMode()

        self.cpu_progress_bar = CircularProgressBar(
            name="cpu-progress-bar", size=24, line_style='butt'
        )
        self.progress_bars_overlay = Overlay(
            child=self.cpu_progress_bar,
            overlays=[
                Label("", style="margin: 0px 6px 0px 0px; font-size: 12px; color: #69C3FF;"),
            ],
        )

        self.status_container = Box(
            name="widgets-container",
            spacing=4,
            orientation="h",
            children=self.progress_bars_overlay,
        )
        self.status_container.add(VolumeWidget()) if AUDIO_WIDGET is True else None

        self.children = CenterBox(
            name="bar-inner",
            start_children=Box(
                name="start-container",
                spacing=4,
                orientation="h",
                children=[self.progress_container, self.command_layer.command_box],
            ),
            center_children=Box(
                name="center-container",
                spacing=0,
            ),
            end_children=Box(
                name="end-container",
                spacing=4,
                orientation="h",
                children=[
                    self.active_window,
                    self.status_container,
                    self.system_tray,
                    self.date_time,
                    self.language,
                ],
            ),
        )

        self.BLINK=1
        self.STATE=False

        invoke_repeater(850, self.update_progress_bars)


       
        self.show_all()
        self.command_layer.hide()
        self.command_layer.add_keybinding("Escape", lambda *_: self.toggle_off())
        self.command_layer.entry.connect("activate", self.fire_command)

    def toggle_off(self):
        self.command_layer.hide()
        self.STATE = not self.STATE
        self.command_layer.entry.set_text("")
        self.command_layer.command_input.set_label("Enter commands...")
        self.command_layer.command_box.add_style_class("inactive")
        self.command_layer.command_box.remove_style_class("active")

    def fire_command(self):
        self.command_layer.hide()
        self.STATE = not self.STATE
        process_cmd(self.command_layer.entry.get_text())
        self.command_layer.entry.set_text("")
        self.command_layer.command_input.set_label("Output ?")
        self.command_layer.command_box.add_style_class("inactive")
        self.command_layer.command_box.remove_style_class("active")

    def update_progress_bars(self):
         self.disk_progress.value = psutil.disk_usage('/home').percent
         self.ram_progress.value = psutil.virtual_memory().percent
         if not (bat_sen := psutil.sensors_battery()):
             self.bat_circular.value = 42
         else:
             self.bat_circular.value = bat_sen.percent


         self.cpu_progress_bar.value = psutil.cpu_percent() / 100
         if self.BLINK==0 and self.STATE:
             self.BLINK=1
             self.command_layer.command_input.set_label(f"{self.command_layer.entry.get_text()}")
         else:
             self.BLINK=0
             if self.STATE:
                 self.command_layer.command_input.set_label(f"{self.command_layer.entry.get_text()}█")
 

         return True


# running
if __name__ == "__main__":
    bar = StatusBar()

    def toggle_cmd_mode():
        if not bar.STATE:
            bar.command_layer.hide()
        else:
            bar.command_layer.show()
            bar.command_layer.command_box.add_style_class("active")
            bar.command_layer.command_box.remove_style_class("inactive")
            bar.command_layer.command_input.set_label("█")

    def on_change(monitor, file, other, event):
        if event == Gio.FileMonitorEvent.CHANGES_DONE_HINT:
            GLib.idle_add(toggle_cmd_mode)
            bar.STATE = not bar.STATE

    file = Gio.File.new_for_path(get_relative_path("../../../../.local/state/lobosstaterc"))
    monitor = file.monitor_file(
            Gio.FileMonitorFlags.NONE,
            None
        )
     
    monitor.connect("changed", on_change)

    app = Application("bar", bar)
    app.set_stylesheet_from_file(get_relative_path("bar.css"))

    app.run()
