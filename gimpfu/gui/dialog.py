
import gi

gi.require_version("GimpUi", "3.0")
from gi.repository import GimpUi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk



"""
Thin wrapper around Gimp and GTK functions.

Provides parent widget for ControlDialog and ExceptionDialog

implemented using Gimp.Dialog, which takes care of parenting
"""


class Dialog:
    def create(fuProcedure, gimpProcedure):
        # Configure use_header_bar from Gtk settings, not Gimp settings?
        use_header_bar = Gtk.Settings.get_default().get_property("gtk-dialogs-use-header")

        # TODO i18n ?
        # Configure title the same as the menu label
        # title = gimpProcedure.get_menu_label()  # method of gimpProcedure
        title = fuProcedure.menu_label  # property of fuProcedure

        dialog = GimpUi.Dialog(use_header_bar=use_header_bar,
                             title = title)
        return dialog
