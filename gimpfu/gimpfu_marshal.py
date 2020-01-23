
import gi
gi.require_version("Gimp", "3.0")
from gi.repository import Gimp

# TODO make this module the only one that imports GObject
from gi.repository import GObject


# import wrapper classes
from gimpfu_image import GimpfuImage
from gimpfu_layer import GimpfuLayer




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

        Requires gimp_object is-a Gimp object
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
    def wrap_args(cls, args):
        '''
        Wraps items if they need wrapping.
        Fundamental types do not need wrapping.
        Returns list.
        '''
        print("wrap_args", args)
        # TODO incomplete
        result = []
        for item in args:
            if type(item).__name__ in ('Image', 'Layer',):
                result.append(cls.wrap(item))
            else:
                result.append(item)
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
            result_arg_type = cls.try_upcast_to_drawable(result_arg)
        else:
            result_arg = arg
            # arg may be unwrapped result of previous call e.g. type Gimp.Layer
            # TODO: we wrap and unwrap as needed???
            # hack that might be removed?
            result_arg_type = cls.try_upcast_to_drawable(result_arg)
        print("unwrap_arg", result_arg, result_arg_type)
        return result_arg, result_arg_type



    # TODO optimize.  Get all the args at once, memoize

    def _get_formal_argument_type(proc_name, index):
        '''
        Get the formal argument type for a PDB procedure
        where argument identified by index.
        Returns an instance of GType e.g. GObject.TYPE_INT

        Another implementation: Gimp.get_pdb().run_procedure( proc_name , 'gimp-pdb-get-proc-argument', args)
        '''
        # require procedure in PDB
        procedure = Gimp.get_pdb().lookup_procedure(proc_name)
        ## OLD config = procedure.create_config()
        ## assert config is type Gimp.ProcedureConfig, having properties same as args of procedure

        arg_specs = procedure.get_arguments()    # some docs say it returns a count, it returns a list of GParam??
        print(arg_specs)
        # assert is a list

        ## arg_specs = Gimp.ValueArray.new(arg_count)
        ##config.get_values(arg_specs)

        # assert arg_specs is Gimp.ValueArray, sequence describing args of procedure
        arg_spec = arg_specs[index]   # .index(index)
        print(arg_spec)
        # assert is-a GObject.GParamSpec or subclass thereof
        ## OLD assert arg_spec is GObject.Value, describes arg of procedure (its GType is the arg's type)

        '''
        The type of the subclass of GParamSpec is enough for our purposes.
        Besides, GParamSpec.get_default_value() doesn't work???

        formal_arg_type = type(arg_spec)
        '''

        '''
        print(dir(arg_spec)) shows that arg_spec is NOT a GParamSpec, or at least doesn't have get_default_value.
        I suppose it is a GParam??
        Anyway, it has __gtype__
        '''
        """
        formal_default_value = arg_spec.get_default_value()
        print(formal_default_value)
        # ??? new to GI 2.38
        # assert is-a GObject.GValue

        formal_arg_type = formal_default_value.get_gtype()
        """
        formal_arg_type = arg_spec.__gtype__

        print( "get_formal_argument returns", formal_arg_type)

        # assert type of formal_arg_type is GObject.GType
        ## OLD assert formal_arg_type has python type like GParamSpec<Enum>
        return formal_arg_type


    def try_convert_to_float(proc_name, actual_arg, actual_arg_type, index):
        '''
        Convert the described actual arg to float if is int
        and PDB procedure wants a float
        (procedure's formal parameter is type GObject.TYPE_FLOAT).
        Only converts Python int to float.

        Returns actual_arg, type(actual_arg),    possibly converted

        Later, GObject will convert Python types to GTypes.
        '''
        # require type(actual_arg_type) is Python type or a GType

        result_arg = actual_arg
        result_arg_type = actual_arg_type

        print("Actual arg type:", type(actual_arg))

        if type(actual_arg) is int:
            formal_arg_type = Marshal._get_formal_argument_type(proc_name, index)
            # GType has property "name"
            print("     Formal art type ", formal_arg_type.name )

            #if formal_arg_type == GObject.TYPE_FLOAT or formal_arg_type == GObject.TYPE_DOUBLE :
            if formal_arg_type.name in ('GParamFloat', 'GParamDouble'): # ParamSpec ???
                # ??? Tell Gimpfu plugin author their code would be more clear if they used float() themselves
                # ??? Usually the source construct is a literal such as "1" that might better be float literal "1.0"
                print("GimpFu: Suggest: converting int to float.  Your code might be clearer if you use float literals.")
                result_arg = float(actual_arg)  # type conversion
                result_arg_type = type(result_arg)  # i.e. float

        # ensure result_arg_type == type of actual_arg OR (type(actual_arg) is int AND result_type_arg == float)
        # likewise for value of result_arg
        print("try_convert_to_float returns ", result_arg, result_arg_type)
        return result_arg, result_arg_type


    '''
    Seems like need for upcast is inherent in GObj.
    But probably Gimp should be doing most of the upcasting,
    so that many plugs don't need to do it.
    '''
    @classmethod
    def try_upcast_to_drawable(cls, arg):
        '''
        When type(arg) is subclass of Gimp.Drawable,
        and return new type Gimp.Drawable, else return original type.
        Does not actually change type of arg.

        Require arg a GObject (not wrapped)
        '''
        # idiom for class name
        print("Attempt up cast type", type(arg).__name__ )
        # Note the names are not prefixed with Gimp ???
        if type(arg).__name__ in ("Channel", "Layer"):  # TODO more subclasses
            result = Gimp.Drawable
        else:
            result = type(arg)
        # assert result is-a type (a Gimp type, a GObject type)
        print("upcast result:", result)
        return result



    """
    Cruft: more than necessary, but keep it, it documents how to use GTypes

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
    """
