#!/usr/bin/env python
from gimpfu import *

def special_crop(image):
        #lkk add parens on print
        print("Start")
        pdb = gimp.pdb
        top = pdb.gimp_image_find_next_guide(image, 0)
        top_y = pdb.gimp_image_get_guide_position(image,top)
        bottom = pdb.gimp_image_find_next_guide(image, top)
        bottom_y = pdb.gimp_image_get_guide_position(image,bottom)
        if top_y > bottom_y:
                temp_y = top_y
                top_y = bottom_y
                bottom_y = temp_y
        print ("Cutting from", top_y,"to",bottom_y)
        pdb.gimp_rect_select(image, 0, top_y, image.width, bottom_y-top_y, CHANNEL_OP_REPLACE, FALSE, 0)
        pdb.gimp_edit_copy(image.active_drawable)
        image2 = pdb.gimp_edit_paste_as_new()
        new_filename = image.filename[0:-4]+"_cut.jpg"
        pdb.file_jpeg_save(image2, image2.active_drawable, new_filename, "raw_filename", 0.9, 0.5, 0, 0, "New file", 0, 0, 0, 0)
        pdb.gimp_image_delete(image2)

register(
    "python-fu-special-crop",
    "Crop an image",
    "Crops the image.",
    "Tomasz Muras",
    "Tomasz Muras",
    "2011",
    "Special crop",
    "*",
    [
        (PF_IMAGE, "image","Input image", None),
    ],
    [],
    special_crop,
    menu="<Image>/Filters",
    )

main()
