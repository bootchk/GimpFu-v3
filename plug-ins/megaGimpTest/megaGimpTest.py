

"""
Plugin that mega tests Gimp.
Generates test cases from PDB.
"""


from gimpfu import *

from megaGimpTestUtils import *


import json





gettext.install("gimp30-python", gimp.locale_directory)



def appendParameter(paramString, parameter):
    # trailing comma will be OK to Python
    result = paramString + parameter + ','
    return result

def generateQuotedIntegerLiteral():
    """ Choose an integer with certain testing goals e.g. stress test or not.

    0 is out of range for many tested procedures
    1 tests the least
    """
    return '1'

def generateParamString(procName, inParamList,  image, drawable):
    # TODO why GParam and GimpParam ??
    result = "("
    for aType in inParamList:
        if aType == "GimpParamString" or aType == "GParamString" :
            result = appendParameter(result, '"foo"')
        elif aType == "GParamInt" :
            result = appendParameter(result, generateQuotedIntegerLiteral())
        elif aType == "GParamUInt" :
            # TODO this does not suffice.  Change gimpfu to cast to GParamUint
            result = appendParameter(result, generateQuotedIntegerLiteral())
        elif aType == "GParamDouble" :
            result = appendParameter(result, '1.0003')
        elif aType == "GParamBoolean" :
            # bool is int ??
            result = appendParameter(result, generateQuotedIntegerLiteral())
        elif aType == "GimpParamItem" :
            # Item is superclass of Drawable, etc.
            # Use a convenient one
            result = appendParameter(result, 'drawable')
        elif aType == "GParamEnum" or aType == "GimpParamEnum" :
            # enums are ints
            result = appendParameter(result, generateQuotedIntegerLiteral())
        elif aType == "GimpParamImage" :
            # reference a symbol in Python context at time of eval
            result = appendParameter(result, 'image')
        elif aType == "GimpParamDrawable" :
            # reference a symbol in Python context at time of eval
            result = appendParameter(result, 'drawable')
        elif aType == "GimpParamLayer" :
            # reference a symbol in Python context at time of eval
            # assert drawable is-a Layer
            result = appendParameter(result, 'drawable')
        elif aType == "GimpParamRGB" :
            # a 3-tuple suffices
            result = appendParameter(result, '(12, 13, 14)')

        # TODO more types
        # TODO GimpParamParasite
        # GimpParamUInt8Array
        # GimpParamChannel
        # GParamObject
        # GimpParamUnit
        else:
            # some type we don't handle, abandon
            TestLog.say(f"unhandled type {aType} for {procName}")
            return ""

    result = result + ')'
    return result



def testProcHavingNoParams(procName):
     evalCatchingExceptions(procName, "()")


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
        TestLog.say(f"exception in Gimpfu code: {err} for test: {testStmt}")


def testProcHavingStringParam(procName):
    # TODO get an appropriate name of an existing object, by parsing the procname
    evalCatchingExceptions(procName, '("foo")')



def testPluginWith3Params():
    # Since in GimpFu, no need to pass run mode
    if len(inParamList)==3:
        print("..................test plugin", procName)
        evalCatchingExceptions(procName, '(image, drawable)', image, drawable)
    else:
        TestLog.say(f"omit test plugin: {procName}")



def testProcThatIsPlugin(procName, inParamList, image, drawable):
    """
    Since we are in gimpFu, no need to provide first parameter "mode":
    gimpFu will insert value sorta RUN-NONINTERACTIVE
    """

    # hack off the run mode from formal params
    inParamList.pop(0)

    paramString = generateParamString(procName, inParamList,  image, drawable)
    if paramString:
        evalCatchingExceptions(procName, paramString, image, drawable)
        result = True
    else:
        # already logged why we could not generate params
        result = False




def testGeneralProc(procName, inParamList,  image, drawable):

    paramString = generateParamString(procName, inParamList,  image, drawable)
    if paramString:
        evalCatchingExceptions(procName, paramString, image, drawable)
        result = True
    else:
        # already logged why we could not generate params
        result = False

    # success means we tested it, not that it succeeded
    return result




def testProcGivenInParams(procName, inParamList,  image, drawable):

    # Exclude certain procs
    if not shouldTestProcedure(procName):
        TestLog.say(f"omit certain: {procName}")
        return

    """
    Dispatch on various flavors of procedure signature.
    """
    if not len(inParamList):
        print("No in", procName)
        testProcHavingNoParams(procName)
    elif (len(inParamList) == 1) and inParamList[0] == "GimpParamString":
        testProcHavingStringParam(procName)
    elif isPlugin(procName):
        testProcThatIsPlugin(procName, inParamList,  image, drawable)
    elif testGeneralProc(procName, inParamList,  image, drawable):
        pass
    else:
        # Omitted: unhandled signature or unhandled parameter type or is interactive
        print(f".....................Omitting test of {procName}")




def testAProc(procName, paramsDict,  image, drawable):
    # We don't care about the out params
    # not len(paramsDict["out"]
    testProcGivenInParams(procName, paramsDict["in"], image, drawable)




def testProcs(data,  image, drawable):
    """ Iterate over procs, and wrap each test in various contexts e.g. a test image. """
    for key in data.keys():
        # print(key)

        """
        So testing is always from a known base, test on a copy of original image
        Note there is no undo() operation in the PDB.
        Alternatively, use the same image over and over, but errors will be different?
        """
        testImage = pdb.gimp_image_duplicate(image)
        testDrawable = pdb.gimp_image_get_active_drawable(testImage)

        # pass procName, its paramDict
        testAProc(key, data[key],  testImage, testDrawable)

        # delete test image or undo changes made by procedure
        pdb.gimp_image_delete(testImage)



def plugin_main(image, drawable):
    """
    """
    # get dictionary of PDB signatures
    with open("testPDB/pdb.json", "r") as read_file:
        data = json.load(read_file)

        # run tests
        testProcs(data, image, drawable)

    TestLog.summarize()

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
