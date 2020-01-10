

import gi
gi.require_version("Gimp", "3.0")
from gi.repository import Gimp




'''
see comments at gimpfu_image, which is very similar
'''




# TODO how do we make instances appear to be the type of the adaptee
# when passed as args to Gimp?????

class GimpfuLayer( ) :

    def __init__(self, width, height, image_mode):
        # adaptee has constructor name "new"
        self._adaptee = Gimp.Layer.new(width, height, image_mode)


    # Methods we specialize

    def insert_layer(self, layer):
        print("insert_layer called")
        # additional args
        position = 1  #TODO
        # TODO layer unwrap?
        # TODO self is not a Gimp type.  v2 used an ID??
        self._adaptee.insert_layer(self, layer, -1, position)


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
