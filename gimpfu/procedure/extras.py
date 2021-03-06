
from gimpfu.enums.gimpfu_enums import *
from gimpfu.message.deprecation import Deprecation


class Extras():
    """
    The extra declarations in a GimpFu formal parameter declaration.

    Extras is an optional tuple describing a range of valid values.
    """

    def _on_extras_error(message):
        """ Log an Author's error in source, in the Params

        Don't use proceed(), don't need its stack trace.
        But the user's code was not fixed so this should be more severe than a warning?
        """
        Deprecation.say("Error in plugin author's source: " + message)


    def derive_min_max_from_extras(pf_type, extras):
        """ Parse extras tuple, yield min and max. """
        extras_type = map_PF_TYPE_to_extras_type[pf_type]

        min = None
        max = None
        if extras_type == 0:
            if extras:
                proceed("Unexpected extras on parameter spec.")
            pass
        elif extras_type == 1:
            if extras:
                min = extras[0]
                max = extras[1]
            else:
                # !!! -1
                min = -1000000 # Fail: - (sys.maxsize - 1) # Fail: float("-inf")
                max = 1000000 # Fail: sys.maxsize # float("inf")
        elif extras_type == 2:
            # Bool represented as int
            # TODO extras[0][1]
            min = 0
            max = 1
        elif extras_type == 3:
            # PF_RADIO and PF_OPTION
            if extras:
                # TODO should extract the min and max of the given list of option ordinals
                # For most cases, this will suffice but max should be len()-1 ??

                """
                Not currently using the given extras values,
                but warn if they are not of valid type.
                """
                if not isinstance (extras[0][1], int):
                    Extras._on_extras_error(f"String literals for extras are obsolete.")

                min = 0
                max = len(extras)
            else:
                Extras._on_extras_error("Missing extras")
        else:
            # Could be missing code in GimpFu ?
            Extras._on_extras_error(f"Unhandled extras type: {extras_type} on PF_TYPE: {self.PF_TYPE}")

        return (min, max)


    def derive_min_max_step_from_extras(pf_type, extras):
        """ Return a (min, max, step) tuple """
        assert len(extras) == 3
        return extras


"""
EXTRAS is a mini language or format of gimpfu
The tuples describe both the GUI widget and the valid ranges for parameter.

extras type  Python type of extras                     example
0            no extras (typically string or other non-ordered types)
1            a three-tuple                             (min, max, step)
2            extras is a tuple of two-tuple dict       (("label", min), ("label", max))
3            tuple of strings                          ("label", ...)
                       each label is name of an int-valued choice
"""

map_PF_TYPE_to_extras_type = {
    PF_INT8:      1,
    PF_INT16:     1,
    PF_INT32:     1,
    PF_INT:       1,
    PF_FLOAT:     1,
    PF_STRING:    0,
    PF_TEXT:      0,    # an alternate string valued chooser

    # PF_VALUE:    # TODO what is this??

    # Gimp chooser widget, no extras
    PF_COLOR:     0,    # PF_COLOUR is alias
    PF_ITEM:      0,
    PF_DISPLAY:   0,
    PF_IMAGE:     0,
    PF_LAYER:     0,
    PF_CHANNEL:   0,
    PF_DRAWABLE:  0,
    PF_VECTORS:   0,

    # int/bool valued checkbox or toggle widget
    PF_BOOL:      2,  # PF_TOGGLE is alias, same widget
    PF_SLIDER:    1,
    PF_SPINNER:   1,  # PF_ADJUSTMENT is alias, same widget

    # float valued
    PF_RADIO:     3,  # radio buttons for a int or string valued enum
    PF_OPTION:    3,  # pulldown combobox

    PF_FONT:      0,

    PF_BRUSH:     0,
    PF_PATTERN:   0,
    PF_GRADIENT:  0,
    PF_PALETTE:   0,

    # Gtk widgets, no extras
    PF_FILE:      0,
    PF_FILENAME:  0,    # GFile valued file chooser widget
    PF_DIRNAME:   0,

    # Arrays have no extras
    # Arrays have no widgets
    PF_INT8ARRAY:   0,
    PF_INT32ARRAY:  0,
    PF_FLOATARRAY:  0,
    PF_STRINGARRAY: 0,
    PF_GIMP_OBJECT_ARRAY: 0,
    PF_GIMP_RGB_ARRAY:    0,
}
