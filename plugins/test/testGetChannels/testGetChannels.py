"""
Test calling procedure that returns ObjectArray

A GimpFu plugin that calls another plugin.
"""

from gimpfu import *

def plugin_func(image, drawable):

    count, channels = pdb.gimp_image_get_channels(image)
    # returns a Gimp.ObjectArray
    print(f"Count {count} channels {channels}")

    count, strings = pdb.gimp_context_list_paint_methods()
    # returns a Gimp.StringArray
    print(f"Count: {count} paint method names: {strings}")

    color = channels[0].get_color()
    print(color)


register(
      "python-fu-test-array-results",
      "blurb",
      "help message",
      "author",
      "copyright",
      "year",
      "Test procedures that return Array...",
      "*",
      [
          (PF_IMAGE, "image", "Input image", None),
          (PF_DRAWABLE, "drawable", "Input drawable", None),
      ],
      [],
      plugin_func,
      menu="<Image>/Test")
main()
