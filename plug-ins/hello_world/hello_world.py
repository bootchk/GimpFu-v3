# lkk omit hash bang specific to OSX
#        ![path to Gimp application]/GIMP-2.10.app/Contents/MacOS/python


'''
lkk
As a test case:
expect "! Hello world written to status bar"

Also, you must open an image.
As written (image_type=="") without an image, generates an error from Gimp.
'''

from gimpfu import *
# lkk commented out: this causes failure?
# import gimp

def python_message(image, drawable, message):
    gimp.message(message)


register(
        "python_fu_message",
        "Show message",
        "Show message",
        "Pin-Chou Liu",
        "Pin-Chou Liu",
        "2019",
        "<Image>/Filters/Hello World...",
        "",
        [
            (PF_STRING, "message", "message", "Hello World"),
        ],
        [],
        python_message)


main()
