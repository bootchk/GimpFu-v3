#!/usr/bin/env python

# Font texture generator in GIMP. Python

from gimpfu import *

def prepare_character_array():
    lines = [None] * 16
    for i in range(0, 16):
        chars = [None] * 16
        for j in range(0, 16):
            # lkk python 2 unichr() => python 3 chr()
            # chars[j] = str(unichr(i*16 + j))
            chars[j] = str(chr(i*16 + j))
        lines[i] = ''.join(chars);
    return lines

def generate(font, size, color) :
    # Prepare the image:
    image_size = int(size * 16)
    img = gimp.Image(image_size, image_size, RGB)

    pdb.gimp_context_push()

    gimp.set_foreground(color)

    lines = prepare_character_array()
    # Draw bitmap
    for i in range(0, 16):
        # Create a new text layer for each line
        layer = pdb.gimp_text_fontname(img, None, 0, size * i, lines[i], 0,
                                   True, size, PIXELS, font)

    gimp.Display(img)
    gimp.displays_flush()

    pdb.gimp_context_pop()

register(
    "python_fu_font_bitmap",
    "Bitmap for mono font",
    "Create a bitmap 16x16 character image with font",
    "Sergii Iarovyi",
    "CC0",
    "2018",
    "Font bitmap",
    "",
    [
        (PF_FONT, "font", "Font face", "Press Start 2P Medium"),
        (PF_SPINNER, "size", "Font size", 16, (1, 3000, 1)),
        (PF_COLOR, "color", "Text color", (1.0, 1.0, 1.0))
    ],
    [],
    generate,
    menu="<Image>/File/Create")

main()
