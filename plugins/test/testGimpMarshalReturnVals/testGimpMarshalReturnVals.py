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
        ["foo", "bar"]
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
          (PF_IMAGE, "image", "Input image", None),
          (PF_DRAWABLE, "drawable", "Input drawable", None),
          (PF_STRINGARRAY, "returned_strings", "returned strings", None),
      ],
      plugin_func,
      menu="<Image>/Test")
main()
