#!/usr/bin/env python

#   Gimp-Python - allows the writing of Gimp plugins in Python.
#   Copyright (C) 2005  Werner Hartnagel <info@dotmagic.de>
#

software_license="""
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
"""

from gimpfu import *
import sys

def python_fu_fisheye(img, drawable, scale, border, border_color):

	# Find the area that has been selected in the original image
	img_is_sel, img_x1, img_y1, img_x2, img_y2 = pdb.gimp_selection_bounds(img)
	if  not img_is_sel:
		pdb.gimp_message("FATAL: Missing eclipse selection in Image!")

	else:
		# Disable Undo
		img.undo_group_start()

		img_width = img_x2 - img_x1
		img_height = img_y2 - img_y1
		width = img_width * scale
		height = img_height * scale
		w = ((img_x2-img_x1) / 2) - width / 2
		h = ((img_y2-img_y1) / 2) - height / 2

		# Copy the selected area
		#pdb.gimp_selection_shrink(img, border)
		#pdb.gimp_selection_feather(img, 0);
		pdb.gimp_edit_copy(drawable)

		# Create a new layer and set the size of the layer = the size of the initial selection
		layer = gimp.Layer(img, "fisheye",img_x2-img_x1 , img_y2-img_y1, 0, 100, 0)
		img.add_layer(layer, 0)
		layer.add_alpha()

		# Add the copied selection to the layer, and the layer to the image
		layer.fill(TRANSPARENT_FILL)
		layer.set_offsets(int(img_x1), int(img_y1))
		pdb.gimp_edit_paste(layer, 1)
		pdb.gimp_floating_sel_anchor(pdb.gimp_image_get_floating_sel(img))
		pdb.plug_in_whirl_pinch(img, layer, 0, -1, 2)
		pdb.gimp_layer_scale(layer, width, height, 0)
		layer.set_offsets(int(img_x1+w), int(img_y1+h))
		pdb.gimp_ellipse_select(img, img_x1+w, img_y1+h, width, height, CHANNEL_OP_REPLACE, True, 1, 1)
		pdb.gimp_ellipse_select(img, img_x1+w+border/2, img_y1+h+border/2, width-border, height-border, CHANNEL_OP_SUBTRACT, True, 1, 1)
		pdb.gimp_edit_bucket_fill(layer, FG_BUCKET_FILL, NORMAL_MODE, 100, 0, 0, 0, 0)
	#	print img_x1, img_y1, width, height

		#cell = img.merge_visible_layers(1)
		#img.merge_visible_layers(1)
		pdb.gimp_selection_none(img)

		# Enable Undo
		img.undo_group_end()

# Register with The Gimp
register(
	"python_fu_fisheye",
	"Create a Layer with a Fisheye Effect",
	"Create a Layer with a Fisheye Effect from a eclipse selection",
	"Werner Hartnagel",
	"(c) 2005, Werner Hartnagel",
	"2005-08-28",
	"<Image>/Python-Fu/Create Layers/Fisheye",
	"RGB*, GRAY*",
	[
		(PF_FLOAT, 'scale', 'Scale Factor: ', 2.2),
		(PF_SPINNER, 'border', 'Border: ', 2, (0, 20, 1)),
		(PF_COLOR, 'border_color', 'BorderColor: ', (0,0,0))
	],
	[],
	python_fu_fisheye);

main()
