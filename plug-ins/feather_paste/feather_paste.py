#! /usr/bin/env python
# coding: utf-8

"""
PLUG-in for gimp 2.8 and 2.9
(might work with previous versions)

Allows one to paste the contents of the
clipboard in an image with its contents
feathered from the border.

The ammoutn of feathreing is selected interactively
during the Plug-in execution, in a call to
the Gaussian Blur plug-in.

WHen the Gaussian blur dialog pops-up, one is free
to select the pasted temporary layer
on the Layers dialog and move it around to the
desired location.



"""

from gimpfu import *

def feathered_paste(img, layer):
    pdb.gimp_image_undo_group_start(img)
    sel = pdb.gimp_edit_paste(layer, False)
    #lkk Fails if clipboard is empty, i.e. this plugin is not user friendly
    pdb.gimp_floating_sel_to_layer(sel)
    pdb.gimp_layer_resize_to_image_size(sel)
    # lkk ADD_ALPHA_TRANSFER_MASK => ADD_MASK_ALPHA_TRANSFER
    mask = pdb.gimp_layer_create_mask(sel, ADD_MASK_ALPHA_TRANSFER)
    pdb.gimp_layer_add_mask(sel, mask)
    pdb.gimp_displays_flush()
    # this should be a call to the
    # gegl plug-in to allow for on-screen preview
    pdb.plug_in_gauss(img, mask, 40, 40, 1, run_mode=False)

    # level the mask so that it actually is 0 at the pasted image border
    # (else it will be more like

    # lkk change int to floats, and add "clamp" parameters bool
    """
    pdb.gimp_levels(mask, HISTOGRAM_VALUE,
                    128, 255, # input levels
                    1, #gamma - applying a high gaussian blur and haking
                       # a way to see this gamma on screen would be nice
                    0, 255 # output levels
                   )
    """
    pdb.gimp_levels(mask, HISTOGRAM_VALUE,
                    0.5, 1.0, # input levels
                    True,   # clamp
                    1, #gamma - applying a high gaussian blur and haking
                       # a way to see this gamma on screen would be nice,
                    0.0, 1.0, # output levels,
                    True
                   )
    # one might prefer to comment the line bellow and remaing with the
    # pasted selection in a separate layer:
    pdb.gimp_image_merge_down(img, sel, EXPAND_AS_NECESSARY)
    pdb.gimp_image_undo_group_end(img)

register(
     "feather_paste",
     "Feathered paste",
     "Allows one to feather a pasted object "
     "borders before commiting to the image",
     "João S. O. Bueno",
     "Creative Commons v 3.0 attribution required",
     " 2013",
     "Feathered paste",
    "*",
     [
        (PF_IMAGE, "img", "Input image", None),
        (PF_DRAWABLE, "layer", "Input layer", None)
     ],
     [],
     feathered_paste,
     menu="<Image>/Edit"
    )

main()
