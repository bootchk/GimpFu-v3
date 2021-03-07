
from gimpfu.enums.gimpfu_enums import *
from gimpfu.message.deprecation import Deprecation

from enum import Enum, auto

"""
EXTRAS is a mini language or format of gimpfu
The tuples describe the valid ranges for formal parameter.
Closely related to the widget associated with the PF_ formal parameter

StringsTuple: each string is name of an int-valued choice.
Values are assigned sequentially starting at 0.

KeyValueTuples: each value can be int or string.
TODO or float?
TODO how do we order strings for min, max?
"""

class ExtrasType(Enum):
    NotAny = auto()             # no extras (typically string or other non-ordered types)
    MinMaxStepTuple = auto()    # a three-tuple             (min, max, step)
    KeyValueTuples = auto()     # tuple of two-tuple dict       (("label", min), ("label", max))
    StringsTuple = auto()       # tuple of strings ("label", ...)




class Extras():
    """
    The extra declarations in a GimpFu formal parameter declaration.

    Extras is an optional tuple describing a range of valid values.
    """

    def _on_extras_error(message):
        """ Log an Author's error in source, in the Params

        Don't use proceed(), don't need its stack trace.
        But GimpFu did not fixup user's code so this should be more severe than a warning?
        """
        Deprecation.say("Error in plugin author's source: " + message)


    def derive_min_max_from_extras(pf_type, extras):
        """ Parse extras tuple, yield min and max. """
        extras_type = map_PF_TYPE_to_extras_type[pf_type]

        min = None
        max = None
        if extras_type == ExtrasType.NotAny:
            if extras:
                proceed("Unexpected extras on parameter spec.")
            pass
        elif extras_type == ExtrasType.MinMaxStepTuple:
            if extras:
                min = extras[0]
                max = extras[1]
            else:
                # !!! -1
                min = -1000000 # Fail: - (sys.maxsize - 1) # Fail: float("-inf")
                max = 1000000 # Fail: sys.maxsize # float("inf")
        elif extras_type == ExtrasType.KeyValueTuples:
            # PF_RADIO and PF_OPTION
            if extras:
                # TODO extract the min and max of the given list of option ordinals
                # For most cases, this will suffice but max should be len()-1 ??
                if len(extras) < 2:
                    # Nonsensical author specification
                    Extras._on_extras_error(f"Too few extras for PF_OPTION or PF_RADIO.")
                else:
                    # Author must understand that values start at 0
                    # TODO this is wrong for string values.
                    min = 0
                    max = len(extras) - 1
                    # TODO if values not sequential ints
                """
                See elsewhere.  GimpFu allows string values.
                #if not isinstance (extras[0][1], int):
                #    Extras._on_extras_error(f"String literals for extras are obsolete.")
                """
            else:
                Extras._on_extras_error("Missing extras")

        elif extras_type == ExtrasType.StringsTuple:
            if pf_type == PF_BOOL:
                if extras:
                    if  len(extras) != 2:
                        Extras._on_extras_error(f"Require none or two values for extras for PF_BOOL.")
                else:
                    # user provided no labels, use default labels.
                    min = 0
                    max = 1
            else:
                # Mistake in the map or in this code
                Extras._on_extras_error("Error in GimpFu extras map")
        else:
            # Incorrect implementation in GimpFu
            Extras._on_extras_error(f"Unhandled extras type: {extras_type} on PF_TYPE: {self.PF_TYPE}")

        return (min, max)


    def derive_min_max_step_from_extras(pf_type, extras):
        """ Return a (min, max, step) tuple """
        assert len(extras) == 3
        return extras




map_PF_TYPE_to_extras_type = {
    # TODO does an Entry widget enforce this?
    PF_INT8:      ExtrasType.MinMaxStepTuple,
    PF_INT16:     ExtrasType.MinMaxStepTuple,
    PF_INT32:     ExtrasType.MinMaxStepTuple,
    PF_INT:       ExtrasType.MinMaxStepTuple,
    PF_FLOAT:     ExtrasType.MinMaxStepTuple,
    PF_STRING:    ExtrasType.NotAny,
    PF_TEXT:      ExtrasType.NotAny,    # an alternate string valued chooser

    # PF_VALUE:    # TODO what is this??

    # Gimp chooser widget, no extras
    PF_COLOR:     ExtrasType.NotAny,    # PF_COLOUR is alias
    PF_ITEM:      ExtrasType.NotAny,
    PF_DISPLAY:   ExtrasType.NotAny,
    PF_IMAGE:     ExtrasType.NotAny,
    PF_LAYER:     ExtrasType.NotAny,
    PF_CHANNEL:   ExtrasType.NotAny,
    PF_DRAWABLE:  ExtrasType.NotAny,
    PF_VECTORS:   ExtrasType.NotAny,

    # int/bool valued checkbox or toggle widget
    PF_BOOL:      ExtrasType.StringsTuple,  # PF_TOGGLE is alias, same widget

    # float valued
    PF_SLIDER:    ExtrasType.MinMaxStepTuple,
    PF_SPINNER:   ExtrasType.MinMaxStepTuple,  # PF_ADJUSTMENT is alias, same widget

    PF_RADIO:     ExtrasType.KeyValueTuples,  # radio buttons for a int or string valued enum
    PF_OPTION:    ExtrasType.KeyValueTuples,  # pulldown combobox

    PF_FONT:      ExtrasType.NotAny,

    PF_BRUSH:     ExtrasType.NotAny,
    PF_PATTERN:   ExtrasType.NotAny,
    PF_GRADIENT:  ExtrasType.NotAny,
    PF_PALETTE:   ExtrasType.NotAny,

    # Gtk widgets, no extras
    PF_FILE:      ExtrasType.NotAny,
    PF_FILENAME:  ExtrasType.NotAny,    # GFile valued file chooser widget
    PF_DIRNAME:   ExtrasType.NotAny,

    # Arrays have no extras
    # Arrays have no widgets
    PF_INT8ARRAY:   ExtrasType.NotAny,
    PF_INT32ARRAY:  ExtrasType.NotAny,
    PF_FLOATARRAY:  ExtrasType.NotAny,
    PF_STRINGARRAY: ExtrasType.NotAny,
    PF_GIMP_OBJECT_ARRAY: ExtrasType.NotAny,
    PF_GIMP_RGB_ARRAY:    ExtrasType.NotAny,
}
