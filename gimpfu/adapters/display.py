import gi
gi.require_version("Gimp", "3.0")
from gi.repository import Gimp

from adapters.adapter import Adapter

from message.proceed_error import *



class GimpfuDisplay( Adapter) :

    """
    Has no properties, or dynamic adapted properties,
    and inherits dynamic adapted properties from Adapter.
    """

    def __init__(self, img=None, name=None, width=None, height=None, type=None, opacity=None, layer_mode=None, adaptee=None):

        if img is not None:
            # Totally new adaptee, created at behest of author
            # Gimp constructor named "new"
            super().__init__( Gimp.Display.new(img.unwrap()))
        else:
            # Create wrapper for existing adaptee (from Gimp)
            # Adaptee was created earlier at behest of Gimp user and is being passed into GimpFu plugin
            # Rarely does Gimp pass a Display to a plugin?
            # But not inconceivable that one plugin passes a Display to another.
            assert adaptee is not None
            super().__init__(adaptee)

        # super Adaptor logs this




    '''
    Methods for convenience.
    '''

    '''
    Override superclass Adapter.copy()
    Displays should not be copied.
    '''
    def copy(self):
        do_proceed_error("Cannot copy Display")
        return None
