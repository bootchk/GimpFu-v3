

'''
Hack, may go away when Gimp is fixed re add_argument_from_property
'''


import gi
from gi.repository import GObject


'''
A class whose *instances* will have a prop attribute

Class has one property of each type.
Properties used only for their type.
In calls to set_args_from_property
'''
class PropHolder (GObject.GObject):
    # copied and hacked to remove '-' from Python GTK+ 3 website tutorial
    __gproperties__ = {
        "intprop": (int, # type
                     "integer prop", # nick
                     "A property that contains an integer", # blurb
                     1, # min
                     5, # max
                     2, # default
                     GObject.ParamFlags.READWRITE # flags
                    ),
    }

    def __init__(self):
        GObject.GObject.__init__(self)
        self.int_prop = 2

    def do_get_property(self, prop):
        if prop.name == 'intprop':
            return self.int_prop
        else:
            raise AttributeError('unknown property %s' % prop.name)

    def do_set_property(self, prop, value):
        if prop.name == 'intprop':
            self.int_prop = value
        else:
            raise AttributeError('unknown property %s' % prop.name)
