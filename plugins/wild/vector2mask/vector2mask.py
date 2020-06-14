

# GIMP plug-in to convert or update path to layer mask.
# (c) Rumen Belev 2018
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

# Place the vector2mask.py file in .gimp-2.8\plug-ins\ folder.
# In Gimp, right click on active layer and run "Vector to Mask" command.

# Usage:
# The plug-in requires the names of the layer and the path to use as mask to be identical.
# Select the layer, right click and choose "Vector to Mask" command.
# This will create or update the existing mask for the layer.
# The mask is feathered by 2 pixels and can be adjusted additionally with the Levels Tool.
# If you don't want this step to be performed comment out the line in the script below.

from gimpfu import *

def plugin_vector2mask(image, drawable):
    #create list of existing vectors for the active image
    vectors_list = image.vectors
    # loop the list to see if any path has the same name as the active layer
    for v in vectors_list:
        if(drawable.name == v.name):
            #if found - check if the layer already have mask and destroy it if true
            if (drawable.mask != None):
                drawable.remove_mask(1) # 1 - removes mask, 0 - applies it
            #lkk obsolete
            # v.to_selection()
            image.select_item( CHANNEL_OP_REPLACE, v)
            # optional feather selection by 2, comment out the line below to disable it
            pdb.plug_in_gauss_rle2(image,image.selection,2.0,2.0)
            # 4 - creates mask from selection
            # lkk 4=> ADD_MASK_SELECTION
            # lkk break into two statements
            # drawable.add_mask(drawable.create_mask(4))
            mask = drawable.create_mask(ADD_MASK_SELECTION)
            drawable.add_mask(mask)
            pdb.gimp_selection_none(image)
    return

# lkk in procname: _ => -
register(
   "plugin-vector2mask",
   "Convert or update path to layer mask",
   "Convert or update path to layer mask if the name of both is the same. Adds feather of 2px to the mask",
   "Rumen Belev",
   "copyright Rumen Belev",
   "2018",
   "Vector to Mask",
   "*",
   [
      (PF_IMAGE, "image", "Input image", None),
      (PF_DRAWABLE, "drawable", "Input drawable", None)
   ],
   [],
   plugin_vector2mask,
   # lkk appears in popup menu in Layers dialog
   menu="<Layers>")
main()
