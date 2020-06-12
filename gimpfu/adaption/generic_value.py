
import gi
from gi.repository import GObject

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp

from gi.repository import GLib  # GLib.guint ???
from gi.repository import Gio   # Gio.File

from adapters.rgb import GimpfuRGB

from message.proceed_error import do_proceed_error
from message.suggest import Suggest


# TODO foo_type getters should be computed properties, not mutable

class FuGenericValue():
    '''
    A (type, value) that holds any ('generic') value.
    Similar to GValue.

    Adapts Python types to GTypes.

    Stateful:
    Operations in this sequence:  init, apply conversions and upcasts, get_gvalue

    In type is a GType or Python type.
    Result type is also GType or Python type.
    Only get_gvalue definitely returns a GType.

    Responsible for:
    - performing conversions and Upcasts
    - produce a Gvalue

    Is not a singleton, but only one is ever in use.
    '''


    def __init__(self, actual_arg, actual_arg_type):
        self._actual_arg = actual_arg
        self._actual_arg_type = actual_arg_type

        # result is None until converted or upcast
        self._result_arg = None
        self._result_arg_type = None
        self._gvalue = None

        self._did_convert = False
        self._did_upcast = False
        self._did_create_gvalue = False


    def __repr__(self):
        return ','.join((str(self.actual_arg), str(self._actual_arg_type),
                         str(self._result_arg), str(self._result_arg_type),
                         str(self._did_convert), str(self._did_upcast) ))


    def get_gvalue(self):
        ''' Return gvalue for original arg with all conversions and upcasts applied.  '''
        if self._did_create_gvalue:
            result_gvalue = self._gvalue
        elif self._did_convert or self._did_upcast:
            result_gvalue =  FuGenericValue.new_gvalue(self._result_arg_type, self._result_arg)
        else:
            # Idempotent, the original type and arg
            result_gvalue =  FuGenericValue.new_gvalue(self._actual_arg_type, self._actual_arg)
        return result_gvalue

    '''
    properties

    Not all fields are exposed to public.
    Only some are queried by callers.
    None are settable by callers.
    '''

    @property
    def actual_arg_type(self):
        return self._actual_arg_type

    @property
    def actual_arg(self):
        return self._actual_arg

    @property
    def did_convert(self):
        return self._did_convert

    @property
    def did_upcast(self):
        return self._did_upcast


    '''
    Conversions

    Some conversions (float array) require the production of a GValue right away.
    That might change.
    '''
    def convert(self, type_converter):
        ''' Convert result_type using given conversion method. '''

        '''
        It is not a requirement that the actual_arg_type is different from
        the type_converter type.
        Since the type_converter will do nothing in that case.
        But now, all callers insure the type IS different before they call.
        '''
        # TODO logger print(type_converter.__name__)

        # Usually the source construct is a literal such as "1" that might better be float literal "1.0"
        # Except for float array conversions?
        Suggest.say(f"converted {self._actual_arg_type.__name__} to {type_converter.__name__}.")

        self._result_arg = type_converter(self._actual_arg)  # type conversion
        self._result_arg_type = type(self._result_arg)
        self._did_convert = True

    '''
    To convert, pass built-in type converter method to self.convert()
    I.E. below is functional programming, passing a func as an arg.

    Note this often converts to a different Python type,
    and PyGObject subsequently converts to the appropriate GType.
    In upcast cases we convert the declared type to a GType.
    '''
    def float(self):
        self.convert(float)

    def str(self):
        self.convert(str)

    def int(self):
        self.convert(int)

    def unsigned_int(self):
        # Not a conversion, an upcast only?
        # TODO need to check for negative value?
        # Gimp.ParamUInt does not exist (to take its .__gtype__) so use a gtype directly
        # Failed names for gtypes: GLib.guint, GObject.G_TYPE_UINT, GObject.GType.G_TYPE_UNIT
        self.upcast(GObject.TYPE_UINT)

    def unsigned_char(self):
        # Not a conversion, an upcast only
        self.upcast(GObject.TYPE_UCHAR)


    def float_array(self):
        ''' Make self own a GValue holding a GimpFloatArray created from native list'''
        '''
        For now, use Gimp.value_set_float_array,
        which might be the only way to do it.
        But possibly there is a simpler implementation.
        '''
        # require self._actual_arg is-a sequence type

        # TODO use logger (">>>>>>>>>>Converting float list")

        # TODO not sure we need to float(), maybe PyGObject will do it
        #float_list = [float(item) for item in actual_arg]
        float_list = self._actual_arg

        try:
            self._gvalue = GObject.Value (Gimp.FloatArray.__gtype__)

            # PyGObject will convert using sequence and len(sequence)
            # Note that the previous arg (length) is still also passed to the PDB procedure
            Gimp.value_set_float_array(self._gvalue, float_list)
            self._did_create_gvalue = True
            self._did_convert = True

            # OLD result_gvalue = FuFloatArray.new_gimp_float_array_gvalue(float_list)
        except Exception as err:
            do_proceed_error(f"Failed to create Gimp.FloatArray: {err}.")

        # Cruft?
        #>>>>GimpFu continued past error: Exception in type conversion of: [1536, 0, 1536, 1984], type: <class 'list'>, index: 2
        #>>>>GimpFu continued past error: Creating GValue for type: <class 'list'>, value: [1536, 0, 1536, 1984], err: Must be GObject.GType, not type

        # This is not right, this is a type, not a GObject.type
        # result_arg_type = Gimp.GimpParamFloatArray


    def file_descriptor(self):
        assert isinstance(self._actual_arg, str)

        # create a GObject file descriptor
        try:
            gfile =  Gio.file_new_for_path(self._actual_arg)
        except Exception as err:
            do_proceed_error(f"Failed  Gio.file_new_for_path: {self._actual_arg}.")
        if gfile is None:
            do_proceed_error(f"Failed to create GFile for filename: {self._actual_arg}.")
        else:
            self._result_arg = gfile
            self._result_arg_type = Gio.File
            self._did_convert = True




    def color(self):
        ''' Convert result_arg to instance of type Gimp.RGB '''
        assert self._did_upcast

        RGB_result = GimpfuRGB.color_from_python_type(self._actual_arg)
        # assert RGB_result is-a Gimp.RGB or None
        if not RGB_result:
            # formal arg type is Gimp.RGB but could not convert actual_arg
            do_proceed_error(f"Not convertable to color: {self._actual_arg}.")
            self._did_convert = False
        else:
            self._result_arg = RGB_result
            self._result_arg_type = Gimp.RGB
            # assert result_type is-a GType
            self._did_convert = True
        # assert self._did_convert is True and (self.result_type is Gimp.RGB and self.result_arg is-a Gimp.RGB)
        # or (self._did_convert is False and self.result_arg is still None)


    '''
    upcasts
    '''

    def upcast(self, cast_to_type):
        '''
        Change result (type and value) to cast_to_type.
        The value is not converted.
        '''
        self._result_arg_type = cast_to_type
        self._result_arg = self._actual_arg
        self._did_upcast = True


    def upcast_to_None(self, cast_to_type):
        '''
        Cast to cast_to_type and change result to None (from e.g. -1).
        I.E. result is Null instance of the type.
        None is an instance of every type in some type systems.
        '''
        self.upcast(cast_to_type)
        self._result_arg = None
        assert self._did_upcast




    '''
    Utility.
    Here for lack of a better place for it.
    Not quite private.
    '''

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
        An exception is usually not caused by author, usually GimpFu programming error.
        Usually "Must be a GObject.GType, not a type"
        '''
        try:
            result = GObject.Value(gvalue_type, value)
        except Exception as err:
            do_proceed_error(f"Creating GValue for type: {gvalue_type}, value: {value}, err: {err}")
            # Return some bogus value so can proceed
            result = FuGenericValue.new_int_gvalue()
            # TODO would this work??
            # result = GObject.Value( GObject.TYPE_NONE, None )
        return result


    @staticmethod
    def new_int_gvalue():
        """ Return a gvalue of type INT and value 1. """
        return GObject.Value( GObject.TYPE_INT, 1 )

    @staticmethod
    def new_rgb_value():
        """ Return a gvalue of type Gimp.RGB and value black. """
        color = GimpfuRGB.color_from_python_type("black")
        return GObject.Value( Gimp.RGB, color )

    @staticmethod
    def new_procedure_gvalue():
        """ Return a gvalue of type Gimp.Procedure and value 1. """
        # ??? doesn't work, value must be a procedure?
        return GObject.Value( Gimp.Procedure, 1 )
