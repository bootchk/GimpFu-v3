#!/usr/bin/env python3

#   Gimp-Python - allows the writing of Gimp plugins in Python.
#   Copyright (C) 2003, 2005  Manish Singh <yosh@gimp.org>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.

# based on Perl version by Marc Lehmann


"""
Only saves.

"Color XHTML" is not the name of a format.
It is a text file in HTML format that renders like "ASCII art."
Only usually read by a browser that renders HTML.

Character glyphs simulate screen dots, having color/intensity.
So the current GIMP image is like a color map applied to a text file.
The plugin by default generates a text file
in the shape of the image from default characters e.g. XOXO.

Since character glyphs are taller than they are wide,
the plugin scales the in image vertically.
Thus the result image is same dimensions as original image.
I.E. downscale vertically reciprocal to
the aspect ratio of glyph height/width.

Unlike some ASCII art, the shape of the character glyphs
does not usually contribute as drawing strokes.
Usually only a few glyphs are used.
Although a user can upload a file that contains stroke-like characters e.g.
 (...(;)...)
 (...(;)...) etc.
that would then be rendered in the colors of the image.

That works best when the text file is the dimensions of the image.
"""

# TODO allow greyscale image


import string
import struct
import os.path
import sys

import gi
gi.require_version('Gimp', '3.0')
gi.require_version('GimpUi', '3.0')
from gi.repository import Gimp
from gi.repository import GimpUi

from gi.repository import GObject
from gi.repository import GLib
from gi.repository import Gio

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

import gettext
_ = gettext.gettext
def N_(message): return message

escape_table = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;'
}


# Some template strings, %s and %d are placeholder

# bold renders  with more color in browser
style_def = """body {
   width: 100%%;
   font-size: %dpx;
   font-weight: bold;
   background-color: %s;
   color: #ffffff;
}
"""

preamble = """<!DOCTYPE html>
<html>
<head>
<title>ASCII art from GIMP</title>
%s
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
</head>
<body>
<pre>
"""

glyph_style_string = 'color:#%s;'



postamble = """\n</pre>\n</body>\n</html>\n"""

fmt_from_bpp = {
        3: 'BBB',
        6: 'HHH',
        12: 'III'
}


def scale_image_to_glyph_aspect_ratio(image):
    """
    Scale down an image duplicate in the vertical dimension
    so result not appear stretched.

    We scale down since performance is usually challenged anyway.

    Scale by typical aspect ratio of monospace Courier font = .43 .
    I think that is after kerning (accounts for glyph separation.)
    Not ideal to guess what the font aspect ratio is,
    but usually better than no scaling at all.
    Note the output html does not specify a font (but we should?)
    """
    image = image.duplicate()
    drawable = image.get_active_layer()
    image.scale(drawable.width(), drawable.height() * .43)
    return image, drawable



def get_background_color_name_from_gimp():
    """ Return a string for name of output background color,
    'white' if GIMP is, else 'black'

    Result string is valid html color name.
    Make html background crudely match the Gimp context.
    Each glyph has its own color,
    color of the glyphs is the html foreground.
    """
    # returns a tuple (bool, Gimp.RGB)
    gimp_background_color = Gimp.context_get_background()[1]

    """
    Better to compare to a named color.
    But there is no equality operator?
    Not used.

    parsed_white = Gimp.RGB() # construct new color, unknown value
    parsed_white.parse_name('white') # set new value, discard boolean result
    print(parsed_white)
    """
    # white is (1.0, 1.0, 1.0), were it really a tuple
    if (    (gimp_background_color.r == 1.0)
        and (gimp_background_color.g == 1.0)
        and (gimp_background_color.b == 1.0) ):
        result = 'white'
    else:
        # default to black
        # TODO mangle GIMP background color into an html color
        # Better to create GIMP function Gimp.RGB.to_nearest_name()
        result = 'black'
    return result



