

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
