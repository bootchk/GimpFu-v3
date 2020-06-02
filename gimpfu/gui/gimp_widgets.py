

import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

import logging



"""
Set of classes.
Each class is a GUI widget.

Each class ultimately inherits a Gimp widget.
Gimp widgets are GTK widgets but Gimp specialized for image editing.

Each class implements get_value().  (ABC has get_value)
get_value often converts type returned by Gtk widget to another type.
"""

module_logger = logging.getLogger("GimpFu.gimp_widgets")

"""
A Gimp.ColorButton displays a color, and pops up a Gimp.ColorSelector when clicked.
"""
class ColorEntry(Gimp.ColorButton):
    def __init__(self, default="", title = "Foo", ):
        module_logger.debug(f"ColorButton: default: {default} title: {title}")

        Gtk.Button.__init__(self)

        #TODO set default

        # Gimp requires title, so the pop-up ColorSelector can be titled.
        # Here, title is same as label of button
        # TODO Gimp throws critical : gimp_color_button_set_title: assertion 'title != NULL' failed but works anyway?

        self.set_title(title)
        # self.set_title("Border")

        #self.set_text(str(default))
        #self.set_activates_default(True)
        pass

    def get_value(self):
        return self.get_color()
