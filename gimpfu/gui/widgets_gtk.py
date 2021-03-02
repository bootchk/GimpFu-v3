


import gi

# !!! Even though docs generated from .gir say widgets are in Gimp, they are in GimpUi
#gi.require_version("GimpUi", "3.0")
#from gi.repository import GimpUi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

import logging

module_logger = logging.getLogger("GimpFu.WidgetsGtk")



"""
Classes of GimpFu widgets
that inherit GTK widgets.
"""

# TODO: DirnameSelector



"""
Is a button for text entry, when clicked shows file chooser dialog.

Lets user choose any file, not just image file formats.


Note some docs say Gimp.FileEntry is deprecated.
Since Gimp adds nothing to Gtk.FileChooserButton (?) we use the latter.
Besides Gimp.FileEntry throws: TypeError: function takes at most 0 arguments (1 given)
"""

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


'''
v2

def FileSelector(default="", title=None):
    # FIXME: should this be os.path.separator?  If not, perhaps explain why?
    if default and default.endswith("/"):
        if default == "/": default = ""
        return DirnameSelector(default)
    else:
        return FilenameSelector(default, title=title, save_mode=False)

class FilenameSelector(Gtk.HBox):
    #gimpfu.FileChooserButton
    def __init__(self, default, save_mode=True, title=None):
        super(FilenameSelector, self).__init__()
        if not title:
            self.title = _("Python-Fu File Selection")
        else:
            self.title = title
        self.save_mode = save_mode
        box = self
        self.entry = Gtk.Entry()
        image = Gtk.Image()
        image.set_from_stock(Gtk.STOCK_FILE, Gtk.ICON_SIZE_BUTTON)
        self.button = Gtk.Button()
        self.button.set_image(image)
        box.pack_start(self.entry)
        box.pack_start(self.button, expand=False)
        self.button.connect("clicked", self.pick_file)
        if default:
            self.entry.set_text(default)

    def show(self):
        super(FilenameSelector, self).show()
        self.button.show()
        self.entry.show()

    def pick_file(self, widget):
        entry = self.entry
        dialog = Gtk.FileChooserDialog(
                     title=self.title,
                     action=(Gtk.FILE_CHOOSER_ACTION_SAVE
                                 if self.save_mode else
                             Gtk.FILE_CHOOSER_ACTION_OPEN),
                     buttons=(Gtk.STOCK_CANCEL,
                            Gtk.RESPONSE_CANCEL,
                            Gtk.STOCK_SAVE
                                 if self.save_mode else
                            Gtk.STOCK_OPEN,
                            Gtk.RESPONSE_OK)
                    )
        dialog.set_alternative_button_order ((Gtk.RESPONSE_OK, Gtk.RESPONSE_CANCEL))
        dialog.show_all()
        response = dialog.run()
        if response == Gtk.RESPONSE_OK:
            entry.set_text(dialog.get_filename())
        dialog.destroy()

    def get_value(self):
        return self.entry.get_text()


class DirnameSelector(Gtk.FileChooserButton):
    def __init__(self, default=""):
        Gtk.FileChooserButton.__init__(self,
                                       _("Python-Fu Folder Selection"))
        self.set_action(Gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER)
        if default:
            self.set_filename(default)

    def get_value(self):
        return self.get_filename()
'''
