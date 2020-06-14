#! /usr/bin/env python
# coding: utf-8

"""
PLUG-in for gimp 2.8 and 2.9
(might work with previous versions)

Adds all visible paths to the selection -

This way it precludes one of having to
do so manually, or having combine the visible paths
and dean deal with the in/out filling issues.


"""

from gimpfu import *

def visible_paths_to_selection(img, selected):
    pdb.gimp_image_undo_group_start(img)

    pdb.gimp_selection_none(img)
    for vector in img.vectors:
        if not vector.visible:
            continue
        pdb.gimp_image_select_item(img, CHANNEL_OP_ADD, vector)

    pdb.gimp_image_undo_group_end(img)

register(
     "visible_paths_to_selection",
     "Visible Paths To Selection",
     "Merges all visible paths to the selection ",
     "João S. O. Bueno",
     "Creative Commons v 3.0 attribution required",
     "2013",
     "Visible Paths To Selection",
    "*",
     [
        (PF_IMAGE, "img", "Selected Image", None),
        (PF_VECTORS, "selected", "Selected path", None),
     ],
     [],
     visible_paths_to_selection,
     menu="<Vectors>"
    )

main()
