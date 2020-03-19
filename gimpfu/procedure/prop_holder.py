

'''
Hack, may go away when Gimp is fixed re add_argument_from_property
'''


import gi
from gi.repository import GObject

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp   # for Gimp enum RunMode


"""
Don't touch this unless you want to deal with mysterious GObject failures.
Any mistakes give error messages that are not helpful.
At best, test after every small change.
Much of this is 'magic' that I don't understand why/how it works.

Long form of property declaration, instead of GObject.Propery decorator form.
"""

'''
A class whose *instances* will have a "props" attribute.
E.G. prop_holder.props is-a dictionary
E.G. prop_holder.props.IntProp is-a GProperty

TODO Class has pools of properties of each type.
Class has one property of each type.
Properties used only for their type.
In calls to set_args_from_property
'''
class PropHolder (GObject.GObject):



    """
    ??? This breaks the comment strings.

    @GObject.Property(type=Gimp.RunMode,
                      default=Gimp.RunMode.NONINTERACTIVE,
                      nick="Run mode", blurb="The run mode")
    """

    # Seems to be required by PyGobject or GObject
    __gtype_name__ = "PropHolder"

    '''
    class attribute, but we still need an instance to pass to procedure.add_argument_from_property

    These properties are constants, no one sets them? Maybe Gimp does?
    We only use them to convey plugin arg spec declarations to Gimp
    '''
    # copied and hacked to remove '-' from Python GTK+ 3 website tutorial
    __gproperties__ = {
        # type, nick, blurb, default, min, max, flags
        "IntProp1": (int, "nick", "blurb", 1, 5, 2, GObject.ParamFlags.READWRITE ),
        "IntProp2": (int, "nick", "blurb", 1, 5, 2, GObject.ParamFlags.READWRITE ),
        "IntProp3": (int, "nick", "blurb", 1, 5, 2, GObject.ParamFlags.READWRITE ),
        "IntProp4": (int, "nick", "blurb", 1, 5, 2, GObject.ParamFlags.READWRITE ),
        "IntProp5": (int, "nick", "blurb", 1, 5, 2, GObject.ParamFlags.READWRITE ),
        "IntProp6": (int, "nick", "blurb", 1, 5, 2, GObject.ParamFlags.READWRITE ),
        "FloatProp1": (float, "nick", "blurb", 1., 5., 2., GObject.ParamFlags.READWRITE ),
        "FloatProp2": (float, "nick", "blurb", 1., 5., 2., GObject.ParamFlags.READWRITE ),
        "FloatProp3": (float, "nick", "blurb", 1., 5., 2., GObject.ParamFlags.READWRITE ),
        "FloatProp4": (float, "nick", "blurb", 1., 5., 2., GObject.ParamFlags.READWRITE ),
        "FloatProp5": (float, "nick", "blurb", 1., 5., 2., GObject.ParamFlags.READWRITE ),
        "StrProp1": (str, "nick", "blurb", "foo", GObject.ParamFlags.READWRITE ),
        "StrProp2": (str, "nick", "blurb", "foo", GObject.ParamFlags.READWRITE ),
        "StrProp3": (str, "nick", "blurb", "foo", GObject.ParamFlags.READWRITE ),
        "StrProp4": (str, "nick", "blurb", "foo", GObject.ParamFlags.READWRITE ),
        "RunmodeProp": (Gimp.RunMode,
                 "Run mode",
                 "Run mode",
                 Gimp.RunMode.NONINTERACTIVE,  # default
                 GObject.ParamFlags.READWRITE),
        }

    """
    ??? Don't know why PropHolder.__gproperties__ is not accessible???
    But this seems to be
    """
    map_property_to_value = {
        "IntProp1": 1,
        "IntProp2": 2,
        "IntProp3": 3,
        "IntProp4": 4,
        "IntProp5": 5,
        "IntProp6": 6,
        "FloatProp1": 1.0,
        "FloatProp2": 2.0,
        "FloatProp3": 3.0,
        "FloatProp4": 4.0,
        "FloatProp5": 5.0,
        "StrProp1": "1",
        "StrProp2": "2",
        "StrProp3": "3",
        "StrProp4": "4",
        "RunmodeProp": Gimp.RunMode.INTERACTIVE
    }


    def __init__(self):
        GObject.GObject.__init__(self)

        # give arbitrary value to shadow properties
        self.int_prop1 = 2

        # TODO give arbitrary value to the property of type Gimp.RunMode
        self.runmode_prop = Gimp.RunMode.NONINTERACTIVE

        # indexes over pool
        self._next_int_prop = 1
        self._next_float_prop = 1
        self._next_str_prop = 1


    def next_prop_name(self, type):
        """ Return next unused property of given type. """
        if type == int:
            result = "IntProp" + str(self._next_int_prop)
            self._next_int_prop += 1
        elif type == float:
            result = "FloatProp" + str(self._next_float_prop)
            self._next_float_prop += 1
        elif type == str:
            result = "StrProp" + str(self._next_str_prop)
            self._next_str_prop += 1
        else:
            raise RuntimeError(f"Unhandled formal parameter type: {type}")

        return result



    """
    See gtk3-tutorial.
    We are using the "verbose" form (__gproperties__)
    which means we must also define do_get_property and do_set_property
    Our code does not access it directly,
    but prop_holder.props.foo invokes it.
    """



    def do_get_property(self, prop):
        # if prop.name in cls.__gproperties__:
        if prop.name in PropHolder.map_property_to_value:
            return PropHolder.map_property_to_value[prop.name]
        #elif prop.name == 'RunmodeProp':
        #    raise AttributeError("Access RunmodeProp")
        else:
            raise AttributeError(f"unknown property {prop.name}")

    def do_set_property(self, prop, value):
        # if prop.name in PropHolder.__gproperties__:
        if prop.name in PropHolder.map_property_to_value:
            PropHolder.map_property_to_value[prop.name] = value
        else:
            raise AttributeError('unknown property %s' % prop.name)
