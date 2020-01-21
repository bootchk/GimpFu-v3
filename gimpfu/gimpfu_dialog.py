
'''

!!!
This all should go away when Gimp support for auto plugin GUI lands in Gimp 3.
Not well known that such support is on the roadmap.
!!!

'''

from collections import namedtuple

import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from gimpfu_types import *

from gimpfu_widgets import *

import gettext
t = gettext.translation("gimp30-python", Gimp.locale_directory, fallback=True)
_ = t.gettext

#from gi.repository import GObject




class EntryValueError(Exception):
    pass

# FUTURE i.e. work in progress
# TODO param actual_args of type Gimp.ValueArray.
def show_plugin_procedure_dialog():
    '''
    Implement using Gimp.ProcedureDialog

    Gimp is capable of displaying a dialog for a Gimp.Procedure.
    It takes a ProcedureConfig.
    Before the dialog run, ProcedureConfig contains initial values for widgets.
    After the dialog run, ProcedureConfig contains values the user chose.
    '''
    config = procedure.create_config()
    config.begin_run(image, Gimp.RunMode.INTERACTIVE, args)  # GObject.NULL)  # image, run_mode, args
    procedureDialog = Gimp.ProcedureDialog.new(procedure, config, 'foo')
    procedureDialog.run()
    config.end_run(GIMP_PDB_SUCCESS)

    '''
    , the above is somewhat based on this code from despeckle
  if (run_mode == GIMP_RUN_INTERACTIVE)
    {
      if (! despeckle_dialog (procedure, G_OBJECT (config), drawable))
        {
          return gimp_procedure_new_return_values (procedure,
                                                   GIMP_PDB_CANCEL,
                                                   NULL);
        }
    }

  despeckle (drawable, G_OBJECT (config));

  gimp_procedure_config_end_run (config, GIMP_PDB_SUCCESS);
  g_object_unref (config);
    '''

def _get_args_for_widget_factory(formal_param, widget_default_value):
    ''' Get args from formal spec, but override default with widget_default_value.  Returns list of args '''
    print("_get_args_for_widget_factory", formal_param, widget_default_value)
    # This is a switch statement on  PF_TYPE
    # Since data comes from GimpFu author, don't trust it
    if formal_param.PF_TYPE in ( PF_RADIO, ):
        args = [widget_default_value, formal_param.EXTRAS]
    elif formal_param.PF_TYPE in (PF_FILE, PF_FILENAME):
        # TODO need keyword 'title'?
        # args = [widget_default_value, title= "%s - %s" % (proc_name, tooltip_text)]
        args = [widget_default_value, "%s - %s" % (proc_name, tooltip_text)]
    elif formal_param.PF_TYPE in (PF_INT, PF_STRING, PF_BOOL ):
        args = [widget_default_value]
    elif formal_param.PF_TYPE in (PF_SLIDER, ):
        # Hack, we are using FloatEntry, should use Slider???
        args = [widget_default_value,]
    elif formal_param.PF_TYPE in (PF_COLOR, ):
        # Omitted, use a constant color
        color = Gimp.RGB()
        color.parse_name("orange", 6)
        args = [color,]
    else:
        # PF_SPINNER,, PF_OPTION
        raise RuntimeError("Unhandled PF_ widget type.")

    return args



def _add_control_widgets_to_dialog(box, actual_args, guiable_formal_params):
    ''' add control widget for each formal param, returning tuple of controls'''
    '''
    actual_args: is-a Gimp.ValueArray, actual_args (could be defaults or last values) as specified by how we registered with Gimp
    FUTURE: use them to create widget's initial values

    guiable_formal_params: a Python type, the original formal specs from plugin author in GimpFu notation,
       but just those that should have control widgets
    '''
    print("add_control_widgets")

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
    # TODO hacked to 2
    for i in range(2, len(guiable_formal_params)):
        print("Create control, index: ", i)
        # unpack tuple into namedtuple
        a_formal_param = GimpFuFormalParam(*guiable_formal_params[i])

        # Grid left hand side is LABEL
        label = Gtk.Label(a_formal_param.LABEL)
        label.set_use_underline(True)
        label.set_alignment(0.0, 0.5)
        grid.attach(label, 1, i, 1, 1)
        label.show()

        # Grid right hand side is control widget

        # widget types not range checked earlier
        # plugin author COULD have entered any integer
        try:
            #  e.g. widget_factory = StringEntry
            widget_factory = _edit_map[a_formal_param.PF_TYPE]
        except KeyError:
            exception_str = f"Invalid or not implemented PF_ widget type: {a_formal_param.PF_TYPE}"
            raise Exception(exception_str)


        '''
        There is a default specified in the guiable_formal_params,
        but override it with a value passed in, i.e. from LAST_VALS
        i.e. from the last value the user entered in the GUI.
        The default is now the default for the widget (not for the procedure.)
        TODO
        '''
        widget_default_value = a_formal_param.DEFAULT_VALUE
        tooltip_text = 'foo'  # TODO
        proc_name = 'bar' # TODO procedure.procedure_name()

        factory_specs = _get_args_for_widget_factory(a_formal_param, widget_default_value)

        print("Calling factory with specs", widget_factory, factory_specs)
        control_widget = widget_factory(*factory_specs)
        # e.g. control_widget = StringEntry(widget_default_value)
        label.set_mnemonic_widget(control_widget)
        grid.attach(control_widget, 2, i, 1, 1)

        '''
        TODO
        if pf_type != PF_TEXT:
            wid.set_tooltip_text(tooltip_text)
        else:
            # Attach tip to TextView, not to ScrolledWindow
            wid.view.set_tooltip_text(tooltip_text)
        '''

        control_widget.show()
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



