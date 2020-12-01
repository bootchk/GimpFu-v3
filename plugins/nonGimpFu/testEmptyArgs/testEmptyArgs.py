#!/usr/bin/env python3

import sys

import gi
gi.require_version('Gimp', '3.0')
from gi.repository import Gimp
from gi.repository import Gio
from gi.repository import GLib



'''
A GI plugin
Test a call to PDB with empty args.
'''

def foo(procedure, run_mode, image, drawable, args, data):

    # gimp-context-list-paint-methods(void) is an INTERNAL procedure taking no arguments



    result = Gimp.get_pdb().run_procedure('gimp-context-list-paint-methods', [] )
    # Throws (testEmptyArgs.py:192): LibGimp-CRITICAL **: 16:44:10.397: gimp_pdb_run_procedure_argv: assertion 'arguments != NULL' failed

    print(f"Return value: {result}")
    # prints "None" but expect a tuple (True, ['gimp-pencil', ...])

    """
    Another similar thing that works, a call to libgimp:

    result = Gimp.gimp-context-list-paint-methods()
    print(f"Return value: {result}")
    # Prints a tuple: (True, ['gimp-pencil', ...])
    """

    """
    Another thing I tried that fails:

    args = Gimp.ValueArray.new(0)
    result = Gimp.get_pdb().run_procedure('gimp-context-list-paint-methods', args )
    # Throws Python exception: TypeError: Must be sequence, not ValueArray
    """

    """
    Also fails.

    result = Gimp.get_pdb().run_procedure('gimp-context-list-paint-methods' )
    """

    return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())




class Foo (Gimp.PlugIn):
    ## Parameters ##

    ## GimpPlugIn virtual methods ##
    def do_query_procedures(self):
        self.set_translation_domain("gimp30-python",
                                    Gio.file_new_for_path(Gimp.locale_directory()))

        return [ 'python-fu-test-empty-args' ]  # Return procedure name, elsewhere this is "name"

    def do_create_procedure(self, name):
        procedure = Gimp.ImageProcedure.new(self, name,
                                            Gimp.PDBProcType.PLUGIN,
                                            foo, None)
        procedure.set_image_types("*");
        procedure.set_documentation ("Test empty args to PDB call",
                                     "",
                                     name)
        procedure.set_menu_label("Empty args")
        procedure.set_attribution("Konneker",
                                  "Konneker",
                                  "2020")
        procedure.add_menu_path ("<Image>/Test")
        return procedure

Gimp.main(Foo.__gtype__, sys.argv)
