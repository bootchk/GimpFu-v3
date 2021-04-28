'''
A GimpFu plugin
that:
calls a PDB procedure with a numeric names
'''

from gimpfu import *

import gi
from gi.repository import GObject


def plugin_func(image, drawable):
      print("plugin_func called")
      pdb.210_script_fu_testGegl(image, drawable)




register(
      "python-fu-numericPDBName",
      "blurb",
      "help message",
      "author",
      "copyright",
      "year",
      "Numeric PDB name...",
      "*",
      [
          (PF_IMAGE, "image", "Input image", None),
          (PF_DRAWABLE, "drawable", "Input drawable", None),
      ],
      [],
      plugin_func,
      menu="<Image>/Test")
main()
