'''
A test Gimp plugin
that:
- tests what Gimp does at startup with a .py file inside a Python package directory
'''

from gimpfu import *

def plugin_func(image, drawable):
     print("testPackage does nothing")


register(
      "python-fu-test-package",
      "blurb",
      "help message",
      "author",
      "copyright",
      "year",
      "test package...",
      "*",
      [
          (PF_IMAGE, "image", "Input image", None),
          (PF_DRAWABLE, "drawable", "Input drawable", None),
      ],
      [],
      plugin_func,
      menu="<Image>/Test")
main()
