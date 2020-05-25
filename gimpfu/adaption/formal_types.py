
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
        return formal_arg_type.name in ('GParamInt', )

    def is_unsigned_int_type(formal_arg_type):
        return formal_arg_type.name in ('GParamUInt', )

    def is_unsigned_char_type(formal_arg_type):
        return formal_arg_type.name in ('GParamUChar', )

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
