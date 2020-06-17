
from gimppdb.gimppdb import GimpPDB

import logging



class FormalTypes():
    '''
    Understands type comparisons between Gimp/GObject and Python type systems.

    Formal arg specs for a PDB procedure are in the PDB.
    GParamSpec's have a type field.
    TODO this should be a thin wrapper around GParamSpec?

    Uses type names (strings) on the Gimp/GObject side.
    '''
    '''
    type_name is like 'GimpParamDrawable'.
    type is-a GType
    GType has property "name" which is the short name

    !!! GObject type names are like GParamDouble
    but Gimp GObject type names are like GimpParamDrawable
    !!! *G* versus *Gimp*

    !!! Not type_name == GObject.TYPE_FLOAT or type_name == GObject.TYPE_DOUBLE

    TODO caller might be using the wrong field for name of type
    Is it spec.value_type.name or spec.name?
    '''

    logger = logging.getLogger("GimpFu.Types")

    """
    These classify groups/sets of typenames.
    assert isinstance(type_name, str)
    """
    def is_float_type(type_name):        return type_name in ('GParamFloat', 'GParamDouble')
    def is_str_type(type_name):          return type_name in ('GParamString', )
    def is_int_type(type_name):          return type_name in ('GParamInt', )
    def is_unsigned_int_type(type_name): return type_name in ('GParamUInt', )
    def is_unsigned_char_type(type_name): return type_name in ('GParamUChar', )

    # !!!! GimpParam... not GParam...
    def is_object_array_type(type_name): return type_name in ('GimpParamObjectArray', )
    def is_float_array_type(type_name):   return type_name in ('GimpParamFloatArray', )

    def is_file_descriptor_type(type_name):
        # ??? PDB Browser says 'GFile' but is 'GParamObject'
        # TODO this might be too general, could catch other param types?
        result = (type_name in ('GParamObject', ))
        FormalTypes.logger.debug(f"is_file_descriptor_type: {type_name} is: {result}")
        return result

    # TODO rename is_drawable_formal_type
    @staticmethod
    def is_drawable_type(type_name):
        result = type_name in ('GimpParamDrawable', )
        FormalTypes.logger.debug(f"is_drawable_type formal arg name: {formal_arg_type.name} ")
        return result


    @staticmethod
    def is_formal_type_equal_type(formal_type, actual_type):
        ''' Compare GType name versus PythonType.__name__ '''
        formal_type_name = formal_type.name
        actual_type_name = actual_type.__name__

        mangled_formal_type_name = formal_type_name.replace('GimpParam', '')
        result = mangled_formal_type_name == actual_type_name
        FormalTypes.logger.debug(f"{result}    formal {formal_type_name} == actual {actual_type_name}")
        return result
