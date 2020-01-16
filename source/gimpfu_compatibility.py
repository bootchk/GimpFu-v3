
import gi
gi.require_version("Gimp", "3.0")
from gi.repository import Gimp



class Compat():
    '''
    Knows backward compatibility.

    And other hacky workarounds of limitations in Gimp
    ???
    '''
    def try_upcast_to_drawable(arg):
        '''
        When type(arg) is subclass of Gimp.Drawable, up cast to Gimp.drawable
        and return new type, else return original type.

        Require arg a GObject (not wrapped)
        '''
        # idiom for class name
        print("Attempt up cast type", type(arg).__name__ )
        # Note the names are not prefixed with Gimp ???
        if type(arg).__name__ in ("Channel", "Layer"):  # TODO more subclasses
            result = Gimp.Drawable
        else:
            result = type(arg)
        print("upcast result:", result)
        return result
