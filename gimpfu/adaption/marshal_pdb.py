
import gi
gi.require_version("Gimp", "3.0")
from gi.repository import Gimp


from adaption.wrappable import *
from adaption.marshal import Marshal
from adaption.types import Types
from adaption.upcast import Upcast
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
            proceed(f"Failed to get formal arg type for index: {index}.")
            return

        MarshalPDB.logger.debug(f"_try_type_conversions: index {index} formal type: {formal_arg_type}" )

        Upcast.try_gimp_upcasts(formal_arg_type, gen_value, index)
        if gen_value.did_upcast:
            return

        Types.try_usual_python_conversion(formal_arg_type, gen_value)
        if gen_value.did_convert:
            return

        Types.try_array_conversions(formal_arg_type, gen_value)
        if gen_value.did_convert:
            return

        Types.try_file_descriptor_conversion(formal_arg_type, gen_value)
        if not gen_value.did_convert:
            MarshalPDB.logger.debug(f"No type conversions: index {index} formal type: {formal_arg_type}" )

        # !!! We don't upcast deprecated constant TRUE to G_TYPE_BOOLEAN

        # TODO is this necessary? I think it is only drawable that gets passed None
        # Types.try_convert_to_null(proc_name, gen_value)



    @staticmethod
    def synthesize_marshalled_run_mode(proc_name, *args):
        MarshalPDB.logger.debug(f"Synthesized runmode NONINTERACTIVE")
        return FuGenericValue.new_gvalue( Gimp.RunMode.__gtype__, Gimp.RunMode.NONINTERACTIVE)


    @staticmethod
    def marshal_args(proc_name, *args):
        '''
        Marshal args to a PDB procedure.

        Accepts: sequence of wrapped or primitive args
        Returns: sequence of GValue

        (We are returning a sequence, not a GValueArray.
        If it were a GValueArray, we would use: result.insert(index, gvalue) )

        Optionally synthesize (prefix result) with run mode
        GimpFu feature: hide run_mode from calling author

        For each arg:
        - Unwrap wrapped arguments so result is GObjects (not a GimpFu object)
        - Upcasts and conversions
        - check for error "passing func" FunctionInfo
        '''

        result = []

        formal_args_index = 0

        # Called procedure knows its formal parameters
        procedure =  GimpPDB.get_procedure_by_name(proc_name)

        """
        Check count of formal versus actual args.

        GimpFu allows count actual args to be less by one,
        if the procedure takes runmode, and then we insert it.
        But some callers may have passed runmode
        (did not use the GimpFu shortcut.)
        """
        if (len(args) == procedure.formal_arg_count - 1
           and procedure.takes_runmode_arg) :
           """
           Assume the case that run mode is in the formal args, not in passed actual args.
           Synthesizing runmode might now work, the caller might have made an error
           and not just using the GimpFu convention of not passing runmode.
           """
           result.append( synthesizeRunMode() )
           # skip to the next formal arg
           formal_args_index = 1
        elif len(args) != procedure.formal_arg_count :
            '''
            If more actual args than formal_args we can't know the formal type of the excess actual args.
            If less actual args than formal_args, we could convert the given args,
            but Gimp would return an error when we call the PDB procedure with too few args.
            '''
            proceed(f"Mismatched count of formal versus actual args for {proc_name}")

        for x in args:
            MarshalPDB.logger.debug(f"marshalling arg value: {x} index: {formal_args_index}" )
            # to dump more uncomment this
            # MarshalPDB.logger.debug(f"cumulative marshalled args: {result}" )

            go_arg, go_arg_type = MarshalPDB._unwrap_to_param(x)
            # assert are GObject types, i.e. fundamental or Boxed
            # We may yet convert some fundamental types (tuples) to Boxed (Gimp.RGB)

            gen_value = FuGenericValue(go_arg, go_arg_type)

            # One of the main capabilities of GimpFu: accept loose, Pythonic code and do convenient upcasts/conversions
            try:
                MarshalPDB._try_type_conversions(procedure, gen_value, formal_args_index)
            except Exception as err:
                proceed(f"Exception in _try_type_conversions: {gen_value}, formal_args_index: {formal_args_index}, {err}")


            if is_wrapped_function(go_arg):
                proceed("Passing function as argument to PDB.")

            a_gvalue = gen_value.get_gvalue()
            result.append(a_gvalue)

            formal_args_index += 1

        MarshalPDB.logger.debug(f"marshal_args returns: {result}" )

        """
        result sequence could be empty (normal)
        or may be short or long, since we may have proceeded past an error.
        """
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
            if len(result_list) == 1:
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
        which is what Gimp does with ParamSpec.

        Warns when result_arg is None, result_arg_type is NoneType
        TODO Not acceptable in a call to PDB??
        '''

        # TODO, possible optimization if arg is already unwrapped, or lazy?
        result_arg = Marshal.unwrap(arg)
        result_arg_type = type(result_arg)

        if result_arg is None:
            MarshalPDB.logger.warning(f"_unwrap_to_param returns None, NoneType")

        MarshalPDB.logger.debug(f"_unwrap_to_param returns: {result_arg} of type {result_arg_type}")
        return result_arg, result_arg_type
