


"""
We don't use gi directrly,
but it must be in scope for exec
"""
import gi
from gi.repository import GObject

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp   # for Gimp enum RunMode

import string



"""
Factory that creates a GObject having a templated property.
"""
class PropHolderFactory():

    # counter = 1

    def __init__(self):
        self.template_string = r'''
global Foo
class Foo(GObject.GObject):
    __gproperties__ = {
        # type, nick, blurb, default, min, max, flags
        "$property_name": ($type, "nick", "blurb", $default, 5, 2, GObject.ParamFlags.READWRITE ),
    }
'''

    def produce(self, type_name, default_name):
        # TODO get template appropriate to type
        template = string.Template(self.template_string)

        # TODO generate unique property name, unique over life of factory
        unique_prop_name = "IntProp1"

        # substitute into template
        code_string = template.substitute(property_name=unique_prop_name, type=type_name, default=default_name)

        # create class Foo in globals by exec template
        exec(code_string)

        # create instance of class
        instance = Foo()
        # assert instance is-a GObject with property named

        return instance, unique_prop_name
