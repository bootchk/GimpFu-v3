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
        self.logger = logging.getLogger("GimpFu.GimpProcedure")

    @property
    def argument_specs(self):
        # Another implementation: Gimp.get_pdb().run_procedure( proc_name , 'gimp-pdb-get-proc-argument', args)
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
        """ Examine signature of proc to determine whether it takes run_mode arg.

        The most reliable implementation:
        Get GParamSpec, and compare its type.name to 'GimpRunMode'
        """

        arg_specs = self.argument_specs
        # assert arg_specs is-a list of GObject.GParamSpec or subclass thereof
        if len(arg_specs) > 0:
            # run-mode is the first arg
            type_name = self.get_formal_argument_type_name(0)
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

    """
    to dump a GParamSpec:    print(dir(arg_specs[0]))
    We find that it has attributes 'name' and 'value_type' and '__gtype__'
    __gtype__ is GParamSpec, not what we want
    Also, type(arg_specs[0]) is <class gobject.GParamSpec>, also not what we want.
    value_type is the formal type of the parameter, what we want

    to dump a type: dir(param_type)
    We find that it has attribute 'name'
    We want to compare name to 'GimpRunMode'
    Fails: str(param_type) is not succint
    Fails: type comparison param_type == Gimp.RunMode  ???
    !!! Gimp.RunMode is-a class, i.e. a type, why can't we compare types?
    """

    def get_formal_argument_type_name(self, index):
        '''
        Get the formal argument's type's name for a PDB procedure
        for argument with ordinal: index.
        Returns an instance of str
        '''
        arg_spec = self.get_formal_argument_spec(index)
        if arg_spec is None:
            result = None
        else:
            result = arg_spec.value_type.name
        # ensure result is-a str or None
        return result


    def get_formal_argument_spec(self, index):
        '''
        Get the formal argument spec for a PDB procedure
        for argument with ordinal: index.
        Returns an instance of GParamSpec
        '''
        # not require index is in range (will proceed_error)

        arg_specs = self.argument_specs    # some docs say it returns a count
        # assert arg_specs is-a list of GParamSpec

        ## arg_specs = Gimp.ValueArray.new(arg_count)
        ##config.get_values(arg_specs)
        # assert arg_specs is Gimp.ValueArray, sequence describing args of procedure
        try:
            result = arg_specs[index]   # .index(index) ??
            # assert is-a GObject.GParamSpec or subclass thereof
            ## OLD assert arg_spec is GObject.Value, describes arg of procedure (its GType is the arg's type)

        except IndexError:
            proceed("Formal argument not found, probably too many actual args.")
            result = None

        self.logger.debug(f"get_formal_argument_spec returns: {result}")

        # assert result is-a GParamSpec
        return result


    def get_formal_argument_type(self, index):
        '''
        Get the formal argument type for a PDB procedure
        for argument with ordinal: index.
        Returns an instance of GType e.g. GObject.TYPE_INT
        '''
        # not require index is in range (will proceed_error)

        arg_spec = self.get_formal_argument_spec(index)

        '''
        Documenting various things I tried, which we may need to try again.

        (dir(arg_spec)) at this point shows attributes of arg_spec

        1) formal_arg_type = type(arg_spec)

        2) formal_default_value = arg_spec.get_default_value()
           formal_arg_type = formal_default_value.get_gtype()

        ??? Why not arg_spec.value_type
        '''
        if arg_spec is None:
            result = None
        else:
            result = arg_spec.__gtype__

        self.logger.debug(f"get_formal_argument_type returns: {result}")

        # assert result is-a GObject.GType
        return result
