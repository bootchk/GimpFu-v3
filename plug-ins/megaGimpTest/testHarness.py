
from gimpfu import *

def generateNamedItems():
    """ Generate into Gimp, instances of various kinds, each instance named "foo"

    To be used as data for testing.

    The object model, from GIMP App Ref Manual:
    GimpData
        GimpBrush
            GimpBrushClipboard
            GimpBrushGenerated
            GimpBrushPipe
        GimpCurve
        GimpDynamics
        GimpGradient
        GimpPalette
        GimpPattern
            GimpPatternClipboard
        GimpToolPreset
    GimpBuffer
    GimpItem

    Most of these kinds are GimpData

    Kinds:
    palette
    gradient
    pattern ? API is different
    named buffer
    font ?

    We use 'foo' as a string type parameter whenever one is needed,
    and the use is often as the name of a kind of Gimp object.

    Not all these Gimp objects have Gimp classes.
    """

    """
    The pattern is:
    context_get
    duplicate
    rename
    """
    current_palette_name = gimp.context_get_palette()
    print(current_palette_name)
    duplicate_palette_name = gimp.palette_duplicate(current_palette_name)
    print(duplicate_palette_name)
    gimp.palette_rename(duplicate_palette_name, "foo")

    # TODO brush has same API
    # TODO gradient has same API
    # TODO curve, dynamics, pattern NOT

    # for pattern, GUI allows duplicate and delete, but not rename, name is e.g. "Amethyst copy"
    # no API for duplicate, rename, or delete
    # script-fu-paste-as-pattern will allow create a named pattern
