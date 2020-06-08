#!/usr/bin/env python
# -*- coding: utf-8 -*-
# trim-to-size.py: GIMP plugin to trim an image to the size specified
# Author: Júlio Reis
# Copyright 2016 Júlio Reis
# License: GPL v3. See LICENSE.md or LICENSE.txt

from gimpfu import *

gettext.install("gimp30-python", gimp.locale_directory)

# horizontal alignment: left, centre, or right
HALIGN_LEFT = 0
HALIGN_CENTRE = 1
HALIGN_RIGHT = 2
# vertical alignment: top, middle, or bottom
VALIGN_TOP = 0
VALIGN_MIDDLE = 1
VALIGN_BOTTOM = 2

def trim_to_size(img, drw, desired_width, desired_height, scaling, h_align, v_align):

	# set up undo group
    # lkk gimp.pgb => pdb, everywhere
	pdb.gimp_undo_push_group_start(img)

	# scaling
	if scaling:
		# calculate dimensions for scaling
		original_aspect = float(img.width) / float(img.height)
		desired_aspect = float(desired_width) / float(desired_height)
		if original_aspect < desired_aspect:
			# scale to width
			scale_factor = float(desired_width) / float(img.width)
		else:
			# scale to height
			scale_factor = float(desired_height) / float(img.height)
		scaled_width = img.width * scale_factor
		scaled_height = img.height * scale_factor
		# scale the image
		pdb.gimp_image_scale(img, scaled_width, scaled_height)

	# cropping
	# calculate starting position for cropping
	width_to_trim = img.width - desired_width
	height_to_trim = img.height - desired_height
	# calculate horizontal position for cropping
	switcher = {
		HALIGN_LEFT: lambda x: 0,
		HALIGN_CENTRE: lambda x: x/2,
		HALIGN_RIGHT: lambda x: x,
	}
	crop_x = (switcher.get(h_align))(width_to_trim)
	# calculate vertical position for cropping
	switcher = {
		VALIGN_TOP: lambda x: 0,
		VALIGN_MIDDLE: lambda x: x/2,
		VALIGN_BOTTOM: lambda x: x,
	}
	crop_y = (switcher.get(v_align))(height_to_trim)

	pdb.gimp_image_crop(img, desired_width, desired_height, crop_x, crop_y)

	# close undo group
	pdb.gimp_undo_push_group_end(img)

# lkk image_type "" => "*"
register(
	"trim_to_size",
	"Trim to Size",
	_("""Trims an image to the specified dimensions, with optional scaling"""),
	"Júlio Reis",
	"© Júlio Reis – " + _("licensed via GPL v3"),
	"2016",
	_("<Image>/Image/Trim to size"),
	"*",
    # lkk give unique names to formal parameters, number2 and option2
	[
		(PF_INT, "number", _("Width"), 1280),
		(PF_INT, "number2", _("Height"), 625),
		(PF_BOOL, "scale", _("Allow scaling"), True),
		(PF_OPTION, "option", _("Horizontal alignment:"), 1, (_("Left"), _("Center"), _("Right") )),
		(PF_OPTION, "option2", _("Vertical alignment:"), 1, (_("Top"), _("Middle"), _("Bottom") ))
	],
	[],
	trim_to_size,
	domain=("gimp30-python", gimp.locale_directory)
)

main()
