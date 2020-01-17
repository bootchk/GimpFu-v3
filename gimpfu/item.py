
import gi
gi.require_version("Gimp", "3.0")
from gi.repository import Gimp

from adapter import Adapter



'''
Not instantiable by itself, only inheritable.
No GimpFu plugin author should/can use "Item.foo"
In other words, private to GimpFu
'''


class GimpfuItem( Adapter ) :
    '''
    GimpFu convenience methods.
    E.G. alias Gimp methods, etc.

    Attributes common to Drawable and Vector
    '''


    '''
    methods
    '''

    def translate(self, x, y):
        # alias
        # assert adaptee is-a Gimp.Item that has transform methods
        self._adaptee.transform_translate(x,y)


    '''
    Properties
    '''


    @property
    def name(self):
        print("Calling Foo.get_name(): ")
        #print(dir(self._adaptee))
        result = self._adaptee.get_name()
        print("name() returns item name: ", result)
        return result
    @name.setter
    def name(self, name):
        return self._adaptee.set_name(name)
