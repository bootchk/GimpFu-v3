#!/usr/bin/env python3
# lkk add hashbang


import math
from gimpfu import *

def clothify(timg, tdrawable, bx=9, by=9, azimuth=135, elevation=45, depth=3):
    width = tdrawable.width
    height = tdrawable.height

    img = gimp.Image(width, height, RGB)
    # lkk was disable_undo
    img.undo_disable()

    layer_one = gimp.Layer(img, "X Dots", width, height, RGB_IMAGE,
                           100, NORMAL_MODE)
    img.insert_layer(layer_one)
    pdb.gimp_edit_fill(layer_one, BACKGROUND_FILL)

    pdb.plug_in_noisify(img, layer_one, 0, 0.7, 0.7, 0.7, 0.7)

    layer_two = layer_one.copy()
    layer_two.mode = MULTIPLY_MODE
    layer_two.name = "Y Dots"
    img.insert_layer(layer_two)

    # lkk add float()
    pdb.plug_in_gauss_rle(img, layer_one, float(bx), 1, 0)
    pdb.plug_in_gauss_rle(img, layer_two, float(by), 0, 1)

    img.flatten()

    bump_layer = img.active_layer

    pdb.plug_in_c_astretch(img, bump_layer)
    pdb.plug_in_noisify(img, bump_layer, 0, 0.2, 0.2, 0.2, 0.2)
    #lkk add float()
    pdb.plug_in_bump_map(img, tdrawable, bump_layer, float(azimuth),
                         float(elevation), depth, 0, 0, float(0), float(0), True, False, 0)

    gimp.delete(img)

register(
        "python-fu-clothify",
        "Make the image look like it is printed on cloth",
        "Make the specified layer look like it is printed on cloth",
        "James Henstridge",
        "James Henstridge",
        "1997-1999",
        "_Clothify...",
        "RGB*, GRAY*",
        [
            (PF_IMAGE, "image", "Input image", None),
            (PF_DRAWABLE, "drawable", "Input drawable", None),
            (PF_INT, "x-blur", "X blur", 9),
            (PF_INT, "y-blur", "Y blur", 9),
            (PF_INT, "azimuth", "Azimuth", 135),
            (PF_INT, "elevation", "Elevation", 45),
            (PF_INT, "depth", "Depth", 3)
        ],
        [],
        clothify, menu="<Image>/Filters/Artistic")

main()
