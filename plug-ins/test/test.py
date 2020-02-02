'''
A test Gimp plugin
that:
- has two parameters

Exercises properties of image
'''

from gimpfu import *

def plugin_func(image, drawable, arg, arg2):
      print("plugin_func called args: ", arg, ",", arg2)
      print("Plugin called, type(image):", type(image))
      print("Plugin called, dir(image) is:", dir(image))

      # Image.width
      # Not implemented yet, but should be
      # print("width:", image.width)
      # Image.base_type
      print("base_type:", image.base_type)
      # Image.filename
      print("Getting filename...")
      print("filename:", image.filename)
      #etc

register(
      "testProperties",
      "blurb",
      "help message",
      "author",
      "copyright",
      "year",
      "Exercise image.prop...",
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
