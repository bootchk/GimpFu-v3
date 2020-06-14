#!/usr/bin/env python
# -*- coding: <utf-8> -*-
# Author: Ethan Blackwelder
# Copyright 2013 Ethan Blackwelder
# License: MIT (http://eib.mit-license.org/)
# Version 0.1
# GIMP compatibilty ???
# PyGIMP plugins to create scaled layers:
#  - create a new layer from visible, scaled down to a maximum dimension
#  - create a new layer from an existing layer, scaled down to a maximum dimension


from gimpfu import *
import os

def scale_down_layer(layer, max_dimension):
    width = layer.width
    height = layer.height
    if height > 0 and width > max_dimension or height > max_dimension:
        perspective = float(width) / height
        new_width = min(width, max_dimension)
        new_height = int(new_width * perspective)
        if new_height > max_dimension and perspective > 0:
            new_height = max_dimension
            new_width = int(new_height / perspective)
        # lkk TRUE => True
        pdb.gimp_layer_scale(layer, new_height, new_width, True)

# lkk added drawable arg
def create_scaled_layer_from_visible(img, drawable, max_dimension = 1200):
    layer_name = "Visible @%d" % max_dimension
    layer = pdb.gimp_layer_new_from_visible(img, img, layer_name)
    img.add_layer(layer)
    scale_down_layer(layer, max_dimension)
    img.active_layer = layer

def duplicate_to_scaled_layer(img, old_layer, max_dimension = 1200):
    layer_name = old_layer.name + " @%d" % max_dimension
    layer = pdb.gimp_layer_new_from_drawable(old_layer, img)
    pdb.gimp_item_set_name(layer, layer_name)
    img.add_layer(layer)
    scale_down_layer(layer, max_dimension)
    img.active_layer = layer

register(
    proc_name=("python-fu-create-scaled-layer-from-visible"),
    blurb=("Create Scaled Layer from Visible"),
    help=("Creates a new layer (from visible) and scales down the layer to some maximum dimension."),
    author=("Ethan Blackwelder"),
    copyright=("Ethan Blackwelder"),
    date=("2013"),
    label=("Create Scaled Layer From Visible"),
    imagetypes=("*"),
    params=[
        (PF_IMAGE, "img", "Image", None),
        (PF_LAYER, "old_layer", "Ignored", None),   # lkk added this
        (PF_INT, "max_dimension", "Max Dimension", 1200)
        ],
    results=[],
    function=(create_scaled_layer_from_visible),
    menu=("<Image>/Layer"),
    domain=("gimp20-python", gimp.locale_directory)
    )

register(
    proc_name=("python-fu-duplicate-to-scaled-layer"),
    blurb=("Duplicate to Scaled Layer"),
    help=("Duplicates the current layer and scales down the layer to some maximum dimension."),
    author=("Ethan Blackwelder"),
    copyright=("Ethan Blackwelder"),
    date=("2013"),
    label=("Duplicate to Scaled Layer"),
    imagetypes=("*"),
    params=[
        (PF_IMAGE, "img", "Image", None),
         (PF_LAYER, "old_layer", "Ignored", None),
        (PF_INT, "max_dimension", "Max Dimension", 1200)
        ],
    results=[],
    function=(duplicate_to_scaled_layer),
    menu=("<Layers>"),
    domain=("gimp20-python", gimp.locale_directory)
    )

main()
