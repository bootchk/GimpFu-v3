
import gi
gi.require_version("Gimp", "3.0")
from gi.repository import Gimp

# !!! Channel => Drawable => Item => Adapter
from gimpfu.adapters.drawable import GimpfuDrawable



"""
Notes:

opacity is property of Layer and Channel, not of the superclass Drawable.

color and show_masked are unique to Channel

name inherited from item
width, height inherited from drawable

TODO GimpFu v2 had property "visible" and "layer_mask"
"""

class GimpfuChannel( GimpfuDrawable ) :

    @classmethod
    def DynamicWriteableAdaptedProperties(cls):
        return ('color', 'show_masked', 'opacity' ) + super().DynamicWriteableAdaptedProperties()

    @classmethod
    def DynamicReadOnlyAdaptedProperties(cls):
        return tuple() + super().DynamicReadOnlyAdaptedProperties()

    # DynamicTrueAdaptedTrueProperties() inherited from GimpfuDrawable


    def __init__(self, img=None, name=None, width=None, height=None, opacity=None, color=None, adaptee=None):

        if img is not None:
            # Totally new adaptee, created at behest of author
            # Gimp constructor named "new"
            super().__init__( Gimp.Channel.new(img.unwrap(), name, width, height, opacity, color) )
        else:
            # Create wrapper for existing adaptee (from Gimp)
            # Adaptee was created earlier at behest of Gimp user and is being passed into GimpFu plugin
            assert adaptee is not None
            super().__init__(adaptee)

        # super Adapter does logging of __init__

        # !!! Any assign to attributes must use __setattr__ to avoid adaption pattern recursion





    '''
    Methods for convenience.
    i.e. these were defined in PyGimp v2

    They specialize methods that might exist in Gimp.
    Specializations:
    - add convenience parameters
    - alias or rename: old name => new or simpler name
    - encapsulate: one call => many subroutines

    see other examples  adapters.image.py
    '''

    # GimpFu v2 provided Channel.copy
    def copy(self, alpha=False):
        ''' Return copy of self. '''
        '''
        FBC Param "alpha" is convenience, on top of Gimp.Layer.copy()

        !!! TODO alpha not used.  Code to add alpha if "alpha" param is true??
        The docs are not clear about what the param means.
        If it means "add alpha", should rename it should_add_alpha
        '''
        # delegate to adapter
        return super().copy()
        # If this class had any data members, we would need to copy their values also





    '''
    Properties.

    For convenience, GimpFu makes certain attributes have property semantics.
    I.E. get without parenthesises, and set by assignment, without calling setter() func.

    Properties that are canonically (with get_foo, and set_foo) implemented by Adaptee Gimp.Layer
    are handled aby Adaptor.

    TODO, does Gimp GI provide properties?
    '''
