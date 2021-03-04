import gi

gi.require_version("GimpUi", "3.0")
from gi.repository import GimpUi

# for LayerMode
gi.require_version("Gimp", "3.0")
from gi.repository import Gimp


import logging

module_logger = logging.getLogger("GimpFu.gui.widget.brush")

"""
Widgets for choosing Gimp resources: Brush.

Brush is slightly different from other resources.
More args to getter and setter, which we do not expose to GimpFu authors,
instead passing values which mean "no change"
"""
class FuBrushWidget(GimpUi.BrushSelectButton):
    def __init__(self, default=None ):
        module_logger.debug(f"FuBrushWidget: default: {default}")
        super().__init__()
        self.set_brush(default, -1, -1, Gimp.LayerMode.NORMAL)
        # ??? binding does not take None, None, None)
        # (  .., -1) throws ValueError

    def get_value(self):
        # delegate to superclass
        name, opacity, spacing, paint_mode = self.get_brush()
        # print(f"Opacity is {opacity}")
        # discard all but name
        return name