def translate_and_escape_raw_data(stream, respect_whitespace=False):
    """
    Translate control and whitespace characters in stream.
    Escape characters that are html control characters.
    Return translated stream.

    Control characters are unprintable (do not advance the printhead.)

    TODO: Only handles ascii files?  FUTURE: handle unicode, any language.
    """
    goodchars = string.digits + string.ascii_letters + string.punctuation
    if respect_whitespace:
        # whitespace is printable (has visible effects) not a pure control character
        goodchars = goodchars + string.whitespace
    # else strip whitespace (especially blanks and newline)

    badchars = ''.join(chr(i) for i in range(256) if chr(i) not in goodchars)
    allchars = str.maketrans('', '', badchars)
    stream = stream.translate(allchars)

    result = [escape_table.get(c, c) for c in stream]
    # !!! result is no longer a list of chars, but a list of strings
    return result



class InfiniteGenerator(object):
    """
    Generate infinite sequence,
    from a finite sequence, wrapping around.
    """
    def __init__(self, finite):
        # assert finite is iterable e.g. a list
        # but not an iterator
        self._finite = finite
        self._iter = iter(finite)

    def __iter__(self):
        return self

    # Python 3 compatibility
    def __next__(self):
        return self.next()

    def next(self):
        #print("InfiniteGenerator next")
        while True:
            try:
                return next(self._iter)
            except StopIteration:
                # create new iterator, can't reset the existing one
                self._iter = iter(self._finite)


class RowGenerator(object):
    """
    Generate rows of strings from a sequence of strings.
    Row of len row_len.

    Stops generating after row_count rows are generated.

    When the sequence is not long enough, wrap around,
    i.e. make it infinite.

    Returns (row_index, row)

    Respecting new lines and padding with spaces.
    """
    def __init__(self, strings, row_count, row_len):
        self._row_count = row_count
        self._row_len = row_len
        self._row_index = 0

        # RowGenerator is a generator composed on another generator
        self.string_generator = InfiniteGenerator(strings)

    def __iter__(self):
        return self

    # Python 3 compatibility
    def __next__(self):
        return self.next()

    def next(self):
        # print(" RowGenerator next", self._row_index)
        if self._row_index < self._row_count:

            row_strings = []

            while len(row_strings) < self._row_len:
                # next_string = self.string_generator.next()
                next_string = self.string_generator.next()

                """
                Respect newline character, but don't keep it.
                We add newline after every row, later.

                Windows: the CR/LF problem.
                Python "universal newlines" solves it for us
                during reading the text and writing the output.
                """
                if next_string == '\n':
                    # pad, i.e. fill rest of row,  with blanks
                    while len(row_strings) < self._row_len:
                        row_strings.append(' ')
                else:
                    row_strings.append(next_string)

            self._row_index += 1
            return self._row_index-1, row_strings
        else:
            raise StopIteration()


"""
GUI
"""

def show_warn_slow_dialog():

    # Gimp.message() not adequate: not in front, not offer Cancel

    message_dialog = Gtk.MessageDialog(parent= None, # parent_dialog,
                                    modal=True, # destroy_with_parent=True
                                    message_type=Gtk.MessageType.INFO,
                                    buttons=Gtk.ButtonsType.OK_CANCEL,
                                    text=_("The image is large and may export slowly")
                                    )


    response = message_dialog.run()
    message_dialog.destroy()
    if response == Gtk.ResponseType.OK:
        return False
    elif response == Gtk.ResponseType.CANCEL:
        return True



