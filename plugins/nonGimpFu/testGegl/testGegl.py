"""
A plugin that is:

introspects Gegl
"""

# PyGObject: GObject Introspection for Python language
import gi

# Binding to libgimp
gi.require_version('Gimp', '3.0')
from gi.repository import Gimp

from gi.repository import Gegl

# Binding to GLib, for GLib.Error
from gi.repository import GLib

# for sys.argv
import sys



def testGegl(procedure, run_mode, image, drawable, args, data):


    print("testGegl start!")
    # introspect an operation by name

    Gegl.init(sys.argv)
    print("Gegl.init() passed")

    print(f"Version: {Gegl.get_version()}")

    # Why doesn't this work?
    print(f"Operations: {Gegl.list_operations()}")

    print(f"Has op median-blur: {Gegl.has_operation('gegl:median-blur')}")
    print(f"Has op ripple: {Gegl.has_operation('gegl:ripple')}")

    # Fail GLib assertion
    props = Gegl.Operation.list_properties("gegl:median-blur")
    print(props)

    # Not checking that drawable is attached to image
    node = Gegl.Node()
    print("Created node")

    # Create a processing node, parented?
    processing_node = node.create_child("gegl:median-blur")

    # Not sure this is correct, creates a pass-through node?
    #node.set_property("operation", "gegl:media-blur")
    # print("Set operation property")

    """
    <GeglParamEnum 'neighborhood'>, <GeglParamInt 'radius'>, <GeglParamDouble 'percentile'>, <GeglParamDouble 'alpha-percentile'>, <GeglParamEnum 'abyss-policy'>, <GParamBoolean 'high-precision'>]
    """
    print(f"Property neighborhood: {processing_node.get_property('neighborhood')}")

    # set the properties of the operation onto the processing node
    processing_node.set_property("neighborhood", 1)
    # print("Set neighborhood property")
    """
    Accept the defaults?
    processing_node.set_property("radius", 1)
    processing_node.set_property("percentile", 100.0)
    processing_node.set_property("alpha-percentile", 100.0)
    processing_node.set_property("neighborhood", 1)
    """

    # gimp_drawable_apply_operation is not exposed in libgimp?????
    drawable.apply_operation(processing_node)
    print(f"Apply operation")

    """
    from pdb/plug_in_compat.pdb for a PDB procedure that calls gegl

    	code => <<'CODE'
    {
      if (gimp_pdb_item_is_attached (GIMP_ITEM (drawable), NULL,
                                     GIMP_PDB_ITEM_CONTENT, error) &&
          gimp_pdb_item_is_not_group (GIMP_ITEM (drawable), error))
        {
          GeglNode *node =
            gegl_node_new_child (NULL,
                                 "operation", "gegl:texturize-canvas",
                                 "direction", direction,
                                 "depth",     depth,
                                 NULL);

          gimp_drawable_apply_operation (drawable, progress,
                                         C_("undo-type", "Apply Canvas"),
                                         node);
          g_object_unref (node);
        }
      else
        success = FALSE;
    }
    CODE
    """


    return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())



# a plugin is a subclass of Gimp.PlugIn
class MyPlugin (Gimp.PlugIn):

    # Gimp.PlugIn virtual methods

    def do_query_procedures(self):
        return [ 'python-fu-test-gegl', ]



    def do_create_procedure(self, name):
        procedure = Gimp.ImageProcedure.new(self, name,
                                            Gimp.PDBProcType.PLUGIN,
                                            testGegl, # pass a function
                                            None)

        procedure.set_image_types("RGB*, GRAY*")

        procedure.set_menu_label("Test gegl..")
        procedure.add_menu_path ("<Image>/Test")

        return procedure


"""
At Python import time, call into Gimp.
Expect callbacks later.
"""
Gimp.main(MyPlugin.__gtype__, sys.argv)
