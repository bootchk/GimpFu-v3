import gi
gi.require_version("Gimp", "3.0")
from gi.repository import Gimp
from gi.repository import GObject   # types

from message.proceed_error import proceed
import logging




class GimpProcedure:
    """ Thin wrapper around Gimp.Procedure

    For introspection of the PDB.

    !!! Distinct from FuProcedure.
    This is not an adapter, an Author does not use this,
    only the GimpFu implementation uses it.
    """

    def __init__(self, gimp_procedure):
        self._procedure = gimp_procedure
        self.logger = logging.getLogger("GimpProcedure")

    @property
    def argument_specs(self):
        return self._procedure.get_arguments()

    @property
    def name(self):
        return self._procedure.get_name()




    def _does_procedure_take_runmode_from_name(self):
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
        proc_name = self.name
        result = ( proc_name.startswith('plug-in-')
                or proc_name.startswith('script-fu-')
                or proc_name.startswith('python-fu-')
                )
        return result

    def _does_procedure_take_runmode_from_signature(self):
        """ Examine signature of proc to determine whether it takes run_mode arg. """

        arg_specs = self.argument_specs
        if len(arg_specs) > 0:
            # assert arg_specs is-a list of GObject.GParamSpec or subclass thereof
            # TODO this is not specific enough, can we compare to Gimp type GimpRunMode ??


            # DEBUG dump a GParamSpec
            #print(dir(arg_specs[0]))
            #print(arg_specs[0].name)


            # FAIL: examine the type of the GParamSpec
            # gtype = arg_specs[0].__gtype__
            # self.logger.debug(f"first arg gtype: {gtype}")
            # result = (gtype.is_a(GObject.TYPE_ENUM))
            # result = (gtype == GObject.TYPE_ENUM)
            # result = (gtype == GObject.GParamEnum)

            # TODO file-gbr-save is aberrant, name is "dummy-param"
            # TODO compare type to "GimpRunMode" ???

            # Examine the name of the ParamSpec, not the type
            param_name = arg_specs[0].name
            self.logger.debug(f"first arg name: {param_name}")
            result = ( param_name == 'run-mode')    # !!! - not _
        else:
            result = False
        return result


    @property
    def takes_runmode(self):
        """ Does first formal arg signify run mode?

        type GimpParamEnum ??? or GimpRunMode ???
        """
        # Alternative implementations
        result = self._does_procedure_take_runmode_from_signature()
        #result = self._does_procedure_take_runmode_from_name()
        self.logger.debug(f"{self.name}: takes_runmode: {result}")
        return result





    # TODO optimized, cache result from Gimp instead of getting it each call

    def get_formal_argument_type(self, index):
        '''
        Get the formal argument type for a PDB procedure
        for argument with ordinal: index.
        Returns an instance of GType e.g. GObject.TYPE_INT

        Another implementation: Gimp.get_pdb().run_procedure( proc_name , 'gimp-pdb-get-proc-argument', args)
        '''
        # not require index is in range (will proceed_error)

        arg_specs = self.argument_specs    # some docs say it returns a count, it returns a list of GParam??
        # assert arg_specs is-a list

        ## arg_specs = Gimp.ValueArray.new(arg_count)
        ##config.get_values(arg_specs)

        # assert arg_specs is Gimp.ValueArray, sequence describing args of procedure
        # index may be out of range,  may have provided too many args
        try:
            arg_spec = arg_specs[index]   # .index(index) ??
            # assert is-a GObject.GParamSpec or subclass thereof
            ## OLD assert arg_spec is GObject.Value, describes arg of procedure (its GType is the arg's type)

            '''
            Documenting various things I tried, which we may need to try again.

            (dir(arg_spec)) at this point shows attributes of arg_spec

            1) formal_arg_type = type(arg_spec)

            2) formal_default_value = arg_spec.get_default_value()
               formal_arg_type = formal_default_value.get_gtype()
            '''
            formal_arg_type = arg_spec.__gtype__

        except IndexError:
            proceed("Formal argument not found, probably too many actual args.")
            formal_arg_type = None

        self.logger.debug(f"get_formal_argument_type returns: {formal_arg_type}")

        # assert type of formal_arg_type is-a GObject.GType
        return formal_arg_type
