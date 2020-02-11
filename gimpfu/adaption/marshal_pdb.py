
import gi
gi.require_version("Gimp", "3.0")
from gi.repository import Gimp

# TODO make this module the only one that imports GObject
from gi.repository import GObject


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


        for x in args:
            ## GObject.Value(GObject.TYPE_STRING, tmp))
            ## print("marshal arg:", x )

            go_arg, go_arg_type = Marshal._unwrap_arg_to_param(x)

            '''
            Don't assume any arg does NOT need conversion:
            a procedure can declare any arg of type float

            If more args than formal_args (from GI introspection), conversion will not convert.
            If less args than formal_args, Gimp might return an error when we call the PDB procedure.
            '''
            go_arg, go_arg_type = Types.try_convert_to_float(proc_name, go_arg, go_arg_type, index)

            go_arg, go_arg_type = Types.try_convert_to_null(proc_name, go_arg, go_arg_type, index)

            if is_wrapped_function(go_arg):
                do_proceed_error("Passing function as argument to PDB.")


            # !!! Can't assign GObject to python object: marshalled_arg = GObject.Value(Gimp.Image, x)
            # Must pass directly to insert()

            # ??? I don't understand why GObject.Value() doesn't determine the type of its second argument
            # unless GObject.Value() does some sort of casting

            '''
            This exception is not caused by plugin author, usually GimpFu programming error.
            Usually "Must be a GObject.GType, not a type"
            '''
            try:
                # TODO move GValue constructor to Types
                marshalled_args.insert(index, GObject.Value(go_arg_type, go_arg))
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
