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
                int32,

                bool,
                radio,
                option,

                float,
                slider,
                spinner,

                string,

                file,
                directory,

                color, # GLib CRITICAL
                font,  # selector not stay on top?
                palette,
                brush,
                pattern,
                gradient,

                image,
                drawable,
                layer,
                channel,
                vectors,
                ):
    """ Just prints results. Does nothing substantive. """
    # TODO checks that each value is valid?
    print(f"Test GIMP GUI results:")
    print(f"bool:        {bool}")
    print(f"radio:       {radio}")
    print(f"option:      {option}")

    print(f"slider:      {slider}")
    print(f"spinner:     {spinner}")

    print(f"file:        {file}")
    print(f"directory:   {directory}")

    print(f"color:        {color}")
    print(f"font:         {font}")
    print(f"palette:      {palette}")
    print(f"brush:        {brush}")
    print(f"pattern:      {pattern}")
    print(f"gradient:     {gradient}")

    if True:   # Temporary not test
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

          # Stock image and drawable params need to be declared here.

          # NO widgets for arrays

          # int valued, by widget type

          # PF_8, PF_INT, PF_INT32 all use the same widget
          # (PF_INT8,          "uchar",       "uchar",    1,     (1, 10, 1)),
          (PF_INT32,         "int",         "int",      None),
          # Toggle widget
          (PF_BOOL,          "bool",        "bool",     True),
          # Radio buttons with label,value pairs
          (PF_RADIO,         "radio",       "radio",    1,     (("foo", 1), ("bar", 5))),
          # pull down option menu widget,  labels without values declared, always int-valued
          (PF_OPTION,        "option",       "option",  1,     ("foo", "bar")),

          # float valued, by widget type
          (PF_FLOAT,         "float",       "float",    1.0,    (1.0, 10.0, 1.0)),
          (PF_SLIDER,        "slider",      "slider",   5.0,    (1.0, 10.0, 1.0)),
          (PF_SPINNER,       "spinner",     "spinner",  5.0,    (1.0, 10.0, 1.0)),
          # PF_ADJUSTMENT  is alias

          # string valued, by widget type
          # TODO: PF_TEXT
          (PF_STRING,        "string",      "string",   None),

          # generic objects, using only GTK, not GimpUI
          # a button that opens a dialog that chooses a file from file system
          (PF_FILE,          "file",        "file label",  "tmp.tmp"),
          (PF_DIRNAME,       "dir",         "dir label",   "/# TEMP: "),

          # GIMP objects
          # a button that opens a dialog that chooses a color
          (PF_COLOR,         "color",       "color",    "red"),

          # Resources
          # Names are chosen from stock, but stock may change.
          # In Gimp Dockable dialog, RMB in tab, choose "view as list" to see names
          # !!! Brush name often includes a cardinal number e.g. "2. "
          # but the displayed size e.g. "(55 x 55)" is not part of the name
          (PF_FONT,          "font",        "font",      "Helvetica"),
          (PF_PALETTE,       "palette",     "palette",   "Blues"),
          (PF_BRUSH,         "brush",       "brush",     "2. Star"),
          (PF_PATTERN,       "pattern",     "pattern",   "Sky"),
          (PF_GRADIENT,      "gradient",    "gradient",  "Default"),

          # No Gimp widget: PF_DISPLAY

          # a drop down menu button to choose an image that is open in Gimp app
          (PF_IMAGE,          "img",        "image",    None),
          (PF_DRAWABLE,       "drw",        "drawable", None),
          (PF_LAYER,        "layer",        "layer",    None),
          (PF_CHANNEL,      "channel",      "channel",  None),
          (PF_VECTORS,      "vectors",      "vectors",  None),

          # Parasite, enum, PF_VALUE ??
      ],
      [],   # no return values
      plugin_func,
      menu="<Image>/Test")
main()
