
import gi
from gi.repository import GObject

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp

#from gi.repository import GLib  # GLib.VariantType  GLib.guint ???
#from gi.repository import Gio   # Gio.File

from gimpfu.adapters.rgb import GimpfuRGB

from gimpfu.message.proceed import proceed
#from gimpfu.message.suggest import Suggest

from gimpfu.adaption.formal_types import FormalTypes
#from gimpfu.adaption.types import Types
#from gimpfu.adaption.upcast import Upcast

from collections.abc import Sequence    # ABC for sequences
import logging



# TODO foo_type getters should be computed properties, not mutable

class FuGenericValueArray():
    '''
    A class that understands arrays, for FuGenericValue.

    A singleton class, no instances.
    '''

    logger = logging.getLogger("GimpFu.FuGenericValueArray")


    """
    Utilities for conversion to gimp array
    """

    @staticmethod
    def is_tuple_or_list(obj):
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
    @classmethod
    def contained_gtype_from(cls, container_gtype):
        """
        Return gtype that items of list SHOULD be as specified by to_container_gtype.
        """
        # TODO this is not right
        result = FormalTypes.contained_gtype_from_container_gtype(container_gtype)

        # FAIL: logger.info(f"Contained gtype.__gtype__ is: {contained_gtype.__gtype__}")
        # A GType does not have a GType? Or if it does, it is <GType>

        cls.logger.debug(f"contained_gtype_from: {container_gtype.name} returns: {result.name}")
        # ensure result is a gtype or None ???
        return result

    # OLD
    # self.contained_gtype_from(to_container_gtype)
    # contained_gtype.name == "GBoxed":  # ??? "GimpObjectArray":


    @staticmethod
    def is_contained_gtype_a_gimp_type(container_gtype):
        return container_gtype.name == 'GimpObjectArray'

    @staticmethod
    def is_contained_gtype_a_RGB_type(container_gtype):
        return container_gtype.name == 'GimpRGBArray'




    @staticmethod
    def sequence_for_actual_arg(actual_arg):
        """
        Return sequence from actual_arg.

        actual_arg might already be a list, possibly empty.
        Else contain actual_arg in a non-empty list.
        """
        if FuGenericValueArray.is_tuple_or_list(actual_arg):
            # already a list
            result = actual_arg
            # could be empty list
        else:
            # an item, contain it
            result = [actual_arg,]
            assert(len(result)>0)

        # items in list might still be wrapped
        assert isinstance(result, Sequence)
        return result


    @staticmethod
    def martial_list_to_bindable_types(raw_list, to_container_gtype):
        """
        Return a list whose any elements are:
        - fundamental types
        - or Gimp types unwrapped from GimpFu wrappers
        - or Gimp types fabricated from fundamental Python types (e.g. RGB)
        """

        # return raw_list when no other cases apply
        list = raw_list

        # unwrap GimpFu wrapped types
        from gimpfu.adaption.marshal import Marshal
        if FuGenericValueArray.is_contained_gtype_a_gimp_type(to_container_gtype):
            # Each item should be wrapped, how could it not be???
            # But unwrap_homogenous_sequence doesn't require it.
            # unwrap_homogenous_sequence does check each item is same unwrapped type
            list = Marshal.unwrap_homogenous_sequence(raw_list)
        # else list elements are fundamental types

        # fabricate Gimp types from fundamental types
        if FuGenericValueArray.is_contained_gtype_a_RGB_type(to_container_gtype):
            list = GimpfuRGB.colors_from_list_of_python_type(raw_list)
            # assert list is now a list of Gimp.RGB

        return list


    """
    For now, use Gimp.value_set_<foo>_array factory methods.
    That might be the only way, or maybe is a simpler implementation.
    """
    @classmethod
    def to_gimp_array(cls, actual_arg, to_container_gtype, gvalue_setter, is_setter_take_contained_type=False ):
        """
        Return GValue holding a Gimp<foo>Array
        where <foo> is determined by to_container_gtype,
        and contents are from actual_arg.

        actual_arg can be a single item *or* Python native sequences.
        GimpFu allows Author to pass an item where
        the called PDB procedure expects an array.
        Contain item in a list and then to to_container_gtype.

        gvalue_setter is a method of Gimp e.g. Gimp.value_set_object_array.

        One setter (Gimp.value_set_object_array) has extra arg: contained_gtype.
        """
        cls.logger.info(f"to_gimp_array type: {to_container_gtype}")
        #logger.info(f"to_gimp_array type of type: {type(to_container_gtype)}")
        # prints: <class 'gobject.GType'>
        #print(dir(to_container_gtype))
        #print(dir(GObject.GType))
        #foo =GObject.GType.from_name("GimpObjectArray")
        #logger.info(f"to_gimp_array type of type: {type(foo)}")

        # require a list to create an array
        try:
            list = FuGenericValueArray.sequence_for_actual_arg(actual_arg)
        except Exception as err:
            proceed(f"Exception in sequence_for_actual_arg: _actual_arg: {actual_arg}, {err}")

        # setter i.e. factory method needs gtype of contained items.
        # hack
        # use any GIMP boxed type, setter doesn't actually use it???
        # TEMP This works but is not general
        # it works only when testing GimpObjectArray
        contained_gtype = Gimp.Item.__gtype__

        # Create GObject.Value of the given to_container_gtype
        try:
            # create empty (i.e. no value) GValue of desired type,
            gvalue = GObject.Value (to_container_gtype)
        except Exception as err:
            proceed(f"Fail to create GObject.Value for array, err is: {err}.")

        """
        assert list is-a list, but is empty, or items are wrapped or fundamental types
        But we don't know much about the contained items.
        (They were passed as arguments by Author.)
        Could be:
           GimpFu wrapped GObjects
           ??? unwrapped GObjects (responds to .__gtype__)
           fundamental types
        """
        list = FuGenericValueArray.martial_list_to_bindable_types(list, to_container_gtype)

        try:
            """
            Invoke setter to set value into GValue.
            Invoking via GI i.e. gvalue_setter is-a callable.
            For Gimp array types, setter is a method on Gimp.
            For other array types, setter is ???

            We are calling e.g. Gimp.value_set_object_array()
            whose C signature is like (...len, array...)
            PyGObject will convert "list" to  "len(list), array"
            Fail: Gimp.value_set_object_array(gvalue, len(list), list)

            Elsewhere, the length is also passed to a PDB procedure
            since the PDB API is C-like, not Python-like.
            """

            # Some arrays want to know the contained type.
            if is_setter_take_contained_type:
                # Fail GObject.Type.ensure(GimpObjectArray)
                # Fail GObject.GType.is_a(Gimp.ObjectArray)
                cls.logger.debug(f"Setting array of type: {to_container_gtype.name}, contained_gtype: {contained_gtype}")
                # !!! Must pass a __gtype__, not a Python type
                # assert contained_gtype is-a GObject.GType
                assert isinstance(contained_gtype, GObject.GType)
                gvalue_setter(gvalue, contained_gtype, list)
                #foo = _gvalue.get_boxed() # Gvalue should hold a boxed type
                #print(foo.__gtype__ )
            else:
                cls.logger.debug(f"Setting array of type: {to_container_gtype.name}")
                gvalue_setter(gvalue, list)

        except Exception as err:
            proceed(f"Fail to_gimp_array: {to_container_gtype.name}: {err}.")

        return gvalue



    '''
    OLD
    def to_string_array(self):
       """ Make self's GValue hold a GimpStringArray created from self.actual_arg"""
       self.to_gimp_array(Gimp.StringArray.__gtype__, Gimp.value_set_string_array )
    '''

    @classmethod
    def to_string_array(cls, actual_arg):
        """ Return GValue holding instance of type GStrv created from actual_arg """
        # Fail: GStrv is not a GType, only a C typedef.
        # Fail: GObject.TYPE_BOXED, cannot initialize GValue with type 'GBoxed', this type has no GTypeValueTable implementation
        # Fail: GLib.VariantType
        # G_TYPE_STRV
        # Setter is not a GIMP method, but a method of GObject.Value
        # See GObject>Structures>Value
        # Fail: self.to_gimp_array(GObject.TYPE_STRV, GObject.Value.set_boxed )
        # Fail: gvalue = FuGenericValueArray.to_gimp_array(actual_arg, GObject.TYPE_STRV, GObject.Value.set_variant )

        cls.logger.info(f"to_string_array")
        # require a sequence
        try:
           list = FuGenericValueArray.sequence_for_actual_arg(actual_arg)
        except Exception as err:
           proceed(f"Exception in sequence_for_actual_arg: _actual_arg: {actual_arg}, {err}")

        # Create GObject.Value
        try:
            # create empty (i.e. no value) GValue of desired type,
            gvalue = GObject.Value (GObject.TYPE_STRV)
        except Exception as err:
            proceed(f"Fail to create GObject.Value for array, err is: {err}.")

        # GObject.GStrv is not a class?  Create instance from Python list.
        # Code lifted from PyGObject/tests/test_properties.property
        class GStrv(list):
            __gtype__ = GObject.TYPE_STRV

        GStrv(list)

        # put instance in the gvalue.
        GObject.Value.set_boxed(gstrv)

        return gvalue
