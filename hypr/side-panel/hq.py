from pynput import keyboard
import os
import time
import psutil
import operator
import subprocess
from collections.abc import Iterator
from loguru import logger
from fabric import Application
from fabric.widgets.box import Box
from fabric.widgets.centerbox import CenterBox
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
from fabric.utils import invoke_repeater


memory = []


disk = os.popen("du -h --max-depth=1 ~/ 2>/dev/null | sort -rh | tail -n +2 | head -n 10 | sed \"s|$HOME/|~/|\" | awk '{print $2, $1}'").read()
print(disk)
disk_users = disk.splitlines()
print(disk_users)



def parse_memory(output):
    lines = output.strip().split("\n")
    
    lines.pop(0)
    
    parsed_lines = []
    for line in lines:
        parts = line.rsplit(maxsplit=2)  # Split from the right
        command = parts[1]  # Extract the COMMAND (middle field)
        mem_usage = float(parts[2])  # Extract %MEM and convert to float
        
        
        parsed_lines.append([command, mem_usage])
    
    for i in range(0, len(parsed_lines)-1):
        if parsed_lines[i][0] == "":  parsed_lines[i][0] = "unknown process"


    memory = parsed_lines
    print(memory)
    return parsed_lines

output = os.popen("ps -eo pid,comm,%mem --sort=-%mem | tail -n +2 | awk '{print substr($2, 1, 8), $3}' | head -n 10").read()
memory = output.splitlines() 





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

class Overview(Window):
    @staticmethod
    def bake_progress_bar(value,**kwargs):
        return CircularProgressBar(
            name="mem-bar", min_value=0, max_value=100, line_width=3, line_style="butt", size=24, value=value,**kwargs
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
            exclusivity="normal",
            visible=False,
            all_visible=False,
            **kwargs,
        )



## the widget
#########################################################################################################
        self.profile_pic = Box(
            name="profile-pic",
            size=200,
            style=f"background-image: url(\"file://{get_profile_picture_path() or ''}\")",
        )
        self.uptime_label = Label(label=f"{self.get_current_uptime()}")
 
        self.memory = Box(orientation = "v",
            children = [ Label(label = "MEMORY   &   DISK-SPACE", style = "font-weight: 800;"),

        Box(
            name = "inside-box",
            orientation = "h",
            spacing = 50,
            children = [Box(
                        h_align ="start",
                        v_align = "start",
                        orientation="v",
                        spacing = 14,
                        children = [

                        Label(v_align = "start", h_align = "start",name="memlabels", label = (memory[0]+"%")), 
                        Label(v_align = "start", h_align = "start",name="memlabels", label = (memory[1]+"%")), 
                        Label(v_align = "start", h_align = "start",name="memlabels", label = (memory[2]+"%")),
                        Label(v_align = "start", h_align = "start",name="memlabels", label = (memory[3]+"%")),
                        Label(v_align = "start", h_align = "start",name="memlabels", label = (memory[4]+"%")),
                        Label(v_align = "start", h_align = "start",name="memlabels", label = (memory[5]+"%")), 
                        Label(v_align = "start", h_align = "start",name="memlabels", label = (memory[6]+"%")),
                        Label(v_align = "start", h_align = "start",name="memlabels", label = (memory[7]+"%")),
                        Label(v_align = "start", h_align = "start",name="memlabels", label = (memory[8]+"%")),]
                        ),
                        Box( 
                        h_align = "start",
                        v_align = "start",
                        orientation="v",
                        spacing = 14,
                        children = [
                        Label(v_align = "start", h_align = "start", name="memlabels", label = disk_users[0]), 
                        Label(v_align = "start", h_align = "start",name="memlabels", label = disk_users[1]), 
                        Label(v_align = "start", h_align = "start",name="memlabels", label = disk_users[2]),
                        Label(v_align = "start", h_align = "start",name="memlabels", label = disk_users[3]),
                        Label(v_align = "start", h_align = "start",name="memlabels", label = disk_users[4]),
                        Label(v_align = "start", h_align = "start",name="memlabels", label = disk_users[5]), 
                        Label(v_align = "start", h_align = "start",name="memlabels", label = disk_users[6]),
                        Label(v_align = "start", h_align = "start",name="memlabels", label = disk_users[7]),
                        Label(v_align = "start", h_align = "start",name="memlabels", label = disk_users[8]),]
                        )
                    ]
            )
                        ])

        self.header = Box(
            spacing=14,
            name="header-inner",
            orientation="h",
            children=[
                self.profile_pic,
                Box(
                    spacing=6,
                    orientation="v",
                    children = [
                        Box(
                            name = "inside-box",
                            orientation="v",
                            children= [
                                DateTime(
        name="date-time",
                                    style="margin-top: 4px; min-width: 180px;",
                                ),
                            ],
                        ),
                        Box(
                            name = "inside-box",
                            orientation="v",
                            children= [ self.uptime_label]
                        ),
                        
                    ],
                ),
            ],
        )
        

        self.media_buttons = CenterBox(
            orientation="h",
            start_children = Button(),
            center_children= Button(),
            end_children= Button(),
        )
        self.media_player = Box(name="media-player",
                    orientation="v",
                    children= [
                        Label(max_chars_width=12,
                            line_wrap="char",
                            size=(250, 50),
                            name = "media",
                            label = "Media",
                            style="margin-top: 4px;",
                        ),
                    ]
                )

        self.bottom = Box(
            orientation="h",
            spacing = 50,
            children = [
                self.media_player, 
                self.memory
            ]
        )


        self.hq = Box(
                    orientation="v",
                    name="hq",
                    children=[self.header, self.bottom, self.memory],
                )

        self.add(self.hq)


        invoke_repeater(1000, self.update_membars)
         

        self.show_all()







    def update_membars(self, *args):
        output = os.popen("ps -eo pid,comm,%mem --sort=-%mem | tail -n +2 | awk '{print substr($2, 1, 8), $3}' | head -n 10").read()
        memory = output.splitlines()
        for i in range(0, 8):
            self.memory.children[1].children[0].children[i].set_label(str(memory[i]+"%"))
        print("test")
        media_title= os.popen("playerctl metadata | grep 'xesam:title' | sed 's/^.*xesam:title[[:space:]]*//g'").read()
        media_artist= os.popen("playerctl metadata | grep 'xesam:artist' | sed 's/^.*xesam:artist[[:space:]]*//g'").read()
        text = media_artist+" - "+media_title
        if len(text) > 32: text = text[29:]+"..."
        self.media_player.children[0].set_label(text)
        return True

## some more functions
    def close_widget(self):
        self.close()

    def get_current_uptime(self):
        uptime = time.time() - psutil.boot_time()
        uptime_days, remainder = divmod(uptime, 86400)
        uptime_hours, remainder = divmod(remainder, 3600)
        return f"{int(uptime_days)} {'days' if uptime_days > 1 else 'day'}, {int(uptime_hours)} {'hours' if uptime_hours > 1 else 'hour'}"

    def toggle_overview_widget(self):
        if self.hq.is_visible(): 
            self.hq.hide()
            self.memory.children.clear()



        else: 
            self.hq.show()



if __name__ == "__main__":
    overview = Overview()
    app = Application("hq", overview)
    app.set_stylesheet_from_file(get_relative_path("side_panel.css"))
    app.run()

