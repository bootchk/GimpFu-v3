#!/usr/bin/env python3

import sys

import gi
gi.require_version('Gimp', '3.0')
from gi.repository import Gimp
from gi.repository import Gio
from gi.repository import GLib


import gettext
_ = gettext.gettext
def N_(message): return message



def foo(procedure, run_mode, image, drawable, args, data):

    result = Gimp.pencil(drawable, [100.0, 100.0, 400.0, 400.0])
    #fails: TypeError: Gimp.pencil() takes exactly 2 arguments (3 given)
    # but /usr/local/share/gir-1.0/Gimp-3.0.gir
    # and the code in libgimpbase/gimppainttools_pdb.c says 3 args

    Gimp.displays_flush()

    return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())



class Foo (Gimp.PlugIn):
    ## Parameters ##

    ## GimpPlugIn virtual methods ##
    def do_query_procedures(self):
        self.set_translation_domain("gimp30-python",
                                    Gio.file_new_for_path(Gimp.locale_directory()))

        return [ 'python-fu-foo' ]  # Return procedure name, elsewhere this is "name"

    def do_create_procedure(self, name):
        procedure = Gimp.ImageProcedure.new(self, name,
                                            Gimp.PDBProcType.PLUGIN,
                                            foo, None)
        procedure.set_image_types("*");
        procedure.set_documentation (N_("Test foo"),
                                     "Tests Gimp/PyGObject implementation of conversions.",
                                     name)
        procedure.set_menu_label(N_("_Test gimp_pencil"))
        procedure.set_attribution("Konneker",
                                  "Konneker",
                                  "2020")
        procedure.add_menu_path ("<Image>/Test")
        return procedure

Gimp.main(Foo.__gtype__, sys.argv)
