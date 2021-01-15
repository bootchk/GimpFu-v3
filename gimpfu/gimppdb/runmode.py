
from procedure.metadata import FuProcedureMetadata
from procedure.type import FuProcedureType


"""
Understands run mode.

Understands how to determine whether a procedure takes a run mode parameter.

Much of this is non-working cruft,
but it documents v2 implementation, and ways we can't use.
"""


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
    def _takes_runmode_from_signature(self):
        """
        Examine signature of proc to determine whether it takes run_mode arg.

        The most reliable implementation:
        Get GParamSpec, and compare its type.name to 'GimpRunMode'
        """

        arg_specs = self.argument_specs
        # assert arg_specs is-a list of GObject.GParamSpec or subclass thereof
        if len(arg_specs) > 0:
            # run-mode is the first arg
            type_name = self.get_formal_argument_type_name(0)

            """
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
        return result

    @staticmethod
    def takes_runmode_from_menu_path(procedure):
        """
        Uses GimpFu classes to understand which PDB procedures take run mode.

        Not creating an instance of FuProcedureMetadata, just using one of its class methods.

        Only type Other does not take a run mode arg
        """
        type = FuProcedureMetadata.type_from_menu_path(procedure.menu_path)
        return type != FuProcedureType.Other
