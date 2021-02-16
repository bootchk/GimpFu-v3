
import gi
gi.require_version("Gimp", "3.0")
from gi.repository import Gimp

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from gimpfu.gui.dialog import Dialog


"""
# TODO:
use_header_bar = Gtk.Settings.get_default().get_property("gtk-dialogs-use-header")
dialog = Gtk.FileChooserDialog(use_header_bar=use_header_bar,
"""

class ExceptionDialog:

    # Public so it can be used for logging without a dialog
    @staticmethod
    def create_exception_str():
        ''' Create two strings from latest exception.'''

        import sys, traceback

        exc_str = exc_only_str = _("Missing exception information")

        try:
            etype, value, tb = sys.exc_info()
            exc_str = "".join(traceback.format_exception(etype, value, tb))
            exc_only_str = "".join(traceback.format_exception_only(etype, value))
        finally:
            etype = value = tb = None

        return exc_str, exc_only_str

    '''
    # TODO:
    Preferable to pass the exception string all the way back to Gimp
    as the result of the execution?
    TODO not tested
    '''
    @staticmethod
    def _create_error_dialog(proc_name):
        ''' Return error dialog containing Python trace for latest exception '''

        exc_str, exc_only_str =  ExceptionDialog.create_exception_str()

        title = _("An error occurred running %s") % proc_name

        '''
        This requires a parent, how to get???
        dlg = Gtk.MessageDialog(
                                parent,
                                0, # TODO Gtk.DIALOG_DESTROY_WITH_PARENT,
                                Gtk.MessageType.ERROR,
                                Gtk.ButtonsType.CLOSE,
                                title)
        '''
        # A basic dialog from Gimp works, but is not as pretty as our custom widget
        dlg = Dialog.get(proc_name)

        # TODO this pertains only to Gtk.MessageDialog
        # dlg.format_secondary_text(exc_only_str)

        '''
        #Since Gtk 3.14: Alignment deprecated.
        #TODO use parent properties.

        alignment = Gtk.Alignment(0.0, 0.0, 1.0, 1.0)
        alignment.set_padding(0, 0, 12, 12)
        dlg.vbox.pack_start(alignment)
        alignment.show()

        # TODO Since Gtk 3: broken
        expander = Gtk.Expander(_("_More Information"));
        expander.set_use_underline(True)
        expander.set_spacing(6)
        alignment.add(expander)
        expander.show()
        '''

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_size_request(-1, 200)
        dlg.vbox.pack_start(scrolled, expand=True, fill=True, padding=0)
        # WAS expander.add(scrolled)
        scrolled.show()

        # add full traceback in scrolling window
        label = Gtk.Label(exc_str)
        label.set_alignment(0.0, 0.0)
        label.set_padding(6, 6)
        label.set_selectable(True)
        # Since Gtk 3.8 add_with_viewport deprecated: use add()
        scrolled.add(label)
        label.show()

        def response(widget, id):
            widget.destroy()
            Gtk.main_quit()

        dlg.connect("response", response)
        dlg.set_resizable(True)
        return dlg


    # v3 exported.  v2 private
    @staticmethod
    def show(proc_name):
        ''' Display error dialog, parented. '''
        # require GTK is running.

        error_dialog = ExceptionDialog._create_error_dialog(proc_name)
        error_dialog.show()

        # Enter event loop, does not return until user chooses OK
        Gtk.main()
        # TODO who destroys, error_dialog.destroy()
