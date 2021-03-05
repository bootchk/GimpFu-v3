
'''
!!!
This might go away when Gimp support for auto plugin GUI lands in Gimp 3.
Not well known that such support is on the Gimp roadmap.
'''


"""
Classes GUI widgets.
Primitive types e.g. int.

Each class ultimately inherits a Gtk widget.

Each class implements get_value().  (ABC has get_value)
get_value often converts type returned by Gtk widget to another type.
"""


import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp  # only for locale?

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from gimpfu.gui.value_error import EntryValueError


import gettext
t = gettext.translation("gimp30-python", Gimp.locale_directory, fallback=True)
_ = t.gettext


import logging

module_logger = logging.getLogger("GimpFu.widgets")


class StringEntry(Gtk.Entry):
    def __init__(self, default=""):
        Gtk.Entry.__init__(self)
        self.set_text(str(default))
        self.set_activates_default(True)

    def get_value(self):
        return self.get_text()
'''
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


# TODO Spinner, Slider

# see GimpUi.ScaleEntry
# GimpUi.SpinButton

'''
#    class ArrayEntry(StringEntry):
#            def get_value(self):
#                return eval(self.get_text(), {}, {})


def precision(step):
    import math

    # calculate a reasonable precision from a given step size
    if math.fabs(step) >= 1.0 or step == 0.0:
        digits = 0
    else:
        digits = abs(math.floor(math.log10(math.fabs(step))));
    if digits > 20:
        digits = 20
    return int(digits)

class SliderEntry(Gtk.HScale):
    # bounds is (upper, lower, step)
    def __init__(self, default=0, bounds=(0, 100, 5)):
        step = bounds[2]
        self.adj = Gtk.Adjustment(default, bounds[0], bounds[1],
                                  step, 10 * step, 0)
        Gtk.HScale.__init__(self, self.adj)
        self.set_digits(precision(step))

    def get_value(self):
        return self.adj.value

class SpinnerEntry(Gtk.SpinButton):
    # bounds is (upper, lower, step)
    def __init__(self, default=0, bounds=(0, 100, 5)):
        step = bounds[2]
        self.adj = Gtk.Adjustment(default, bounds[0], bounds[1],
                                  step, 10 * step, 0)
        Gtk.SpinButton.__init__(self, self.adj, step, precision(step))

'''

class ToggleEntry(Gtk.ToggleButton):
    def __init__(self, default=0):
        Gtk.ToggleButton.__init__(self)

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



class RadioButtonsEntry(Gtk.VBox):
    def __init__(self, default=0, items=((_("Yes"), 1), (_("No"), 0))):

        module_logger.debug(f"RadioEntry: default: {default} items: {items}")

        Gtk.VBox.__init__(self, homogeneous=False, spacing=2)

        self.chosen_value = None

        # TODO this is not correct

        #group = Gtk.RadioButtonGroup()
        #group.show()
        # OLD Gtk API passed previous button instead of group
        # button = None
        #button = Gtk.RadioButton(None)
        previous_widget = None

        for (label, value) in items:
            #button = Gtk.RadioButton(group, label)
            # Note we are passing the previous button fo indicate group
            # button = Gtk.RadioButton(button, label)
            # button = Gtk.Button.new_with_label(label)
            button = Gtk.RadioButton.new_with_label_from_widget(previous_widget, label)
            previous_widget = button
            self.pack_start(button, expand=True, fill=True, padding=0)
            button.show()

            button.connect("toggled", self.changed, value)

            if value == default:
                button.set_active(True)
                self.chosen_value = value

        # require local variable set, i.e. the default matches one of the shown values
        assert self.chosen_value is not None

    def changed(self, radio, value):
        if radio.get_active():
            self.chosen_value = value

    def get_value(self):
        return self.chosen_value


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


"""
ComboBoxText is simpler but only delivers a string value.
ComboBox takes a more sophisticated model and delivers an int value.

Copied from Gtk3 tutorial for combo box
and from GimpFu v2 code.
"""
class OptionMenuEntry(Gtk.ComboBox):
    def __init__(self, default=0, items=()):
        # assert items is a tuple of tuples ((label, value), ...)

        """
        Now, the values are just the ordinals (index) of the labels.
        See the caller, which enumerates.
        FUTURE: Author can assign values that are not the index.
        """

        # create a model having two columns
        store = Gtk.ListStore(int, str)
        for item in items:
            # pass a list
            # having two elements: [value, label]
            store.append([item[1], item[0]])
            # store.append([item[0]])

        Gtk.ComboBox.__init__(self, model=store)

        cell = Gtk.CellRendererText()
        # Gtk3 CellLayout takes arg 'expand'
        self.pack_start(cell, expand=False)

        # Tell Gtk which column of model to display: the second column, the label
        self.add_attribute(cell, "text", 1)

        self.set_active(default)

    def get_value(self):
        result = self.get_active()
        module_logger.debug(f"OptionMenuEntry returns: {result}")
        # assert result is the index of the label in the model
        # FUTURE result is the value of the label in the model
        return result



'''
v2

class ComboEntry(Gtk.ComboBox):
    def __init__(self, default=0, items=()):
        store = Gtk.ListStore(str)
        for item in items:
            store.append([item])

        Gtk.ComboBox.__init__(self, model=store)

        cell = Gtk.CellRendererText()
        self.pack_start(cell)
        self.set_attributes(cell, text=0)

        self.set_active(default)

    def get_value(self):
        return self.get_active()
'''
