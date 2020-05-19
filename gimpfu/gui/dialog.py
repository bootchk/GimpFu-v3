
import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk



"""
Thin wrapper around Gimp and GTK functions.

Provides parent widget for ControlDialog and ExceptionDialog

implemented using Gimp.Dialog, which takes care of parenting
"""


class Dialog:
    def get(proc_name):
        use_header_bar = Gtk.Settings.get_default().get_property("gtk-dialogs-use-header")
        dialog = Gimp.Dialog(use_header_bar=use_header_bar,
                             title = proc_name)  # TODO i18n ?
        return dialog
