from fabric import Fabricator
from fabric.utils import get_relative_path
from fabric.widgets.box import Box
from fabric.widgets.label import Label




cava_widget = Box()
box = Box()
cava_label = Label(
        v_align="center",
        h_align="center",
)

script_path = get_relative_path("cava.sh")

box.children = Box(spacing=1, children=[cava_label]).build(
    lambda box, _: Fabricator(
        poll_from=f"bash -c '{script_path}'",
        interval=0,
        stream=True,
        on_changed=lambda f, line: cava_label.set_label(line),
    )
)

cava_widget.add(box)
