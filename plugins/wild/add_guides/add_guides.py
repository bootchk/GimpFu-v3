#!/usr/bin/env python3
# lkk add hashbang

# lkk omit   #![path to Gimp application]/GIMP-2.10.app/Contents/MacOS/python
from gimpfu import *
# lkk omit     import gimp

DIRECTION_HORIZONTAL    = "Horizontal"
DIRECTION_VERTICAL      = "Vertical"
DIRECTION_BOTH          = "Both"
DIRECTION_LIST          = [DIRECTION_BOTH, DIRECTION_VERTICAL, DIRECTION_HORIZONTAL]

SPACE_UNIT_PIXEL        = "Pixel"
SPACE_UNIT_PERCENTAGE   = "Percentage"
SPACE_UNIT_LIST         = [SPACE_UNIT_PIXEL, SPACE_UNIT_PERCENTAGE]

def python_add_guides(image, drawable, direction_index, space, space_unit_index):
    direction = DIRECTION_LIST[direction_index]
    space_unit = SPACE_UNIT_LIST[space_unit_index]

    if direction == DIRECTION_HORIZONTAL or direction == DIRECTION_BOTH:
        if space_unit == SPACE_UNIT_PERCENTAGE:
            space_in_pixel = (float(image.height) / 100.0) * space
        else:
            space_in_pixel = space

        horizontal_position = 0
        while horizontal_position < image.height:
            #lkk subscripts => call, gimp.pdb => pdb, - => _
            pdb.gimp_image_add_hguide(image, horizontal_position)
            horizontal_position += space_in_pixel

        # lkk original    gimp.pdb["gimp-image-add-hguide"](image, image.height)
        pdb.gimp_image_add_hguide(image, image.height)

    if direction == DIRECTION_VERTICAL or direction == DIRECTION_BOTH:
        if space_unit == SPACE_UNIT_PERCENTAGE:
            space_in_pixel = (float(image.width) / 100.0) * space
        else:
            space_in_pixel = space

        vertical_position = 0
        while vertical_position < image.width:
            #gimp.pdb["gimp-image-add-vguide"](image, vertical_position)
            pdb.gimp_image_add_vguide(image, vertical_position)
            vertical_position += space_in_pixel

        #lkk original   gimp.pdb["gimp-image-add-vguide"](image, image.width)
        pdb.gimp_image_add_vguide(image, image.width)


register(
        "python_fu_add_guides",
        "Add multiple guides with same space in between",
        "Add multiple guides with same space in between",
        "Pin-Chou Liu",
        "Pin-Chou Liu",
        "2019",
        "<Image>/Image/Guides/Add Guides...",
        "*",
        # lkk make reasonable defaults: 0 space in between is infinite loop
        [
            (PF_OPTION, "direction", "guides direction", 0, DIRECTION_LIST),
            (PF_FLOAT, "space", "space in between", 100.0),
            (PF_OPTION, "space_unit", "unit of space in between", 0, SPACE_UNIT_LIST),
        ],
        [],
        python_add_guides)


main()
