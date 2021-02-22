
import gi
from gi.repository import GObject

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp

# from gi.repository import GLib  # GLib.guint ???
from gi.repository import Gio   # Gio.File

from gimpfu.adapters.rgb import GimpfuRGB

from gimpfu.message.proceed import proceed
from gimpfu.message.suggest import Suggest

from gimpfu.adaption.formal_types import FormalTypes
from gimpfu.adaption.types import Types
from gimpfu.adaption.upcast import Upcast

from collections.abc import Sequence    # ABC for sequences
import logging



# TODO foo_type getters should be computed properties, not mutable

class FuGenericValue():
    '''
    A (type, value) that holds any ('generic') value.
    A thin class around GObject.Value aka the C GValue struct.

    Adapts Python types to GTypes.

    Stateful:
    Operations in this sequence:  init, apply conversions and upcasts, get_gvalue
    That is, initially the owned GValue is None.
    Then, any conversions/upcasts may set owned GValue.
    Finally, a call to get_gvalue will return the set owned GValue,
    or create a GValue to return.

    In type is a GType or Python type.
    Result type is also GType or Python type.
    Only get_gvalue definitely returns a GType.

    Responsible for:
    - performing conversions and Upcasts
    - produce a Gvalue

    Is not a singleton.
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

        self.logger = logging.getLogger("GimpFu.FuGenericValue")


    def __repr__(self):
        return ','.join((str(self.actual_arg), str(self._actual_arg_type),
                         str(self._result_arg), str(self._result_arg_type),
                         str(self._did_convert), str(self._did_upcast) ))

    # TODO rename getWrappedGValue
    def get_gvalue(self):
        '''
        Return Gimp.Value for original arg with all conversions and upcasts applied.
        '''
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

    # TODO combine these into one isCoherent()
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

    '''
    Conversions that are simple casts.

    The value stays the same, we just label the GValue with a different type.
    Assuming in some cases that GObject is also permissive,
    e.g. allowing any integer to represent a boolean
    (and not requiring only a binary 1 or 0)
    '''
    def boolean(self):
        self.upcast(GObject.TYPE_BOOLEAN)

    def unsigned_int(self):
        # Not a conversion, an upcast only?
        # TODO need to check for negative value?
        # Gimp.ParamUInt does not exist (to take its .__gtype__) so use a gtype directly
        # Failed names for gtypes: GLib.guint, GObject.G_TYPE_UINT, GObject.GType.G_TYPE_UNIT
        self.upcast(GObject.TYPE_UINT)

    def unsigned_char(self):
        # Not a conversion, an upcast only
        self.upcast(GObject.TYPE_UCHAR)


    """
    Utilities for conversion to gimp array
    """

    def is_tuple_or_list(self, obj):
        if isinstance(obj, str):
            # Python thinks a str is a sequence, but we treat it as a single item
            return False
        return isinstance(obj, Sequence)


    """
    The type of the container tells you what the type of the items should be,
    more or less,  e.g. GimpStringArray should contain strings.

    But GimpObjectArray only(?) means it should contain opaque i.e. boxed objects.
    That is, GimpObjectArray is in C an array of pointers.
    The pointed to objects can be of many types,
    e.g. Gimp.Layer *or* Gimp.Channel.

    libgimp's factory methods for Gimp<foo>Array *want* the contained type.
    I am not sure they actually *need* the contained type in all cases.
    Also not sure the factory methods are type checking items to ensure
    items *are* the contained type.

    In particular, for the case container_gtype is GimpObjectArray,
    it doesn't make any difference what the specific contained_gtype is,
    as long as it is some boxed type e.g. Gimp.Layer
    to ensure that an array of pointers is created.

    Also for all the cases where the container_gtype indicates
    contained_gtype is a fundamental type
    (e.g. GimpStringArray indicates contained_gtype is string),
    I am not sure we actually need to pass the correct contained_gtype
    to libgimp's factory method,
    since if the items are the corresponding Python type,
    PyGObject will do the right thing,
    and again, the factory method is not actually checking (or using at all?)
    the passed contained_gtype.

    container_gtype is the type of the container.
    GimpFu does not check that that contained items are gtype specified by
    container_gtype or contained_gtype_from.
    TODO type check or convert contained items.
    """
    def contained_gtype_from(self, container_gtype):
        """
        Return gtype that items of list SHOULD be as specified by to_container_gtype.
        """
        # TODO this is not right
        result = FormalTypes.contained_gtype_from_container_gtype(container_gtype)

        # FAIL: self.logger.info(f"Contained gtype.__gtype__ is: {contained_gtype.__gtype__}")
        # A GType does not have a GType? Or if it does, it is <GType>

        self.logger.debug(f"contained_gtype_from: {container_gtype.name} returns: {result.name}")
        # ensure result is a gtype or None ???
        return result

    # OLD
    # self.contained_gtype_from(to_container_gtype)
    # contained_gtype.name == "GBoxed":  # ??? "GimpObjectArray":

    def is_contained_gtype_a_boxed_type(self, container_gtype):
        return container_gtype.name == 'GimpObjectArray'


    def sequence_for_actual_arg(self):
        """
        Return sequence from self.actual_arg.

        self.actual_arg might already be a list, possibly empty.
        Else contain self.actual_arg in a non-empty list.
        """
        if self.is_tuple_or_list(self._actual_arg):
            # already a list
            result = self._actual_arg
            # could be empty list
        else:
            # an item, contain it
            result = [self._actual_arg,]
            assert(len(result)>0)

        # items in list might still be wrapped
        assert isinstance(result, Sequence)
        return result


    """
    For now, use Gimp.value_set_<foo>_array factory methods.
    That might be the only way, or maybe is a simpler implementation.
    """
    def to_gimp_array(self, to_container_gtype, gvalue_setter, is_setter_take_contained_type=False ):
        """
        Make self's GValue hold a Gimp<foo>Array
        where <foo> is determined by to_container_gtype,
        and contents are from self.actual_arg.

        self.actual_arg can be a single item *or* Python native sequences.
        GimpFu allows Author to pass an item where
        the called PDB procedure expects an array.
        Contain item in a list and then to to_container_gtype.

        gvalue_setter is a method of Gimp e.g. Gimp.value_set_object_array.

        One setter (Gimp.value_set_object_array) has extra arg: contained_gtype.
        """
        self.logger.info(f"to_gimp_array type: {to_container_gtype}")
        #self.logger.info(f"to_gimp_array type of type: {type(to_container_gtype)}")
        # prints: <class 'gobject.GType'>
        #print(dir(to_container_gtype))
        #print(dir(GObject.GType))
        #foo =GObject.GType.from_name("GimpObjectArray")
        #self.logger.info(f"to_gimp_array type of type: {type(foo)}")

        # require a list to create an array
        try:
            list = self.sequence_for_actual_arg()
        except Exception as err:
            proceed(f"Exception in sequence_for_actual_arg: _actual_arg: {self._actual_arg}, {err}")

        """
        assert list is-a list, but is empty, or items are wrapped or fundamental types
        But we don't know much about the contained items.
        (They were passed as arguments by Author.)
        Could be:
           wrapped GObjects
           ??? unwrapped GObjects (responds to .__gtype__)
           fundamental types
        """

        # setter i.e. factory method needs gtype of contained items.
        # hack
        # use any GIMP boxed type, setter doesn't actually use it???
        # TEMP This works but is not general
        # it works only when testing GimpObjectArray
        contained_gtype = Gimp.Item.__gtype__


        # setter requires fundamental or GIMP types, not GimpFu wrapped types
        from gimpfu.adaption.marshal import Marshal
        if self.is_contained_gtype_a_boxed_type(to_container_gtype):
            # Each item should be wrapped, how could it not be???
            # But unwrap_homogenous_sequence doesn't require it.
            # unwrap_homogenous_sequence does check each item is same unwrapped type
            list = Marshal.unwrap_homogenous_sequence(list)
        # else list elements are fundamental types

        """
        assert list is one of:
        - empty
        - contains unwrapped Gimp types
        - fundamental types
        - fundamental types that can be converted to Gimp types (e.g. RGB)
        """

        if to_container_gtype.name == 'GimpRGBArray':
            list = GimpfuRGB.colors_from_list_of_python_type(list)
            # assert list is now a list of Gimp.RGB

        # Require a GObject.Value to holds a boxed Gimp type
        try:
            # create empty (i.e. no value) GValue of desired type,
            self._gvalue = GObject.Value (to_container_gtype)
            # Maybe ??? self._gvalue = GObject.Value (GObject.GBoxed)
        except Exception as err:
            proceed(f"Fail to create GObject.Value for array: {err}.")


        try:
            """
            Invoke Gimp's setter to set value into GValue.
            Invoking via GI i.e. gvalue_setter is-a callable.

            We are calling e.g. Gimp.value_set_object_array()
            whose C signature is like (...len, array...)
            PyGObject will convert "list" to  "len(list), array"

            Elsewhere, the length is also passed to a PDB procedure
            since the PDB API is C-like, not Python-like.

            Fail: Gimp.value_set_object_array(self._gvalue, len(list), list)
            """
            if is_setter_take_contained_type:
                # Fail GObject.Type.ensure(GimpObjectArray)
                # Fail GObject.GType.is_a(Gimp.ObjectArray)
                self.logger.debug(f"Setting array of type: {to_container_gtype.name}, contained_gtype: {contained_gtype}")
                # !!! Must pass a __gtype__, not a Python type
                # assert contained_gtype is-a GObject.GType
                assert isinstance(contained_gtype, GObject.GType)
                gvalue_setter(self._gvalue, contained_gtype, list)
                #foo = self._gvalue.get_boxed() # Gvalue should hold a boxed type
                #print(foo.__gtype__ )
            else:
                self.logger.debug(f"Setting array of type: {to_container_gtype.name}")
                gvalue_setter(self._gvalue, list)
            self._did_create_gvalue = True
            self._did_convert = True

        except Exception as err:
            proceed(f"Fail to_gimp_array: {to_container_gtype.name}: {err}.")




    def to_object_array(self):
        """ Make self own a GValue holding a GimpObjectArray """
        self.to_gimp_array(Gimp.ObjectArray.__gtype__,
                           Gimp.value_set_object_array,
                           is_setter_take_contained_type = True)

    def to_float_array(self):
        """ Make self's GValue hold a GimpFloatArray created from self.actual_arg"""
        self.to_gimp_array(Gimp.FloatArray.__gtype__, Gimp.value_set_float_array )

    def to_string_array(self):
        """ Make self's GValue hold a GimpStringArray created from self.actual_arg"""
        self.to_gimp_array(Gimp.StringArray.__gtype__, Gimp.value_set_string_array )

    def to_uint8_array(self):
        """ Make self's GValue hold a GimpUint8Array created from self.actual_arg"""
        self.to_gimp_array(Gimp.Uint8Array.__gtype__, Gimp.value_set_uint8_array )

    def to_int32_array(self):
        """ Make self's GValue hold a GimpInt32Array created from self.actual_arg"""
        self.to_gimp_array(Gimp.Int32Array.__gtype__, Gimp.value_set_int32_array )

    def to_color_array(self):
        """ Make self's GValue hold a GimpRGBArray created from self.actual_arg"""
        self.to_gimp_array(Gimp.RGBArray.__gtype__, Gimp.value_set_rgb_array )


        # Cruft?
        #>>>>GimpFu continued past error: Exception in type conversion of: [1536, 0, 1536, 1984], type: <class 'list'>, index: 2
        #>>>>GimpFu continued past error: Creating GValue for type: <class 'list'>, value: [1536, 0, 1536, 1984], err: Must be GObject.GType, not type

        # This is not right, this is a type, not a GObject.type
        # result_arg_type = Gimp.GimpParamFloatArray


    def to_file_descriptor(self):
        """ try convert self.actual_arg from string to Gio.File """
        assert isinstance(self._actual_arg, str)

        try:
            gfile =  Gio.file_new_for_path(self._actual_arg)
        except Exception as err:
            proceed(f"Failed  Gio.file_new_for_path: {self._actual_arg}.")
        if gfile is None:
            proceed(f"Failed to create GFile for filename: {self._actual_arg}.")
        else:
            self._result_arg = gfile
            self._result_arg_type = Gio.File
            self._did_convert = True


    def to_color(self):
        ''' Try convert self.actual_arg to type Gimp.RGB '''
        assert self._did_upcast

        RGB_result = GimpfuRGB.color_from_python_type(self._actual_arg)
        # assert RGB_result is-a Gimp.RGB or None
        if not RGB_result:
            # formal arg type is Gimp.RGB but could not convert actual_arg
            proceed(f"Not convertable to color: {self._actual_arg}.")
            self._did_convert = False
        else:
            self._result_arg = RGB_result
            self._result_arg_type = Gimp.RGB
            # assert result_type is-a GType
            self._did_convert = True
        # assert self._did_convert is True and (self.result_type is Gimp.RGB and self.result_arg is-a Gimp.RGB)
        # or (self._did_convert is False and self.result_arg is still None)


    '''
    upcasts.
    See also adaption/upcast.py Upcast
    '''

    def upcast(self, cast_to_type):
        '''
        Change result (type and value) to cast_to_type.
        The value is not converted.
        '''
        self._result_arg_type = cast_to_type
        self._result_arg = self._actual_arg
        self._did_upcast = True
        self.logger.info(f"upcast: {cast_to_type}")


    def upcast_to_None(self, cast_to_type):
        '''
        Cast to cast_to_type and change result to None (from e.g. -1).
        I.E. result is Null instance of the type.
        None is an instance of every type in some type systems.
        '''
        self.upcast(cast_to_type)
        self._result_arg = None
        assert self._did_upcast



    def tryConversionsAndUpcasts(self, formalArgType):
        '''
        Try convert or upcast self to formalArgType.

        Any upcast or conversion is the sole upcast or conversion (return early.)
        But an upcast may also internally convert.
        We don't upcast and also convert in this list.

        The order is not important as we only expect one upcast or convert.

        Try a sequence of upcasts and conversions.
        TODO just get the formal argument type and dispatch on it???
        I.E. invert this logic.
        '''

        Upcast.try_gimp_upcasts(formalArgType, self)
        if self.did_upcast:
            return

        # TODO do this first because it shortcuts coherent types
        # TODO rename try_usual_python_conversion_and_upcast
        Types.try_usual_python_conversion(formalArgType, self)
        if self.did_convert or self.did_upcast:
            return

        Types.try_array_conversions(formalArgType, self)
        if self.did_convert:
            return

        Types.try_file_descriptor_conversion(formalArgType, self)

        # !!! We don't upcast deprecated constant TRUE to G_TYPE_BOOLEAN

        # TODO is this necessary? I think it is only drawable that gets passed None
        # Types.try_convert_to_null(proc_name, self)


    '''
    Utility.
    Here for lack of a better place for it.
    Not quite private.
    TODO move this
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
            proceed(f"Creating GValue for type: {gvalue_type}, value: {value}, err: {err}")
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
