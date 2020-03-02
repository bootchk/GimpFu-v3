#!/usr/bin/env python

from gimpfu import *

# use in console with
# image = gimp.image_list()[0]
# pdb.python_fu_rpg_character_sketch(image, image.layers[0])

# based on this tutorial
# https://www.youtube.com/watch?v=eLgsSN2MsMo


def sketchCharacter (image, drawable) :
    # gimp.progress_init("Sketching...")
    # steps = 10
    # gimp.progress_update(10)

    # Set up an undo group, so the operation will be undone in one step.
    # lkk gimp.pdb => pdb everywhere
    # lkk FALSE => False everywhere
    pdb.gimp_undo_push_group_start(image)

    # create two duplicates of active layer
    image.add_layer(image.active_layer.copy())
    image.add_layer(image.active_layer.copy())

    # adjust saturation of top layer
    layer = image.layers[0]
    pdb.gimp_drawable_hue_saturation(layer, HUE_RANGE_ALL, 0, 0, -100, 0)
    layer.mode = SATURATION_MODE

    # create blur on middle layer
    layer = image.layers[1]
    pdb.gimp_drawable_invert(layer, False)
    layer.mode = DODGE_MODE
    # Gauss scale is 1-500, not 100, so 10 = 10/100*500 = 50
    pdb.plug_in_gauss_rle2(image, layer, 50, 50)

    # adjust threshold of lowest layer
    layer = image.layers[2]
    # levels scale is 0-1, not 0-255, so 10 = 15/255*1 = 0.04
    pdb.gimp_drawable_levels(layer, HISTOGRAM_VALUE, .06, .06, False, 1.0, 0, 1, False)

    # flatten
    pdb.gimp_image_merge_visible_layers(image, EXPAND_AS_NECESSARY)

    # colorize (redish)
    layer = image.layers[0]
    pdb.gimp_drawable_colorize_hsl(layer, 12, 20.7, 47.5) #926a60, RGB(146,106,96)

    # cartoon
    pdb.plug_in_cartoon(image, layer, 25, 0.7)

    pdb.plug_in_autocrop(image, layer)

    # Close the undo group.
    pdb.gimp_undo_push_group_end(image)

register(
    "python_fu_rpg_character_sketch",
    "makes image look hand-drawn",
    "makes image look hand-drawn",
    "Nicholas Shewmaker",
    "Nicholas Shewmaker",
    "2019",
    "<Image>/Filters/Custom/Character Sketch",
    "*",      # Alternately use RGB, RGB*, GRAY*, INDEXED etc.
    [],
    [],
    sketchCharacter)

main()
