
import gi
gi.require_version("Gimp", "3.0")
from gi.repository import Gimp

from gimpfu.message.proceed_error import *

from gimpfu.adapters.adapter import Adapter



"""
# TODO:
The name "Color" does not appear to be in GimpFu v2.
E.G. not gimp.Color similar to gimp.Layer
An author can use Gimp.RGB directly.
But if we find any wild plugins that refer to gimp.Color??
"""

"""
# TODO:
Adapt Gimp.HSV and Gimp.HSL
Test case: palette_sort.py can use Gimp.HSV
"""

class GimpfuRGB(Adapter):
    '''
    Adapts Gimp.RGB

    aka Color
    Mostly used for parameters to PDB.

    Author CAN instantiate.
    But has no methods or properties.
    And usually easier to use 3-tuples and strings, GimpFu automatically converts when passing to PDB.

    That is, typically Author does not need a Color except as an arg to a PDB procedure.
    '''

    """
    Properties: r,g,b,a , the same as the Gimp fields.
    !!! However these are NOT dynamically adapted properties.
    """
    #@classmethod
    #def DynamicWriteableAdaptedProperties(cls):
    #    return ('r', 'g', 'b', 'a' ) + super().DynamicWriteableAdaptedProperties()



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
            proceed(f"Creating GimpfuRGB: {err}")

        # Adapter
        super().__init__(a_adaptee)

        # super logs this


    def __repr__(self):
        # Gimp.RGB has no name() method, so return the fields instead
        return f"GimpfuRGB {self._adaptee.r} {self._adaptee.g} {self._adaptee.b} {self._adaptee.a}"

    """
    subscriptable/slicing protocol

    Refer to "implementing slicing in __get-item__"

    Test case: palette_sort.py
    """
    def __getitem__(self, key):
        if isinstance(key, int):
            if key==0: result = self.r
            elif key==1: result = self.g
            elif key==2: result = self.b
            elif key==3: result = self.a
            else: raise RuntimeError(f"GimpfuRGB: Subscript out of range: {key}")
        elif isinstance(key, slice):
            start, stop, step = key.indices(4)
            # return sliced list
            result = [self[i] for i in range(start, stop, step)]
        else:
            raise TypeError(f'Invalid argument type: {type(key)}')
        return result





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
        TODO alpha?
        """
        result = Gimp.RGB()
        # upcast to type float when type int was passed
        # TODO Gimp.RGB.set does what when values are out of range ???
        result.set(float(tuple[0]), float(tuple[1]), float(tuple[2]) )
        return result


    @classmethod
    def color_from_python_type(cls, value):
        """ Create a Gimp.RGB from a string or 3-tuple of ints.

        !!! Not a GimpFuRGB, a Gimp.RGB, i.e. an unwrapped Gimp type

        Convenience method on the class.
        """
        if isinstance(value, str):
            result = GimpfuRGB.create_RGB_from_string(value)
        elif isinstance(value, tuple):
            result = GimpfuRGB.create_RGB_from_tuple(value)
        else:
            proceed(f"Illegal Python type: {type(value)} for color: {value}.")
            # return an arbitrary color so we can proceed
            result = GimpfuRGB.create_RGB_from_string("orange")
        return result

    @classmethod
    def colors_from_list_of_python_type(cls, list):
        """ Create a list of Gimp.RGB from a list of  string or 3-tuple of ints.

        Convenience method on the class.
        """
        result = []
        try:
            for item in list:
                color = GimpfuRGB.color_from_python_type(item)
                result.append(color)
        except:
            proceed(f"Failed to convert list element to Gimp.RGB: {item}.")
        # assert result is-a list of Gimp.RGB
        return result


    '''
    Properties
    '''

    # FBC reason: adapt C field to Python property
    # TODO setters?
    @property
    def r(self):  return self._adaptee.r
    @property
    def g(self):  return self._adaptee.g
    @property
    def b(self):  return self._adaptee.b
    @property
    def a(self):  return self._adaptee.a
