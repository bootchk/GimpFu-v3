
'''
GimpFu plugin
that:
- has one parameter
- maps deprecated names
'''

from gimpfu import *


def plugin_func(name):
    print("Called")






register(
      "python-fu-map-PDB-name",
      "blurb",
      "help message",
      "author",
      "copyright",
      "year",
      "Map PDB name",
      "*",
      [],
      [],
      plugin_func,
      menu="")
main()
