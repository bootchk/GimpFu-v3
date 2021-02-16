

import gi
from gi.repository import Gio
gi.require_version("Gimp", "3.0")
from gi.repository import Gimp

# imports  for implementation.  Private from Authors
from gimpfu.runner.runner import FuRunner
from gimpfu.procedure.procedure_creator import FuProcedureCreator
from gimpfu.procedures.procedures import FuProcedures


import logging
logger = logging.getLogger("GimpFu.FuPlugin")

'''
See header comments for type Gimp.Plugin in Gimp docs or Gimp C code.

A plugin must define (but not instantiate) a subclass of Gimp.Plugin.
FuPlugin is a subclass of Gimp.Plugin.
At runtime, only methods of such a subclass have access to Gimp and its PDB.

FuPlug is wrapper.
Has no properties itself.
More generally (unwrapped) properties  represent params (sic arguments) to ultimate plugin.

_run() above wraps Authors "function" i.e. ultimate plugin method,
which is referred to as "run_func" here and in Gimp documents.

All methods are invoked (callbacks) from Gimp.
Callbacks occur:
- at Gimp startup: do_query_procedures() and do_create_procedure()
- at Gimp execution time:  the <run method chain>
   - when user interacts with Gimp GUI (INTERACTIVE)
   - when another plugin calls a plugin (NONINTERACTIVE)

 The <run method chain>:
    Gimp invokes the run_func registered for the procedure.
    That is some method that Gimpfu has registered such as _run_imageprocedure.
    Thus the call chain is:  Gimp => _run_imageprocedure() or similar => _run()  => <the Authors function>()
    The middle two are wrappers of the Authors function, and manipulate the args for GimpFu purposes.

TODO: Gimp calls all methods from C code using GI after starting the Gimp interpreter?

TODO: why do we not provide concrete implementation of virtual methods: init_procedures() and quit() ?

GimpFu does not instantiate this.
It is not clear that Gimp does.
Possibly Gimp calls these methods as class methods.
'''

class FuPlugin (Gimp.PlugIn):

    # See prop_holder.py for GProperty stuff

    ## GimpPlugIn virtual methods ##
    '''
    Called at install time,
    OR when ~/.config/GIMP/2.99/pluginrc (a cache of installed plugins) is being recreated.
    '''
    def do_query_procedures(self):
        logger.info("do_query_procedures")

        # TODO Why set the locale again?
        # Maybe this is a requirement documented for class Gimp.Plugin????
        self.set_translation_domain("Gimp30-python",
                                    Gio.file_new_for_path(Gimp.locale_directory()))

        # return list of all procedures implemented in the Authors source code
        # For testing: result =[ gf_procedure.name, ]
        keys = FuProcedures.names()
        # keys is not a list in Python 3

        # Ensure result is GLib.List () (a Python list suffices)
        result = list(keys)

        return result


    '''
    "run-mode"

    Gimp docs says that Gimp calls this back when plugin is executed.
    ??? But it seems to be called back at installation time also,
    once per call of do_query_procedures.

    In the GimpFu source code: at a call to main(), which calls Gimp.main(), which calls back.
    Thus in the source code AFTER the calls to GimpFu register().
    Thus the GimpFu plugin is GimpFu registered in the local cache.
    It also was registered with Gimp (at installation time.)
    '''


    def do_create_procedure(self, name):

        logger.info (f"do_create_procedure: {name}")

        # We need the kind of plugin, and to ensure the passed name is know to us
        gf_procedure = FuProcedures.get_by_name(name)

        # pass all the flavors of wrapped_run_funcs
        procedure = FuProcedureCreator.create(self, name, gf_procedure,
            FuRunner.run_imageprocedure,
            FuRunner.run_context_procedure,
            FuRunner.run_other_procedure)

        # ensure result is-a Gimp.Procedure
        return procedure
