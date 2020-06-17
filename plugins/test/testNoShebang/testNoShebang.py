'''
A test Gimp plugin
that:
- tests plugin loading: no shebang

TODO also test where first character of file is '#'
'''

from gimpfu import *

def plugin_func(image, drawable):

      pass

register(
      "python-fu-test-no-shebang",
      "blurb",
      "help message",
      "author",
      "copyright",
      "year",
      "No shebang...",
      "*",
      [
          (PF_IMAGE, "image", "Input image", None),
          (PF_DRAWABLE, "drawable", "Input drawable", None),
      ],
      [],
      plugin_func,
      menu="<Image>/Test")
main()
