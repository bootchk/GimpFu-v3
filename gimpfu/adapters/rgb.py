
import gi
gi.require_version("Gimp", "3.0")
from gi.repository import Gimp

from adaption.adapter import Adapter



"""
# TODO:
The name "Color" does not appear to be in GimpFu v2.
E.G. not gimp.Color similar to gimp.Layer
An author can use Gimp.RGB directly.
But if we find any wild plugins that refer to gimp.Color??
"""


class GimpfuRGB(Adapter):
    '''
    Color is mostly for parameters to PDB.

    Author CAN instantiate.
    But has no methods or properties.
    And usually easier to use 3-tuples and strings, GimpFu automatically converts
    on passing to PDB.

    That is, typically Author does not need a Color except as an arg to a PDB procedure.
    '''

    """
    Notes on properties: has none?  TODO see PyGimp documents, maybe there is a 'r' property.
    """
    @classmethod
    def DynamicWriteableAdaptedProperties(cls):
        return ()

    @classmethod
    def DynamicReadOnlyAdaptedProperties(cls):
        return ()

    @classmethod
    def DynamicTrueAdaptedProperties(cls):
        return ()


    def __init__(self, r=None, g=None, b=None, name=None, a_tuple=None, adaptee=None):
        '''
        !!! In call to constructor, you must use a keyword
        assert (
            (r is not None and g is not None and b is not None) # and are numbers
            or (name is not None)       # and is str from a certain subset
            or (a_tuple is not None)    # and is a 3-tuple or sequence of number
            or (adaptee is not None)    # and is-a RGB
            )
        '''

        try:
            if r is not None:
                # Totally new adaptee, created at behest of author or GimpFu implementation
                # Gimp constructor NOT named "new"
                a_adaptee = Gimp.RGB()
                a_adaptee.set(float(r), float(g), float(b) )
            elif name is not None:
                a_adaptee = GimpfuRGB.create_RGB_from_string(name)
            elif a_tuple is not None:
                a_adaptee = GimpfuRGB.create_RGB_from_tuple(a_tuple)
            elif adaptee is not None:
                # Create wrapper for existing adaptee (from Gimp)
                # Adaptee was created earlier at behest of Gimp user and is being passed into GimpFu plugin
                a_adaptee = adaptee
            else:
                raise RuntimeError("Illegal call to GimpfuRGB constructor")
        except Exception as err:
            do_proceed_error(f"Creating GimpfuColor: {err}")

        # Adapter
        super().__init__(a_adaptee)

        print("new GimpfuColor with adaptee", self._adaptee)


    def __repr__(self):
        # Gimp.RGB has no name() method, so print the fields
        # TODO field alpha?
        return f"GimpfuRGB {self._adaptee.r} {self._adaptee.g} {self._adaptee.b}"


    @classmethod
    def create_RGB_from_string(cls, value):
        """ Create a Gimp.RGB from a string. """
        result = Gimp.RGB()
        result.parse_name(name, -1)  # -1 means null terminated
        return result

    @classmethod
    def create_RGB_from_tuple(cls, tuple):
        """ Create a Gimp.RGB from a 3-tuple. """
        result = Gimp.RGB()
        # upcast to type float when type int was passed
        result.set(float(tuple[0]), float(tuple[1]), float(tuple[2]) )
        return result


    @classmethod
    def color_from_python_type(cls, value):
        """ Create a Gimp.RGB from a string or 3-tuple of ints.

        Convenience method on the class.
        """
        if isinstance(value, str):
            result = GimpfuRGB.create_RGB_from_string(value)
        elif isinstance(value, tuple):
            result = GimpfuRGB.create_RGB_from_tuple(value)
        else:
            print("Illegal Python type for color.")
            result = None
        return result
