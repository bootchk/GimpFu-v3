"""
Test the need to upcast args
"""

import gi
gi.require_version('Gimp', '3.0')
from gi.repository import Gimp
from gi.repository import GObject
from gi.repository import GLib
from gi.repository import Gio
import time
import sys


import gettext
_ = gettext.gettext
def N_(message): return message


def test(procedure, run_mode, image, drawable, args, data):

    """
    name = args.index(0)
    turbulence = args.index(1)
    opacity = args.index(2)
    """
    name = "foo"
    turbulence = 1.0
    opacity = 50.0

    color = Gimp.RGB()
    color.set(240.0, 180.0, 70.0)

    Gimp.context_push()
    image.undo_group_start()

    if image.base_type() is Gimp.ImageBaseType.RGB:
        type = Gimp.ImageType.RGBA_IMAGE
    else:
        type = Gimp.ImageType.GRAYA_IMAGE

    aLayer = Gimp.Layer.new(image, name,
                         drawable.width(), drawable.height(), type, opacity,
                         Gimp.LayerMode.NORMAL)

    # Test that a Layer instance can be passed for formal parameter type Gimp.Item
    # to libgimp function
    print (aLayer.get_name() )

    # Test that a Layer instance can be passed for formal parameter type Gimp.Item
    # to a PDB procedure, if you declare its type to be Gimp.Item
    args = Gimp.ValueArray.new(1)
    args.insert(0, GObject.Value(Gimp.Item, aLayer))
    print( Gimp.get_pdb().run_procedure('gimp-layer-get-name', args)  )

    # Test that a Layer instance can be passed for formal parameter type Gimp.Item
    # to a PDB procedure, if you declare its type to be Gimp.Item
    args = Gimp.ValueArray.new(1)
    args.insert(0, GObject.Value(Gimp.Item, aLayer))
    print( Gimp.get_pdb().run_procedure('gimp-item-get-name', args)  )

    # Test that a Layer instance can be passed for formal parameter type Gimp.Item
    # to a PDB procedure  FAILS unless you declare  superclass type
    args = Gimp.ValueArray.new(1)
    args.insert(0, GObject.Value(Gimp.Layer, aLayer))
    print( Gimp.get_pdb().run_procedure('gimp-layer-get-name', args)  )



    """
    aLayer.fill(Gimp.FillType.TRANSPARENT)
    image.insert_layer(aLayer, None, 0)

    Gimp.context_set_background(color)
    aLayer.edit_fill(Gimp.FillType.BACKGROUND)

    # create a layer mask for the new layer
    mask = aLayer.create_mask(0)
    aLayer.add_mask(mask)

    # add some clouds to the layer
    args = Gimp.ValueArray.new(5)
    args.insert(0, GObject.Value(Gimp.RunMode, Gimp.RunMode.NONINTERACTIVE))
    args.insert(1, GObject.Value(Gimp.Image, image))
    args.insert(2, GObject.Value(Gimp.Drawable, mask))
    args.insert(3, GObject.Value(GObject.TYPE_INT, int(time.time())))
    args.insert(4, GObject.Value(GObject.TYPE_DOUBLE, turbulence))
    Gimp.get_pdb().run_procedure('plug-in-plasma', args)

    # apply the clouds to the layer
    aLayer.remove_mask(Gimp.MaskApplyMode.APPLY)
    aLayer.set_visible(True)
    """

    image.undo_group_end()
    Gimp.context_pop()

    return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())

class Foggify (Gimp.PlugIn):
    ## Parameters ##
    """
    __gproperties__ = {
        "name": (str,
                 _("Layer name"),
                 _("Layer name"),
                 _("Clouds"),
                 GObject.ParamFlags.READWRITE),
        "color": (Gimp.RGB,
                  _("Fog color"),
                  _("Fog color"),
                  GObject.ParamFlags.READWRITE),
        "turbulence": (float,
                       _("Turbulence"),
                       _("Turbulence"),
                       0.0, 10.0, 1.0,
                       GObject.ParamFlags.READWRITE),
        "opacity": (float,
                    _("Opacity"),
                    _("Opacity"),
                    0.0, 100.0, 100.0,
                    GObject.ParamFlags.READWRITE),
    }
    """

    ## GimpPlugIn virtual methods ##
    def do_query_procedures(self):
        self.set_translation_domain("gimp30-python",
                                    Gio.file_new_for_path(Gimp.locale_directory()))

        return [ 'python-fu-test-upcast' ]

    def do_create_procedure(self, name):
        procedure = Gimp.ImageProcedure.new(self, name,
                                            Gimp.PDBProcType.PLUGIN,
                                            test, None)
        procedure.set_image_types("RGB*, GRAY*");
        procedure.set_documentation (N_("Test need for upcast"),
                                     "",
                                     name)
        procedure.set_menu_label(N_("_Test need for upcast..."))
        procedure.set_attribution("lkk",
                                  "lkk",
                                  "2020")
        procedure.add_menu_path ("<Image>/Test")

        #procedure.add_argument_from_property(self, "name")
        # TODO: add support for GBoxed values.
        #procedure.add_argument_from_property(self, "color")
        #procedure.add_argument_from_property(self, "turbulence")
        #procedure.add_argument_from_property(self, "opacity")
        return procedure

Gimp.main(Foggify.__gtype__, sys.argv)