def show_settings_dialog(characters, size, source_file, separate, respect_whitespace):
    """
    args are reference-by-value of current settings.
    Using the dialog, user may enter new values for settings.
    Return reference to new values.

    Also return whether canceled
    """
    use_header_bar = Gtk.Settings.get_default().get_property("gtk-dialogs-use-header")
    dialog = Gtk.Dialog(use_header_bar=use_header_bar,
                        title=_("Save as ASCII art in HTML..."))
    dialog.add_button("_Cancel", Gtk.ResponseType.CANCEL)
    dialog.add_button("_OK", Gtk.ResponseType.OK)

    choose_file_dialog = Gtk.FileChooserDialog(use_header_bar=use_header_bar,
                                   title=_("Read characters from file..."),
                                   action=Gtk.FileChooserAction.OPEN)
    choose_file_dialog.add_button("_Cancel", Gtk.ResponseType.CANCEL)
    choose_file_dialog.add_button("_OK", Gtk.ResponseType.OK)

    # TODO make the chooser show only mime type txt files
    def choose_file(button, user_data=None):
        choose_file_dialog.show()
        if choose_file_dialog.run() == Gtk.ResponseType.OK:
            characters_entry.set_text(choose_file_dialog.get_filename())

        choose_file_dialog.hide()

    grid = Gtk.Grid()
    grid.set_column_homogeneous(False)
    grid.set_border_width(10)
    grid.set_column_spacing(10)
    grid.set_row_spacing(10)

    row = 0
    label = Gtk.Label(label=_("Characters"))
    label.set_tooltip_text(_("Characters that will be used as colored pixels. "))

    grid.attach(label, 0, row, 1 , 1)
    label.show()

    characters_entry = Gtk.Entry()
    characters_entry.set_width_chars(20)
    characters_entry.set_max_width_chars(80)
    characters_entry.set_text(characters)
    characters_entry.set_placeholder_text(_("Characters or file location"))
    grid.attach(characters_entry, 1, row, 1, 1)
    characters_entry.show()

    row += 1

    characters_checkbox = Gtk.CheckButton(label=_("Read characters from file"))
    characters_checkbox.set_active(source_file)
    characters_checkbox.set_tooltip_text(
        _("If set, the Characters text entry will be used as a file name, "
          "from which the characters will be read. Otherwise, the characters "
          "in the text entry will be used to render the image."))
    grid.attach(characters_checkbox, 0, row, 1, 1)
    characters_checkbox.show()

    choose_file_button = Gtk.Button(label=_("Choose text file"))
    grid.attach(choose_file_button, 1, row, 1, 1)
    choose_file_button.connect("clicked", choose_file)
    choose_file_button.show()

    row += 1

    label = Gtk.Label(label=_("Font Size(px)"))
    grid.attach(label, 0, row, 1 , 1)
    label.show()

    font_size_adj = Gtk.Adjustment.new(size, 0.0, 100.0, 1.0, 0.0, 0.0)
    font_size_spin = Gtk.SpinButton.new(font_size_adj, climb_rate=1.0, digits=0)
    font_size_spin.set_numeric(True)
    grid.attach(font_size_spin, 1, row, 1 , 1)
    font_size_spin.show()

    row += 1

    separate_checkbox = Gtk.CheckButton(label=_("Write separate CSS file"))
    separate_checkbox.set_active(separate)
    grid.attach(separate_checkbox, 0, row, 2, 1)
    separate_checkbox.show()

    row += 1

    respect_whitespace_checkbox = Gtk.CheckButton(label=_("Respect whitespace"))
    respect_whitespace_checkbox.set_active(source_file)
    respect_whitespace_checkbox.set_tooltip_text(
        _("If set, keep whitespace and newline characters "
          "so the result looks more like the text."))
    grid.attach(respect_whitespace_checkbox, 0, row, 1, 1)
    respect_whitespace_checkbox.show()

    dialog.get_content_area().add(grid)
    grid.show()

    dialog.show()
    if dialog.run() == Gtk.ResponseType.OK:
        was_canceled = False
        # Only changes the local reference, still need to return them
        characters =                    characters_entry.get_text()
        size =                            font_size_spin.get_value_as_int()
        source_file =                characters_checkbox.get_active()
        separate =                     separate_checkbox.get_active()
        respect_whitespace = respect_whitespace_checkbox.get_active()
    else:
        was_canceled = True
    dialog.destroy()
    return was_canceled, characters, size, source_file, separate, respect_whitespace



