
# import wrapper classes
from gimpfu_image import GimpfuImage
from gimpfu_layer import GimpfuLayer

from gimpfu_compatibility import Compat



class Marshal():
    '''
    Knows how to wrap Gimp GObjects.

    But each wrapped object has an unwrap method to return its adaptee.

    Hides multiple constructors for wrappers.

    Each wrapper also knows how to create a wrapper for a new'd Gimp GObject
    '''

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
