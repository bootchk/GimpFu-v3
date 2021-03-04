

import gi

# !!! Even though docs generated from .gir say widgets are in Gimp, they are in GimpUi
gi.require_version("GimpUi", "3.0")
from gi.repository import GimpUi
# does not import Gtk

import logging

module_logger = logging.getLogger("GimpFu.gui.widget.resource")

"""
Widgets for choosing Gimp resources.

Resources
"""

class FuFontWidget(GimpUi.FontSelectButton):
    def __init__(self, default=None ):
        module_logger.debug(f"FuFontWidget: default: {default}")
        super().__init__()
        if default:               self.set_font(default)

    def get_value(self):   return self.get_font()

class FuPaletteWidget(GimpUi.PaletteSelectButton):
    def __init__(self, default=None ):
        module_logger.debug(f"FuPaletteWidget: default: {default}")
        super().__init__()
        if default:              self.set_palette(default)

    def get_value(self):  return self.get_palette()

class FuPatternWidget(GimpUi.PatternSelectButton):
    def __init__(self, default=None ):
        module_logger.debug(f"FuPatternWidget: default: {default}")
        super().__init__()
        if default:              self.set_pattern(default)

    def get_value(self):  return self.get_pattern()

class FuGradientWidget(GimpUi.GradientSelectButton):
    def __init__(self, default=None ):
        module_logger.debug(f"FuGradientWidget: default: {default}")
        super().__init__()
        if default:              self.set_gradient(default)

    def get_value(self):  return self.get_gradient()
