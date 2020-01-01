

from collections import namedtuple

import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from gimpfu_types import *


import gettext
t = gettext.translation("gimp30-python", Gimp.locale_directory, fallback=True)
_ = t.gettext

#from gi.repository import GObject




class EntryValueError(Exception):
    pass

def show_plugin_procedure_dialog():
    '''
    Implement using Gimp.ProcedureDialog
    '''
    config = procedure.create_config()
    config.begin_run(image, Gimp.RunMode.INTERACTIVE, args)  # GObject.NULL)  # image, run_mode, args
    procedureDialog = Gimp.ProcedureDialog.new(procedure, config, 'foo')
    procedureDialog.run()
    config.end_run(GIMP_PDB_SUCCESS)

    '''
    work in progress, the above is not finished
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


def add_control_widgets_to_dialog(box, args, formal_params):
    ''' add control widget for each formal param, returning tuple of controls'''
    '''
    args: a Gimp type, actual args (could be defaults or last values) as specified by how we registered with Gimp
    formal_params: a Python type, the original formal specs from plugin author in GimpFu notation
    '''
    label = Gtk.Label.new_with_mnemonic("Off_set")
    box.pack_start(label, False, False, 1)
    label.show()

    # Keep reference so can query during response
    control_widgets = []

    # box layout is grid
    grid = Gtk.Grid()
    grid.set_row_spacing(6)
    grid.set_column_spacing(6)
    # GTK 3: five args (self + 4)
    box.pack_start(grid, expand=False, fill=True, padding=0)
    grid.show()

    # omit leading 2 boilerplate params
    # TODO should have been hacked off earlier?
    for i in range(2, len(formal_params)):
        # unpack tuple into namedtuple
        a_formal_param = GimpFuFormalParam(*formal_params[i])

        # Grid left hand side is LABEL
        label = Gtk.Label(a_formal_param.LABEL)
        label.set_use_underline(True)
        label.set_alignment(0.0, 0.5)
        grid.attach(label, 1, i, 1, 1)
        label.show()

        # Grid right hand side is control widget

        widget_factory = _edit_mapping[a_formal_param.PF_TYPE]
        #  e.g. widget_factory = StringEntry

        # TODO def_val comes from somewhere else? LAST_VALS ?
        def_val = a_formal_param.DEFAULT_VALUE
        tooltip_text = 'foo'  # TODO
        proc_name = 'bar' # TODO procedure.procedure_name()

        # Build args to widget_factory according to PF_TYPE
        if a_formal_param.PF_TYPE in (PF_SPINNER, PF_SLIDER, PF_RADIO, PF_OPTION):
            args = [def_val, a_formal_param.EXTRAS]
        elif a_formal_param.PF_TYPE in (PF_FILE, PF_FILENAME):
            # TODO need keyword 'title'?
            # args = [def_val, title= "%s - %s" % (proc_name, tooltip_text)]
            args = [def_val, "%s - %s" % (proc_name, tooltip_text)]
        else:
            args = [def_val]

        control_widget = widget_factory(*args)
        # e.g. control_widget = StringEntry(def_val)
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



def create_gimp_dialog(args, formal_params):
    '''
    Show plugin dialog implemented using Gimp.Dialog

    Returns a tuple of values or None (user canceled.)
    '''

    use_header_bar = Gtk.Settings.get_default().get_property("gtk-dialogs-use-header")
    dialog = Gimp.Dialog(use_header_bar=use_header_bar,
                         title=_("Offset Palette..."))

    dialog.add_button("_Cancel", Gtk.ResponseType.CANCEL)
    dialog.add_button("_OK", Gtk.ResponseType.OK)

    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,
                  homogeneous=False, spacing=12)
    dialog.get_content_area().add(box)
    box.show()

    controls = add_control_widgets_to_dialog(box, args, formal_params)

    return controls, dialog

    '''
    TODO Result from procedure exec
        return procedure.new_return_values(Gimp.PDBStatusType.CANCEL,
                                           GLib.Error())
    '''



def show_plugin_dialog(procedure, args, formal_params, run_script):
    '''
    Present GUI.
    Returns was_canceled, tuple of result values from running plugin
    '''

    print("Count actual args", args.length() )
    print("Count formal args", len(formal_params ) )

    Gimp.ui_init('foo')

    # choice of implementation
    controls, dialog = create_gimp_dialog(args, formal_params)  # implemented by GimpFu in Python
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


# define a mapping of param types to edit objects ...
# see below


class StringEntry(Gtk.Entry):
    def __init__(self, default=""):
        Gtk.Entry.__init__(self)
        self.set_text(str(default))
        self.set_activates_default(True)

    def get_value(self):
        return self.get_text()
'''
class TextEntry(Gtk.ScrolledWindow):
    def __init__ (self, default=""):
        Gtk.ScrolledWindow.__init__(self)
        self.set_shadow_type(Gtk.SHADOW_IN)

        self.set_policy(Gtk.POLICY_AUTOMATIC, Gtk.POLICY_AUTOMATIC)
        self.set_size_request(100, -1)

        self.view = Gtk.TextView()
        self.add(self.view)
        self.view.show()

        self.buffer = self.view.get_buffer()

        self.set_value(str(default))

    def set_value(self, text):
        self.buffer.set_text(text)

    def get_value(self):
        return self.buffer.get_text(self.buffer.get_start_iter(),
                                    self.buffer.get_end_iter())
