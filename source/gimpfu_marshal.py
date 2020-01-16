
import gi
gi.require_version("Gimp", "3.0")
from gi.repository import Gimp

# TODO make this module the only one that imports GObject
from gi.repository import GObject


# import wrapper classes
from gimpfu_image import GimpfuImage
from gimpfu_layer import GimpfuLayer

from gimpfu_compatibility import Compat



class Marshal():
    '''
    Knows how to wrap and unwrap Gimp GObjects.

    Hides multiple constructors for wrappers.

    Each wrapped object has an unwrap method to return its adaptee.
    But this provides 'convenience' methods for some cases, like unwrapping args.
    In that case, this hides the need to:
      - upcast (GObject frequently requires explicit upcast)
      - convert (Python will convert int to float), but GimpFu must do that for args to Gimp

    Each wrapper also knows how to create a wrapper for a new'd Gimp GObject
    '''

    # TODO doesn't need to be classmethod
    @classmethod
    def wrap(cls, gimp_object):
        '''
        Wrap Gimp types that GimpFu wraps.
        E.G. Image => GimpfuImage
        '''
        '''
        Invoke the internal constructor for wrapper class.
        I.E. the adaptee already exists,
        the Nones mean we don't know attributes of adaptee,
        but the adaptee has and knows its attributes.
        '''
        print("Wrap ", gimp_object)

        # Dispatch on gimp type
        # This is a switch statement, default is an error
        gimp_type = type(gimp_object).__name__    # idiom for class name
        if  gimp_type == 'Image':
            result = GimpfuImage(None, None, None, gimp_object)
        elif gimp_type == 'Layer':
            result = GimpfuLayer(None, None, None, None, None, None, None, gimp_object)
        #elif gimp_type == 'Channel':
        # result = GimpfuLayer(None, None, None, None, None, None, None, gimp_object)
        else:
            exception_str = f"GimpFu: can't wrap gimp type {gimp_type}"
            raise RuntimeError(exception_str)
        return result


    @classmethod
    def unwrap_arg(cls, arg):
        '''
        Unwrap any GimpFu wrapped types to Gimp types
        E.G. GimpfuImage => Gimp.Image
        For primitive Python types and GTypes, idempotent, returns given arg unaltered.

        Returns unwrapped arg, type of unwrapped arg

        Only primitive Python types and GTypes can be GObject.value()ed
        '''
        # Unwrap wrapped types. Use idiom for class name
        # TODO other class names in list
        if  type(arg).__name__ in ("GimpfuImage", "GimpfuLayer") :
            # !!! Do not affect the original object by assigning to arg
            result_arg = arg.unwrap()

            # hack: up cast drawable sublclass e.g. layer to superclass drawable
            result_arg_type = Compat.try_upcast_to_drawable(result_arg)
        else:
            result_arg = arg
            # arg may be unwrapped result of previous call e.g. type Gimp.Layer
            # TODO: we wrap and unwrap as needed???
            # hack that might be removed?
            result_arg_type = Compat.try_upcast_to_drawable(result_arg)
        print("unwrap_arg", result_arg, result_arg_type)
        return result_arg, result_arg_type




    def _get_formal_argument_type(proc_name, index):
        '''
        Get the formal argument type for a PDB procedure
        where argument identified by index

        Another implementation: Gimp.get_pdb().run_procedure( proc_name , 'gimp-pdb-get-proc-argument', args)
        '''
        # require procedure in PDB
        procedure = Gimp.get_pdb().lookup_procedure(proc_name)
        config = procedure.create_config()
        # assert config is type Gimp.ProcedureConfig, having properties same as args of procedure
        arg_specs = config.get_values()
        # assert arg_specs is Gimp.ValueArray, sequence describing args of procedure
        arg_spec = arg_specs.index(index)
        # assert arg_spec is GObject.Value, describes arg of procedure (its GType is the arg's type)
        formal_arg_type = arg_spec.get_gtype()
        # assert type of formal_arg_type is GType
        return formal_arg_type


    def try_convert_to_float(proc_name, actual_arg, actual_arg_type, index):
        '''
        Convert the described actual arg to float if is int
        and PDB procedure wants a float (procedure's formal parameter is type float)

        Returns arg, arg_type    possibly converted
        '''
        # require actual_arg_type is a GType

        result_arg = actual_arg
        result_arg_type = actual_arg_type

        print("Actual arg type:", actual_arg_type)

        '''
        GType types are enumerated by constants of GObject.
        E.G. GObject.TYPE_INT is-a GType .
        In GObject docs, see "Constants"
        '''
        if actual_arg_type == GObject.TYPE_INT :    # INT_64 ???
            formal_arg_type = _get_formal_argument_type(proc_name, index)
            if formal_arg_type == GObject.TYPE_FLOAT or formal_arg_type == GObject.TYPE_DOUBLE :
                print("GimpFu: Warning: converting int to float.")
                result_arg = float(actual_arg)
                result_arg_type = GObject.TYPE_DOUBLE

        return result_arg, result_arg_type
