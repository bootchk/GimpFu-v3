
'''
GimpFu plugin
that:
- has one parameter
- maps deprecated names
'''

from gimpfu import *

map = {
    "gimp-image-is-valid": "gimp-image-ID-is-valid",
}

def plugin_func(testedName):
    print(f"Called w: {testedName}")

    try:
        result = map[testedName]
    except KeyError:
        result = testedName
    return result

def plugin_func2(image, drawable, testedName):

    # A name not deprecated
    print ( f"Mapped name: {pdb.python_fu_map_PDB_name('foo')[0]}")
    # Note always returns a list, but why does it have a trailing empty string?
    # Expect print "foo"

    # A deprecated name
    print ( f"Mapped name: {pdb.python_fu_map_PDB_name('gimp-image-is-valid')[0]}")
    # Expect print "barbar"





""" A utility procedure, no menu """
register(
      "python-fu-map-PDB-name",
      "Map a deprecated PDB procedure name to the new name",
      "Used internally by ScriptFu for backward compatibility.",
      "author",
      "copyright",
      "year",
      "",   # No menu item
      "",   # No image types
      [ (PF_STRING, "testedName", "Possibly deprecated name to map", ""), ],
      [ (PF_STRING, "mappedName", "Mapped name (deprecated name or unchanged name", ""), ],
      plugin_func,
      menu="")  # Not appear in menus

""" A procedure to test the utility procedure """
register(
      "python-fu-test-map-PDB-name",
      "Map a deprecated PDB procedure name to the new name",
      "Used internally by ScriptFu for backward compatibility.",
      "author",
      "copyright",
      "year",
      "Test map PDB name",
      "",   # No image types
      # GimpFu will fix up missing image, drawable
      [ (PF_STRING, "testedName", "Possibly deprecated name to map", ""), ],
      [],   # void result
      plugin_func2,
      menu="<Image>/Test")
main()
