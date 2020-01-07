'''
A test Gimp plugin
that:
- accesses pdb
'''

from gimpfu import *

def plugin_func(image, drawable, arg, arg2):
      print("plugin_func called")
      drawable = pdb.gimp_image_active_drawable(image)

register(
      "accessPDB",
      "blurb",
      "help message",
      "author",
      "copyright",
      "year",
      "Access PDB...",
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
