
# import wrapper classes
from gimpfu_image import GimpfuImage
from gimpfu_layer import GimpfuLayer


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
