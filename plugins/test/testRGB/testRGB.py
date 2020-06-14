'''
A test Gimp plugin
that:
- tests wrapper of color args
'''

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
