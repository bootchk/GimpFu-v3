


class WidgetWrapper():
    """
    Wraps an other widget class.

    Other widget must implement get_value().
    This is not used when other widget implements get_active,
    see gimp.py ItemWidgetWrapper, which is similar.

    Used when inheriting other widget class does not work.
    """
    def __init__(self, wrapped):
        self.wrapped = wrapped

    def get_inner_widget(self):
        return self.wrapped

    def get_value(self):
        # delegate
        return self.wrapped.get_value()
