

import gi
gi.require_version("Gimp", "3.0")
from gi.repository import Gimp




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

'''
class adapter vs object adapter

Object adapter: does not inherit Gimp.Image, but owns an instance of it
Class adapter: multiple inheritance
TODO which do we need?
'''


# TODO how do we make instances appear to be the type of the adaptee
# when passed as args to Gimp?????

class GimpfuImage( ) :

    def __init__(self, width, height, image_mode):
        # adaptee has constructor name "new"
        self._adaptee = Gimp.Image.new(width, height, image_mode)

    def unwrap(self):
        ''' Return inner object of a Gimp type, when passing arg to Gimp'''
        return self._adaptee


    # Methods we specialize

    def insert_layer(self, layer, parent=None, position=-1):
        print("insert_layer called")

        # Note that first arg to Gimp comes from self
        success = self._adaptee.insert_layer(layer.unwrap(), parent, position)
        if not success:
            raise Exception("Failed insert_layer")

    # Properties

    @property
    def active_layer(self):
        # Delegate to Gimp.Image
        # TODO wrap it?
        return self._adaptee.get_active_layer()

    @active_layer.setter
    def active_layer(self, layer):
        # TODO:
        print("active_layer setter TODO")


    # Methods and properties offered dynamically.
    # __getattr__ is only called for methods not found on self

    def __getattr__(self, name):
        # when name is callable, soon to be called
        # when name is data member, returns value
        return getattr(self.__dict__['_adaptee'], name)


    def __setattr__(self, name, value):
        if name in ('_adaptee',):
            self.__dict__[name] = value
        else:
            setattr(self.__dict__['_adaptee'], name, value)

    def __delattr__(self, name):
        delattr(self.__dict__['_adaptee'], name)
