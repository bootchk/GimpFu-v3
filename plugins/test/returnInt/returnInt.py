"""
Test return Int.

Register a single return value of type int.
"""

from gimpfu import *

def plugin_func(image, drawable):
    return 1

def plugin_func2(image, drawable):
    return 1, 2


register(
      "python-fu-test-return-int",
      "blurb",
      "help message",
      "author",
      "copyright",
      "year",
      "Test return Int...",
      "*",
      [
          (PF_IMAGE, "image", "Input image", None),
          (PF_DRAWABLE, "drawable", "Input drawable", None),
      ],
      [   (PF_INT, "name", "desc"),
      ],
      plugin_func,
      menu="<Image>/Test")

register(
      "python-fu-test-return-ints",
      "blurb",
      "help message",
      "author",
      "copyright",
      "year",
      "Test return two Ints...",
      "*",
      [
          (PF_IMAGE, "image", "Input image", None),
          (PF_DRAWABLE, "drawable", "Input drawable", None),
      ],
      [
          (PF_INT, "name", "desc"),
          (PF_INT, "name2", "desc"),
      ],
      plugin_func2,
      menu="<Image>/Test")




main()
