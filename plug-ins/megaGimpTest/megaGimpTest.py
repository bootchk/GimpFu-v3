

"""
Plugin that mega tests Gimp.
Generates test cases from PDB.
"""


'''
A GIMP plugin.
Generates another plugin (in Python language).
Then invokes the plugin.

Generated plugin is a test plugin.
'''


from gimpfu import *

import json
from string import Template


template = r'''
from gimpfu import *

def plugin_main(image, drawable):
    # just execute
    pdb.$name

register(
    "python_fu_test_$name",
    "", "", "", "",
    "2020",
    N_("Megatest $name..."),  # menu item
    "*", # image types: blank means don't care but no image param
    [(PF_IMAGE,  "i", _("_Image"), None),
     (PF_DRAWABLE, "d", _("_Drawable"), None),
    ],
    [], # No return value
    plugin_main,
    menu=N_("<Image>/Filters"), # menupath
    domain=("gimp30-python", gimp.locale_directory))

main()
'''



gettext.install("gimp30-python", gimp.locale_directory)


# Don't need this?
def createNewPluginSource():
    # substitute into template
    s = Template(template)
    result = s.substitute(name=newName)
    return result


def testProcHavingNoParams(procName):

     # Skip some, that invoke GUI? They don't return?
     if procName == "extension-script-fu": return

     newName = procName.replace("-", "_")
     testStmt = "pdb." + newName + "()"
     eval(testStmt)

     # TODO check the status result

def testProcHavingStringParam(procName):
    newName = procName.replace("-", "_")
    testStmt = "pdb." + newName + "('foo')"
    eval(testStmt)

def testProcs(data):
    for key in data.keys():
        # print(key)
        """
        if not len(data[key]["in"]) and not len(data[key]["out"]):
            print("No in or out", key)
            testProcHavingNoParams(key)
        """

        if (len(data[key]["in"]) == 1) and data[key]["in"][0] == "GimpParamString":
            testProcHavingStringParam(key)




def plugin_main(image, drawable):
    """

    """

    # get dictionary of PDB signatures
    with open("pdb.json", "r") as read_file:
        data = json.load(read_file)
        testProcs(data)

    # regex for procedure_type as given from PDBBrowser
    #count, names = pdb.gimp_pdb_query("","","","","","","Internal GIMP procedure")
    # pdb.query_procedures("","","","","","","","","","")
    #print(count)




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
