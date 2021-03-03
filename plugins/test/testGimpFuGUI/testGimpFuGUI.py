'''
A test Gimp plugin
that:
- takes (has formal param of) all types, to test GimpFu GUI

I.E. foreach PF_ value that should have a widget
See the dictionary _edit_map in gimpfu/gui/widget_factory.py
that defines which PF_ values have widgets.

See gimpfu/enums/gimpfu_enums.py for definition of PF_ enum

To test:
  Prep:
    new image
    create a vector
    create a custom channel (doesn't list color or alpha channel)
    invoke Test>GimpFu GUI
  Expect:
    in the console, every value returned by widgets is not -1 or otherwise None
'''

from gimpfu import *

def plugin_func(img, drw,
                int8, int32, float, string,
                file,
                #dir

                #color, # GLib CRITICAL
                font,  # selector not stay on top?

                image,
                drawable,
                layer,
                channel,
                vectors,
                ):
    """ Just prints results. Does nothing substantive. """
    # TODO checks that each value is valid?
    print(f"Test GIMP GUI results:")
    print(f"File:        {file}")
    print(f"Font:        {font}")
    print(f"Image    ID: {image}")
    print(f"Drawable ID: {drawable}")
    print(f"Layer    ID: {layer}")
    print(f"Channel  ID: {channel}")
    print(f"Vectors  ID: {vectors}")
    return


register(
      "python-fu-test-gimpfu-gui",
      "blurb",
      "help message",
      "author",
      "copyright",
      "year",
      "GimpFu GUI",
      "",
      [
          # the names do NOT need to match the formal names in plugin_func
          # but the names must be unique.
          # PF_              name          displayed   default  extras
          #                                    name

          # These are really not needed?
          #(PF_IMAGE,         "image",      "foo",      None),
          #(PF_DRAWABLE,      "drawable",      "foo",      None),
          # NO widgets for arrays

          # int primitives
          # PF_INT         : IntEntry,
          #PF_INT16       : IntEntry,
          (PF_INT8,          "uchar",       "uchar",    1,     (1, 10, 1)),
          (PF_INT32,         "int",         "int",      None),
          # float primitives by widget type
          (PF_FLOAT,         "float",       "float",    1.0,    (1.0, 10.0, 1.0)),
          #PF_SLIDER      : FloatEntry,
          #PF_SPINNER     : FloatEntry,
          #PF_ADJUSTMENT  : FloatEntry,
          # TODO:
          (PF_STRING,        "string",      "string",   None),
          # generic objects, using only GTK, not GimpUI
          # a button that opens a dialog that chooses a file from file system
          (PF_FILE,          "file",        "file",     None),
          # TODO PF_DIR

          # GIMP objects
          # a button that opens a dialog that chooses a color
          #(PF_COLOR,         "color",       "color",    "red"),
          # a drop down menu button to choose a font
          (PF_FONT,          "font",        "font",     "Helvetica"),

          #(PF_DISPLAY,      "display",   "foo", None),

          # a drop down menu button to choose an image that is open in Gimp app
          (PF_IMAGE,          "img",        "image",    None),

          (PF_DRAWABLE,       "drw",        "drawable", None),
          (PF_LAYER,        "layer",        "layer",    None),
          (PF_CHANNEL,      "channel",      "channel",  None),
          (PF_VECTORS,      "vectors",      "vectors",  None),

          # Parasite, bool, enum
      ],
      [],   # no return values
      plugin_func,
      menu="<Image>/Test")
main()
