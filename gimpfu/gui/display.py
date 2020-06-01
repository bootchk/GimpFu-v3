import gi
gi.require_version("Gimp", "3.0")
from gi.repository import Gimp

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

import logging


"""
Understands:

- how to initialize GUI framework.
- window/display for a plugin procedure
"""


class Display:

    '''
    OLD
    Now there *is* another API for getting display.

    def get(proc_name, maybe_image):
        """ Return the display of maybe_image, else None.

        Must be called before opening dialogs.
        Also initializes GTK.

        TODO a plugin might not have an image arg.
        Gimp has no API to get the display without supplying an image?
        """



        result = None
        if maybe_image :
            if type(maybe_image).__name__  == 'Image':
                # assert maybe_image is-a Gimp.Image

                # Label any child dialogs with proc_name
                Gimp.ui_init(proc_name)
                result = Gimp.ui_get_display_window(maybe_image)
    '''

    logger = logging.getLogger('GimpFu.Display')

    def get_window(proc_name):
        """ Get the parent window (transient-for window) for a plugin procedure. """

        Gimp.ui_init(proc_name)

        display = Gimp.default_display()
        # assert display is-a Gimp.Display

        result = Gimp.ui_get_display_window(display)


        Display.logger.debug(f"get_window returns: {result}")

        #result = display.get_window_handle()
        # assert result is-a GdkX11.X11Window or None??

        return result
