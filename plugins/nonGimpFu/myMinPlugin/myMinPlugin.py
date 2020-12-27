"""
A plugin that is:
- Python 3
- Gimp 3
- an illustrative demo
- annotated
- bare minimum and not well-behaved.  For example, not internationalized.

For tutorial use only, since not well-behaved!

First in a series of tutorial plugins.  Next: MyWellBehavedPlugin
"""

# PyGObject: GObject Introspection for Python language
import gi

# Binding to libgimp
gi.require_version('Gimp', '3.0')
from gi.repository import Gimp

# Binding to GLib, for GLib.Error
from gi.repository import GLib

# for sys.argv
import sys



def myMinPlugin(procedure, run_mode, image, drawable, args, data):
    """
    This is a callback from Gimp, in the "run" phase.
    Perform the actions of this plugin.
    """
    print("MyMinPlugin works!")

    """
    Must return values, even if only a status result.
    This plugin returns 'void', it only has a side effect of print to console.
    """
    return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())



# a plugin is a subclass of Gimp.PlugIn
class MyMinPlugin (Gimp.PlugIn):

    # Gimp.PlugIn virtual methods

    def do_query_procedures(self):
        """
        This is a callback from Gimp, in the 'query' phase.
        Tell Gimp the names of all plugins this .py file implements

        Return a list of possibly many plugin names.
        Names should follow standards: prefix is 'python-fu-'
        """
        return [ 'python-fu-my-min-plugin', ]



    def do_create_procedure(self, name):
        """
        This is a callback from Gimp, in the 'query' phase.
        Register attributes of the plugin having <name>.
        """
        procedure = Gimp.ImageProcedure.new(self, name,
                                            Gimp.PDBProcType.PLUGIN,
                                            myMinPlugin, # pass a function
                                            None)

        procedure.set_image_types("RGB*, GRAY*")

        procedure.set_menu_label("My min plugin...")
        procedure.add_menu_path ("<Image>/Test")

        return procedure


"""
At Python import time, call into Gimp.
Expect callbacks later.
"""
Gimp.main(MyMinPlugin.__gtype__, sys.argv)
