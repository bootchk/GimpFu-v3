
import gi
gi.require_version("Gimp", "3.0")
from gi.repository import Gimp

from adaption.wrappable import *    # is_subclass_of_type

import logging



class Upcast():
    """
    Calls to Gimp understand class hierarchy and accept subclass instances where formal type is superclass.
    Calls to PDB do not; instead GimpFu must upcast.

    Upcast: declare the type of a suclass instance to be the type of a superclass.

    Here we are dealing with GValues.  To upcast, we change the type declared in first field of GValue, the type field.
    The value field of the GValue is unchanged.
    """

    logger = logging.getLogger("GimpFu.Upcast")

    @staticmethod
    def try_gimp_upcasts(formal_arg_type, gen_value, index):
        """
        Try the upcasts required by Gimp PDB.
        """
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



    @staticmethod
    def _try_to_type(formal_arg_type, gen_value, index, cast_to_type):
        '''
        When gen_value.actual_arg_type is subclass of cast_to_type
        and procedure has signature with formal_arg_type at index (proc expects cast_to_type at index)
        return cast_to_type, else return original type.
        Does not actually change type i.e. no conversion, just casting.

        Require gen_value a GObject (not wrapped).
        Require formal_arg_type is-a GType.
        '''
        # assert type is like Gimp.Drawable, cast_to_type has name like Drawable

        Upcast.logger.info(f"Attempt upcast: {gen_value.actual_arg_type} to : {cast_to_type.__name__}")

        from adaption.types import Types

        if Types._should_upcast_or_convert(gen_value.actual_arg_type, formal_arg_type, cast_to_type):
            if is_subclass_of_type(gen_value.actual_arg, cast_to_type):
                gen_value.upcast(cast_to_type)
            elif gen_value.actual_arg == -1:
                # v2 allowed -1 as arg for optional drawables
                # # !!! convert arg given by Author
                gen_value.upcast_to_None(cast_to_type)
            elif gen_value.actual_arg is None:
                # TODO migrate to create_nonetype_drawable or create_none_for_type(type)
                # Gimp wants GValue( Gimp.Drawable, None), apparently
                # This does not work: result = -1
                # But we can upcast NoneType, None is in every type???
                gen_value.upcast(cast_to_type)
            else:
                # Note case Drawable == Drawable will get here, but Author cannot create instance of Drawable.
                proceed(f"Require type: {formal_arg_type} , but got {gen_value} not castable.")

        else:
            # No upcast was done
            pass

        # assert result_type is-a type (a Gimp type, a GObject type)
        Upcast.logger.info(f"_try_to_type returns FuGenericValue: {gen_value}")


    # TODO replace this with data driven single procedure
    @staticmethod
    def try_to_drawable(formal_arg_type, gen_value, index):
        Upcast._try_to_type(formal_arg_type, gen_value, index, Gimp.Drawable)

    @staticmethod
    def try_to_item(formal_arg_type, gen_value, index):
        Upcast._try_to_type(formal_arg_type, gen_value, index, Gimp.Item)

    @staticmethod
    def try_to_layer(formal_arg_type, gen_value, index):
        Upcast._try_to_type(formal_arg_type, gen_value, index, Gimp.Layer)

    @staticmethod
    def try_to_color(formal_arg_type, gen_value, index):
        Upcast._try_to_type(formal_arg_type, gen_value, index, Gimp.RGB)
        if gen_value.did_upcast:
            # also convert value
            try:
                to_color()
            except Exception as err:
                proceed(f"Converting to color: {err}")
            #Upcast.logger.info(type(result))
