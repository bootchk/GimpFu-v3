'''
A GimpFu plugin
that:
calls a gegl op
'''

from gimpfu import *

import gi
from gi.repository import GObject


def plugin_func(image, drawable):
      print("plugin_func called")


      #pass no params
      pdb.gimp_drawable_apply_operation_by_name(drawable, "gegl:median-blur", 0, [], 0, [])

      # pass float for enum
      pdb.gimp_drawable_apply_operation_by_name(drawable, "gegl:median-blur",
          2, ["radius", "neighborhood"], 2, [10.0, 1.0])

      # pass int instead of float for an enum
      pdb.gimp_drawable_apply_operation_by_name(drawable, "gegl:median-blur",
          2, ["radius", "neighborhood"], 2, [10.0, 1])

     # pass True for float for Boolean
      pdb.gimp_drawable_apply_operation_by_name(drawable, "gegl:median-blur",
          3, ["radius", "neighborhood", "high-precision"], 3, [10.0, 1.0, True])

      # Non PDB
      drawable.apply_operation_by_name('gegl:median-blur', ['radius'], [100.0] )

      """
      Not GimpFu, straight GI
      Fails: expected boxed.
      StringArray not working in GI??

      Gimp.get_pdb().run_procedure('gimp_drawable_apply_operation_by_name',
        [
           GObject.Value(GObject.TYPE_STRING, 'gegl:median-blur'),
           GObject.Value(GObject.TYPE_INT, 1),
           GObject.Value(Gimp.StringArray, ['radius',]),
           GObject.Value(GObject.TYPE_INT, 1),
           GObject.Value(Gimp.FloatArray, [10.0,]),
        ])
        """


      # Fail cases

      print("Test case lengths not same.")
      # Dictionary not same length
      pdb.gimp_drawable_apply_operation_by_name(drawable, "gegl:median-blur",
          1, ["radius"], 3, [10.0, 1.0, True])

      print("Test case unknown op.")
      # unknown op
      pdb.gimp_drawable_apply_operation_by_name(drawable, "gegl:foo",
          2, ["radius", "neighborhood"], 2, [10.0, 1.0])

      print("Test case unknown property.")
      print("Expect fail, and GEGL warning.")
      # unknown property
      pdb.gimp_drawable_apply_operation_by_name(drawable, "gegl:median-blur",
          1, ["foo"], 1, [1.0])

      print("Test case layer group.")
      # layer group
      # Not mixing gimpfu with Gimp
      aLayerGroup = Gimp.Layer.group_new(image.unwrap())
      #aLayerGroup = gimp.Layer.group_new(image)
      # Note not attached: image.insert_layer(aLayerGroup)
      pdb.gimp_drawable_apply_operation_by_name( aLayerGroup, "gegl:median-blur", 1, ["radius"], 1, [100.0] )



register(
      "python-fu-gegl",
      "blurb",
      "help message",
      "author",
      "copyright",
      "year",
      "Call PDB to apply gegl op...",
      "*",
      [
          (PF_IMAGE, "image", "Input image", None),
          (PF_DRAWABLE, "drawable", "Input drawable", None),
      ],
      [],
      plugin_func,
      menu="<Image>/Test")
main()
