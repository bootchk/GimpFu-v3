'''
A test Gimp plugin
that:
- returns all types, to test marshalling return types, to a caller

!!! Only things that can cross the wire i.e. Gimp Protocol aka GP
See libgimp/gimpgpparams-body.c

GIMP has other classes that don't cross the wire.
And are exposed to GI ??
Font, Brush, Pallette, Gradient, Pattern

Note LayerMask and Selection are subclasses of Channel.
Drawable, Layer, Channel are subclasses of Item.
'''

from gimpfu import *

def plugin_func(image, drawable):
    """ Return a value for each type. """
    return (
        image,
        drawable,

        # arrays
        [1, 2],         # 8
        [1, 2],         #32
        [1.01, 2.01],   # float
        ["foo", "bar"], # str
        ["black", "white"], # rgb
        [drawable, drawable], # object

        # bool, downcast?
        255,   # uchar
        64000, # int
        99.99, # float
        "foo", # str

        # color
        drawable, # item
        # display
        drawable, # layer
        # channel
        # vectors
        )


register(
      "python-fu-test-gimp-marshal-return-vals",
      "blurb",
      "help message",
      "author",
      "copyright",
      "year",
      "Marshal return vals",
      "",
      [
          (PF_IMAGE, "image", "Input image", None),
          (PF_DRAWABLE, "drawable", "Input drawable", None),
      ],
      [
          (PF_IMAGE,             "image",      "foo", None),
          (PF_DRAWABLE,          "drawable",   "foo", None),
          # arrays
          (PF_INT8ARRAY,         "int8array",  "foo", None),
          (PF_INT32ARRAY,        "int32array", "foo", None),
          (PF_FLOATARRAY,        "floatarray", "foo", None),
          (PF_STRINGARRAY,       "strings",    "foo", None),
          (PF_GIMP_RGB_ARRAY,    "colors",     "foo", None),
          (PF_GIMP_OBJECT_ARRAY, "objects",    "foo", None),
          # atoms that are primitives
          (PF_INT8,         "uchar",    "foo", None),   # TODO Downcast needed?
          (PF_INT32,        "int",      "foo", None),
          (PF_FLOAT,        "float",    "foo", None),
          (PF_STRING,       "string",   "foo", None),
          # atoms that are GIMP objects
          #(PF_COLOR,        "color",    "foo", None),
          (PF_ITEM,         "item",      "foo", None),
          #(PF_DISPLAY,      "display",   "foo", None),
          (PF_LAYER,        "layer",     "foo", None),
          #(PF_CHANNEL,      "channel",   "foo", None),
          #(PF_VECTORS,      "vectors",   "foo", None),

          # FILE, filename, dir

          # Parasite, bool, enum

          #
      ],
      plugin_func,
      menu="<Image>/Test")
main()
