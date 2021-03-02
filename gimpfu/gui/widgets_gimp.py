

import gi

# !!! Even though docs generated from .gir say widgets are in Gimp, they are in GimpUi
gi.require_version("GimpUi", "3.0")
from gi.repository import GimpUi
# does not import Gtk

import logging

module_logger = logging.getLogger("GimpFu.gimp_widgets")



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
"""
class ItemWidgetWrapper():
    """ Base class for GimpFu widgets that choose Gimp Items"""

    def __init__(self, owned_widget_constructor, description):
        self.description = description

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
        #result = Gimp.Drawable.get_by_id(id)
        # assert is-a Gimp.Drawable
        result = id
        module_logger.debug(f"ItemWidgetWrapper.get_value type: {self.description}.ID: {result} ")
        return result


class FuImageWidget(ItemWidgetWrapper):
    def __init__(self, ):
        super().__init__(GimpUi.ImageComboBox.new, "Image")

class FuDrawableWidget(ItemWidgetWrapper):
    def __init__(self, ):
        super().__init__(GimpUi.DrawableComboBox.new, "Drawable")

class FuChannelWidget(ItemWidgetWrapper):
    def __init__(self, ):
        super().__init__(GimpUi.ChannelComboBox.new, "Channel")

class FuLayerWidget(ItemWidgetWrapper):
    def __init__(self, ):
        super().__init__(GimpUi.LayerComboBox.new, "Layer")

class FuVectorsWidget(ItemWidgetWrapper):
    def __init__(self, ):
        super().__init__(GimpUi.VectorsComboBox.new, "Vectors")



"""
A Gimp.ColorButton displays a color, and pops up a Gimp.ColorSelector dialog when clicked.
"""
class FuColorEntry(GimpUi.ColorButton):
    def __init__(self, default="", title = "Foo", ):
        module_logger.debug(f"ColorButton: default: {default} title: {title}")

        # try setting title before superclass init
        # throws not initialized
        #module_logger.debug(f"FuColorEntry: set_title")
        #self.set_title(title)

        # ColorButton has no init() method but GTK expects its __init__ to be called ???
        # Both the following yield the same result
        #Gtk.Button.__init__(self)
        super().__init__("foo")

        # Gimp requires title, so the pop-up ColorSelector can be titled.
        # Otherwise, at click time:  gimp_dialog_new: assertion 'title != NULL' failed

        # Here, title is same as label of button

        # ??? Gimp constructor has already thrown
        # critical : gimp_color_button_set_title: assertion 'title != NULL' failed but works anyway?
        # We will ignore it.

        module_logger.debug(f"FuColorEntry: set_title")
        self.set_title(title)
        # self.set_title("Border")

        # set default
        self.set_color(default)

        # cruft from StringEntry
        #self.set_activates_default(True)


    def get_value(self):
        return self.get_color()




class FuFontEntry(GimpUi.FontSelectButton):
    def __init__(self, default="" ):
        module_logger.debug(f"FuFontEntry: default: {default}")

        # Gimp.FontSelectButton has no init() method but GTK expects its __init__ to be called ???
        # Gimp.FontSelectButton inherits Gtk.Widget
        # TODO super().__init__()
        #Gtk.Widget.__init__(self)
        super().__init__()

        # Has no set_title

        # set default
        self.set_font(default)

    def get_value(self):
        return self.get_font()



class FuPaletteEntry(GimpUi.PaletteSelectButton):
    def __init__(self, default="" ):
        module_logger.debug(f"FuPaletteEntry: default: {default}")

        # Gimp.FontSelectButton has no init() method but GTK expects its __init__ to be called ???
        # Gimp.FontSelectButton inherits Gtk.Widget
        super().__init__()

        # Has no set_title

        self.set_palette(default)

    def get_value(self):
        return self.get_palette()
