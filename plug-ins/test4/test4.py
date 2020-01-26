'''
A test Gimp plugin
that:
- accesses a missing attribute of Drawable, as a property
'''

from gimpfu import *

def plugin_func(image, drawable, arg, arg2):
      print("plugin_func called")

      foo = drawable.bar

register(
      "test-missing-drawable-attribute",
      "blurb",
      "help message",
      "author",
      "copyright",
      "year",
      "Test missing drawable attribute...",
      "*",
      [
          (PF_IMAGE, "image", "Input image", None),
          (PF_DRAWABLE, "drawable", "Input drawable", None),
      ],
      [],
      plugin_func,
      menu="<Image>/Test")
main()
