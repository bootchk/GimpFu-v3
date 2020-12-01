"""
Test calling procedure that returns Array

A GimpFu plugin that calls another plugin.
"""

from gimpfu import *

def plugin_func(image, drawable):

    pdb.gimp_image_thumbnail(image, 2, 2)
    # returns a GimpParamUInt8Array


register(
      "python-fu-test-array-testArrayResult",
      "blurb",
      "help message",
      "author",
      "copyright",
      "year",
      "Plugin that returns array...",
      "*",
      [
          (PF_IMAGE, "image", "Input image", None),
          (PF_DRAWABLE, "drawable", "Input drawable", None),
      ],
      [],
      plugin_func,
      menu="<Image>/Test")
main()
