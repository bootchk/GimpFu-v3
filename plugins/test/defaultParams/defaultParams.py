"""
Test calling procedure with too few args.

A GimpFu plugin that calls another plugin with too few args.
"""

from gimpfu import *

def plugin_func(image, drawable):

    pdb.script_fu_grid_system(1, image, drawable)
    # signature requires two more args, strings like '(1 g 1)'

register(
      "python-fu-test-default-params",
      "blurb",
      "help message",
      "author",
      "copyright",
      "year",
      "Default params to PDB...",
      "*",
      [
          (PF_IMAGE, "image", "Input image", None),
          (PF_DRAWABLE, "drawable", "Input drawable", None),
      ],
      [],
      plugin_func,
      menu="<Image>/Test")
main()
