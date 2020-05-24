
import gi
gi.require_version("Gimp", "3.0")
from gi.repository import Gimp

from gi.repository import GObject    # GObject type constants

from adaption.wrappable import *    # is_subclass_of_type
from adaption.formal_types import FormalTypes

from gimppdb.gimppdb import GimpPDB

from message.proceed_error import *

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
    def try_convert_to_null(proc_name, actual_arg, actual_arg_type, index):
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
    def try_float_array_conversion(proc_name, gen_value, index):
        ''' Convert list of int to list of float when formal_arg_type requires FloatArray. '''

        Types.logger.info(f"try_float_array_conversion {gen_value}")
        if isinstance(gen_value.actual_arg, list):
            formal_arg_type = GimpPDB.get_formal_argument_type(proc_name, index)
            if formal_arg_type is not None:
                # Types.logger.info(formal_arg_type)
                if FormalTypes.is_float_array_type(formal_arg_type):
                    gen_value.float_array()
            else:
                # Probably too many actual args.
                # Do not convert type.
                do_proceed_error(f"Failed to get formal argument type for index: {index}.")
        # else not a list i.e. not a Gimp array



    @staticmethod
    def try_usual_python_conversion(proc_name, gen_value, index):
        '''
        Perform the usual automatic Python conversion from int to (str, float).

        Return converted actual arg to an other type if is type int
        and PDB procedure wants the other type.
        (procedure's formal parameter type in (GObject.TYPE_FLOAT, TYPE_STRING).

        Returns a GValue, possibly converted.
        !!! Note that the caller must ensure that the original variable is not converted,
        only the variable being passed to Gimp.

        GObject also converts Python fundamental types to GTypes as they are passed to Gimp.
        '''
        # require type(actual_arg_type) is Python type or a GType

        Types.logger.info(f"Actual arg type: {gen_value}")

        # TODO faster if we short circuit where actual == formal
        # TODO make the converter log what the conversion was
        '''
        The matrix of conversions:
        int => float, str
        float => int, str
        TODO str => float, int ???
        '''
        formal_arg_type = GimpPDB.get_formal_argument_type(proc_name, index)
        # ("     Formal arg type ", formal_arg_type.name )
        if formal_arg_type is not None:
            if gen_value.actual_arg_type is int:
                if FormalTypes.is_float_type(formal_arg_type):
                    gen_value.float()
                elif FormalTypes.is_str_type(formal_arg_type):
                    gen_value.str()
            elif gen_value.actual_arg_type is float:
                if FormalTypes.is_int_type(formal_arg_type):
                    gen_value.int()
                elif FormalTypes.is_str_type(formal_arg_type):
                    gen_value.str()
            # else not a usual Python conversion, or doesn't need conversion
        else:
            # Probably too many actual args.
            # Do not convert type.
            do_proceed_error(f"Failed to get formal argument type for index: {index}.")


        # ensure result_arg_type == type of actual_arg OR (type(actual_arg) is int AND result_type_arg == float)
        # likewise for value of result_arg
        Types.logger.info(f"try_usual_python_conversion returns {gen_value}")

        # WAS return result_arg, result_arg_type, did_convert



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
    '''
    @staticmethod
    def _should_upcast_or_convert(instance_type, formal_arg_type, cast_to_type):
        result = (
                (instance_type != cast_to_type)
            and FormalTypes.is_formal_type_equal_type(formal_arg_type, cast_to_type)
            )
        Types.logger.info(f"_should_upcast_or_convert: {result}")
        return result




    '''
    Seems like need for upcast is inherent in GObj.
    But probably Gimp should be doing most of the upcasting,
    so that many plugs don't need to do it.
    '''
    @staticmethod
    def try_upcast_to_type(proc_name, gen_value, index, cast_to_type):
        '''
        When gen_value.actual_arg_type is subclass of cast_to_type
        and proc_name expects cast_to_type at index,
        return cast_to_type, else return original type.
        Does not actually change type i.e. no conversion, just casting.

        Require gen_value a GObject (not wrapped).
        Require proc_name a PDB procedure name.
        '''
        # assert type is like Gimp.Drawable, cast_to_type has name like Drawable

        Types.logger.info(f"Attempt upcast: {gen_value} to : {cast_to_type.__name__}")

        formal_arg_type = GimpPDB.get_formal_argument_type(proc_name, index)
        # TODO exception index out of range

        if Types._should_upcast_or_convert(gen_value.actual_arg_type, formal_arg_type, cast_to_type):
            if is_subclass_of_type(gen_value.actual_arg, cast_to_type):
                gen_value.upcast(cast_to_type)
            elif gen_value.actual_arg == -1:
                # v2 allowed -1 as arg for optional drawables
                # # !!! convert arg given by Author
                gen_value.upcast_to_None(cast_to_type)
            elif gen_value.actual_arg is None:
                # TODO migrate to create_nonetype_drawable or create_none_for_type(type)
                # Gimp wants GValue( Gimp.Drawable, None), apparently
                # This does not work: result = -1
                # But we can upcast NoneType, None is in every type???
                gen_value.upcast(cast_to_type)
            else:
                # Note case Drawable == Drawable will get here, but Author cannot create instance of Drawable.
                do_proceed_error(f"Require type: {formal_arg_type} , but got {gen_value} not castable.")

        else:
            # No upcast was done
            pass

        # assert result_type is-a type (a Gimp type, a GObject type)
        Types.logger.info(f"try_upcast_to_type returns: {gen_value}")


    # TODO replace this with data driven single procedure
    @staticmethod
    def try_upcast_to_drawable(proc_name, gen_value, index):
        Types.try_upcast_to_type(proc_name, gen_value, index, Gimp.Drawable)

    @staticmethod
    def try_upcast_to_item(proc_name, gen_value, index):
        Types.try_upcast_to_type(proc_name, gen_value, index, Gimp.Item)

    @staticmethod
    def try_upcast_to_layer(proc_name, gen_value, index):
        Types.try_upcast_to_type(proc_name, gen_value, index, Gimp.Layer)

    @staticmethod
    def try_upcast_to_color(proc_name, gen_value, index):
        Types.try_upcast_to_type(proc_name, gen_value, index, Gimp.RGB)
        if gen_value.did_upcast:
            # also convert value
            try:
                gen_value.color()
            except Exception as err:
                do_proceed_error(f"Converting to color: {err}")
            #Types.logger.info(type(result))



    @staticmethod
    def convert_gimpvaluearray_to_list_of_gvalue(array):
        ''' Convert type of array from  to from *GimpValueArray*, to *list of GValue*. '''

        list_of_gvalue = []
        len = array.length()   # !!! not len(actual_args)
        for i in range(len):
            gvalue = array.index(i)
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
        ''' Try convert item from to list(str). Returns item, possibly converted.'''
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
