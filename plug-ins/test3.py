'''
A test Gimp plugin
that:
- alias gimp exists and delegates to Gimp gobject
'''

from gimpfu import *

def plugin_func(image, drawable, arg, arg2):
      print("plugin_func called")

      # test that gimp alias is defined
      print("gimp inside plugin_func", gimp)
      img = gimp.Image(10, 20, RGB)

register(
      "accessGimp",
      "blurb",
      "help message",
      "author",
      "copyright",
      "year",
      "Access gimp...",
      "*",
      [
          (PF_IMAGE, "image", "Input image", None),
          (PF_DRAWABLE, "drawable", "Input drawable", None),
          (PF_STRING, "arg", "The string argument", "default-value"),
          (PF_INT, "arg2", "The int argument", 1)
      ],
      [],
      plugin_func,
      menu="<Image>/Test")
main()
