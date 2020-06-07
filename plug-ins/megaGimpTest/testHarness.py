
from gimpfu import *

def generateFooGimpData(drawable):
    """ Generate into Gimp, instances of various kinds, each instance named "foo"

    To be used as data for testing.
    Data chosen is arbitrary, we only care that it exists with name 'foo'.
    Arbitrary: get from the current Gimp context.

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
    The code pattern is:
    context_get
    duplicate
    rename
    """

    # palette
    current_name = gimp.context_get_palette()
    duplicate_name = gimp.palette_duplicate(current_name)
    gimp.palette_rename(duplicate_name, "foo")
    print(f"Created 'foo' palette instance from {duplicate_name}")

    #brush
    current_name = gimp.context_get_brush()
    duplicate_name = gimp.brush_duplicate(current_name)
    gimp.brush_rename(duplicate_name, "foo")
    print(f"Created 'foo' brush instance from {duplicate_name}")

    # gradient
    current_name = gimp.context_get_gradient()
    duplicate_name = gimp.gradient_duplicate(current_name)
    gimp.gradient_rename(duplicate_name, "foo")
    print(f"Created 'foo' gradient instance from {duplicate_name}")

    # channel
    # layer mask
    # selection
    # text layer
    # vectors
    # tattoo

    # buffer: this is a edit buffer from a cut/copy
    # FAIL: gone in v3?  buffer = pdb.gimp_drawable_get_buffer(drawable)
    result = pdb.gimp_edit_copy(drawable)   # buffer from selection
    buffers = pdb.gimp_buffers_get_list("")
    print(f"Buffers: {buffers}")
    # TODO is returning a list of length 0 of type GimpStringArray which GimpFu doesn't handle
    #pdb.gimp_buffer_rename(old, "foo")

    # TODO curve, dynamics, pattern NOT have same approximation

    # for pattern, GUI allows duplicate and delete, but not rename, name is e.g. "Amethyst copy"
    # no API for duplicate, rename, or delete
    # script-fu-paste-as-pattern will allow create a named pattern
