

import gi

# !!! Even though docs generated from .gir say widgets are in Gimp, they are in GimpUi
gi.require_version("Gimp",   "3.0")
gi.require_version("GimpUi", "3.0")
from gi.repository import GimpUi
from gi.repository import Gimp
# does not import Gtk

import logging

module_logger = logging.getLogger("GimpFu.gui.widgets.gimp")



## TODO:  for each Gimp.FooSelectButton, create a FuFooSelectButton widget wrapper
# Brush, Color, Font, Gradient, Palette, Pattern,

# TODO for each Gimp.FooComboBox, create a widget wrapper
# Channel, ColorProfile, Drawable, Image, Layer, Unit, Vectors
# Int, String, Enum ???


"""
Set of classes.
Each class is a GUI widget.

Each class uses a Gimp widget.
Gimp widgets inherit GTK widgets.

I found that inheriting Gimp widgets in Python fails.
So the relationship is ownership:
an instance of a Fu class owns (wraps) an instance of a Gimp class.

Each class implements get_value().  (ABC has get_value)
get_value often converts type returned by Gimp widget to another type.

Use the word "widget" i.e. don't use "entry" or "button".
Reserve the right to change the look and feel later.
"""



"""
Items:  Drawable, Layer, Vectors, Image, Channel.
See elsewhere for class diagram.

GimpUi implements widget classes for each Item subclass.
Each inherits GimpUi.IntComboBox which ultimately inherits Gtk combobox.
They return (get_value) integer ID's.
They display item's that are open in the GIMP app (not files that can be opened.)

!!! The Channels widget further excludes color and alpha channels:
it only displays custom channels.
I.E. it does NOT display all "open" channels, only "open, custom" channels.
"""
class ItemWidgetWrapper():
    """ Base class for GimpFu widgets that choose Gimp Items"""

    def __init__(self, owned_widget_constructor, description, result_class=None):
        self.description = description
        self.result_class = result_class

        # instantiate the owned widget by calling its constructor
        # constraints=None, data=None
        self.widget = owned_widget_constructor(None, None)

    def get_inner_widget(self):
        return self.widget

    def get_value(self):
        """ Returns an ID """
        # Delegate to inner widget
        active = self.widget.get_active()
        # Discard first element, usually True
        id = active[1]
        module_logger.debug(f"ItemWidgetWrapper.get_value type: {self.description}.ID: {id} ")


        #result = Gimp.Drawable.get_by_id(id)
        # assert is-a Gimp.Drawable
        # OLD result = id

        # class get instance by ID
        result = self.result_class.get_by_id(id)

        module_logger.debug(f"ItemWidgetWrapper.get_value type returns: {result} ")
        return result


class FuImageWidget(ItemWidgetWrapper):
    def __init__(self, ):
        super().__init__(GimpUi.ImageComboBox.new, "Image")

class FuDrawableWidget(ItemWidgetWrapper):
    def __init__(self, ):
        super().__init__(GimpUi.DrawableComboBox.new, "Drawable", Gimp.Drawable)

class FuChannelWidget(ItemWidgetWrapper):
    def __init__(self, ):
        super().__init__(GimpUi.ChannelComboBox.new, "Channel")

class FuLayerWidget(ItemWidgetWrapper):
    def __init__(self, ):
        super().__init__(GimpUi.LayerComboBox.new, "Layer")

class FuVectorsWidget(ItemWidgetWrapper):
    def __init__(self, ):
        super().__init__(GimpUi.VectorsComboBox.new, "Vectors")
