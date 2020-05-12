

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


def appendParameter(paramString, parameter):
    # trailing comma will be OK to Python
    result = paramString + parameter + ','
    return result

def generateParamString(inParamList,  image, drawable):
    result = "("
    for aType in inParamList:
        if aType == "GimpParamString":
            result = appendParameter(result, '"foo"')
        elif aType == "GParamInt" :
            result = appendParameter(result, '0')
        elif aType == "GParamItem" :
            # items are ints
            result = appendParameter(result, '1')
        elif aType == "GimpParamImage" :
            # reference a symbol in Python context at time of eval
            result = appendParameter(result, 'image')
        elif aType == "GimpParamDrawable" :
            # reference a symbol in Python context at time of eval
            result = appendParameter(result, 'drawable')
        # TODO more types
        else:
            # some type we don't handle, abandon
            return ""

    result = result + ')'
    return result





def testProcHavingNoParams(procName):

     # Skip some, that invoke GUI? They don't return?
     if procName == "extension-script-fu": return

     evalCatchingExceptions(procName, "()")


def printPDBError(testStmt):
    """
    megaGimpTest is-a GimpFu plugin, so pdb is defined,
    but get_last_error() is not *in* the PDB, only a method of the pdb.
    Hence we call Gimp.get_pdb().

    PDB is stateful on errors so we can get the last error until we call the next PDB procedure.

    error_str = Gimp.get_pdb().get_last_error()
    print(f"Error string from pdb procedure execution: {error_str}")
    if error_str != 'success':
    """

    """
    GimpFu continues past exceptions on PDB procedures.
    also has already printed an error like "Error: Gimp PDB execution error: <foo>"
    But that mechanism doesn't print the stmt.
    """
    print(f"Error executing {testStmt}")


def evalCatchingExceptions(procName, params, image=None, drawable=None):
    # not all pdb procedures use the current image and Drawable
    # They are passed so they are in scope when we eval

    newName = procName.replace("-", "_")
    testStmt = "pdb." + newName + params

    try:
        eval(testStmt)

    except Exception as err:
        """
        An exception here emanates from faulty Gimpfu code.
        Since Gimpfu catches and proceeds past exceptions while doing
        its own eval of author source.
        """
        print(f"Gimpfu: ******exception in Gimpfu code: {err}")
        printPDBError(testStmt)


def testProcHavingStringParam(procName):
    # TODO get an appropriate name of an existing object, by parsing the procname
    evalCatchingExceptions(procName, '("foo")')


def testProcThatIsPlugin(procName, inParamList, image, drawable):

    # Skip a plugin that opens Window and hangs the test
    if procName == "plug-in-animationplay":
        return

    if len(inParamList)==3:
        print("..................test plugin", procName)
        """
        Since we are in gimpFu, no need to provide first parameter "mode":
        gimpFu will insert value sorta RUN-NONINTERACTIVE
        """
        evalCatchingExceptions(procName, '(image, drawable)', image, drawable)


def testGeneralProc(procName, inParamList,  image, drawable):
    paramString = generateParamString(inParamList,  image, drawable)
    if paramString:
        evalCatchingExceptions(procName, paramString, image, drawable)
        result = True
    else:
        result = False

    # success means we tested it, not that it succeeded
    return result


def testProcGivenInParams(procName, inParamList,  image, drawable):
    """
    Dispatch on various flavors of procedure,
    based on inspecting the signature.
    """
    if not len(inParamList):
        print("No in", procName)
        testProcHavingNoParams(procName)
    elif (len(inParamList) == 1) and inParamList[0] == "GimpParamString":
        testProcHavingStringParam(procName)
    elif (len(inParamList) > 0) and procName.find("plug-in-")==0:
        #inParamList[0] == "GimpParamString":
        testProcThatIsPlugin(procName, inParamList,  image, drawable)
    elif testGeneralProc(procName, inParamList,  image, drawable):
        pass
    else:
        # unhandled signature or unhandled parameter type
        print(f".....................Omitting test of {procName}")




def testAProc(procName, paramsDict,  image, drawable):
    # We don't care about the out params
    # not len(paramsDict["out"]
    testProcGivenInParams(procName, paramsDict["in"], image, drawable)

def undo():
    """
    Restore the image to previous state.
    So testing is always from a known base.

    Note there is no undo() operation in the PDB.
    """
    # TODO
    pass


def testProcs(data,  image, drawable):
    for key in data.keys():
        # print(key)

        # create copy of original image
        # Alternatively, use the same image over and over, but errors will be different?
        testImage = pdb.gimp_image_duplicate(image)
        testDrawable = pdb.gimp_image_get_active_drawable(testImage)

        # pass procName, its paramDict
        testAProc(key, data[key],  testImage, testDrawable)

        # optionally undo the last changes
        # undo()


def plugin_main(image, drawable):
    """
    """
    # get dictionary of PDB signatures
    with open("pdb.json", "r") as read_file:
        data = json.load(read_file)
        testProcs(data, image, drawable)

    # regex for procedure_type as given from PDBBrowser
    #count, names = pdb.gimp_pdb_query("","","","","","","Internal GIMP procedure")
    # pdb.query_procedures("","","","","","","","","","")
    #print(count)




register(
    "python-fu-mega-test-gimp",
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
