
from gimppdb.gimppdb import GimpPDB
'''
OLD
import gi
gi.require_version("Gimp", "3.0")
from gi.repository import Gimp
'''

from message.proceed_error import do_proceed_error
import logging



class FormalTypes():
    '''
    Knows formal argument types declared for a PDB procedure.

    Formal type specs are in the PDB, ParamSpec's specify types.
    '''

    logger = logging.getLogger("GimpFu.Types")


    @staticmethod
    def _get_formal_argument_type(proc_name, index):
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

        FormalTypes.logger.info(f"get_formal_argument_type returns: {formal_arg_type}")

        # assert type of formal_arg_type is-a GObject.GType
        return formal_arg_type


    '''
    formal_arg_type is like GimpParamDrawable.
    formal_arg_type is-a GType
    GType has property "name" which is the short name

    !!! GObject type names are like GParamDouble
    but Gimp GObject type names are like GimpParamDrawable
    !!! *G* versus *Gimp*

    !!! Not formal_arg_type == GObject.TYPE_FLOAT or formal_arg_type == GObject.TYPE_DOUBLE
    '''
    @staticmethod
    def is_float_type(formal_arg_type):
        # use the short name
        return formal_arg_type.name in ('GParamFloat', 'GParamDouble')

    # TODO missing @staticmethod ?
    def is_str_type(formal_arg_type):
        return formal_arg_type.name in ('GParamString', )

    def is_int_type(formal_arg_type):
        return formal_arg_type.name in ('GParamInt', )  # ??? GParamUInt

    # !!!! GimpParam...
    def is_float_array_type(formal_arg_type):
        return formal_arg_type.name in ('GimpParamFloatArray', )


    # TODO rename is_drawable_formal_type
    @staticmethod
    def is_drawable_type(formal_arg_type):
        # use the short name
        result = formal_arg_type.name in ('GimpParamDrawable', )
        FormalTypes.logger.debug(f"is_drawable_type formal arg name: {formal_arg_type.name} ")
        return result


    @staticmethod
    def is_formal_type_equal_type(formal_type, actual_type):
        ''' Compare GType.name versus PythonType.__name__ '''
        formal_type_name = formal_type.name
        actual_type_name = actual_type.__name__

        mangled_formal_type_name = formal_type_name.replace('GimpParam', '')
        result = mangled_formal_type_name == actual_type_name
        FormalTypes.logger.debug(f"{result}    formal {formal_type_name} == actual {actual_type_name}")
        return result
