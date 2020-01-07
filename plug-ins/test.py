'''
A test Gimp plugin
that:
- has two parameters
- prints the parameters to console
'''

from gimpfu import *

def plugin_func(image, drawable, arg, arg2):
      print("plugin_func called args: ", arg, ",", arg2)

register(
      "argsTwo",
      "blurb",
      "help message",
      "author",
      "copyright",
      "year",
      "ArgsTwo",
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
