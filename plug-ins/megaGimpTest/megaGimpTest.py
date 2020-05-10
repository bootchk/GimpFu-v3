

"""
Plugin that mega tests Gimp.
Generates test cases from PDB.
"""


'''
A GIMP plugin.
Generates another plugin (in Python language).
Generated plugin is sequence of commands.
A command is a call to:
- a target plugin
- or a PDB procedure
- or a macro builtin to this app.
Generated wrapper plugin can be:

- a shortcut (simple renaming and simplification of parameters to one command)
- a sequence (the combined function of a sequence.)
The purpose of wrapping is:
1) alias or link to target command
2) simplify settings dialog (standard, current, or preset options for the target commands.)
3) automate a sequence
4) hide certain complexities of PDB programming, i.e. change the model slightly
(e.g. always add a new object to the image, unlike in the PDB.)
Help text is in /doc and the .glade file.
Future:
Note that the parameters you choose not to defer for the wrapper DO NOT become the last values
for the target plugin (it is run non-interactive.)
You can't change the not deferred parameters later without editing the wrapper.
The parameters you choose to defer DO become the last values for the wrapper plugin
(they will appear as the initial values the next time you run the wrapper.)
Versions:
beta 0.1 : simple shortcut to one plugin using last values
beta 0.2 2010 : presets: let user enter parameters for target plugin.
beta 0.3 April 2011 : renamed Gimpscripter.  Sequences.  Macros.  Calls to PDB procedures.
To Do:
More functionality:
  defaults for parameters taken from plugins themselves or modify PDB to support

User friendliness:
  gui non-modal: Apply/Quit
  let user root wrappers elsewhere in menu tree
  domain i8n
  check if menu item already used?
  Since the menu item is not the same as the filename?
  check if the filename already used
  tell the user we created it but GIMP restart required
  and don't show that message more than once.
  Disallow making wrapper to wrapper?
  Disallow making wrapper to Load/Save?
  Return key in name text entry Apply
Copyright 2010 Lloyd Konneker
License:
  This program is free software; you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation; either version 2 of the License, or
  (at your option) any later version.
'''


from gimpfu import *

gettext.install("gimp30-python", gimp.locale_directory)



def plugin_main(image, drawable):
    """
    from gimpscripter.gui import main_gui

    # Build data that drives the app: dictionary of views on dbs
    # For each kind of db, import the glue module to the db
    # and get the dictofviews from the glue module.

    # Here, there is only one view, a treeview on GIMP plugins.
    from gimpscripter.mockmenu import plugindb # glue to the Gimp PDB
    dictofviews = plugindb.dictofviews.copy()

    app = main_gui.gimpscripterApp(dictofviews)  # create instance of gtkBuilder app
    app.main()  # event loop for app
    """

    with open("pdb.json", "r") as read_file:
        data = json.load(read_file)

    # regex for procedure_type as given from PDBBrowser
    count, names = pdb.gimp_pdb_query("","","","","","","Internal GIMP procedure")
    # pdb.query_procedures("","","","","","","","","","")
    print(count)

    pdb.gimp_airbrush(drawable, 2.0, 2, [1.0, 2.0, 100.0, 200.0])






register(
    "python_fu_mega_test_gimp",
    "Exhaustively test Gimp",
    "This plugin creates and executes more plugins, each tests a call to a PDB procedure.",
    "Lloyd Konneker",
    "Copyright 2020 Lloyd Konneker",
    "2020",
    N_("Megatest Gimp..."),  # menu item
    "*", # image types: blank means don't care but no image param
    [(PF_IMAGE,  "i", _("_Image"), None),
     (PF_DRAWABLE, "d", _("_Drawable"), None),
    ],
    [], # No return value
    plugin_main,
    menu=N_("<Image>/Filters"), # menupath
    domain=("gimp30-python", gimp.locale_directory))

print("Starting Megatest Gimp")
main()
