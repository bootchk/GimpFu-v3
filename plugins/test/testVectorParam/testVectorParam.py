'''
A test Gimp plugin
that:
- tests wrapper of vector arg
'''

from gimpfu import *

def plugin_func(image, drawable):

      # create a Vectors instance, empty of strokes
      vectors = gimp.Vectors(image, "foo")

      # pass it to a PDB procedure that examines the Vectors instance
      count_strokes, list_strokes = pdb.gimp_vectors_get_strokes( vectors )

      # TODO: expect count_strokes == 0, but can't test the Boxed list_strokes

register(
      "python-fu-test-vector-param",
      "blurb",
      "help message",
      "author",
      "copyright",
      "year",
      "Vector param...",
      "*",
      [
          (PF_IMAGE, "image", "Input image", None),
          (PF_DRAWABLE, "drawable", "Input drawable", None),
      ],
      [],
      plugin_func,
      menu="<Image>/Test")
main()
