#!/usr/bin/env python3
# lkk add hashbang

#   Gimp-Python - allows the writing of Gimp plugins in Python.
#   Copyright (C) 1997  James Henstridge <james@daa.com.au>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.

from gimpfu import *

# v2 gettext.install("gimp20-python", gimp.locale_directory, unicode=True)
gettext.install("gimp30-python", gimp.locale_directory)

def shadow_bevel(img, drawable, blur, bevel, do_shadow, drop_x, drop_y):
    # disable undo for the image
    img.undo_group_start()

    # copy the layer
    # v2 shadow = drawable.copy(True)
    # lkk drawable.copy is not specialized to have param add_alpha
    # doesn't it copy alpha also, so technically copy(True) not needed?
    # TODO specialize copy() to have extra param, I think I already did that
    shadow = drawable.copy()
    img.insert_layer(shadow, position=img.layers.index(drawable) + 1)
    shadow.name = drawable.name + " shadow"
    shadow.lock_alpha = False

    # threshold the shadow layer to all white
    # lkk comment out, needs work
    # ??? pdb.gimp_drawable_threshold(shadow, foo, 0.0, 1.0)
    # pdb.gimp_threshold(shadow, 0, 255)
    # lkk replace threshold with fill
    pdb.gimp_drawable_fill(shadow, WHITE_FILL)


    # blur the shadow layer
    pdb.plug_in_gauss_iir(img, shadow, blur, True, True)

    # do the bevel thing ...
    if bevel:
        pdb.plug_in_bump_map(img, drawable, shadow, 135, 45, 3,
                             0, 0, 0, 0, True, False, 0)

    # make the shadow layer black now ...
    pdb.gimp_drawable_invert(shadow, False)

    # translate the drop shadow
    shadow.translate(drop_x, drop_y)

    if not do_shadow:
        # delete shadow ...
        gimp.delete(shadow)

    # enable undo again
    img.undo_group_end()


register(
    "python-fu-shadow-bevel",
    N_("Add a drop shadow to a layer, and optionally bevel it"),
    "Add a drop shadow to a layer, and optionally bevel it",
    "James Henstridge",
    "James Henstridge",
    "1999",
    N_("_Drop Shadow and Bevel..."),
    "RGBA, GRAYA",
    [
        (PF_IMAGE, "image", "Input image", None),
        (PF_DRAWABLE, "drawable", "Input drawable", None),
        (PF_SLIDER, "blur",   _("_Shadow blur"), 6, (1, 30, 1)),
        (PF_BOOL,   "bevel",  _("_Bevel"),       True),
        (PF_BOOL,   "shadow", _("_Drop shadow"), True),
        (PF_INT,    "drop-x", _("Drop shadow _X displacement"), 3),
        (PF_INT,    "drop-y", _("Drop shadow _Y displacement"), 6)
    ],
    [],
    shadow_bevel,
    menu="<Image>/Filters/Light and Shadow/Shadow",
    domain=("gimp20-python", gimp.locale_directory)
    )

main()
