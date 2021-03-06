

import gi
gi.require_version("GimpUi", "3.0")
from gi.repository import GimpUi


from gimpfu.gui.widget.wrapper import WidgetWrapper

"""
Widgets float-valued

See also primitive.py FloatEntry

Not inherit, but wrap, so we can use a convenience constructor.
"""
class SpinnerWidget(WidgetWrapper):
    # bounds is (upper, lower, step)
    def __init__(self, default=0, bounds=(0, 100, 5)):
        wrapped = GimpUi.SpinButton.new_with_range(*bounds)
        super().__init__(wrapped)

class SliderWidget(WidgetWrapper):
    # bounds is (upper, lower, step)
    def __init__(self, title, default=0, bounds=(0, 100, 5)):
        """
        !!! We pass empty string for label, otherwise it creates
        an extra label on the slider portion.
        We already labeled the entire widget in the dialog.
        """
        wrapped = GimpUi.ScaleEntry.new( "", default, *bounds)
        super().__init__(wrapped)


        """
        step = bounds[2]
        self.adj = Gtk.Adjustment(default, bounds[0], bounds[1],
                                  step, 10 * step, 0)
        super().__init__(self, self.adj, step, precision(step))
        """
'''

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
'''
