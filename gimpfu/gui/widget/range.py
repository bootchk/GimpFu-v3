

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

import logging

module_logger = logging.getLogger("GimpFu.gui.widget.range")


"""
Widgets integer-valued from a defined range or set of values
"""


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
