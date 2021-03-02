
'''
!!!
This all should go away when Gimp support for auto plugin GUI lands in Gimp 3.
Not well known that such support is on the roadmap.
'''

import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
#from gi.repository import GObject

from gimpfu.gui.dialog import Dialog
from gimpfu.gui.warning_dialog import WarningDialog
from gimpfu.gui.value_error import EntryValueError
from gimpfu.gui.widget_factory import WidgetFactory

from gimpfu.message.deprecation import Deprecation

import logging


import gettext
t = gettext.translation("gimp30-python", Gimp.locale_directory, fallback=True)
_ = t.gettext



"""
Probably CRUFT
# FUTURE i.e. work in progress
# TODO param guiable_initial_values of type Gimp.ValueArray.
def show_plugin_procedure_dialog():
    '''
    Implement using Gimp.ProcedureDialog

    Gimp is capable of displaying a dialog for a Gimp.Procedure.
    It takes a ProcedureConfig.
    Before the dialog run, ProcedureConfig contains initial values for widgets.
    After the dialog run, ProcedureConfig contains values the user chose.
    '''
    procedureDialog = Gimp.ProcedureDialog.new(procedure, config, 'foo')
    procedureDialog.run()
  """


class PluginControlDialog():

    logger = logging.getLogger("GimpFu.PluginControlDialog")

    @staticmethod
    def _add_tooltip_to_widget(wid, a_formal_param ):

        tooltip_text = a_formal_param.tooltip_text

        if WidgetFactory.does_widget_have_view(a_formal_param):
            # Attach tip to TextView, not to ScrolledWindow
            wid.view.set_tooltip_text(tooltip_text)
        else:
            # attach tooltip to entry box of control widget
            wid.set_tooltip_text(tooltip_text)


    @staticmethod
    def _add_control_widgets_to_dialog(box, guiable_initial_values, guiable_formal_params):
        ''' add control widget for each formal param, returning tuple of controls'''
        '''
        guiable_initial_values: is-a Gimp.ValueArray, guiable_initial_values (could be defaults or last values)
        as specified by how we registered with Gimp

        guiable_formal_params: a Python type, formal specs from author in GimpFu notation,
        but just guiable (those that should have control widgets.)
        '''
        PluginControlDialog.logger.debug(f"add_control_widgets: {guiable_initial_values}")

        # This is a label above the column of value entry Widgets
        # TODO what should it say?
        label = Gtk.Label.new_with_mnemonic("Off_set")
        box.pack_start(label, False, False, 1)
        label.show()

        # Keep reference so can query during response
        control_widgets = []

        # box layout is grid
        grid = Gtk.Grid()
        grid.set_row_spacing(6)
        grid.set_column_spacing(6)
        box.pack_start(grid, expand=False, fill=True, padding=0)
        grid.show()

        # assert leading 2 boilerplate params image and drawable hacked off earlier?
        # TODO hacked to (2,
        for i in range(0, len(guiable_formal_params)):
            a_formal_param = guiable_formal_params[i]

            # Grid left hand side is LABEL
            label = Gtk.Label(a_formal_param.label)
            label.set_use_underline(True)
            label.set_alignment(1.0, 0.5)
            grid.attach(label, 1, i, 1, 1)
            label.show()

            # Grid right hand side is control widget
            control_widget = WidgetFactory.produce(a_formal_param, guiable_initial_values[i])

            if WidgetFactory.is_wrapped_widget(a_formal_param):
                inner_widget = control_widget.get_inner_widget()
            else:
                inner_widget = control_widget
            # assert inner_widget is a Gtk widget

            """
            Do stuff with the Gtk inner widget.
            """
            label.set_mnemonic_widget(inner_widget)
            grid.attach(inner_widget, 2, i, 1, 1)
            PluginControlDialog._add_tooltip_to_widget(inner_widget, a_formal_param )
            inner_widget.show()

            # Keep the outer widget
            control_widget.desc = a_formal_param.DESC
            control_widgets.append(control_widget)

        return control_widgets


    '''
    Cruft from pallette.py ?
    Illustrating using properties

    Create control widget using Gimp and property

    amount = self.set_property("amount", amount)

    spin = Gimp.prop_spin_button_new(self, "amount", 1.0, 5.0, 0)
    spin.set_activates_default(True)
    box.pack_end(spin, False, False, 1)
    spin.show()
    '''



    @staticmethod
    def _create_gimp_dialog(procname, guiable_initial_values, guiable_formal_params):
        '''
        Create plugin dialog

        Returns list of control widgets and dialog
        '''
        PluginControlDialog.logger.debug(f"_create_gimp_dialog:  {guiable_initial_values}: {guiable_formal_params} ")

        dialog = Dialog.get(procname)

        dialog.add_button("_Cancel", Gtk.ResponseType.CANCEL)
        dialog.add_button("_OK", Gtk.ResponseType.OK)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,
                      homogeneous=False, spacing=12)
        dialog.get_content_area().add(box)
        box.show()

        controls = PluginControlDialog._add_control_widgets_to_dialog(box, guiable_initial_values, guiable_formal_params)

        return controls, dialog

        '''
        TODO Result from procedure exec
            return procedure.new_return_values(Gimp.PDBStatusType.CANCEL,
                                               GLib.Error())
        '''



    '''
    v2 this took a function argument run_script (the plugin algorithem)
    and called it, returning its results.
    So that the dialog would stay up with its progress bar
    while the plugin algorithm executed.

    v3 does not take a function argument.
    Caller executes the plugin algorithm
    Progress is still shown, but in the image's display window's progress bar.
    '''
    @classmethod
    def show(cls, procedure, guiable_initial_values, guiable_formal_params):
        '''
        Present GUI.
        Returns (was_canceled, tuple of result values) from running plugin
        '''
        PluginControlDialog.logger.debug(f"show_plugin_dialog for {procedure} values: {guiable_initial_values} formal: {guiable_formal_params}")
        #assert type(procedure.__name == )
        #assert len(guiable_initial_values) == len(guiable_formal_params )
        #print("after assert")

        # This was done eariler:  Gimp.ui_init('foo') # TODO procedure.name()

        # choice of implementation
        controls, dialog = PluginControlDialog._create_gimp_dialog(
            procedure.get_name(),
            guiable_initial_values,
            guiable_formal_params)  # implemented by GimpFu in Python
        # show_plugin_procedure_dialog() # implemented by Gimp in C

        # TODO transient

        # Cancellation is not an error or exception, but part of result
        # if was_canceled is True, result_values is tuple of unknown contents
        # else result_values are the user edited args (values from controls)
        control_values = []
        was_canceled = False

        '''
        Callback for responses.
        Continuation is either with dialog still waiting for user, or after Gtk.main() call
        Plugin func executes with dialog still shown, having progress bar.
        '''
        def response(dialog, id):
            nonlocal control_values
            nonlocal was_canceled
            nonlocal controls
            nonlocal procedure

            if id == Gtk.ResponseType.OK:
                # Ideal user feedback is disable buttons while working
                #dlg.set_response_sensitive(Gtk.ResponseType.OK, False)
                # TODO shouldn't Cancel remain true
                #dlg.set_response_sensitive(Gtk.ResponseType.CANCEL, False)

                # clear, because prior response might have aborted with partial control_values
                control_values = []

                try:
                    for control in controls:
                        control_values.append(control.get_value())
                except EntryValueError:
                    # Modal dialog whose parent is plugin dialog
                    # Note control has value from for loop
                    WarningDialog.show(dialog, _("Invalid input for '%s'") % control.desc)
                    # abort response, dialog stays up, waiting for user to fix or cancel??
                else:   # executed when try succeeds
                    # assert control values valid
                    was_canceled = False
                    Gtk.main_quit()
                    # caller will execute run_func with control_values

            elif id == Gtk.ResponseType.CANCEL:
                was_canceled = True
                control_values = []
                Gtk.main_quit()

            else:
                # TODO a RESET response??
                raise RuntimeError("Unhandled dialog response.")

        dialog.connect("response", response)
        dialog.show()
        # enter event loop, does not return until main_quit()
        Gtk.main()
        dialog.destroy()

        PluginControlDialog.logger.debug(f"dialog returns: {control_values}")
        return was_canceled, control_values




