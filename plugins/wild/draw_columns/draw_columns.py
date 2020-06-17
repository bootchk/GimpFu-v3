#!/usr/bin/env python3
# lkk add hashbang
'''
Created on 11/04/2012
@author: Kedde
'''

from gimpfu import *

# lkk default column size 1000
def python_drawcols(timg, tdrawable, rowSize=10, columnSize=1000, fontname="Arial", fontsize=8, unit=3, textPos=20):
    gimp.context_push()
    timg.undo_group_start()

    # start plugin
    width = tdrawable.width
    height = tdrawable.height

    # draw rows - black - red -green - blue - yellow - white - purple - gray
    colors = [(0,0,0), (255,0,0), (0,255,0), (0,0,255), (255,255,0), (255,255,255), (255,0,255), (128,128,128)]
    verCounter = 0
    colorIndex = 0

    toggleTextPos = 0

    # draw rows
    while (verCounter < width):
        # CHANNEL-OP-ADD (0), CHANNEL-OP-SUBTRACT (1), CHANNEL-OP-REPLACE (2), CHANNEL-OP-INTERSECT (3)
        pdb.gimp_image_select_rectangle(timg, CHANNEL_OP_REPLACE, verCounter, 0, columnSize, height)
        color = colors[colorIndex]
        # lkk change to pdb
        # gimp.set_foreground(color)
        pdb.gimp_context_set_foreground(color)
        pdb.gimp_edit_fill(tdrawable, FOREGROUND_FILL)

        # text
        textColor = (255,255,255)
        if (color == (0,0,0)):
            textColor = (255,255,255)
        if (color == (255,255,255)):
            textColor = (0,0,0)
        #gimp.set_foreground(textColor)
        pdb.gimp_context_set_foreground(color)
        layer = pdb.gimp_text_layer_new(timg, verCounter, fontname, fontsize, unit)


        if (toggleTextPos == 0):
            toggleTextPos = 20
        else:
            toggleTextPos = 0

        layer.translate(verCounter, textPos  + toggleTextPos)
        # gimp-image-insert-layer image, layer, parent, position
        pdb.gimp_image_insert_layer(timg, layer, None, 0)
        textColor = (255,255,255)

        verCounter = verCounter + columnSize
        # change the colorIndex
        colorIndex = colorIndex + 1
        if colorIndex == len( colors ):
            colorIndex = 0

    # clean up
    timg.undo_group_end()
    gimp.displays_flush()
    gimp.context_pop()

register(
        "python_fu_drawcols",
        "draw columns",
        "draw columns",
        "Christian Thillemann",
        "Christian Thillemann",
        "1997-1999",
        "<Image>/Filters/Artistic/_DrawColumns...",
        "RGB*, GRAY*",
        [
                (PF_INT, "row_size", "Size of row in color", 10),
                (PF_INT, "column_size", "Size of column in color", 1000),
                (PF_FONT, "font", "font", "Arial"),
                (PF_INT, "font_size", "Font size", 8),
                (PF_INT, "unit_size", "Unit", 3),
                (PF_INT, "textPosition", "Text Position (y)", 20)

        ],
        [],
        python_drawcols)

main()
