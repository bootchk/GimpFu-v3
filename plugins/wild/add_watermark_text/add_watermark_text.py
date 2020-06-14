#!/usr/bin/env python
# -*- coding: <utf-8> -*-
# Author: Ethan Blackwelder
# Copyright 2013 Ethan Blackwelder
# License: MIT (http://eib.mit-license.org/)
# Version 0.1
# GIMP compatibilty ???
# PyGIMP plugin to add watermark/copyright text

from gimpfu import *
import getpass

SIZE_IN_PIXELS = 0
SIZE_IN_POINTS = 1

# lkk add drawable
def add_watermark_text(img, drawable, text, points, antialias, letter_spacing, fontname, color):
    text = u'\xa9' + " " + text
    x = 0
    y = 0
    border = -1

    #undo-start
    pdb.gimp_context_push();
    pdb.gimp_image_undo_group_start(img);

    #create text-layer (adds it to the image)
    text_layer = pdb.gimp_text_fontname(img, None, x, y, text, border, antialias, points, SIZE_IN_POINTS, fontname)

    layer_margins = 5
    x = layer_margins #left
    # lkk rearrange for testing
    y = img.height - layer_margins
    y = y - text_layer.height
    # y = img.height - text_layer.height - layer_margins #bottom

    pdb.gimp_text_layer_set_color(text_layer, color)
    pdb.gimp_text_layer_set_text(text_layer, text)
    pdb.gimp_item_set_name(text_layer, "Watermark")
    pdb.gimp_layer_set_offsets(text_layer, x, y)
    pdb.gimp_text_layer_set_letter_spacing(text_layer, letter_spacing)

    #undo-end
    pdb.gimp_image_undo_group_end(img);
    pdb.gimp_context_pop();


register(
    proc_name=("python-fu-add-watermark-text"),
    blurb=("Adds watermark text"),
    help=("Adds a text layer with watermark-friendly defaults."),
    author=("Ethan Blackwelder"),
    copyright=("Ethan Blackwelder"),
    date=("2013"),
    label=("Add Watermark Text"),
    imagetypes=("*"),
    params=[
        (PF_IMAGE, "img", "Image", None),
        (PF_DRAWABLE, "drawable", "Input drawable", None), # lkk
        (PF_TEXT, "copyright", "Copyright Owner", getpass.getuser()),
        (PF_INT, "points", "Size (pts)", 100),
        (PF_BOOL, "antialias", "Antialias", True),
        (PF_INT, "letter_spacing", "Letter Spacing", -3),
        (PF_FONT, "fontname", "Font Name", "Sans"),
        (PF_COLOR, "color", "Color", (255, 255, 255)),
        ],
    results=[],
    function=(add_watermark_text),
    menu=("<Image>/Image"),
    domain=("gimp20-python", gimp.locale_directory)
    )

main()
