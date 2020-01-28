
import gi
gi.require_version("Gimp", "3.0")
from gi.repository import Gimp


from item import GimpfuItem



'''
Not instantiable by itself, only inheritable.
No GimpFu plugin author should/can use "Item.foo"
In other words, private to GimpFu
'''


class GimpfuDrawable( GimpfuItem ) :
    '''
    GimpFu convenience methods.
    E.G. alias Gimp methods, etc.

    Attributes common to subclasses Layer and Channel
    '''


    '''
    methods
    '''




    '''
    Properties
    '''


    '''
    Simple adaption of callable to property, without renaming.
    '''
    @property
    def height(self):
        return self._adaptee.height()

    @property
    def width(self):
        return self._adaptee.width()

    @property
    def has_alpha(self):
        return self._adaptee.has_alpha()

    @property
    def is_rgb(self):
        return self._adaptee.is_rgb()




    @property
    def mask_bounds(self):
        #print("Calling Foo.get_name(): ")
        #print(dir(self._adaptee))
        #x1, y1, x2, y2 = None, None, None, None
        #is_selection = self._adaptee.mask_bounds(x1, y1, x2, y2)
        #result = (x1, y1, x2, y2)
        bounds = self._adaptee.mask_bounds()
        '''
        bounds is (is_selection, x1, y1, x2, y2)
        The is_selection value was never of any use,
        since the bounding box can be empty even if there is a selection.
        Discard is_selection
        '''
        result = bounds[1:]
        print(f"mask_bounds() returns {result}")
        return result
    # no setter