def _create_gimp_dialog(actual_args, guiable_formal_params):
    '''
    Show plugin dialog implemented using Gimp.Dialog

    Returns a tuple of values or None (user canceled.)
    '''
    print("_create_gimp_dialog", actual_args, guiable_formal_params)

    use_header_bar = Gtk.Settings.get_default().get_property("gtk-dialogs-use-header")
    dialog = Gimp.Dialog(use_header_bar=use_header_bar,
                         title=_("Foo..."))

    dialog.add_button("_Cancel", Gtk.ResponseType.CANCEL)
    dialog.add_button("_OK", Gtk.ResponseType.OK)

    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,
                  homogeneous=False, spacing=12)
    dialog.get_content_area().add(box)
    box.show()

    controls = _add_control_widgets_to_dialog(box, actual_args, guiable_formal_params)

    return controls, dialog

    '''
    TODO Result from procedure exec
        return procedure.new_return_values(Gimp.PDBStatusType.CANCEL,
                                           GLib.Error())
    '''



def show_plugin_dialog(procedure, actual_args, guiable_formal_params, run_script):
    '''
    Present GUI.
    Returns (was_canceled, tuple of result values) from running plugin
    '''
    print("show_plugin_dialog", procedure, actual_args, guiable_formal_params, run_script)
    #assert type(procedure.__name == )
    #assert len(actual_args) == len(guiable_formal_params )
    #print("after assert")

    Gimp.ui_init('foo') # TODO procedure.name()

    # choice of implementation
    controls, dialog = _create_gimp_dialog(actual_args, guiable_formal_params)  # implemented by GimpFu in Python
    # show_plugin_procedure_dialog() # implemented by Gimp in C

    # TODO transient

    # Cancellation is not an error or exception, but part of result
    # if was_canceled is True, result_values is tuple of unknown contents
    result_values = []
    was_canceled = False

    '''
    Callback for responses.
    Continuation is either with dialog still waiting for user, or after Gtk.main() call
    Plugin func executes with dialog still shown, having progress bar.
    '''
    def response(dialog, id):
        nonlocal result_values
        nonlocal was_canceled
        nonlocal controls
        nonlocal procedure

        if id == Gtk.ResponseType.OK:
            # Ideal user feedback is disable buttons while working
            #dlg.set_response_sensitive(Gtk.ResponseType.OK, False)
            # TODO shouldn't Cancel remain true
            #dlg.set_response_sensitive(Gtk.ResponseType.CANCEL, False)

            try:
                result_values = []
                control_values = []
                for control in controls:
                    control_values.append(control.get_value())
            except EntryValueError:
                # Modal dialog whose parent is dialog
                # Note control has value from for loop
                warning_dialog(dialog, _("Invalid input for '%s'") % control.desc)
                # dialog stays up, waiting for user to fix or cancel??
            else:
                # control values valid
                was_canceled = False
                try:
                    # execute plugin with user inputs
                    # not cancelable?  In Gimp future, plugins should connect to a signal for cancel.
                    # TODO run_script is in caller
                    result_values = run_script(control_values)
                    '''
                except CancelError:
                    pass
                    '''
                except Exception:
                    dialog.set_response_sensitive(Gtk.ResponseType.CANCEL, True)
                    error_dialog(dialog, procedure.get_name())
                    raise
                    # ??? continuation ???
                else:
                    # result values from execution are valid
                    Gtk.main_quit()

        elif id == Gtk.ResponseType.CANCEL:
            was_canceled = True
            Gtk.main_quit()

        else:
            # TODO a RESET response??
            raise RuntimeError("Unhandled dialog response.")

    dialog.connect("response", response)
    dialog.show()
    # enter event loop, does not return until main_quit()
    Gtk.main()
    dialog.destroy()

    return was_canceled, result_values




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

def warning_dialog(parent, primary, secondary=None):
    dlg = Gtk.MessageDialog(parent, Gtk.DIALOG_DESTROY_WITH_PARENT,
                                    Gtk.MESSAGE_WARNING, Gtk.BUTTONS_CLOSE,
                                    primary)
    if secondary:
        dlg.format_secondary_text(secondary)
    dlg.run()
    dlg.destroy()


def error_dialog(parent, proc_name):
    ''' Display error dialog containing Python trace for latest exception '''
    import sys, traceback

    exc_str = exc_only_str = _("Missing exception information")

    try:
        etype, value, tb = sys.exc_info()
        exc_str = "".join(traceback.format_exception(etype, value, tb))
        exc_only_str = "".join(traceback.format_exception_only(etype, value))
    finally:
        etype = value = tb = None

    title = _("An error occurred running %s") % proc_name
    dlg = Gtk.MessageDialog(parent, 0, # TODO Gtk.DIALOG_DESTROY_WITH_PARENT,
                                    Gtk.MessageType.ERROR,
                                    Gtk.ButtonsType.CLOSE,
                                    title)
    dlg.format_secondary_text(exc_only_str)

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

    dlg.connect("response", response)
    dlg.set_resizable(True)
    dlg.show()


# Map PF_ enum to Widget class
_edit_map = {
        PF_INT         : IntEntry,
        PF_STRING      : StringEntry,
        PF_BOOL        : ToggleEntry,
        PF_TOGGLE      : ToggleEntry,
        PF_SLIDER      : FloatEntry,
        PF_RADIO       : RadioEntry,
        PF_COLOR       : OmittedEntry,
        }
