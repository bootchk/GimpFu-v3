

import gi

# !!! Even though docs generated from .gir say widgets are in Gimp, they are in GimpUi
gi.require_version("GimpUi", "3.0")
from gi.repository import GimpUi
# does not import Gtk

import logging

module_logger = logging.getLogger("GimpFu.widgets_resource")

"""
Widgets for choosing Gimp resources.

Resources
"""


"""
A Gimp.ColorButton displays a color, and pops up a Gimp.ColorSelector dialog when clicked.
"""
class FuColorEntry(GimpUi.ColorButton):
    def __init__(self, default="", title = "Foo", ):
        module_logger.debug(f"ColorButton: default: {default} title: {title}")

        # try setting title before superclass init
        # throws not initialized
        #module_logger.debug(f"FuColorEntry: set_title")
        #self.set_title(title)

        # ColorButton has no init() method but GTK expects its __init__ to be called ???
        # Both the following yield the same result
        #Gtk.Button.__init__(self)
        super().__init__("foo")

        # Gimp requires title, so the pop-up ColorSelector can be titled.
        # Otherwise, at click time:  gimp_dialog_new: assertion 'title != NULL' failed

        # Here, title is same as label of button

        # ??? Gimp constructor has already thrown
        # critical : gimp_color_button_set_title: assertion 'title != NULL' failed but works anyway?
        # We will ignore it.

        module_logger.debug(f"FuColorEntry: set_title")
        self.set_title(title)
        # self.set_title("Border")

        # set default
        self.set_color(default)

        # cruft from StringEntry
        #self.set_activates_default(True)


    def get_value(self):
        return self.get_color()




class FuFontEntry(GimpUi.FontSelectButton):
    def __init__(self, default="" ):
        module_logger.debug(f"FuFontEntry: default: {default}")

        # Gimp.FontSelectButton has no init() method but GTK expects its __init__ to be called ???
        # Gimp.FontSelectButton inherits Gtk.Widget
        # TODO super().__init__()
        #Gtk.Widget.__init__(self)
        super().__init__()

        # Has no set_title

        # set default
        self.set_font(default)

    def get_value(self):
        return self.get_font()



class FuPaletteEntry(GimpUi.PaletteSelectButton):
    def __init__(self, default="" ):
        module_logger.debug(f"FuPaletteEntry: default: {default}")

        # Gimp.FontSelectButton has no init() method but GTK expects its __init__ to be called ???
        # Gimp.FontSelectButton inherits Gtk.Widget
        super().__init__()

        # Has no set_title

        self.set_palette(default)

    def get_value(self):
        return self.get_palette()
