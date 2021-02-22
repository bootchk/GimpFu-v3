import gi
gi.require_version("Gimp", "3.0")
from gi.repository import Gimp
from gi.repository import GObject   # types

from gimpfu.gimppdb.runmode import RunMode
from gimpfu.message.proceed import proceed

import logging


class GimpProcedure:
    """
    Knows how to introspect a PDB procedure's metadata.

    Thin wrapper around Gimp.Procedure
    !!! Distinct from FuProcedure
    (GimpFu local knowledge of an author declared procedure.)
    FUTURE use FuProcedureMetadata for both GimpProcedure and FuProcedure

    This is not an adapter, an Author does not use this,
    only the GimpFu implementation uses it.
    (Although we could expose it?)
    """

    def __init__(self, gimp_procedure):
        assert isinstance(gimp_procedure, Gimp.Procedure)
        self._procedure = gimp_procedure
        self.logger = logging.getLogger("GimpFu.GimpProcedure")


    """
    Delegated to the wrapped instance of Gimp.Procedure
    """

    @property
    def argument_specs(self):
        """ Returns list of GParamSpec for arguments. """
        # Another implementation: Gimp.get_pdb().run_procedure( proc_name , 'gimp-pdb-get-proc-argument', args)
        # Method of wrapped Gimp.Procedure
        return self._procedure.get_arguments()

    @property
    def return_specs(self):
        """ Returns list of GParamSpec for return values. """
        # Method of wrapped Gimp.Procedure
        return self._procedure.get_return_values()

    @property
    def name(self):
        return self._procedure.get_name()

    """ Compare to PDB procedure gimp-pdb-get-proc-info() """
    # TODO rename procType
    @property
    def type(self):
        """ Returns value of type Gimp.PDBProcType """
        return self._procedure.get_proc_type()

    @property
    def menu_path(self):
        """ Returns string for the single menu path?
        TODO Why would a procedure have many menu paths?
        """
        paths = self._procedure.get_menu_paths()
        if len(paths) == 0:
            result = ""
        elif len(paths) == 1:
            result = paths[0]
        else :
            raise Exception("Can't handle many menu paths")
        self.logger.debug(f"menu path: {result}")
        return result


    """
    GimpFu hides the need for runmode in Author scripts.
    """
    @property
    def takes_runmode_arg(self):
        """ is first argument a "run mode" arg """
        result = RunMode.does_procedure_take_runmode_arg(self)
        self.logger.debug(f"_takes_runmode_arg for: {self.name} returns: {result}")
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

    @property
    def formal_arg_count(self):
        result = len(self.argument_specs)
        self.logger.debug(f"formal_arg_count returns: {result}")
        return result


    def get_formal_argument_type_name(self, index):
        value_type = self.get_formal_argument_value_type(index)
        # assert value_type is-a ???
        return value_type.name


    def get_formal_argument_value_type(self, index):
        '''
        Get the formal argument's type for a PDB procedure
        for argument with ordinal: index.

        Returns an instance of ??? not a str
        '''
        arg_spec = self.get_formal_argument_spec(index)
        if arg_spec is None:
            result = None
        else:
            result = arg_spec.value_type
        # ensure result is-a ??? or None
        self.logger.debug(f"get_formal_argument_value_type returns: {result}")
        return result


    def get_formal_argument_spec(self, index):
        '''
        Get the formal argument spec for a PDB procedure
        for argument with ordinal: index.
        Returns an instance of GParamSpec
        '''
        # not require index is in range (will proceed)

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


    """
    TODO this works, but why?  the __gtype__ of a GParamSpec signifies what???

    It logs e.g. as <GType GimpRunMode (39624048)> or <GType GimpParamDrawable (40117744)>
    """
    def get_formal_argument_type(self, index):
        '''
        Get the formal argument type for a PDB procedure
        for argument with ordinal: index.
        Returns an instance of GType e.g. GObject.TYPE_INT
        '''
        # not require index is in range (will proceed)

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
