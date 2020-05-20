
"""
Thin wrapper around Gtk or Gimp GUI methods.
"""

class WarningDialog:

    # TODO this should just call Gimp.message ??
    # TODO WIP this v2 code crashes
    def show(parent, primary, secondary=None):
        dlg = Gtk.MessageDialog(parent, Gtk.DIALOG_DESTROY_WITH_PARENT,
                                        Gtk.MESSAGE_WARNING, Gtk.BUTTONS_CLOSE,
                                        primary)
        if secondary:
            dlg.format_secondary_text(secondary)
        dlg.run()
        dlg.destroy()
