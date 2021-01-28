"""
A GimpFu plugin

tests plugin mapPDBName
"""
from gimpfu import *

def plugin_func(image, drawable, testedName):

    # A name not deprecated
    print ( f"Mapped name: {pdb.python_fu_map_pdb_name('foo')[0]}")
    # Note always returns a list, but why does it have a trailing empty string?
    # Expect print "foo"

    # A deprecated name
    print ( f"Mapped name: {pdb.python_fu_map_pdb_name('gimp-image-is-valid')[0]}")
    # Expect print "barbar"

""" A procedure to test the utility procedure """
register(
      "python-fu-test-map-pdb-name",
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
      plugin_func,
      menu="<Image>/Test")

main()
