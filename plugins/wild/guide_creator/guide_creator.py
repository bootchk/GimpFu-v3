
# GIMP plug-in for creating guides based on simple instructions or using active layer or selection as reference.
# (c) Rumen Belev 2018
#
#   History:
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

# Installation:

# Place the guide_creator.py file in .gimp-2.8\plug-ins\ folder.
# In Gimp, the plug-in is located in Image - > Guides -> Guide Creator menu.

# Usage:

# Guides can be created using "Add guides from:" menu.
# "Formula" option:
# You can add guides by describing them using text description. H for horisontal (-) guide and V for vertical (|) guide followed by number (indeger or float) describing guide's position starting from the top left corner of the image. Position can be percent of the image width or height or distance in pixels, depending on the toggle "Use percent/pixels".
# Example: H25V36.4H50
# This will add horiszontal guides at 25%( or at 25-th pixel), 50%(or at 50 pixel) along Y axis and a vertical guide at 36.4% (or 36-th pixel) along X axis.
# Another use of "Formula" is equidistant guide distribution. In this case use only letters to indicate the number of guides of different type.
# Example: HHHVVVVV
# This will add a 5x3 grid of guides.
# Avoid spaces or other letters in the formula for accurate results.
# "Include mirrored guides" toggle can add also guides that are symmetrical to those from the formula.
# "Remove previous guides" toggle can clear existing guides before adding the new ones.
# The rest of the options use active layer or selection bounds as reference for adding new guides.

from gimpfu import *
import re

def guides_from_formula(image, list, h, w, units, mirror, dh, dv):
	if len(list)%2 == 0:
        # lkk use int division / => //
		for i in range(len(list)//2):
			if list[i*2+1].isalnum:
				pos = float(list[i*2+1])
				if units == True:
					h_guide_pos = int(h*(pos/100))
					v_guide_pos = int(w*(pos/100))
				else:
					h_guide_pos = int(pos)
					v_guide_pos = int(pos)
				if re.match('[hH]',list[i*2]):
					image.add_hguide(h_guide_pos)
					if mirror == True:
						image.add_hguide(h - h_guide_pos)
				if re.match('[vV]',list[i*2]):
					image.add_vguide(v_guide_pos)
					if mirror == True:
						image.add_vguide(w - v_guide_pos)
			else:
				break
	if dh > 0:
		space = int(h/(dh+1))
		pos = space
		for i in range(dh):
			image.add_hguide(pos)
			pos += space
	if dv > 0:
		space = int(w/(dv+1))
		pos = space
		for i in range(dv):
			image.add_vguide(pos)
			pos += space

def guide_creator(image, drawable, mode, formula, units, mirror, clear_guides):
	image.undo_group_start()
	if clear_guides:
		pdb.script_fu_guides_remove(image, drawable)
	formula_params = []
	w = image.width
	h = image.height
	non_empty, x1, y1, x2, y2 = pdb.gimp_selection_bounds(image)
	dist_h = 0
	dist_v = 0
	if len(formula):
		if formula.isalpha():
			pat_h = re.compile('[hH]')
			pat_v = re.compile('[vV]')
			dist_h = len(re.findall(pat_h,formula))
			dist_v = len(re.findall(pat_v,formula))
		else:
			formula_params = re.split(r'(\d+)',formula)[:-1]
	if mode==0:
		guides_from_formula(image, formula_params, h, w, units, mirror, dist_h, dist_v)
	if mode==1:
		image.add_hguide(drawable.offsets[1])
		image.add_vguide(drawable.offsets[0])
	if mode==2:
		image.add_hguide(drawable.offsets[1])
		image.add_vguide(drawable.offsets[0])
		image.add_hguide(drawable.offsets[1]+drawable.height)
		image.add_vguide(drawable.offsets[0]+drawable.width)
	if mode==3:
		image.add_hguide(int(drawable.offsets[1]+drawable.height/2))
		image.add_vguide(int(drawable.offsets[0]+drawable.width/2))
	if mode==4:
		if non_empty == True:
			image.add_vguide(x1)
			image.add_hguide(y1)
	if mode==5:
		if non_empty == True:
			image.add_vguide(x1)
			image.add_hguide(y1)
			image.add_vguide(x2)
			image.add_hguide(y2)
	if mode==6:
		if non_empty == True:
			image.add_vguide(int(x1+(x2-x1)/2))
			image.add_hguide(int(y1+(y2-y1)/2))
	image.undo_group_end()
	return
register(
   # lkk _ => -
   "guide-creator",
   "Add vertical and/or horisontal guides in various ways!",
   "Sellect method from Add menu and adjust the settings to add guides to the image",
   "Rumen Belev",
   "copyright Rumen Belev",
   "2018",
   "Guide Creator",
   "*",
   [
      (PF_IMAGE, "image", "Input image", None),
      (PF_DRAWABLE, "drawable", "Input drawable", None),
	  (PF_OPTION, "mode", "Add gudes from:", 0, ("Formula","Layer Position", "Layer Bounds", "Layer Center","Selection Position", "Selection Bounds", "Selection Center")),
	  (PF_STRING, "formula", "Formula:\nNo spaces! Try:\nH5V35H40.5V18\nHHHVHVVVV", "H3.5H5V3.5V5V16.25"),
	  (PF_BOOL, "units", "Use percent(Yes)/pixels(No)", True),
	  (PF_BOOL, "mirror", "Include mirrored guides", False),
	  (PF_BOOL, "clear_guides", "Remove previous guides", False),
   ],
   [],
   guide_creator, menu="<Image>/Image/Guides/")
main()
