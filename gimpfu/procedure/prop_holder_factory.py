


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



    def __init__(self):
        self.counter = 1

        """
        Indentation important on template strings.
        # type, nick, blurb, default, min, max, flags
        """
        # TODO float() for float, insure is proper type literal
        self.template_string_numeric = r'''
global Foo
class Foo(GObject.GObject):
    __gproperties__ = {
        "$name": ($type, "nick", "blurb", $min, $max, $default, GObject.ParamFlags.READWRITE ),
    }
'''

        # !!! note default is quoted
        self.template_string_str = r'''
global Foo
class Foo(GObject.GObject):
  __gproperties__ = {
    "$name": ($type, "nick", "blurb", "$default", GObject.ParamFlags.READWRITE ),
  }
'''



    def get_unique_name(self):
        """ Generate unique property name, unique over life of factory """
        result = "DummyProp" + str(self.counter)
        self.counter += 1
        return result


    def produce(self, type, default, min, max):
        print(f"Producing property type: {type} default: {default}, min: {min}, max: {max}")
        unique_prop_name = self.get_unique_name()

        # substitute into template
        # !!! need strings but str() and repr() don't work for type
        # dispatch on type
        if type is int:
            template = string.Template(self.template_string_numeric)
            code_string = template.substitute(type="int", name=unique_prop_name, default=default, min=min, max=max)
        elif type is float:
            template = string.Template(self.template_string_numeric)
            code_string = template.substitute(type="float", name=unique_prop_name, default=default, min=min, max=max)
        elif type is str:
            template = string.Template(self.template_string_str)
            code_string = template.substitute(type="str", name=unique_prop_name, default=default)
        elif type is Gimp.RGB:
            template = string.Template(self.template_string_str)
            code_string = template.substitute(type="Gimp.RGB", name=unique_prop_name, default=default)
        else:
            raise RuntimeError(f"Unhandled property type: {type}")

        # create class Foo in globals by exec template
        exec(code_string)

        # create instance of class
        instance = Foo()
        # assert instance is-a GObject with property as specified

        return instance, unique_prop_name
