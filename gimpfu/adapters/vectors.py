import gi
gi.require_version("Gimp", "3.0")
from gi.repository import Gimp

# !!! Vectors => Drawable => Item => Adapter
from adapters.drawable import GimpfuDrawable





class GimpfuVectors( GimpfuDrawable ) :

    '''
    Notes on dynamic adapted properties: all inherited from super
    "name" inherited from GimpfuItem
    '''


    def __init__(self, img=None, name=None, adaptee=None):

        # Require (img, name) not None, or adaptee not None

        if img is not None:
            # Totally new adaptee, created at behest of author
            # Gimp constructor named "new", takes two params
            assert name is not None, "gimp.Vectors() called without a name parameter."
            super().__init__( Gimp.Vectors.new(img.unwrap(), name ) )
        else:
            # Create wrapper for existing adaptee (from Gimp)
            # Adaptee was created earlier at behest of Gimp user and is being passed into GimpFu plugin
            assert adaptee is not None, "gimp.Vectors() called with invalid parameters."
            super().__init__(adaptee)

        # super logs this




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


    # copy is inherited

    def to_selection(self):
        raise RuntimeError("Obsolete: use image.select_item()")
