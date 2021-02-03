'''
A test Gimp plugin
that:
- returns all types, to test marshalling return types, to a caller
'''

from gimpfu import *

def plugin_func(image, drawable):
    """ Return a value for each know type. """
    return (
        image,
        drawable,
        [1, 2],         # 8
        #[1, 2],         #32
        [1.01, 2.01],   # float
        ["foo", "bar"], # str
        ["black", "white"], # rgb
        [drawable, drawable] # object
        )


register(
      "python-fu-test-gimp-marshal-return-vals",
      "blurb",
      "help message",
      "author",
      "copyright",
      "year",
      "Marshal return vals",
      "*",
      [
          (PF_IMAGE, "image", "Input image", None),
          (PF_DRAWABLE, "drawable", "Input drawable", None),
      ],
      [
          (PF_IMAGE,             "image",      "foo", None),
          (PF_DRAWABLE,          "drawable",   "foo", None),
          (PF_INT8ARRAY,         "int8array",  "foo", None),
          #(PF_INT32ARRAY,        "int32array", "foo", None),
          # (PF_INTARRAY,          "intarray",   "foo", None),    # Why?
          (PF_FLOATARRAY,        "floatarray", "foo", None),
          (PF_STRINGARRAY,       "strings",    "foo", None),
          (PF_GIMP_RGB_ARRAY,    "colors",     "foo", None),
          (PF_GIMP_OBJECT_ARRAY, "objects",    "foo", None),
      ],
      plugin_func,
      menu="<Image>/Test")
main()