'''
class IntEntry(StringEntry):
    def get_value(self):
        try:
            return int(self.get_text())
        except ValueError as e:
            raise EntryValueError(e.args)
'''
class FloatEntry(StringEntry):
        def get_value(self):
            try:
                return float(self.get_text())
            except ValueError as e:
                raise EntryValueError(e.args)

#    class ArrayEntry(StringEntry):
#            def get_value(self):
#                return eval(self.get_text(), {}, {})


def precision(step):
    # calculate a reasonable precision from a given step size
    if math.fabs(step) >= 1.0 or step == 0.0:
        digits = 0
    else:
        digits = abs(math.floor(math.log10(math.fabs(step))));
    if digits > 20:
        digits = 20
    return int(digits)

class SliderEntry(Gtk.HScale):
    # bounds is (upper, lower, step)
    def __init__(self, default=0, bounds=(0, 100, 5)):
        step = bounds[2]
        self.adj = Gtk.Adjustment(default, bounds[0], bounds[1],
                                  step, 10 * step, 0)
        Gtk.HScale.__init__(self, self.adj)
        self.set_digits(precision(step))

    def get_value(self):
        return self.adj.value

class SpinnerEntry(Gtk.SpinButton):
    # bounds is (upper, lower, step)
    def __init__(self, default=0, bounds=(0, 100, 5)):
        step = bounds[2]
        self.adj = Gtk.Adjustment(default, bounds[0], bounds[1],
                                  step, 10 * step, 0)
        Gtk.SpinButton.__init__(self, self.adj, step, precision(step))

class ToggleEntry(Gtk.ToggleButton):
    def __init__(self, default=0):
        Gtk.ToggleButton.__init__(self)

        self.label = Gtk.Label(_("No"))
        self.add(self.label)
        self.label.show()

        self.connect("toggled", self.changed)

        self.set_active(default)

    def changed(self, tog):
        if tog.get_active():
            self.label.set_text(_("Yes"))
        else:
            self.label.set_text(_("No"))

    def get_value(self):
        return self.get_active()

class RadioEntry(Gtk.VBox):
    def __init__(self, default=0, items=((_("Yes"), 1), (_("No"), 0))):
        Gtk.VBox.__init__(self, homogeneous=False, spacing=2)

        button = None

        for (label, value) in items:
            button = Gtk.RadioButton(button, label)
            self.pack_start(button)
            button.show()

            button.connect("toggled", self.changed, value)

            if value == default:
                button.set_active(True)
                self.active_value = value

    def changed(self, radio, value):
        if radio.get_active():
            self.active_value = value

    def get_value(self):
        return self.active_value

class ComboEntry(Gtk.ComboBox):
    def __init__(self, default=0, items=()):
        store = Gtk.ListStore(str)
        for item in items:
            store.append([item])

        Gtk.ComboBox.__init__(self, model=store)

        cell = Gtk.CellRendererText()
        self.pack_start(cell)
        self.set_attributes(cell, text=0)

        self.set_active(default)

    def get_value(self):
        return self.get_active()

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

_edit_mapping = {
        PF_INT         : IntEntry,
        PF_STRING      : StringEntry,
        }
