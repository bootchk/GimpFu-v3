'''
A test Gimp plugin
that:
- alias gimp exists and delegates to Gimp gobject
'''

from gimpfu import *

def plugin_func(image, drawable, arg, arg2):
      print("plugin_func called")

      # test that gimp alias is defined
      print("gimp inside plugin_func", gimp)
      img = gimp.Image(10, 20, RGB)

      # test GimpInt32Array result
      a_vectors = pdb.gimp_image_get_active_vectors(image)
      print(f"vectors: {a_vectors}")

      count, stroke_list = pdb.gimp_vectors_get_strokes(a_vectors)
      print(f"count: {count} stroke id list: {stroke_list}")

register(
      "accessGimp",
      "blurb",
      "help message",
      "author",
      "copyright",
      "year",
      "Access gimp...",
      "*",
      [
          (PF_IMAGE, "image", "Input image", None),
          (PF_DRAWABLE, "drawable", "Input drawable", None),
          (PF_STRING, "arg", "The string argument", "default-value"),
          (PF_INT, "arg2", "The int argument", 1)
      ],
      [],
      plugin_func,
      menu="<Image>/Test")
main()
