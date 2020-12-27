
#!/usr/bin/env python3
"""
[1] The above "shebang" or "hashbang" is a Linux thing
that lets this file be click-to-execute from the desktop.
Not absolutely required, but highly recommended.
"""

"""
A plugin that is:
- Python 3
- Gimp 3
- an illustrative demo
- annotated
- well-behaved

Well-behaved for other users:
1. clickable
2. internationalized aka 118n aka localization aka translated
3. self-documenting, i.e. describing self to Gimp

Second in a series of tutorial plugins.
Previous: MyMinPlugin
Next: MyParameterizedPlugin

!!!
When a plugin is just for yourself, it doesn't need to be well-behaved.
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

"""
[2] import Python module that supports internationalization

Any text that should be translated should be enclosed with _().
Getting it actually translated involves much more adminstrative work.
"""
import gettext
_ = gettext.gettext


"""
[2] Your plugin's translation file's names and locations.
Needed when your plugin implements its own GUI.
"""
textdomain = 'myWellBehavedPlugin'
gettext.bindtextdomain(textdomain, Gimp.locale_directory())
gettext.bind_textdomain_codeset(textdomain, 'UTF-8')
gettext.textdomain(textdomain)




def myMinPlugin(procedure, run_mode, image, drawable, args, data):

    print("MyMinPlugin works!") # Untranslated
    return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())



class MyMinPlugin (Gimp.PlugIn):

    def do_query_procedures(self):

        """
        [2] Include this code here to support i18n
        for common text your plugin presents to user (in a GUI)
        that is already translated in Gimp.
        """
        self.set_translation_domain("gimp30-python",
                                    Gio.file_new_for_path(Gimp.locale_directory()))

        return [ 'python-fu-my-min-plugin', ]


    def do_create_procedure(self, name):
        procedure = Gimp.ImageProcedure.new(self, name,
                                            Gimp.PDBProcType.PLUGIN,
                                            myMinPlugin, # pass a function
                                            None)

        procedure.set_image_types("RGB*, GRAY*")

        procedure.set_menu_label(_("My min plugin..."))
        procedure.add_menu_path ("<Image>/Test")

        """
        [2],[3] Register attributes of the plugin
        that tell users what the plugin does, etc.
        Info will appear in the PDB Browser and in tooltips
        """
        procedure.set_documentation (
            _("Demo a well behaved plugin"),    # short blurb
            _("Demo a plugin that is internationalized and documented."),  # long help
            name)
            
        """
        [3] Register attributes of the plugin that tell author,
        copyright owner, date.
        """
        procedure.set_attribution("First Surname",
                                  "First Surname",
                                  "2020")

        return procedure


Gimp.main(MyMinPlugin.__gtype__, sys.argv)