'''
    # rest of this v2


    dialog = Gtk.Dialog(proc_name, "python-fu", None, 0, None, proc_name,
                           (Gtk.STOCK_CANCEL, Gtk.RESPONSE_CANCEL,
                            Gtk.STOCK_OK, Gtk.RESPONSE_OK))

    dialog.set_alternative_button_order((Gtk.RESPONSE_OK, Gtk.RESPONSE_CANCEL))

    dialog.set_transient()

    vbox = Gtk.VBox(False, 12)
    vbox.set_border_width(12)
    dialog.vbox.pack_start(vbox)
    vbox.show()

    if blurb:
        if domain:
            try:
                (domain, locale_dir) = domain
                trans = gettext.translation(domain, locale_dir, fallback=True)
            except ValueError:
                trans = gettext.translation(domain, fallback=True)
            blurb = trans.ugettext(blurb)
        box = gimpui.HintBox(blurb)
        vbox.pack_start(box, expand=False)
        box.show()

    grid = Gtk.Grid ()
    grid.set_row_spacing(6)
    grid.set_column_spacing(6)
    vbox.pack_start(grid, expand=False)
    grid.show()

    def response(dlg, id):
        if id == Gtk.RESPONSE_OK:
            dlg.set_response_sensitive(Gtk.RESPONSE_OK, False)
            dlg.set_response_sensitive(Gtk.RESPONSE_CANCEL, False)

            params = []

            try:
                for wid in edit_wids:
                    params.append(wid.get_value())
            except EntryValueError:
                warning_dialog(dialog, _("Invalid input for '%s'") % wid.desc)
            else:
                try:
                    dialog.res = run_script(params)
                except CancelError:
                    pass
                except Exception:
                    dlg.set_response_sensitive(Gtk.RESPONSE_CANCEL, True)
                    error_dialog(dialog, proc_name)
                    raise

        Gtk.main_quit()

    dialog.connect("response", response)

    edit_wids = []
    for i in range(len(params)):
        pf_type = params[i][0]
        name = params[i][1]
        desc = params[i][2]
        def_val = defaults[i]

        label = Gtk.Label(desc)
        label.set_use_underline(True)
        label.set_alignment(0.0, 0.5)
        grid.attach(label, 1, i, 1, 1)
        label.show()

        # Remove accelerator markers from tooltips
        tooltip_text = desc.replace("_", "")

        if pf_type in (PF_SPINNER, PF_SLIDER, PF_RADIO, PF_OPTION):
            wid = _edit_mapping[pf_type](def_val, params[i][4])
        elif pf_type in (PF_FILE, PF_FILENAME):
            wid = _edit_mapping[pf_type](def_val, title= "%s - %s" %
                                          (proc_name, tooltip_text))
        else:
            wid = _edit_mapping[pf_type](def_val)


        label.set_mnemonic_widget(wid)

        grid.attach(wid, 2, i, 1, 1)

        if pf_type != PF_TEXT:
            wid.set_tooltip_text(tooltip_text)
        else:
            # Attach tip to TextView, not to ScrolledWindow
            wid.view.set_tooltip_text(tooltip_text)
        wid.show()

        wid.desc = desc
        edit_wids.append(wid)

    progress_vbox = Gtk.VBox(False, 6)
    vbox.pack_end(progress_vbox, expand=False)
    progress_vbox.show()

    progress = gimpui.ProgressBar()
    progress_vbox.pack_start(progress)
    progress.show()

#    progress_label = Gtk.Label()
#    progress_label.set_alignment(0.0, 0.5)
#    progress_label.set_ellipsize(pango.ELLIPSIZE_MIDDLE)

#    attrs = pango.AttrList()
#    attrs.insert(pango.AttrStyle(pango.STYLE_ITALIC, 0, -1))
#    progress_label.set_attributes(attrs)

#    progress_vbox.pack_start(progress_label)
#    progress_label.show()

    dialog.show()

    Gtk.main()

    if hasattr(dialog, "res"):
        res = dialog.res
        dialog.destroy()
        return res
    else:
        dialog.destroy()
        raise CancelError
'''
