
import gi
gi.require_version("Gimp", "3.0")
from gi.repository import Gimp

from gi.repository import GObject    # GObject type constants

from gimpfu.adaption.formal_types import FormalTypes
from gimpfu.gimppdb.gimppdb import GimpPDB
from gimpfu.message.proceed import proceed

import logging


class Types():
    '''
    Knows Gimp and Python types
    Type conversions.
    Upcasts.

    Collaborates with:
    - Marshal
    - FormalTypes
    - FuGenericValue (some args are instances, but does not import the module)

    GimpFu converts Python ints to floats to satisfy Gimp.

    GimpFu upcasts e.g. Layer to Drawable where Gimp is uneccessarily demanding.
    GimpFu upcasts None to e.g. Layer when passed as actual arg.
    GimpFu upcasts -1 to e.g. Layer when passed as actual arg.
    '''

    '''
    Many methods return a GValue (instead of a (type, value))
    because only Gimp.value_set_float_array()
    lets properly converts native lists to FloatArray.
    '''
    # TODO optimize.  Get all the args at once, memoize

    logger = logging.getLogger("GimpFu.Types")

    # not used????
    @staticmethod
    def try_convert_to_null(proc_name, actual_arg, actual_arg_type):
        '''
        When actual arg is None, convert to GValue that represents None
        '''
        result_arg = actual_arg
        result_arg_type = actual_arg_type
        if actual_arg is None:
            result_arg = -1     # Somewhat arbitrary
            result_arg_type = GObject.TYPE_INT
        Types.logger.info(f"try_convert_to_null returns: {result_arg} of type: {result_arg_type}")
        return result_arg, result_arg_type



    @staticmethod
    def try_file_descriptor_conversion(formal_arg_type, gen_value):
        """
        Here we first check that a file descriptor is wanted.
        Then we check whether we convert a string filename.
        Then we check whether it already is a gtype that is-a file.
        """
        formal_arg_type_name = formal_arg_type.name
        if FormalTypes.is_file_descriptor_type(formal_arg_type_name):
            # Yes, we need a GFile
            if isinstance(gen_value.actual_arg, str):
                gen_value.to_file_descriptor()
            else:
                Types.logger.warning(f"GFile needed but str not passed.")

            """
            TODO:
            if it already is a GObject of type GLocalFile,
            we simply need to make a GValue, telling it the type is GFile.
            We really expect a str, to accept a GLocalFile might be more forgiving.
            elif gen_value.actual_arg.__gtype__ == GLocalFile
            """




    @staticmethod
    def try_usual_python_conversion(formal_arg_type, gen_value):
        '''
        Perform the usual automatic Python conversions.

        Given:
           author's actual arg in Python (in a FuGenericValue)
           a GObject type (formal_arg_type) that a PDB procedure requires.
        Returns:
            Returns a FuGenericValue (wrapper of GValue), possibly converted.
            I.E. side effects on gen_value.

        Procedure's formal parameter type in (GObject.TYPE_FLOAT, TYPE_STRING).

        !!! Note that the caller must ensure that the original variable is not converted,
        only the variable being passed to Gimp.

        PyGObject also converts Python fundamental types to GTypes as they are passed to Gimp.
        This is similar, but for our marshalling of calls to PDB.
        '''
        # require type(actual_arg_type) is Python type or a GType

        # TODO faster if we short circuit where actual == formal
        # TODO make the converter log what the conversion was
        '''
        A table of conversions:
        Python type => Gimp C types (GObject types)
        ---------------------------
        int   => boolean, float, str, unsigned int, unsigned char, unsigned 64
        float => boolean, int,   str

        TODO str => float, int ???
        TODO True/False => boolean
        TODO unsigned 64
        '''

        Types.logger.info(f" try_usual_python_conversion: actual type: {gen_value} formal type: {formal_arg_type}")
        # ("     Formal arg type ", formal_arg_type.name )
        assert formal_arg_type is not None

        # FormalTypes.is_foo() requires str
        formal_arg_type_name = formal_arg_type.name
        assert isinstance(formal_arg_type_name, str)

        if gen_value.actual_arg_type is int:
            if FormalTypes.is_int_type(formal_arg_type_name):
                gen_value.accept()
            elif FormalTypes.is_boolean_type(formal_arg_type_name):
                gen_value.boolean()
            elif FormalTypes.is_float_type(formal_arg_type_name):
                gen_value.float()
            elif FormalTypes.is_str_type(formal_arg_type_name):
                gen_value.str()
            elif FormalTypes.is_unsigned_int_type(formal_arg_type_name):
                gen_value.unsigned_int()
            elif FormalTypes.is_unsigned_char_type(formal_arg_type_name):
                gen_value.unsigned_char()
        elif gen_value.actual_arg_type is float:
            # TODO convert float to boolean
            if FormalTypes.is_float_type(formal_arg_type_name):
                gen_value.accept()
            elif FormalTypes.is_int_type(formal_arg_type_name):
                gen_value.int()
            elif FormalTypes.is_str_type(formal_arg_type_name):
                gen_value.str()
        else:
            # TODO convert str to usual types a la SNOBOL
            # !!! That will require more work, not simple upcasts.
            Types.logger.info(f"try_usual_python_conversion {gen_value.actual_arg_type}"
               "is not a usual Python conversion")

        # ensure result_arg_type == type of actual_arg OR (type(actual_arg) is int AND result_type_arg == float)
        # likewise for value of result_arg
        Types.logger.info(f"try_usual_python_conversion returns {gen_value}")



    '''
    Upcast or convert when
    formal_arg_type equals cast_to_type
    and instance_type is not already cast_to_type
    E.G.
    Layer, Drawable, Drawable => True
    Layer, Layer, Layer => False
    Layer, Drawable, Item => False
    tuple, RGB, RGB => True

    Note that Layer is-a Drawable is-a Item
    and we may call this with (Layer, Drawable, Item)
    but we don't upcast since the procedure wants Drawable

    TODO this is only used by Upcast, should be there.
    Only for upcasts combined with a conversion??
    Other conversions don't use this method???
    '''
    @staticmethod
    def _should_upcast_or_convert(instance_type, formal_arg_type, cast_to_type):
        result = (
                (instance_type != cast_to_type)
            and FormalTypes.is_formal_type_equal_type(formal_arg_type, cast_to_type)
            )
        Types.logger.info(f"_should_upcast_or_convert => {result}")
        return result



    def try_array_conversions(formal_arg_type, gen_value):
        """
        Try convert gen_value to GObject arrays.
        Typically actual arg is a Python sequence,
        but we allow actual arg to be a single element.

        These are only the array types currently used in the PDB for IN params to PDB procedures.
        TODO needed for marshalling to lib gimp calls (alias gimp adaptor)?

        Ordered by prevalence in PDB signatures.
        """
        Types.logger.info(f"try_array_conversions ( {formal_arg_type} )")
        # dispatch on formal_arg_type
        formal_arg_type_name = formal_arg_type.name
        Types.logger.info(f"try_array_conversions formal type name: {formal_arg_type_name}")
        if FormalTypes.is_float_array_type(formal_arg_type_name):
            gen_value.to_float_array()
        elif FormalTypes.is_object_array_type(formal_arg_type_name):
            gen_value.to_object_array()
        elif FormalTypes.is_string_array_type(formal_arg_type_name):
            gen_value.to_string_array()
        elif FormalTypes.is_uint8_array_type(formal_arg_type_name):
            gen_value.to_uint8_array()
        elif FormalTypes.is_int32_array_type(formal_arg_type_name):
            gen_value.to_int32_array()
        elif FormalTypes.is_color_array_type(formal_arg_type_name):
            gen_value.to_color_array()
        else:
            Types.logger.info(f"try_array_conversions did NOT convert: {formal_arg_type_name}")
            Types.logger.info(f"Check GimpFu code for typos in type names.")
            if isinstance(gen_value.actual_arg, tuple) or isinstance(gen_value.actual_arg, list):
                Types.logger.warning(f"sequences SHOULD convert to arrays!")

        """
         OLD
        Types.try_float_array_conversion(formal_arg_type, gen_value)
        if gen_value.did_convert:  return
        Types.try_object_array_conversion(formal_arg_type, gen_value)
        if gen_value.did_convert:  return
        Types.try_string_array_conversion(formal_arg_type, gen_value)
        if gen_value.did_convert:  return
        #Types.try_uint8_array_conversion(formal_arg_type, gen_value)
        #if gen_value.did_convert:  return
        #Types.try_int32_array_conversion(formal_arg_type, gen_value)

        Types.logger.info(f"try_array_conversions did NOT convert")
        """




    @staticmethod
    def convert_gimpvaluearray_to_list_of_gvalue(array):
        ''' Convert from type *GimpValueArray*, to *list of GValue*. '''

        list_of_gvalue = []
        len = array.length()   # !!! not len()
        Types.logger.info(f"convert_gimpvaluearray_to_list_of_gvalue length: {len}")
        for i in range(len):
            try:
                gvalue = array.index(i)
            except:
                from gimpfu.adaption.generic_value import FuGenericValue
                # Probably a bug in Gimp
                proceed(f"Fail GimpValueArray.index() at index: {i}.")
                # Fixup with some arbitrary GValue
                gvalue = FuGenericValue.new_int_gvalue()
            # Not convert elements from GValue to Python types
            list_of_gvalue.append(gvalue)

        # ensure is list of elements of type GValue, possibly empty
        return list_of_gvalue


    # TODO this whole routine is misguided?  We can't convert anything
    # All we can do is warn of GBoxed?
    # An Author can subsequently use the instances of GBoxed, but only as parameters to other Gimp calls
    # i.e. GBoxed can only be dealt with by GObject methods, and not python
    # and GObject methods don't let you do much with it.
    '''
    Only certain Gimp types need conversion.
    E.G. Gimp.StringArray => list(str).
    PyGObject handles fundamental simple types, lists, and array?
    TODO why isn't a Gimp.StringArray returned as a GSList that PyGobject handles?

    Also assume that Gimp never returns a deep tree of Arrays inside Arrays,
    except for Gimp.ValueArray containing Gimp.StringArray.
    This does not descend enough, only one level.
    '''
    @staticmethod
    def convert_list_elements_to_python_types(list):
        ''' Walk (recursive descent) Python list of GValues, converting elements to Python types. '''
        ''' !!! This is converting, but not wrapping. '''
        ''' list comprises fundamental objects, and GArray-like objects that need conversion to lists. '''

        '''
        TODO this should be driven by formal return type
        Some formal return types take many elements from the list???
        '''
        result = []
        for item in list:
            Types.logger.info(f"Type of item in list: {type(item)}" )
            result.append(item)

            if isinstance(item, GObject.GBoxed):
                Types.logger.warn(f"PDB procedure returned an item of type GObject.GBoxed")

            # OLD result = [Types.try_convert_string_array_to_list_of_str(item) ]
            # TODO get type: gobject.GBoxed

        # Can't use this because it throws an exception for GBoxed
        # Types.logger.info(f"convert_list_elements_to_python_types returns: {result}")
        return result


    '''
    See Marshal.wrap_adaptee_results() to wrap elements of list.
    '''


    @staticmethod
    def try_convert_string_array_to_list_of_str(item):
        ''' Try convert item from Gimp.StringArray to list(str). Returns item, possibly converted.'''
        if isinstance(item, Gimp.StringArray):
            # Gimp.StringArray has fields, not methods
            Types.logger.info(f"StringArray length: {item.length}")
            # Types.logger.info("StringArray data", array.data)
            # 0xa0 in first byte, unicode decode error?
            Types.logger.info("Convert StringArray to list(str)")
            # Types.logger.info(type(item.data)) get utf-8 decode error
            # Types.logger.info(item.data.length()) get same errors
            # Types.logger.info(item.data.decode('latin-1').encode('utf-8')) also fails
            Types.logger.info(f"item is: {item}")
            # Gimp.StringArray is not iterable
            Types.logger.info(f"item.static_data is: {item.static_data}")
            # says "False"
            result = []
            result.append("foo")    # TEMP
            Types.logger.info(f"convert string result: {result}")
        else:
            result = item
        return result
