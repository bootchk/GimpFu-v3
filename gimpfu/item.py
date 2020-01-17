
import gi
gi.require_version("Gimp", "3.0")
from gi.repository import Gimp

from adapter import Adapter



'''
ABC, not instantiable.

No GimpFu plugin author should/can use "Item.foo"
'''


class GimpfuItem( Adapter ) :
    '''
    '''
