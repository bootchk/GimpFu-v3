'''
A test Gimp plugin
that:
- accesses pdb
'''

from gimpfu import *

def plugin_func(image, drawable, arg, arg2):
      print("plugin_func called")

      # test that pdb is accessible
      # This works (except for the args) i.e. PDB has a method run_procedure
      # Gimp.get_pdb().run_procedure('plug-in-plasma', 1)

      # test that pdb is accessible
      # This fails, attribute gimp_image... not exist
      #drawable = Gimp.get_pdb().gimp_image_active_drawable(image)

      # test that pdb alias is defined
      # This works in that pdb is defined, and that gimp_image... seems like an attribute of PDB
      print("pdb inside plugin_func", pdb)
      drawable = pdb.gimp_image_active_drawable(image)

register(
      "accessPDB",
      "blurb",
      "help message",
      "author",
      "copyright",
      "year",
      "Access PDB...",
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
