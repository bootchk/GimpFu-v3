
import gi
gi.require_version("Gimp", "3.0")
from gi.repository import Gimp

from gimpfu.adapters.adapter import Adapter



'''
Not instantiable by itself, only inheritable.
No author should/can use "Item.foo"
In other words, private to GimpFu
'''


class GimpfuItem( Adapter ) :
    '''
    GimpFu convenience methods.
    E.G. alias Gimp methods, etc.

    Attributes common to Drawable and Vector
    '''

    '''
    We invoke super()...AdaptedProperties even though we know it is empty.

    Empty DynamicReadOnlyAdaptedProperties()  and DynamicTrueAdaptedProperties()
    are inherited from Adapter.
    '''
    @classmethod
    def DynamicWriteableAdaptedProperties(cls):
        # !!! return ('name') is not a tuple, use tuple('name') or ('name',)
        return ( 'name', ) + super().DynamicWriteableAdaptedProperties()

    # Name of getter() func is property name prefixed with 'get_'
    @classmethod
    def DynamicReadOnlyAdaptedProperties(cls):
        return ('image', ) + super().DynamicReadOnlyAdaptedProperties()


    '''
    methods
    '''

    # Reason: alias.  Deprecated name is "translate", new name is "transform_translate"
    def translate(self, x, y):
        # assert adaptee is-a Gimp.Item that has transform methods
        self._adaptee.transform_translate(x,y)


    '''
    Properties
    '''

    # FBC Reason:alias, upper case to lower case
    # FBC Reason: make readonly.  No setter
    def ID(self):
        # !!! id is true property of Item, accessed without parens
        return self._adaptee.id
