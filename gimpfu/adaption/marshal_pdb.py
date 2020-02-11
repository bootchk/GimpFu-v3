
import gi
gi.require_version("Gimp", "3.0")
from gi.repository import Gimp


from adaption.wrappable import *
from adaption.marshal import Marshal
from adaption.types import Types

from message.proceed_error import *



class MarshalPDB():
    '''
    Knows how to marshal args to, and unmarshal results from, PDB.

    Crux: PDB wants GParamSpec's, not just GObjects.
    I.E. more specialized than ordinary Marshal
    '''


    @staticmethod
    def try_type_conversions(proc_name, go_arg, go_arg_type, index):
        '''
        Attempt type conversions.

        Don't assume any arg does NOT need conversion:
        a procedure can declare any arg of type float
        '''
        # hack: upcast  subclass e.g. layer to superclass drawable
        # hack that might be removed if Gimp was not wrongly stringent

        # TODO optimize, getting type is simpler when is fundamental
        # We could retain that the arg is fundamental during unwrapping

        # TODO do only one conversion if

        go_arg, go_arg_type, did_convert = Types.try_upcast_to_drawable(proc_name, go_arg, go_arg_type, index)

        if not did_convert:
            go_arg, go_arg_type = Types.try_convert_to_float(proc_name, go_arg, go_arg_type, index)

        # TODO is this necessary? I think it is only drawable that gets passed None
        #go_arg, go_arg_type = Types.try_convert_to_null(proc_name, go_arg, go_arg_type, index)

        return go_arg, go_arg_type





    @staticmethod
    def marshal_args(proc_name, *args):
        '''
        Marshal args to a PDB procedure.

        1. Gather many args into Gimp.ValueArray and return it.
        2. Optionally prefix args with run mode
        GimpFu feature: hide run_mode from calling author
        3. Unwrap wrapped arguments so all args are GObjects
        4. Hacky upcast to Drawable ???
        5. float(arg) as needed
        6. Check error FunctionInfo
        '''

        # TODO extract method
        # TODO python-fu- ?? What procedure names signify need run_mode?
        # Better to introspect ??
        if proc_name.startswith('plug-in-'):
            marshalled_args = Gimp.ValueArray.new(len(args)+1)
             # no GUI, this is a call from a plugin
            marshalled_args.insert(0, Gimp.RunMode.NONINTERACTIVE)
            index = 1
        else:
            marshalled_args = Gimp.ValueArray.new(len(args))
            index = 0


        '''
        If more args than formal_args (from GI introspection), conversion will not convert.
        If less args than formal_args, Gimp might return an error when we call the PDB procedure.
        '''
        for x in args:
            ## print("marshal arg:", x )

            go_arg, go_arg_type = MarshalPDB._unwrap_to_param(x)

            go_arg, go_arg_type = MarshalPDB.try_type_conversions(proc_name, go_arg, go_arg_type, index)

            if is_wrapped_function(go_arg):
                do_proceed_error("Passing function as argument to PDB.")

            '''
            This exception is not caused by plugin author, usually GimpFu programming error.
            Usually "Must be a GObject.GType, not a type"
            '''
            try:
                marshalled_args.insert(index, Types.new_gvalue(go_arg_type, go_arg))
            except Exception as err:
                do_proceed_error(f"Exception marshalling arg {x} to pdb, {err}")
                # ??? After this exception, often get: LibGimpBase-CRITICAL **: ...
                # gimp_value_array_insert: assertion 'index <= value_array->n_values' failed
                # The PDB procedure call is usually going to fail anyway.

            index += 1

        print("marshalled_args", marshalled_args )
        return marshalled_args


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
        print("PDB status result is:", values.index(0))

        # caller should have previously checked that values is not a Gimp.PDBStatusType.FAIL
        if values:
            # Remember, values is-a Gimp.ValueArray, not has Pythonic methods
            result_list = Types.convert_gimpvaluearray_to_list_of_gvalue(values)

            # discard status by slicing
            result_list = result_list[1:]

            # Recursively convert type of elements to Python types
            result_list = Types.convert_list_elements_to_python_types(result_list)

            # unpack list of one element
            # TODO is this always the correct thing to do?
            # Some procedure signatures may return a list of one?
            if len(result_list) is 1:
                print("Unpacking single element list.")
                result = result_list[0]
            else:
                result = result_list
        else:
            result = None

        # ensure result is None or result is list or result is one object
        # TODO ensure wrapped?
        print("unmarshal_pdb_result", result)
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

        print("_unwrap_to_param", result_arg, result_arg_type)
        return result_arg, result_arg_type
