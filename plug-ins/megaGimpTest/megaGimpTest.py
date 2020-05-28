

"""
Plugin that mega tests Gimp.

Test calling procedures in PDB.
Some procedures are omitted.

Test via GimpFu

Goals:
- stress test GimpFu
- find crashes in Gimp

Parameters to PDB procedures are arbitrary.

Tests do NOT test semantics:
- don't know the expected result,
- mostly that a procedure should not crash

FUTURE more fuzzy: pass edge case values
"""


from gimpfu import *

from megaGimpTestUtils import *
from testHarness import *
from params import *
from testLog import TestLog
from stats import TestStats

import json

# Plugin is not i18n ???
gettext.install("gimp30-python", gimp.locale_directory)





def testProcHavingNoParams(procName):
     evalCatchingExceptions(procName, "()")


def evalCatchingExceptions(procName, params, image=None, drawable=None):
    # not all pdb procedures use the current image and Drawable
    # They are passed so they are in scope when we eval

    newName = procName.replace("-", "_")
    testStmt = "pdb." + newName + params

    # Log start of test so we know what test hangs (takes too long time)
    TestLog.say(f"Begin test: {testStmt}")
    try:
        eval(testStmt)

    except Exception as err:
        """
        An exception here emanates from faulty Gimpfu code.
        Since Gimpfu catches and proceeds past exceptions while doing
        its own eval of author source.
        That is, GimpFu will log exceptions that the tested procedure throws.
        """
        TestStats.sample("GimpFu exception", str(err) )
        TestLog.say(f"exception in Gimpfu code: {err} for test: {testStmt}")

    # Log end of test, with weak result.
    # get the pdb status, it is a weak form of pass/fail
    error_str = Gimp.get_pdb().get_last_error()
    TestLog.say(f"End test, PDB status: {error_str}")
    if error_str != "success":
        TestStats.sample("fail", error_str)
    else:
        TestStats.sample("pass")

    # TODO stronger form of pass, test effects are as expected


def testProcHavingStringParam(procName):
    # TODO get an appropriate name of an existing object, by parsing the procname
    evalCatchingExceptions(procName, '("foo")')



"""
OLD
def testPluginWith3Params():
    # Since in GimpFu, no need to pass run mode
    if len(inParamList)==3:
        TestLog.say(f"test plugin: {procName}")
        evalCatchingExceptions(procName, '(image, drawable)', image, drawable)
    else:
        TestLog.say(f"omit test plugin: {procName}")
"""



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
        result = False




def testGeneralProc(procName, inParamList,  image, drawable):

    paramString = generateParamString(procName, inParamList,  image, drawable)
    if paramString:
        evalCatchingExceptions(procName, paramString, image, drawable)
        result = True
    else:
        result = False

    # success means we tested it, not that it succeeded
    return result




def testProcGivenInParams(procName, inParamList,  image, drawable):

    # Exclude certain procs
    if not shouldTestProcedure(procName):
        TestStats.sample("omit bad actor")
        TestLog.say(f"omit certain: {procName}")
        return

    """
    Dispatch on various flavors of procedure signature.
    """
    if not len(inParamList):
        TestLog.say(f"No in params: {procName}")
        testProcHavingNoParams(procName)
    elif (len(inParamList) == 1) and inParamList[0] == "GimpParamString":
        testProcHavingStringParam(procName)
    elif isPlugin(procName):
        testProcThatIsPlugin(procName, inParamList,  image, drawable)
    elif testGeneralProc(procName, inParamList,  image, drawable):
        pass
    else:
        # Omitted: unhandled signature or unhandled parameter type or is interactive
        TestLog.say(f"Omitting test of {procName}")




def testAProc(procName, paramsDict,  image, drawable):
    # We don't care about the out params
    # not len(paramsDict["out"]
    testProcGivenInParams(procName, paramsDict["in"], image, drawable)




def testProcs(data,  image, drawable):
    """ Iterate over procedures, testing them.

    TODO sort so that procedures that delete global test data come last?

    Setup each test in various contexts e.g. a test image.
    """

    # unsorted: for key in data.keys():

    # sort the data by procedure name
    for key in sorted(data):

        # print(key)
        TestStats.sample("procedures")

        """
        So testing is always from a known base, test on a copy of original image
        Note there is no undo() operation in the PDB, to undo the previous test.
        Alternatively, use the same image over and over, but errors will be different?
        """
        testImage = pdb.gimp_image_duplicate(image)
        testDrawable = pdb.gimp_image_get_active_drawable(testImage)

        # Not testing undo. Disable it for speed.
        pdb.gimp_image_undo_disable(testImage)

        # pass procName, its paramDict
        testAProc(key, data[key],  testImage, testDrawable)

        # delete test image or undo changes made by procedure
        pdb.gimp_image_delete(testImage)



def plugin_main(image, drawable):
    """
    """

    # Generate named data in Gimp
    generateFooGimpData()

    """
    Generate instances (passed as args to PDB procedures, not by a name known to Gimp).
    Used like 'image', 'drawable', instances passed into the tests,
    but here it is global.
    """
    global fooVectors   # declare global so can assign to global
    # GimpFu notation, not gi
    fooVectors = gimp.Vectors()

    # Note testing undo.  Disable it for speed.
    pdb.gimp_image_undo_disable(image)

    # Success on many tested procedures depends on existence of certain things
    # Person running the test should also insure:
    # selection in image
    # strokes in image

    # get dictionary of PDB signatures
    with open("testPDB/pdb.json", "r") as read_file:
        data = json.load(read_file)

        # assert data is-a dictionary

        # run tests
        testProcs(data, image, drawable)

    # TODO cleanup any excess test data and stuff generated by tested procedures
    # Otherwise, they accumulate in Gimp settings
    # Alternative, delete gimp config/settings regularly

    TestStats.summarize()
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

TestLog.say(f"Starting")
main()
