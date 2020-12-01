#!/usr/bin/env python3

import sys

import gi
gi.require_version('Gimp', '3.0')
from gi.repository import Gimp
from gi.repository import GObject
from gi.repository import GLib
from gi.repository import Gio


import gettext
_ = gettext.gettext
def N_(message): return message


"""
This tests receiving an array from a libgimp routine.
"""





def foo(procedure, run_mode, image, drawable, args, data):

    # Note this is not a call to the PDB, but to a GI'd libgimp routine.

    result = Gimp.context_list_paint_methods()

    print(result)
    print("test array in call to Gimp.context_list_paint_methods succeeded.\n")

    return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())



class Foo (Gimp.PlugIn):
    ## Parameters ##

    ## GimpPlugIn virtual methods ##
    def do_query_procedures(self):
        self.set_translation_domain("gimp30-python",
                                    Gio.file_new_for_path(Gimp.locale_directory()))

        return [ 'python-fu-test-array-from-libgimp' ]  # Return procedure name, elsewhere this is "name"

    def do_create_procedure(self, name):
        procedure = Gimp.ImageProcedure.new(self, name,
                                            Gimp.PDBProcType.PLUGIN,
                                            foo, None)
        procedure.set_image_types("*");
        procedure.set_documentation (N_("Test array from libgimp"),
                                     "Tests PyGObject marshalling.",
                                     name)
        procedure.set_menu_label(N_("_Test array from libgimp"))
        procedure.set_attribution("Konneker",
                                  "Konneker",
                                  "2020")
        procedure.add_menu_path ("<Image>/Test")
        return procedure

Gimp.main(Foo.__gtype__, sys.argv)
