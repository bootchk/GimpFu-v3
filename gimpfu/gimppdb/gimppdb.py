
import gi
gi.require_version("Gimp", "3.0")
from gi.repository import Gimp

import logging




class GimpPDB:
    """ Thin wrapper around the Gimp PDB.

    For introspection of the PDB.

    !!! Distinct from GimpfuPDB.
    This is not an adapter, an Author does not use this,
    only the GimpFu implementation uses it.
    See aliases/pdb for the adapter used by Authors, see class GimpfuPDB
    """

    logger = logging.getLogger("GimpFu.GimpPDB")


    def get_procedure_by_name(proc_name):
        """ Returns Gimp.Procedure for procname, else None. """
        return Gimp.get_pdb().lookup_procedure(proc_name)


    def does_procedure_take_runmode(proc_name):
        """ Is the first arg of type GimpParamEnum signifying run mode?

        Implemented using string compares.
        We don't use the field plug-type,
        since it can be "Temporary Procedure" or "GIMP Plug-In"

        Alternatively, get the type of first formal arg???
        """
        result = ( proc_name.startswith('plug-in-')
                or proc_name.startswith('script-fu-')
                or proc_name.startswith('python-fu-')
                )
        return result


    # TODO optimized, cache result from Gimp instead of getting it each call

    def get_formal_argument_type(proc_name, index):
        '''
        Get the formal argument type for a PDB procedure
        for argument with ordinal: index.
        Returns an instance of GType e.g. GObject.TYPE_INT

        Another implementation: Gimp.get_pdb().run_procedure( proc_name , 'gimp-pdb-get-proc-argument', args)
        '''
        # require procedure in PDB, it was checked earlier
        procedure = GimpPDB.get_procedure_by_name(proc_name)
        # OLD Gimp.get_pdb().lookup_procedure(proc_name)

        arg_specs = procedure.get_arguments()    # some docs say it returns a count, it returns a list of GParam??
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
            do_proceed_error("Formal argument not found, probably too many actual args.")
            formal_arg_type = None

        GimpPDB.logger.debug(f"get_formal_argument_type returns: {formal_arg_type}")

        # assert type of formal_arg_type is-a GObject.GType
        return formal_arg_type


# Gimp.procedure
