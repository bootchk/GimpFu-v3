
from gimpfu.procedure.metadata import FuProcedureMetadata
from gimpfu.procedure.type import FuProcedureType

import logging

"""
Understands run mode.

Understands how to determine whether a procedure takes a run mode parameter.

Much of this is non-working cruft,
but it documents v2 implementation, and ways we can't use.
"""


module_logger = logging.getLogger("GimpFu.RunMode")

class RunMode() :

    def _takes_runmode_from_name(self):
        """ Parse name of proc to determine whether it should take a run_mode arg.

        Implementation as in GimpFu v2.
        Implemented using string compares.
        We don't use the field plug-type,
        since it can be:
           "Temporary Procedure" : Gimp.org and Author submitted plugins
           or "GIMP Plug-In"  : Gimp.org and Author submitted plugins
           or "Internal Gimp Procedure" : e.g. gimp-file-load by Gimp.org
        """
        # TODO file load and save
        # TODO gimp-file-load and other anomalously named plug-ins ??

        # TODO move this to procedure/metadata.py
        proc_name = self.name
        result = ( proc_name.startswith('plug-in-')
                or proc_name.startswith('script-fu-')
                or proc_name.startswith('python-fu-')
                )
        return result


    """
    This is NOT reliable to determine whether to insert a run mode arg.
    Some procedures that are type INTERNAL (NOT type PLUGIN)
    take a first arg that is run mode.
    e.g. gimp-file-load-layers.
    """
    @staticmethod
    def _takes_runmode_from_signature(procedure):
        """
        Examine signature of proc to determine whether it takes run_mode arg.

        The most reliable implementation:
        Get GParamSpec, and compare its type.name to 'GimpRunMode'
        """
        # Gimp not defined. assert isinstance(procedure, Gimp.Procedure)

        module_logger.info(f"_takes_runmode_from_signature: {procedure}")

        if procedure.formal_arg_count > 0:
            # If takes run mode, is always the first arg
            type_name = procedure.get_formal_argument_type_name(0)

            module_logger.info(f"_takes_runmode_from_signature, first arg type name {type_name}")

            """
            ??? Maybe
            Fails to work because actual gtype name is GParamEnum
            which is not specific enough for GimpRunMode.
            """
            result = (type_name == 'GimpRunMode')

            """
            We cannot examine the name of the ParamSpec, instead of the type,
            because some are named 'run-mode' and some 'dummy-param'.
            file-gbr-save is aberrant, first arg name is "dummy-param"

            param_name = arg_specs[0].name
            result = ( param_name == 'run-mode')
            """
        else:
            result = False
        module_logger.info(f"_takes_runmode_from_signature: {result}")
        return result

    @staticmethod
    def _takes_runmode_from_menu_path(procedure):
        """
        Uses GimpFu classes to understand which PDB procedures take run mode.

        Not creating an instance of FuProcedureMetadata, just using one of its class methods.

        Only type Other does not take a run mode arg.

        This fails because some "engine" plugins register as type Plugin but without a menu path.
        """
        # !!! procedure is-a Gimp.Procedure, not a FuProcedure
        type = FuProcedureMetadata.type_from_menu_path(procedure.menu_path)
        return type != FuProcedureType.Other


    @staticmethod
    def does_procedure_take_runmode_arg(procedure):

        # Choose an implementation
        # TODO Not all are correct

        # only type Plugin requires insertion of run mode arg
        #result = self.type == Gimp.PDBProcType.PLUGIN

        return RunMode._takes_runmode_from_signature(procedure)
        #result = self._takes_runmode_from_name()
        # Feb. 2021 commented out
        #return RunMode._takes_runmode_from_menu_path(procedure)