# We would expect n_drawables parameter is unnecessary with introspection but
# now that isn't working. Until issue #5312 is resolved we keep n_drawables.
def save_colorxhtml(procedure, run_mode, image, n_drawables, drawables, file, args, data):

    assert(isinstance(drawables, list))
    drawable = drawables[0]

    """
    Preflight limitations of plugin.

    The protocol for plugins should prevent some of these,
    and might in the future,
    but for now it doesn't.
    """

    # plugins do not register whether they accept multiple layers
    if len(drawables) > 1:
        error = N_("Format does not support multiple layers")
        return procedure.new_return_values(Gimp.PDBStatusType.CALLING_ERROR,
                                           GLib.Error(error))
    # expect the protocol to prevent this, so probably superfluous
    if file is None:
        error = 'No file given'
        return procedure.new_return_values(Gimp.PDBStatusType.CALLING_ERROR,
                                           GLib.Error(error))
    # Because we register image type RGB,
    # expect not to be called with alpha, but we are???
    if not (drawable.bpp() in (3, 6, 12)):  # keys in fmt_from_bpp
        error =  N_('Cannot save image with alpha channel')
        return procedure.new_return_values(Gimp.PDBStatusType.CALLING_ERROR,
                                           GLib.Error(error))
    # plugin does calculations only for integer precision
    precision = image.get_precision()
    if not (precision in (
                Gimp.Precision.U8_LINEAR,
                Gimp.Precision.U8_NON_LINEAR,
                Gimp.Precision.U8_PERCEPTUAL,
                Gimp.Precision.U16_LINEAR,
                Gimp.Precision.U16_NON_LINEAR,
                Gimp.Precision.U16_PERCEPTUAL,
                Gimp.Precision.U32_LINEAR,
                Gimp.Precision.U32_NON_LINEAR,
                Gimp.Precision.U32_PERCEPTUAL, )):
        error =  N_('Cannot save image with floating precision')
        return procedure.new_return_values(Gimp.PDBStatusType.CALLING_ERROR,
                                           GLib.Error(error))


    source_file = args.index(0)
    characters =  args.index(1)
    size =        args.index(2)
    separate =    args.index(3)
    respect_whitespace = args.index(4)

    image, drawable = scale_image_to_glyph_aspect_ratio(image)
    # image and drawable now refer to a scaled duplicate

    width = drawable.width()
    height = drawable.height()
    bpp = drawable.bpp()

    if run_mode == Gimp.RunMode.INTERACTIVE:

        GimpUi.init ("colorxhtml.py")

        # Warn user progress can be glacial (since processing per pixel.)
        if ((width * height) > 500000): # approximately 800x600 pixels
            was_canceled = show_warn_slow_dialog()
            if was_canceled:
                 return procedure.new_return_values(Gimp.PDBStatusType.CANCEL,
                                           GLib.Error())
                 # assert "Export As" dialog remains visible
                 # User can choose another format, or must Cancel it also

        was_canceled, characters, size, source_file, separate, respect_whitespace = \
           show_settings_dialog(characters, size, source_file, separate, respect_whitespace )

        # Assert settings dialog is destroyed
        # "Export As" dialog remains visible, contains progress bar
        if was_canceled:
             return procedure.new_return_values(Gimp.PDBStatusType.CANCEL,
                                       GLib.Error())

    html = open(file.peek_path(), 'w')

    if separate:
        dirname, cssfile = os.path.split(file.peek_path())
        cssfile = os.path.splitext(cssfile)[0] + '.css'
        cssname = os.path.join(dirname, cssfile)

        css = open(cssname, 'w')

    if source_file:
        characters_file = open(characters, 'r')
        raw_chars = characters_file.read()
        characters_file.close()
    else:
        raw_chars = characters

    glyph_strings = translate_and_escape_raw_data(raw_chars, respect_whitespace)
    """
    glyph_strings has some non-printable control chars removed,
    and optionally whitespace removed (printable but not visible)
    and html control chars escaped.
    glyph_strings is a list of strings.
    Each string is html for a glyph (renders in the box of a character).
    Often the string is a single character,
    but e.g. the string for an html escape is '&gt;'
    """

    if not glyph_strings:
        # file was empty or user cleared out the text entry field. Default.
        glyph_strings = list('X' * 80)

    Gimp.progress_init(_("Saving as HTML"))

    # substitute into the html style string for the html body
    style = style_def % ( size, get_background_color_name_from_gimp())

    if separate:
        ss = '<link rel="stylesheet" type="text/css" href="%s" />' % cssfile
        css.write(style)
    else:
        ss = '<style type="text/css">\n%s</style>' % style

    html.write(preamble % ss)

    colors = {}

    # Constants used for formatting the pixel color. We can handle image
    # types where each color is 8 bits, 16 bits, or 32 bit integers.
    fmt = fmt_from_bpp[bpp]
    pixel_shift = 8 * (bpp//3 - 1)

    for y, row_of_glyph_strings in RowGenerator(glyph_strings, row_count=height, row_len=width):
        # row_of_glyphs is a list of strings, each string an html string for one glyph
        #debug: print(row_of_glyph_strings)

        # required because we index by width
        assert(len(row_of_glyph_strings) == width)

        for x in range(0, width):
            pixel_bytes = drawable.get_pixel(x, y)
            pixel_tuple = struct.unpack(fmt, pixel_bytes)
            if bpp > 3:
                 pixel_tuple=(
                   pixel_tuple[0] >> pixel_shift,
                   pixel_tuple[1] >> pixel_shift,
                   pixel_tuple[2] >> pixel_shift,
                 )
            html_color = '%02x%02x%02x' % pixel_tuple
            style = glyph_style_string % html_color
            glyph_string = row_of_glyph_strings[x]

            if separate:
                if html_color not in colors:
                    css.write('span.N%s { %s }\n' % (html_color, style))
                    colors[html_color] = 1
                html.write('<span class="N%s">%s</span>' % (html_color, glyph_string))
            else:
                html.write('<span style="%s">%s</span>' % (style, glyph_string))

        html.write('\n')

        Gimp.progress_update(y / float(height))

    html.write(postamble)
    html.close()

    if separate:
        css.close()

    return Gimp.ValueArray.new_from_values([
        GObject.Value(Gimp.PDBStatusType, Gimp.PDBStatusType.SUCCESS)
    ])


class ColorXhtml(Gimp.PlugIn):
    ## Parameters ##
    __gproperties__ = {
        "source-file":(bool,
                     _("_Read characters from file, if true, or use text entry"),
                     _("_Read characters from file, if true, or use text entry"),
                      False,
                     GObject.ParamFlags.READWRITE),
        "characters": (str,
                      _("_File to read or characters to use"),
                      _("_File to read or characters to use"),
                      "XOXO",
                      GObject.ParamFlags.READWRITE),
        "font-size": (int,
                      _("Fo_nt size in pixels"),
                      _("Fo_nt size in pixels"),
                      5, 100, 10,
                      GObject.ParamFlags.READWRITE),
        "separate": (bool,
                     _("_Write a separate CSS file"),
                     _("_Write a separate CSS file"),
                      False,
                     GObject.ParamFlags.READWRITE),
         "respect_whitespace": (bool,
                      _("_Respect whitespace"),
                      _("_Respect whitespace"),
                       False,
                      GObject.ParamFlags.READWRITE)

    }

    ## GimpPlugIn virtual methods ##
    def do_query_procedures(self):
        self.set_translation_domain("gimp30-python",
                                    Gio.file_new_for_path(Gimp.locale_directory()))
        return [ 'file-colorxhtml-save' ]

    def do_create_procedure(self, name):
        procedure = None
        if name == 'file-colorxhtml-save':
            procedure = Gimp.SaveProcedure.new(self, name,
                                           Gimp.PDBProcType.PLUGIN,
                                           save_colorxhtml, None)
            procedure.set_image_types("RGB")  # ("RGB*, GRAY*")
            procedure.set_documentation (
                N_("Save as HTML containing ASCII art"),
                "Saves the image as .html that a browser shows as color ASCII art",
                name)
            procedure.set_menu_label(N_("ASCII art in HTML"))
            procedure.set_attribution("Manish Singh and Carol Spears",
                                      "(c) GPL V3.0 or later",
                                      "2003")

            procedure.set_extensions ("html");

            procedure.add_argument_from_property(self, "source-file")
            procedure.add_argument_from_property(self, "characters")
            procedure.add_argument_from_property(self, "font-size")
            procedure.add_argument_from_property(self, "separate")
            procedure.add_argument_from_property(self, "respect_whitespace")

        return procedure

Gimp.main(ColorXhtml.__gtype__, sys.argv)
