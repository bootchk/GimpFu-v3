
import gi
gi.require_version("Gimp", "3.0")
from gi.repository import Gimp


from adaption.wrappable import *
from adaption.marshal import Marshal
from adaption.types import Types
from adaption.upcast import Upcast
from adaption.value_array import FuValueArray
from adaption.generic_value import FuGenericValue

from gimppdb.gimppdb import GimpPDB

from message.proceed_error import proceed

import logging


class MarshalPDB():
    '''
    Knows how to marshal args to, and unmarshal results from, PDB.

    Crux: PDB wants GParamSpec's, not just GObjects.
    I.E. more specialized than ordinary Marshal

    Many methods operate on a stateful FuGenericValue, and don't return a result.
    '''

    logger = logging.getLogger("GimpFu.MarshalPDB")

    @staticmethod
    def _try_type_conversions(procedure, gen_value, index):
        '''
        Attempt type conversions and upcast when passing to Gimp procedures.
        Conversion: changes Python type of fundamental types, i.e. int to float
        Upcast: not change any type, just return superclass type that Gimp wants.

        Don't assume any arg does NOT need conversion:
        a procedure can declare any arg of type float
        '''
        # hack: upcast  subclass e.g. layer to superclass drawable
        # hack that might be removed if Gimp was not wrongly stringent

        # TODO optimize, getting type is simpler when is fundamental
        # We could retain that the arg is fundamental during unwrapping

        '''
        Any upcast or conversion is the sole upcast or conversion.
        (But un upcast may also internally convert)
        We don't upcast and also convert in this list.

        The order is not important as we only expect one upcast or convert.

        Try a sequence of upcasts and conversions.
        TODO just get the formal argument type and dispatch on it???
        '''
        MarshalPDB.logger.debug(f"_try_type_conversions: index {index}" )

        formal_arg_type = procedure.get_formal_argument_type(index)
        if formal_arg_type is None:
            # Probably too many actual args.
            proceed(f"Failed to get formal argument type for index: {index}.")
            return

        MarshalPDB.logger.debug(f"_try_type_conversions: index {index} formal type: {formal_arg_type}" )

        Upcast.try_to_drawable(formal_arg_type, gen_value, index)
        if gen_value.did_upcast:
            return
        Upcast.try_to_item(formal_arg_type, gen_value, index)
        if gen_value.did_upcast:
            return
        Upcast.try_to_layer(formal_arg_type, gen_value, index)
        if gen_value.did_upcast:
            return
        Upcast.try_to_color(formal_arg_type, gen_value, index)
        if gen_value.did_upcast:
            return

        # Continue trying conversions
        Types.try_usual_python_conversion(formal_arg_type, gen_value, index)
        if gen_value.did_convert:
            return
        Types.try_float_array_conversion(formal_arg_type, gen_value, index)
        if gen_value.did_convert:
            return
        #Types.try_object_array_conversion(formal_arg_type, gen_value, index)
        #if gen_value.did_convert:
        #    return
        Types.try_file_descriptor_conversion(formal_arg_type, gen_value, index)
        if not gen_value.did_convert:
            MarshalPDB.logger.debug(f"No type conversions: index {index} formal type: {formal_arg_type}" )

        # !!! We don't upcast deprecated constant TRUE to G_TYPE_BOOLEAN

        # TODO is this necessary? I think it is only drawable that gets passed None
        # Types.try_convert_to_null(proc_name, gen_value, index)






    @staticmethod
    def marshal_args(proc_name, *args):
        '''
        Marshal args to a PDB procedure.

        1. Gather many args into Gimp.ValueArray and return it.
        2. Optionally prefix args with run mode
        GimpFu feature: hide run_mode from calling author
        3. Unwrap wrapped arguments so all args are GObjects
        4. Upcasts and conversions
        5. Check error FunctionInfo
        '''

        # FuValueArray is global adaptor of Gimp.ValueArray.  Empty it.
        FuValueArray.reset()

        formal_args_index = 0

        procedure =  GimpPDB.get_procedure_by_name(proc_name)
        if procedure.takes_runmode:
            # no GUI, this is a call from a plugin

            a_gvalue = FuGenericValue.new_gvalue( Gimp.RunMode.__gtype__, Gimp.RunMode.NONINTERACTIVE)
            FuValueArray.push_gvalue( a_gvalue )
            # Run mode is in the formal args, not in passed actual args
            formal_args_index = 1

        '''
        If more actual args than formal_args (from GI introspection), conversion will fail
        since we can't know the formal type of the excess actual args.
        If less actual args than formal_args, we convert the given args,
        but Gimp might return an error when we call the PDB procedure with too few args.
        '''
        for x in args:
            MarshalPDB.logger.debug(f"marshalling arg: {x} index: {formal_args_index}" )
            # to dump more uncomment this
            # MarshalPDB.logger.debug(f"cumulative marshalled args: {FuValueArray.dump()}" )

            go_arg, go_arg_type = MarshalPDB._unwrap_to_param(x)
            # assert are GObject types, i.e. fundamental or Boxed
            # We may yet convert some fundamental types (tuples) to Boxed (Gimp.RGB)

            gen_value = FuGenericValue(go_arg, go_arg_type)

            """
            """
            try:
                MarshalPDB._try_type_conversions(procedure, gen_value, formal_args_index)
            except Exception as err:
                proceed(f"Exception in _try_type_conversions: {gen_value}, formal_args_index: {formal_args_index}, {err}")


            if is_wrapped_function(go_arg):
                proceed("Passing function as argument to PDB.")

            a_gvalue = gen_value.get_gvalue()
            FuValueArray.push_gvalue(a_gvalue)

            formal_args_index += 1

            """
            cruft
            try:
                marshalled_args.insert(index, gvalue)
            except Exception as err:
                proceed(f"Exception inserting {gvalue}, index {index}, to pdb, {err}")
                # ??? After this exception, often get: LibGimpBase-CRITICAL **: ...
                # gimp_value_array_insert: assertion 'index <= value_array->n_values' failed
                # The PDB procedure call is usually going to fail anyway.
            """

        result = FuValueArray.get_gvalue_array()

        MarshalPDB.logger.debug(f"marshal_args returns: {FuValueArray.dump()}" )
        return result


    @staticmethod
    def unmarshal_results(values):
        ''' Convert result of a pdb call to Python objects '''

        '''
        values is-a GimpValueArray
        First element is a PDBStatusType, discard it.
        If count remaining elements > 1, return a list,
        else return the one remaining element.

        For all returned objects, wrap as necessary.
        '''
        MarshalPDB.logger.debug(f"unmarshal_results called: {values}")

        # caller should have previously checked that values is not a Gimp.PDBStatusType.FAIL
        if values:
            # Remember, values is-a Gimp.ValueArray, not has Pythonic methods
            # TODO should be a method of FuValueArray
            result_list = Types.convert_gimpvaluearray_to_list_of_gvalue(values)

            # discard status by slicing
            result_list = result_list[1:]

            # Recursively convert type of elements to Python types
            result_list = Types.convert_list_elements_to_python_types(result_list)

            result_list = Marshal.wrap_adaptee_results(result_list)

            # unpack list of one element
            # TODO is this always the correct thing to do?
            # Some procedure signatures may return a list of one?
            if len(result_list) is 1:
                MarshalPDB.logger.debug("Unpacking single element list.")
                result = result_list[0]
            else:
                result = result_list
        else:
            result = None

        # ensure result is None or result is list or result is one object
        # NOT ensure each element is a fundamental Python type: some are opaque gobject.GBoxed
        # TODO ensure certain Gimp types are wrapped?

        # This throws exception for GBoxed
        # MarshalPDB.logger.debug(f"unmarshal_results returns: {result}")
        # TODO log the types, not the values???

        return result



    @staticmethod
    def _unwrap_to_param(arg):
        '''
        Returns a tuple: (unwrapped arg, type of unwrapped arg)
        For use as arg to PDB, which requires ParamSpec tuple.

        Only fundamental Python types and GTypes can be GObject.value()ed,
        which is what Gimp does with ParamSpec
        '''

        # TODO, possible optimization if arg is already unwrapped, or lazy?
        result_arg = Marshal.unwrap(arg)
        result_arg_type = type(result_arg)

        MarshalPDB.logger.debug(f"_unwrap_to_param returns: {result_arg} of type {result_arg_type}")
        return result_arg, result_arg_type
