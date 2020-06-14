#!/usr/bin/env python

# tile_indexer.py: GIMP plug-in for adding indexed grids to 2D tilesets.

# Copyright (C) 2020 by Canaan Manley

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from gimpfu import *

def add_indexed_grid_layer(image, layer, tileWidth, tileHeight, color, shouldAddIndices, font, fontSize):
    pdb.gimp_selection_none(image)
    gridLayer = pdb.gimp_layer_new_from_visible(image, image, 'TileGrid')
    pdb.gimp_image_insert_layer(image, gridLayer, None, -1)
    pdb.gimp_selection_all(image)
    pdb.gimp_edit_clear(gridLayer)
    pdb.gimp_selection_none(image)
    tileWidth = int(tileWidth)
    tileHeight = int(tileHeight)
    draw_grid_lines(gridLayer, tileWidth, tileHeight, color)
    if shouldAddIndices:
        add_grid_indices(image, gridLayer, tileWidth, tileHeight, color, font, fontSize)
    pdb.gimp_displays_flush()
    return


def draw_grid_lines(layer, tileWidth, tileHeight, color):
    set_pencil(color)
    width = int(layer.width)
    height = int(layer.height)
    for y in range(tileHeight, height, tileHeight):
        lineStart = [0, y]
        lineEnd = [layer.width, y]
        line = lineStart + lineEnd
        pdb.gimp_pencil(layer, 4, line)
    for x in range(tileWidth, width, tileWidth):
        lineStart = [x, 0]
        lineEnd = [x, layer.height]
        line = lineStart + lineEnd
        print(line)
        pdb.gimp_pencil(layer, 4, line)


def add_grid_indices(image, layer, tileWidth, tileHeight, color, font, fontSize):
    set_pencil(color)
    centerOfTile = [int(tileWidth/2), int(tileHeight/2)]
    centerOfText = int(fontSize/2)
    width = int(layer.width)
    height = int(layer.height)
    index = 0
    lastTextLayer = None
    for y in range(centerOfTile[1], height, tileHeight):
        for x in range(centerOfTile[0], width, tileWidth):
            lastTextLayer = pdb.gimp_text_fontname(
                image,
                layer,
                x - centerOfText,
                y - centerOfText,
                str(index),
                0,
                False,
                fontSize,
                PIXELS,
                font
            )
            index += 1

    pdb.gimp_floating_sel_anchor(lastTextLayer)


def set_pencil(color):
    pdb.gimp_context_set_brush('1. Pixel')
    pdb.gimp_context_set_brush_size(1)
    pdb.gimp_context_set_opacity(100)
    pdb.gimp_context_set_foreground(color)


register(
    'python_fu_tile_indexer',
    'Add indexed grid layer',
    'Adds an indexed grid layer for tilesets',
    'Canaan Manley',
    'Canaan Manley',
    '2020',
    '<Image>/Layer/Add Indexed Grid',
    '*',
    [
        # lkk default tile size larger for testing convenience
        # lkk TRUE => True
        (PF_SPINNER, 'tileWidth', 'Tile Width:', 512, (1, 512, 1)),
        (PF_SPINNER, 'tileHeight', 'Tile Height:', 512, (1, 512, 1)),
        (PF_COLOR, 'color', 'Color:', (255, 255, 255)),
        (PF_TOGGLE, 'shouldAddIndices', 'Add Indices:', True),
        (PF_FONT, 'font', 'Font:', 'Sans Bold'),
        (PF_SPINNER, 'fontSize', 'Font Size (Pixels):', 16, (1, 48, 1))
    ],
    [],
    add_indexed_grid_layer
)

main()
