

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

        # ColorButton has no init() method but GTK expects its __init__ to be called ???
        Gtk.Button.__init__(self)



        # Gimp requires title, so the pop-up ColorSelector can be titled.
        # Otherwise, at click time:  gimp_dialog_new: assertion 'title != NULL' failed

        # Here, title is same as label of button

        # ??? Gimp constructor has already thrown
        # critical : gimp_color_button_set_title: assertion 'title != NULL' failed but works anyway?
        # We will ignore it.

        self.set_title(title)
        # self.set_title("Border")

        # set default
        self.set_color(default)

        # cruft from StringEntry
        #self.set_activates_default(True)


    def get_value(self):
        return self.get_color()




"""
Is a button for text entry, when clicked shows file chooser dialog.

Note some docs say Gimp.FileEntry is deprecated.
Since Gimp adds nothing to Gtk.FileChooserButton (?) we use the latter.
Besides Gimp.FileEntry throws: TypeError: function takes at most 0 arguments (1 given)
"""
#
#class FuFileEntry:
#class FuFileEntry(Gimp.FileEntry):
class FuFileEntry(Gtk.FileChooserButton):


    def __init__(self, title = "Foo", default="", directory_only=False, check_valid=True):
        module_logger.debug(f"FuFileEntry: default: {default} title: {title}")

        #self.fe = Gimp.FileEntry()
        # TypeError: struct cannot be created directly; try using a constructor, see: help(Gimp.FileEntry)
        #module_logger.debug(f"After")

        # GTK expects its __init__ to be called ???
        Gtk.FileChooserButton.__init__(self)

        '''
        Requires title, so pop-up dialogs can be titled.
        Otherwise, at click time:  gimp_dialog_new: assertion 'title != NULL' failed
        Here, title is same as label of button
        '''
        self.set_title(title)

        # set default filename
        # File need not exist.
        self.set_filename(default)



    def get_value(self):
        # using the Gtk FileChooser interface
        return self.get_filename()
