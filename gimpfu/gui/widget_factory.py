
# WidgetFactory is main use of PF_enum
from gimpfu_enums import *

# No GI of Gimp here

# WidgetFactory is main use of Widget constructors
from gui.widgets import *


class WidgetFactory:

    def does_widget_have_view(a_formal_param):

        return a_formal_param.PF_TYPE == PF_TEXT


    def produce(a_formal_param, guiable_initial_value):
        # widget types not range checked earlier
        # author COULD err by specifying out of range widget type
        try:
            #  e.g. widget_constructor = StringEntry
            widget_constructor = _edit_map[a_formal_param.PF_TYPE]
        except KeyError:
            exception_str = f"Invalid or not implemented PF_ widget type: {a_formal_param.PF_TYPE}"
            raise Exception(exception_str)

        '''
        There is a default specified in the guiable_formal_params.
        But initial value is passed in,
        i.e. from the last value the user entered in the GUI.
        This is a hack until FuProcedureConfig works, i.e.
        until we can register args with Gimp using GProperty or GParamSpec
        '''
        is_use_defaults = True
        if is_use_defaults:
            widget_initial_value = a_formal_param.DEFAULT_VALUE
        else:
            widget_initial_value = guiable_initial_values[i]

        proc_name = 'bar' # TODO procedure.procedure_name()

        factory_specs = WidgetFactory._get_args_for_widget_constructor(a_formal_param, widget_initial_value)

        # TODO pass tooltip_text
        # tooltip_text = a_formal_param.tooltip_text)
        print("Calling factory with specs", widget_constructor, factory_specs)
        result = widget_constructor(*factory_specs)

        return result


    def _get_args_for_widget_constructor(formal_param, widget_initial_value):
        ''' Get args from formal spec, but override default with widget_initial_value.  Returns list of args '''
        print("_get_args_for_widget_constructor", formal_param, widget_initial_value)
        # This is a switch statement on  PF_TYPE
        # Since data comes from , don't trust it
        pf_type = formal_param.PF_TYPE


        if pf_type == PF_COLOUR:
            Deprecation.say("Use PF_COLOR instead of PF_COLOUR")

        if pf_type in ( PF_RADIO, ):
            args = [widget_initial_value, formal_param.EXTRAS]
        elif pf_type in (PF_FILE, PF_FILENAME):
            # TODO need keyword 'title'?
            # args = [widget_initial_value, title= "%s - %s" % (proc_name, tooltip_text)]
            # args = [widget_initial_value, "%s - %s" % (proc_name, tooltip_text)]
            # TEMP: widget is omitted, use default defined by author

            # TODO this should work, but its not
            # args = [widget_initial_value,]
            args = ["/tmp/lkkfoopluginout"]
        elif pf_type in (PF_INT, PF_INT8, PF_INT16, PF_INT32, PF_STRING, PF_BOOL, PF_OPTION, PF_FONT, PF_TEXT ):
            args = [widget_initial_value]
        elif pf_type in (PF_SLIDER, PF_FLOAT, PF_SPINNER, PF_ADJUSTMENT):
            # Hack, we are using FloatEntry, should use Slider???
            args = [widget_initial_value,]
        elif pf_type in (PF_COLOR, PF_COLOUR):
            # Omitted, use a constant color
            color = Gimp.RGB()
            color.parse_name("orange", 6)
            args = [color,]
        elif pf_type in (PF_PALETTE,):
            # TODO hack, should not even be a control
            # Omitted, use None
            args = [None,]
        else:
            # PF_SPINNER,, PF_OPTION
            if pf_type == PF_COLOUR:
                Deprecation.say("Deprecated PF_COLOUR")
            raise RuntimeError(f"Unhandled PF_ widget type {pf_type}.")

        return args



'''
Map PF_ enum to Widget class

Key is-a PF_ enum.
Value is-a FuWidget class.

Many-to-one.
Many PF_enums map to same FuWidget class.

A FuWidget class is also many-to-one with Gtk widgets.
E.g. a Gtk string entry widget may be used to enter both strings and ints.
The FuWidget class may convert types yielded by Gtk widgets.

A PF_enum specifies both the look and feel of the widget,
and the type yielded by the widget, back to GimpFu.

Currently a PF_enum may describe a more restrictive type (E.G. INT8)
than the FuWidget class yields (E.G. INT)
but in some cases that is not enforced at GUI time.

The formal param spec declares a PF_ enum, as well as an EXTRAS.
EXTRAS further specifies parameters of the FuWidget class,
and the widget enforces that type restriction at GUI time.

Feb. 2020 status:
complete keys, but hacked values (should implement more widgets)
'''
_edit_map = {
        PF_INT         : IntEntry,
        PF_INT8        : IntEntry,
        PF_INT16       : IntEntry,
        PF_INT32       : IntEntry,

        # both return strings, just different widgets?
        PF_STRING      : StringEntry,
        PF_TEXT        : StringEntry,

        # checkbox
        # both return bool,  just different widgets?
        PF_BOOL        : ToggleEntry,
        PF_TOGGLE      : ToggleEntry,

        # TODO slider and spinner floats, or int?
        PF_FLOAT       : FloatEntry,
        PF_SLIDER      : FloatEntry,
        PF_SPINNER     : FloatEntry,
        PF_ADJUSTMENT  : FloatEntry,

        # radio buttons, set of choices
        PF_RADIO       : RadioEntry,


        # For omitted, subsequently GimpFu uses the default value
        # which should be sane
        PF_COLOR       : OmittedEntry,
        PF_COLOUR      : OmittedEntry,

        # Widgets provided by GTK ?
        PF_FILE        : OmittedEntry,
        PF_FILENAME    : OmittedEntry,
        PF_DIRNAME     : OmittedEntry,

        # meaning ?
        PF_OPTION      : OmittedEntry,

        # ??? meaning?
        PF_VALUE       : OmittedEntry,

        # Widgets provided by Gimp for Gimp ephemeral objects
        PF_ITEM        : OmittedEntry,
        PF_DISPLAY     : OmittedEntry,
        PF_IMAGE       : OmittedEntry,
        PF_LAYER       : OmittedEntry,
        PF_CHANNEL     : OmittedEntry,
        PF_DRAWABLE    : OmittedEntry,
        PF_VECTORS     : OmittedEntry,

        # Widgets provided by Gimp for Gimp data objects?
        # "data" objects are loaded at run-time, not as ephemeral
        # i.e. configured, static data of the app
        PF_FONT        : StringEntry,
        PF_BRUSH       : StringEntry,
        PF_PATTERN     : StringEntry,
        PF_GRADIENT    : StringEntry,
        # formerly gimpui.palette_selector
        # Now I think palette is a parameter, but should not have a control?
        # since the currently selected palette in palette dialog is passed?
        PF_PALETTE     : OmittedEntry,
        }
