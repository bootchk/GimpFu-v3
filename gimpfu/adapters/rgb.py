
import gi
gi.require_version("Gimp", "3.0")
from gi.repository import Gimp

from message.proceed_error import *

from adapters.adapter import Adapter



"""
# TODO:
The name "Color" does not appear to be in GimpFu v2.
E.G. not gimp.Color similar to gimp.Layer
An author can use Gimp.RGB directly.
But if we find any wild plugins that refer to gimp.Color??
"""


class GimpfuRGB(Adapter):
    '''
    RGB aka Color is mostly for parameters to PDB.

    Author CAN instantiate.
    But has no methods or properties.
    And usually easier to use 3-tuples and strings, GimpFu automatically converts when passing to PDB.

    That is, typically Author does not need a Color except as an arg to a PDB procedure.
    '''

    """
    Properties: has none.
    Inherits dynamic adapted properties from Adapter
    """


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
            do_proceed_error(f"Creating GimpfuRGB: {err}")

        # Adapter
        super().__init__(a_adaptee)

        # super logs this


    def __repr__(self):
        # Gimp.RGB has no name() method, so return the fields
        # TODO field alpha?
        return f"GimpfuRGB {self._adaptee.r} {self._adaptee.g} {self._adaptee.b}"


    @classmethod
    def create_RGB_from_string(cls, colorName):
        """ Create a Gimp.RGB from a string. """
        result = Gimp.RGB()
        # TODO Gimp.RGB.parse_name does what when colorName invalid?
        # the GIR doc does not say what
        # result.parse_name(colorName, -1)  # -1 means null terminated
        # TODO the GIR doc says len should be passed, possibly -1
        # The following doesn't seem to throw for invalid name.
        result.parse_name(colorName)
        return result

    @classmethod
    def create_RGB_from_tuple(cls, tuple):
        """ Create a Gimp.RGB from a tuple.

        Expects a 3-tuple.
        If tuple has less than three items, will raise Exception
        If tuple has more than three items, will use the first three.


        """
        result = Gimp.RGB()
        # upcast to type float when type int was passed
        # TODO Gimp.RGB.set does what when values are out of range ???
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
            do_proceed_error("Illegal Python type for color.")
            result = None
        return result
