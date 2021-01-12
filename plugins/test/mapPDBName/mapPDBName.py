
'''
GimpFu plugin
that:
- has one parameter
- maps deprecated names
'''

from gimpfu import *


def plugin_func(testedName):
    print(f"Called w: {deprecatedName}")






register(
      "python-fu-map-PDB-name",
      "Map a deprecated PDB procedure name to the new name",
      "help message",
      "author",
      "copyright",
      "year",
      "",   # No menu item
      "",   # No image types
      [ (PF_STRING, "testedName", "Possibly deprecated name to map", ""), ],
      [ (PF_STRING, "mappedName", "Mapped name (deprecated name or unchanged name", ""), ],
      plugin_func,
      menu="")  # Not appear in menus
main()
