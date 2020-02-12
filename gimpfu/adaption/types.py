
import gi
gi.require_version("Gimp", "3.0")
from gi.repository import Gimp

from gi.repository import GObject    # GObject type constants

from adaption.wrappable import *    # is_subclass_of_type

from message.proceed_error import *



class Types():
    '''
    Knows Gimp and Python types, and ParamSpec's which specify types.
    Type conversions.
    Formal type specs

    Collaborates with Marshal.

    GimpFu converts Python ints to floats on behalf of Gimp.

    GimpFu upcasts e.g. Layer to Drawable where Gimp is uneccessarily demanding.
    GimpFu upcasts None to e.g. Layer when passed as actual arg.
    GimpFu upcasts -1 to e.g. Layer when passed as actual arg.
    '''

    # TODO optimize.  Get all the args at once, memoize

    @staticmethod
    def _get_formal_argument_type(proc_name, index):
        '''
        Get the formal argument type for a PDB procedure
        where argument identified by index.
        Returns an instance of GType e.g. GObject.TYPE_INT

        Another implementation: Gimp.get_pdb().run_procedure( proc_name , 'gimp-pdb-get-proc-argument', args)
        '''
        # require procedure in PDB, it was checked earlier
        procedure = Gimp.get_pdb().lookup_procedure(proc_name)
        ## OLD config = procedure.create_config()
        ## assert config is type Gimp.ProcedureConfig, having properties same as args of procedure

        arg_specs = procedure.get_arguments()    # some docs say it returns a count, it returns a list of GParam??
        print(arg_specs)
        # assert is a list

        ## arg_specs = Gimp.ValueArray.new(arg_count)
        ##config.get_values(arg_specs)

        # assert arg_specs is Gimp.ValueArray, sequence describing args of procedure
        # index may be out of range, GimpFu author may have provided too many args
        try:
            arg_spec = arg_specs[index]   # .index(index) ??
            print(arg_spec)
            # assert is-a GObject.GParamSpec or subclass thereof
            ## OLD assert arg_spec is GObject.Value, describes arg of procedure (its GType is the arg's type)

            '''
            CRUFT, some comments may be pertinent.

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

        except IndexError:
            do_proceed_error("Formal argument not found, probably too many actual args.")
            formal_arg_type = None


        print( "get_formal_argument returns", formal_arg_type)

        # assert type of formal_arg_type is GObject.GType
        ## OLD assert formal_arg_type has python type like GParamSpec<Enum>
        return formal_arg_type



    '''
    !!! Can't assign GValue to python object: foo = GObject.Value(Gimp.Image, x) ???
    Must pass directly to Gimp.ValueArray.insert() ???

    ??? I don't understand why GObject.Value() doesn't determine the type of its second argument
    I suppose GObject.Value() can't know all the types, is generic.
    '''
    @staticmethod
    def new_gvalue(gvalue_type, value):
        ''' Returns GValue'''
        # assert gvalue_type is a GObject type constant like GObject.TYPE_STRING
        '''
        An exception is usually not caused by plugin author, usually GimpFu programming error.
        Usually "Must be a GObject.GType, not a type"
        '''
        try:
            result = GObject.Value(gvalue_type, value)
        except Exception as err:
            do_proceed_error(f"Exception creating GValue for {gvalue_type}, {value}, err {err}")
            # Return some bogus value so can proceed
            result = GObject.Value( GObject.TYPE_INT, 1 )
            # TODO would this work??
            # result = GObject.Value( GObject.TYPE_NONE, None )
        return result



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


    # TODO rename is_drawable_formal_type
    @staticmethod
    def is_drawable_type(formal_arg_type):
        # use the short name
        result = formal_arg_type.name in ('GimpParamDrawable', )
        print(f"is_drawable_type formal arg name: {formal_arg_type.name} ")
        return result


    @staticmethod
    def is_formal_type_equal_type(formal_type, actual_type):
        # !!! GType.name versus PythonType.__name__
        formal_type_name = formal_type.name
        actual_type_name = actual_type.__name__

        mangled_formal_type_name = formal_type_name.replace('GimpParam', '')
        result = mangled_formal_type_name == actual_type_name
        print(f"{result}    formal {formal_type_name} == actual {actual_type_name}")
        return result


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
        print("try_convert_to_null returns ", result_arg, result_arg_type)
        return result_arg, result_arg_type


    @staticmethod
    def try_convert_to_float(proc_name, actual_arg, actual_arg_type, index):
        '''
        Convert the described actual arg to float if is int
        and PDB procedure wants a float
        (procedure's formal parameter is type GObject.TYPE_FLOAT).
        Only converts Python int to float.

        Returns actual_arg, type(actual_arg), possibly converted

        Later, GObject will convert Python types to GTypes.
        '''
        # require type(actual_arg_type) is Python type or a GType

        result_arg = actual_arg
        result_arg_type = actual_arg_type

        print("Actual arg type:", type(actual_arg))

        if type(actual_arg) is int:
            formal_arg_type = Types._get_formal_argument_type(proc_name, index)
            if formal_arg_type is not None:
                print("     Formal arg type ", formal_arg_type.name )
                if Types.is_float_type(formal_arg_type):
                    # ??? Tell Gimpfu plugin author their code would be more clear if they used float() themselves
                    # ??? Usually the source construct is a literal such as "1" that might better be float literal "1.0"
                    print("GimpFu: Suggest: converting int to float.  Your code might be clearer if you use float literals.")
                    result_arg = float(actual_arg)  # type conversion
                    result_arg_type = type(result_arg)  # i.e. float
            else:
                # Failed to get formal argument type.  Probably too many actual args.
                # Do not convert type.
                do_proceed_error(f"Failed to get formal argument type for index: {index}.")

        # ensure result_arg_type == type of actual_arg OR (type(actual_arg) is int AND result_type_arg == float)
        # likewise for value of result_arg
        print("try_convert_to_float returns ", result_arg, result_arg_type)
        return result_arg, result_arg_type


    '''
    Seems like need for upcast is inherent in GObj.
    But probably Gimp should be doing most of the upcasting,
    so that many plugs don't need to do it.
    '''
    @staticmethod
    def try_upcast_to_type(proc_name, arg, arg_type, index, cast_to_type):
        '''
        When type(arg) is subclass of cast_to_type
        and proc_name expects arg of cast_to_type at index,
        return cast_to_type, else return original type.
        Does not actually change type of arg i.e. no conversion, just casting.

        Require arg a GObject (not wrapped).
        Require proc_name a PDB procedure name.
        '''
        # assert type is like Gimp.Drawable, cast_to_type has name like Drawable

        print(f"Attempt upcast type: {get_type_name(arg)} to : {cast_to_type.__name__}")

        formal_arg_type = Types._get_formal_argument_type(proc_name, index)
        # TODO exception index out of range

        should_upcast = Types.is_formal_type_equal_type(formal_arg_type, cast_to_type)

        result = arg # result is unaltered arg except for cases below

        if should_upcast:
            if is_subclass_of_type(arg, cast_to_type):
                result_type = cast_to_type
                did_upcast = True
            elif arg == -1:
                # v2 allowed -1 as arg for optional drawables
                # # !!! Alter arg given by Author
                result = None
                result_type = cast_to_type
                did_upcast = True
            elif arg is None:
                # TODO migrate to create_nonetype_drawable or create_none_for_type(type)
                # Gimp wants GValue( Gimp.Drawable, None), apparently
                # This does not work: result = -1
                # But we can upcast NoneType, None is in every type???
                result_type = cast_to_type
                did_upcast = True
            else:
                # Note case Drawable == Drawable will get here, but Author cannot create instance of Drawable.
                do_proceed_error(f"Require arg type: {formal_arg_type} , but got {arg_type} not castable.")
                result_type = arg_type
                did_upcast = False
        else:
            result_type = arg_type
            did_upcast = False

        # assert result_type is-a type (a Gimp type, a GObject type)
        print(f"upcast result: {result}, {result_type}")
        return result, result_type, did_upcast



    @staticmethod
    def try_upcast_to_drawable(proc_name, arg, arg_type, index):
        return Types.try_upcast_to_type(proc_name, arg, arg_type, index, Gimp.Drawable)



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
    def convert_list_elements_to_python_types(a_list):
        ''' Walk (recursive descent) converting elements to Python types. '''
        ''' !!! This is converting, but not wrapping. '''
        result = [Types.try_convert_string_array_to_list_of_str(item) for item in a_list]
        print(result)
        return result


    '''
    See Marshal.wrap_adaptee_results() to wrap elements of list.
    '''


    @staticmethod
    def try_convert_string_array_to_list_of_str(item):
        ''' Try convert item from to list(str). Returns item, possibly converted.'''
        if isinstance(item, Gimp.StringArray):
            # Gimp.StringArray has fields, not methods
            print("StringArray length", item.length)
            # print("StringArray data", array.data)
            # 0xa0 in first byte, unicode decode error?
            print("Convert StringArray to list(str)")
            # print(type(item.data)) get utf-8 decode error
            # print(item.data.length()) get same errors
            # print(item.data.decode('latin-1').encode('utf-8')) also fails
            result = []
            result.append("foo")    # TEMP
            print("convert string result:", result)
        else:
            result = item
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
