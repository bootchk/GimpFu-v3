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

'''
A GI plugin
Test that g_error() terminates plugin
(and invokes GIMP debug machinery.)
'''

def foo(procedure, run_mode, image, drawable, args, data):

    # Not exist?
    # GLib.error("here")

    # This causes seg fault, which is caught by GIMP sig handler
    # Not the same thing as the GIMP fatal handler
    # GLib.free(1)

    # apparently there is no way to do the same thing as g_error() using GI
    print("Doing nothing")

    return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())



class Foo (Gimp.PlugIn):
    ## Parameters ##

    ## GimpPlugIn virtual methods ##
    def do_query_procedures(self):
        self.set_translation_domain("gimp30-python",
                                    Gio.file_new_for_path(Gimp.locale_directory()))

        return [ 'python-fu-test-glib-error' ]  # Return procedure name, elsewhere this is "name"

    def do_create_procedure(self, name):
        procedure = Gimp.ImageProcedure.new(self, name,
                                            Gimp.PDBProcType.PLUGIN,
                                            foo, None)
        procedure.set_image_types("*");
        procedure.set_documentation (N_("Test GLib error"),
                                     "Tests GLib error.",
                                     name)
        procedure.set_menu_label(N_("_Test GLib Error"))
        procedure.set_attribution("Konneker",
                                  "Konneker",
                                  "2020")
        procedure.add_menu_path ("<Image>/Test")
        return procedure

Gimp.main(Foo.__gtype__, sys.argv)
