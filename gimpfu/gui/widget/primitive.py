
"""
Classes GUI widgets.

Primitive types e.g. int, float, str

Each class ultimately inherits a Gtk widget.

Each class implements get_value().  (ABC has get_value)
get_value often converts type returned by Gtk widget to another type.
"""


import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from gimpfu.gui.value_error import EntryValueError


"""
i18n: there is some use of _() here.
Assume _() is already in builtin scope.
"""



"""
Simple widget user can type into.
"""
class StringEntry(Gtk.Entry):
    def __init__(self, default=""):
        Gtk.Entry.__init__(self)
        self.set_text(str(default))
        self.set_activates_default(True)

    def get_value(self):
        return self.get_text()


"""
These inherit StringEntry
Specialize by converting string value to a numeric (int or float) type.

TODO announce errors while user types.
"""
class IntEntry(StringEntry):
    def get_value(self):
        try:
            return int(self.get_text())
        except ValueError as e:
            raise EntryValueError(e.args)


class FloatEntry(StringEntry):
        def get_value(self):
            try:
                return float(self.get_text())
            except ValueError as e:
                raise EntryValueError(e.args)



"""
Boolean valued.

TODO What does Gtk do if we omit labels?
TODO should we pass labels from extras?
"""
class ToggleEntry(Gtk.ToggleButton):
    def __init__(self, default=0):
        #Gtk.ToggleButton.__init__(self)
        super().__init__()

        self.label = Gtk.Label(_("No"))
        self.add(self.label)
        self.label.show()

        self.connect("toggled", self.changed)

        self.set_active(default)

    def changed(self, tog):
        if tog.get_active():
            self.label.set_text(_("Yes"))
        else:
            self.label.set_text(_("No"))

    def get_value(self):
        return self.get_active()



'''
To handle author errors.
Just a label, not allowing interaction.
But has a gettable value.
Value is a constant passed at create time, called 'default'
'''
class OmittedEntry(Gtk.Label):
    def __init__(self, default=0):
        super().__init__("Omitted")
        self.value = default

    def get_value(self):
        return self.value


'''
TODO a widget for entering large amounts of text with return characters

v2

class TextEntry(Gtk.ScrolledWindow):
    def __init__ (self, default=""):
        Gtk.ScrolledWindow.__init__(self)
        self.set_shadow_type(Gtk.SHADOW_IN)

        self.set_policy(Gtk.POLICY_AUTOMATIC, Gtk.POLICY_AUTOMATIC)
        self.set_size_request(100, -1)

        self.view = Gtk.TextView()
        self.add(self.view)
        self.view.show()

        self.buffer = self.view.get_buffer()

        self.set_value(str(default))

    def set_value(self, text):
        self.buffer.set_text(text)

    def get_value(self):
        return self.buffer.get_text(self.buffer.get_start_iter(),
                                    self.buffer.get_end_iter())
'''
