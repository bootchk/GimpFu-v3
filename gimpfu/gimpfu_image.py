

import gi
gi.require_version("Gimp", "3.0")
from gi.repository import Gimp

from adapter import Adapter


'''

Adapts (wraps) Gimp.Image.

Constructor appears in GimpFu plugin code as e.g. : gimp.Image(w, h, RGB)
I.E. an attribute of gimp instance (see gimpfu_gimp.py.)

In PyGimp v2, similar concept implemented by pygimp-image.c
Since v3, implemented in Python using GI.

Method kinds:
Most have an identical signature method in Gimp.Image. (delegated)
Some have changed signature here, but same action as in Gimp.Image. (convenience)
Some are unique to PyGimp, not present in Gimp.Image. (augment)
    - methods
    - properties (data members)
    TODO do we need to wrap property get/set
'''






class GimpfuImage( Adapter ) :

    '''
    See SO "How to overload __init__ method based on argument type?"
    '''
    # Constructor exported to Gimpfu authors
    # Called internally for existing images as GimpfuImage(None, None, None, adaptee)
    def __init__(self, width=None, height=None, image_mode=None, adaptee=None):
        '''Initialize  GimpfuImage from attribute values OR instance of Gimp.Image. '''
        if width is None:
            final_adaptee = adaptee
        else:
            # Gimp constructor named "new"
            final_adaptee = Gimp.Image.new(width, height, image_mode)
        super().__init__(final_adaptee)

    '''
    WIP
    Overload constructors using class methods.
    # Hidden constructor
    @classmethod
    def fromAdaptee(cls, adaptee):
         "Initialize GimpfuImage from attribute values"

         return cls(data
    '''


    # Methods we specialize


    # Special: allow optional args
    def insert_layer(self, layer, parent=None, position=-1):
        print("insert_layer called")

        # Note that first arg to Gimp comes from self
        success = self._adaptee.insert_layer(layer.unwrap(), parent, position)
        if not success:
            raise Exception("Failed insert_layer")



    # Properties we specialize
    # In fact GI Gimp does not have property semantics?


    @property
    def layers(self):
        # avoid circular import, import when needed
        from gimpfu_marshal import Marshal

        '''
        Override:
        - to insure returned objects are wrapped ???
        - because the Gimp name is get_layers

        Typical use by authors: position=img.layers.index(drawable) + 1
        And then the result goes out of scope quickly.
        But note that the wrapped item in the list
        won't be equal to other wrappers of the same Gimp.Layer
        UNLESS we also override equality operator for wrapper.

        !!! If you break this, the error is "AttributeError: Image has no attr layers"
        '''
        print("layers property accessed")
        layer_list = self._adaptee.get_layers()
        result_list = []
        for layer in layer_list:
            # rebind item in list
            result_list.append(Marshal.wrap(layer))
        print("layers property returns ", result_list)
        return result_list

    # No layers setter


    @property
    def active_layer(self):
        # Delegate to Gimp.Image
        # TODO wrap result or lazy wrap
        return self._adaptee.get_active_layer()

    @active_layer.setter
    def active_layer(self, layer):
        # TODO:
        raise RuntimeError("not implemented")

    @property
    def base_type(self):
        # Delegate to Gimp.Image
        # Result is fundamental type (enum int)
        return self._adaptee.base_type()
