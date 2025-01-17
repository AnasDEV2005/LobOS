"""
example configuration shows how to make a simple
desktop applications launcher, this example doesn't involve
any styling (except a couple of basic style properties)


the purpose of this configuration is to show to to use
the given utils and mainly how using lazy executors might
make the configuration way more faster than it's supposed to be
"""


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
from fabric.utils import DesktopApp, get_desktop_applications, idle_add, remove_handler, get_relative_path


class AppLauncher(Window):
    def __init__(self, **kwargs):
        super().__init__(
            name="appwindow",
            layer="top",
            anchor="center",
            exclusivity="none",
            keyboard_mode="on-demand",
            visible=False,
            all_visible=False,
            **kwargs,
        )
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
            min_content_size=(280, 320),
            max_content_size=(280 * 2, 320),
            child=self.viewport,
        )

        self.add(
            Box(
                name="appslauncher",
                spacing=10,
                orientation="v",
                style="margin: 2px",
                children=[
                    # the header with the search entry
                    Box(
                        spacing=2,
                        orientation="h",
                        children=[
                            self.search_entry,
                            Button(
                                image=Image(icon_name="window-close"),
                                tooltip_text="Exit",
                                on_clicked=lambda *_: self.application.quit(),
                            ),
                        ],
                    ),
                    # the actual slots holder
                    self.scrolled_window,
                ],
            )
        )
        self.show_all()

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
            on_clicked=lambda *_: (app.launch(), self.application.quit()),
            **kwargs,
        )


if __name__ == "__main__":
    app_launcher = AppLauncher()
    app = Application("app-launcher", app_launcher)
    app.set_stylesheet_from_file(get_relative_path('app_launcher.css'))
    app.run()
