
import gi
gi.require_version("Gimp", "3.0")
from gi.repository import Gimp

# !!! Layer => Drawable => Item => Adapter
from gimpfu.adapters.drawable import GimpfuDrawable

from gimpfu.adapters.adapter_logger import AdapterLogger





class GimpfuLayer( GimpfuDrawable ) :

    @classmethod
    def DynamicWriteableAdaptedProperties(cls):
        return ('mode', 'lock_alpha', 'opacity' ) + super().DynamicWriteableAdaptedProperties()

    @classmethod
    def DynamicReadOnlyAdaptedProperties(cls):
        return ('mask', ) + super().DynamicReadOnlyAdaptedProperties()

    # DynamicTrueAdaptedTrueProperties() inherited from GimpfuDrawable

    '''
    Notes on properties:
    name inherited from item
    mask is a layer mask, has remove_mask() but not set_mask() but some set_<foo>_mask() ???
    '''


    def __init__(self, img=None, name=None, width=None, height=None,
                # Reasonable defaults from Gimp, since GimpFu enums not in scope
                type=Gimp.ImageType.RGB_IMAGE,
                opacity=100,
                layer_mode=Gimp.LayerMode.NORMAL,
                adaptee=None):
        if img is not None:
            # Totally new adaptee, created at behest of author
            # Gimp constructor named "new"
            AdapterLogger.logger.debug(f"Call Gimp.Layer.new( {img}, {width}, {height}, {type}, {opacity}, {layer_mode} )")
            super().__init__( Gimp.Layer.new(img.unwrap(), name, width, height, type, opacity, layer_mode) )
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
