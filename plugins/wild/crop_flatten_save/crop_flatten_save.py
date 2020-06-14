#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Júlio Reis
# Copyright 2016 Júlio Reis
# License: GPL v3. See LICENSE.md or LICENSE.txt
# GIMP plugin to crop, flatten and save an image

from gimpfu import *

# lkk comment this out
#gettext.install("gimp30-python", gimp.locale_directory)

def crop_flatten_save(img, drw):
	# set up undo group
    # lkk change from gimp.pdb. => pdb.
	pdb.gimp_undo_push_group_start(img)

	# crop to selection, if there is one
	non_empty, x1, y1, x2, y2 = pdb.gimp_selection_bounds(img)
	if non_empty:
		pdb.gimp_image_crop(img, x2-x1, y2-y1, x1, y1)

	# Flatten
	img.flatten()

	# Save
	filename = pdb.gimp_image_get_filename(img)
	if filename:
		pdb.gimp_file_save(img, img.active_layer, filename, filename)
		# unset "dirty" flag, i.e. mark the image as saved
		img.clean_all()
	else:
		pdb.gimp_message( "Image has no file name, because it hadn’t been saved yet" )

	# close undo group
    # lkk change from gimp.pdb. => pdb.
	pdb.gimp_undo_push_group_end(img)

# lkk added * for image_types: some image must be open
register(
	"crop_flatten_save",
	"Crop-Flatten-Save",
	"""1. Crops an image to the current selection (if any);
2. Flattens the image;
3. Saves the image. WARNING: overwrites original image""",
	"Júlio Reis",
	"© Júlio Reis – licensed via GPL v3",
	"2016",
	"<Image>/Image/Crop-Flatten-Save",
	"*",
	[],
	[],
	crop_flatten_save,
	domain=("gimp30-python", gimp.locale_directory)
)

main()
