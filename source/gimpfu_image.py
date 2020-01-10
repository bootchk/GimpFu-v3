

import gi
gi.require_version("Gimp", "3.0")
from gi.repository import Gimp




'''

Wraps Gimp.Image.

Constructor appears in GimpFu plugin code as e.g. : gimp.Image(w, h, RGB)
I.E. an attribute of gimp instance.

In PyGimp v2, similar concept implemented by pygimp-image.c
Since v3, implemented in Python using GI.

An adaptor.

Method kinds:
Most have an identical signature method in Gimp.Image. (delegated)
Some have changed signature here, but same action as in Gimp.Image. (convenience)
Some are unique to PyGimp, not present in Gimp.Image. (augment)
    - methods
    - properties (data members)
    TODO do we need to wrap property get/set

'''

class GimpfuImage( Gimp.Image) :

    def __init__(self, width, height, image_mode):
        # delegate to super with changed method name "new"
        super.new(width, height, image_mode)

    def insert_layer(self, layer):
        print("insert_layer called")
        position = 1  #TODO
        # TODO layer unwrap?
        super.insert_layer(self, layer, -1, position)
