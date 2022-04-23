
import gi

gi.require_version("GimpUi", "3.0")
from gi.repository import GimpUi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk



"""
Thin wrapper around Gimp and GTK functions.

Provides parent widget for ControlDialog and ExceptionDialog

implemented using Gimp.Dialog, which takes care of parenting

But is not a Gimp.ProcedureDialog;
is an alternative implementation of Gimp.ProcedureDialog
"""


class Dialog:
    def create(fuProcedure, gimpProcedure=None):
        # Configure use_header_bar from Gtk settings, not Gimp settings?
        use_header_bar = Gtk.Settings.get_default().get_property("gtk-dialogs-use-header")

        # TODO i18n ?

        """
        This dialog is only for the plugin/procedure we are implementing
        (not for procedures we may call.)
        So we can use the local FuProcedure instead of the Gimp.Procedure.
        """
        # Configure title the same as the menu label
        # title = gimpProcedure.get_menu_label()  # method of gimpProcedure
        title = fuProcedure.menu_label  # property of fuProcedure

        dialog = GimpUi.Dialog(use_header_bar=use_header_bar,
                             title = title)
        return dialog
