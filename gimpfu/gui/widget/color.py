

import gi

# !!! Even though docs generated from .gir say widgets are in Gimp, they are in GimpUi
gi.require_version("GimpUi", "3.0")
from gi.repository import GimpUi
# does not import Gtk

import logging


"""
A Gimp.ColorButton displays a color, and pops up a Gimp.ColorSelector dialog when clicked.

Color is not a resource, does not inherit GimpUi.SelectButton

Does not inherit GimpUi.ColorButton, but wraps it.
Failed to init when inherited.
See widget/gimp.py for similar pattern.
"""

class FuColorWidget():
    def __init__(self, defaultColor=None, title = "Foo", ):
        self.logger = logging.getLogger("GimpFu.FuColorWidget")
        self.logger.debug(f"ColorButton: default: {defaultColor} title: {title}")

        self.widget = GimpUi.ColorButton.new(title, 10, 10, defaultColor, GimpUi.ColorAreaType.SMALL_CHECKS)
        # Gimp requires title, so the pop-up ColorSelector can be titled.
        # Otherwise, at click time:  gimp_dialog_new: assertion 'title != NULL' failed

    def get_inner_widget(self):
        return self.widget

    def get_value(self):
        self.logger.debug(f"get_value")
        return self.widget.get_color()

"""
Cruft from attempt to inherit.

# try setting title before superclass init
# throws not initialized
#module_logger.debug(f"FuColorWidget: set_title")
#self.set_title(title)

# ColorButton has no init() method but GTK expects its __init__ to be called ???
# Both the following yield the same result
#Gtk.Button.__init__(self)
#super().__init__("foo")
"""
