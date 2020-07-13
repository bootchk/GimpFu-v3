'''
A test Gimp plugin
that:
- tests a v2 API call to gimp_edit_copy works
'''

from gimpfu import *

def plugin_func(image, drawable):
     success = pdb.gimp_edit_copy(drawable)
     assert(success)


register(
      "python-fu-test-gimp-edit-copy",
      "blurb",
      "help message",
      "author",
      "copyright",
      "year",
      "v2 gimp-edit-copy...",
      "*",
      [
          (PF_IMAGE, "image", "Input image", None),
          (PF_DRAWABLE, "drawable", "Input drawable", None),
      ],
      [],
      plugin_func,
      menu="<Image>/Test")
main()
