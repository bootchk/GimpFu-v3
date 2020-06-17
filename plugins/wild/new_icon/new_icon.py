#!/usr/bin/env python3
# lkk add hashbang

from gimpfu import *

def plugin_func(image, drawable):

      # test that a tuple can be used as a color
      pdb.gimp_context_set_foreground( (20, 30, 40) )
      # test that an appropriate string can be used as a color
      pdb.gimp_context_set_foreground( "orange" )
      # test an inappropriate string as a color
      pdb.gimp_context_set_foreground( "foo" )

register(
      "python-fu-test-color",
      "blurb",
      "help message",
      "author",
      "copyright",
      "year",
      "Color wrapper...",
      "*",
      [
          (PF_IMAGE, "image", "Input image", None),
          (PF_DRAWABLE, "drawable", "Input drawable", None),
      ],
      [],
      plugin_func,
      menu="<Image>/Test")
main()

from gimpfu import gimp, main, register, PF_INT, BACKGROUND_FILL,RGB, NORMAL_MODE

def showWin(width, height):
    img = gimp.Image(width,height,RGB)
    lyr = gimp.Layer(img, 'layer1', width, height, RGB, 100, NORMAL_MODE)
    lyr.fill(BACKGROUND_FILL)
    img.add_layer(lyr)
    gimp.Display(img)
    gimp.displays_flush()

def createIcon(iconWidth, iconHeight):
    showWin(iconWidth,iconHeight)

register(
        "NewIcon",
        "Creates a new image as an LCD icon \nof a given width and height",
        "Lets create an LCD icon",
        "David Muriuki Karibe (karibe.co.ke, @muriukidavid)",
        "Karibe 2019",
        "2019",
        "LCD Icon",#menu entry text
        "",# Create a new image, don't work on an existing one
        [
         (PF_INT, "iconWidth", "Icon Width", 21),
         (PF_INT, "iconHeight", "Icon Height", 12)#(Type, Name, Description, default, extra)
        ],
        [],
        createIcon, menu="<Image>/File/Create/")#path to menu entry, under file

main()
