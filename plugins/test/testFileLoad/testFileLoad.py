#!/usr/bin/env python3

'''
A Gimp plugin that:
- tests Gimp import/export: PDB procedures that save and load image files

!!! See ImageFormat in image_format.py which hides details of image format support by Gimp.

Depends on specific test directory existing.
Does NOT depend on test files existing.
You can empty the test directory, and it can create test files (using save procedure)
(effectively testing both save and load procedures.)

When this plugin cannot dynamically create IN test files (since there is no save procedure in Gimp)
the plugin copies sample files into the test directory.

Optionally will omit testing file formats known to crash the test harness.

Some format loader/savers have defaulted args that are not tested.
I.E. this does not understand the details about a format,
and does not stress test all possibilities for a format.
I.E. only does basic sanity test: creates or reads a file.
Does not compare resulting images or files with known good result images or files.


Varying the test conditions
---------------------------

You should first open an image.
Typically image is of a sophisticated mode, and has alpha.
The plugin then repeatedly saves and loads the image in test formats.

This plugin automatically down converts image mode for some formats.
This plugin automatically removes alpha for some formats.
IOW this plugin tries hard to make a minimal conversion succeed,
using its knowledge of the capabilities of the save/load procedures.
So you can't test the features of a save/load procedure that accomodate or reject variant formats.

You can first open an unsophisticated mode image, say gray or 1-bit B&W.
Then you can test whether load/save procedures handle such modes.

This plugin does NOT up convert mode.

The sample test files are also all known to pass, minimally.

Expect for test all
-------------------

Summary: Gimp should create many images (across the image browser bar)
that look like the original, with some images being special cases.

Assume you first clear out the test directory, start Gimp, and open an image.

From the image that was open prior (the original),
for every format that has a save procedure,
'test all' will save (export) the original image to a new file in the test directory.
(Else this plugin will simply copy a sample file to the test directory, for load testing.)

If the format has a load procedure, this plugin will attempt to load (open),
creating a new image that you will see in Gimp.
Expect the visible image looks similar to the original.
(Except when the format has no save procedure, then expect the image to look like the sample.)

Except when the format requires down moding of the image to save it,
then expect the reloaded, visible image to look down moded from the original.
(Say a black and white of the original.)

Reading the summary of tests in the console.
--------------------------------------------

FAIL for a save procedure means: failed to create a file.
Probably the procedure returned an error code, but it could also have crashed hard.

FAIL for a load procedure means: failed to create an image.
Probably the procedure returned an error code, but it could also have crashed hard.
If the saver PASS, that means it created a file, but the file could be invalid
cause the loader to FAIL.


'''
import os   # file existence
import logging

from gimpfu import *

from image_format import ImageFormat
from all_test_result import AllTestResult, KnownGoodAllTestResult
from test_dir import TestDir

def get_logger():
    logger = logging.getLogger('TestExportImport')

    # TODO make the level come from the command line or the environment
    logger.setLevel(logging.DEBUG)
    #logger.setLevel(logging.WARNING)

    # create file handler which logs even debug messages
    #fh = logging.FileHandler('spam.log')
    #fh.setLevel(logging.DEBUG)
    # create console handler with same log level
    ch = logging.StreamHandler()
    # possible levels are DEBUG, INFO, WARNING, ERROR, CRITICAL
    ch.setLevel(logging.DEBUG)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    #fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    #logger.addHandler(fh)
    logger.addHandler(ch)
    return logger



def call_save_procedure(saver_name, image, drawable, format_moniker, filename):
    """ Invoke save procedure given by saver_name.

    assert saver_name is a string, but save procedure might not exist
    If the pdb procedure does not exist, this fails quietly and file still not exist
    """
    image, drawable = ImageFormat.compatible_mode_image(format_moniker, image, drawable)

    if ImageFormat.saver_takes_single_drawable(format_moniker):
        arg_string = "(image, drawable, filename)"
    else:
        # has signature image, drawable_count, GObjectArray, filename
        # GimpFu will convert single drawable instance to GObjectArray
        arg_string = "(image, 1, drawable, filename)"

    eval_string = "pdb." + saver_name + arg_string
    #logger.info(f"Invoking: {eval_string}")
    eval(eval_string)



# TODO shouldn't save_file and load_file be symmetrical?

def save_file(image, drawable, format_moniker, filename):
    """ Tell Gimp to save file named: *filename* having format: *format_moniker* from: image, drawable.
    """
    # assert filename already has format's extension
    # typical evaluated string: pdb.file_bmp_save(image, drawable, filename)

    if ImageFormat.exists_saver(format_moniker):
        saver_name = ImageFormat.saver_name(format_moniker)
        call_save_procedure(saver_name, image, drawable, format_moniker, filename)
        did_saver_run = True  # at least we tried to run it
        # A dying plug-in might create a file before it dies, so existence of file is not sufficient to pass test
        # TODO this should be a method of GimpFu: did_pdb_procedure_succeed
        error_str = pdb.get_last_error()
        if error_str != "success":
            did_saver_pass = False
        else:
            # Test saver succeeds only if file exists
            did_saver_pass = os.path.isfile(filename)  # At least it created a file
    else:
        did_saver_run = False
        did_saver_pass = False
    return did_saver_run, did_saver_pass


def load_file(image, drawable, filename, format_moniker):
    """ Tell Gimp to load test_file of given format_moniker.

    Return new image or None.
    None means loading failed.

    File must exist.

    Understands loader signatures.
    """
    # filename = ensure_test_file(image, drawable, loader_name, format_moniker)
    assert filename is not None

    loader_name = ImageFormat.loader_name(format_moniker)
    if ImageFormat.has_two_arg_loader(format_moniker) :
        # args (GFile, filename) filename typically a password for pdf?
        arg_string = "(filename, filename)"
    elif  ImageFormat.has_one_arg_loader(format_moniker) :
        # load procedure has args (GFile)
        arg_string = "(filename)"
    elif  ImageFormat.has_three_arg_loader(format_moniker) :
        # from and to frame index.  The saved image has one frame, index 0 ?
        arg_string = "(filename, 0, 0)"
    else:
      raise Exception(f"Not implemented loader args case: {format_moniker}")

    # GimpFu will convert filename to GFile for first arg
    test_image = eval("pdb." + loader_name + arg_string)
    return test_image




def ensure_test_file(image, drawable, format_moniker):
    """ Ensure exists a file having canonical filename for given format: format_moniker.
    If file already exists, return filename.
    Else call save procedure, from given image, drawable.

    Return filename (like /tmp/tmp123/test.jpeg)
    Return whether save_procedure ran, and whether it succeeded.
    """
    extension = ImageFormat.get_extension(format_moniker)
    TestDir.ensure_test_dir()
    filename = TestDir.test_filename_with_extension(extension)
    logger.info(f"Test file: {filename}")

    if os.path.isfile(filename):
        # file already exists
        did_saver_run = False
        did_saver_pass = False
    else:
        # If save procedure exists, invoke it
        did_saver_run, did_saver_pass = save_file(image, drawable, format_moniker, filename)

    if not os.path.isfile(filename):
        filename = None
    # assert file exists or filename is None

    return filename, did_saver_run, did_saver_pass




def condense_results_to_tuple_pair(format_moniker, did_saver_run, did_saver_pass, did_loader_run, did_loader_pass):
    result = []
    if did_saver_run:
        if did_saver_pass:
            result.append("Pass")
        else:
            result.append("Fail")
    else:
        result.append("NoTest")
    if did_loader_run:
        if did_loader_pass:
            result.append("Pass")
        else:
            result.append("Fail")
    else:
        result.append("NoTest")
    return tuple(result)


'''
OLD
def format_result(format_moniker, did_saver_run, did_saver_pass, did_loader_run, did_loader_pass):
    """ Return string describing test results. """
    # TODO say something about file preexists?

    result = format_moniker.ljust(10) + ": "

    if did_saver_run:
        if did_saver_pass:
            result += "Save procedure PASS. "
        else:
            result += "Save procedure FAIL. "
    else:
        result += "Save procedure NO TEST: test file exists or save procedure not exist. "
    if did_loader_run:
        if did_loader_pass:
            result += "Load procedure PASS. "
        else:
            result += "Load procedure FAIL. "
    else:
        result += "Load procedure NO TEST: no test file exists or load procedure not exist. "
    return result
'''

def test_result_to_str(format_moniker, test_result):
    """ Return string describing individual test results. """
    # TODO say something about file preexists?

    # The ideal result if test setup is correct, i.e. empty test directory
    expected_result = KnownGoodAllTestResult.expected_result(format_moniker)

    result = format_moniker.ljust(10) + ": " + test_result[0].ljust(10) + "," + test_result[1].ljust(10)
    #logger.info(test_result, expected_result, test_result==expected_result)

    # append notes for omitted and unexpected results
    if  test_result == ("Omit", "Omit"):
        result += " Reason: " + ImageFormat.get_reason_for_omission(format_moniker)
    if test_result != expected_result :
        # test of the format failed in one or more aspects, from the ideal
        result += " Ideal: " + str(expected_result)
    return result


def test_file_format(image, drawable, format_moniker):
    """ Test loading and/or saving of format_moniker.

    Try create a test file if saver exists.
    When cannot create
    (when there is no Gimp.PDB.file_foo_save procedure of kind "save")

    TODO when file already exists, do we test the saver?

    Then try loading.
    When c
    Return a string describing result.
    """
    filename, did_saver_run, did_saver_pass = ensure_test_file(image, drawable, format_moniker)

    if filename is not None:
        if ImageFormat.exists_loader(format_moniker):
            did_loader_run = True
            test_image = load_file(image, drawable, filename, format_moniker)
            if test_image is not None:
                image_display = pdb.gimp_display_new (test_image)
                did_loader_pass = True
            else:
                did_loader_pass = False
        else:
            did_loader_run = False
            did_loader_pass = False
    else:
        did_loader_run = False
        did_loader_pass = False

    result = condense_results_to_tuple_pair(format_moniker, did_saver_run, did_saver_pass,  did_loader_run, did_loader_pass)
    return result






def test_all_file_formats(image, drawable):
    log = []

    TestDir.populate_sample_files()

    all_result = AllTestResult()

    for format_moniker in ImageFormat.all_format_monikers:
        if ImageFormat.excludeFromTests(format_moniker):
            single_result = ("Omit", "Omit" )
        else:
            single_result = test_file_format(image, drawable, format_moniker)

        log.append(test_result_to_str(format_moniker, single_result))
        all_result[format_moniker] = single_result

    logger.info("testFileLoad summary of 'Test All' ")
    logger.info("Format      Save       Load      Notes")
    for line in log: logger.info(line)
    # This is a GimpFu plugin so other GimpFu messages may precede or follow, and might be pertinent

    # return boolean: did all individual tests match known good result?
    go_nogo_result = (all_result == KnownGoodAllTestResult.known_good_all_test_result)
    logger.info(f"If test result is unexpectedly False, insure test directory is empty before starting.")
    logger.info(f"testFileLoad go/nogo: {go_nogo_result}")
    return go_nogo_result



def plugin_func(image, drawable, run_all, file_format_index):
    """ Run one or all save/load tests of file formats.

    Can be run non-interactive.
    """
    global logger
    logger = get_logger()

    if run_all:
        result = test_all_file_formats(image, drawable)
    else:
        # get moniker from same list we showed in GUI
        format_moniker = ImageFormat.all_format_monikers[file_format_index]
        result = test_file_format(image, drawable, format_moniker)
        logger.info(f"Test>File save/load: {test_result_to_str(format_moniker, result)}")

    # when interactive, show the test images we saved/loaded
    gimp.displays_flush()

    # return boolean result of individual test, or test all
    return result


register(
      "python-fu-test-file-save-load",
      "Test load and/or save images of any/all file formats",
      "See console for results.",
      "Lloyd Konneker",
      "Lloyd Konneker",
      "2020",
      "File save/load...",
      "",
      [
          (PF_IMAGE, "image", "Input image", None),
          (PF_DRAWABLE, "drawable", "Input drawable", None),
          (PF_TOGGLE, "run_all", "Run all?", 1),
          (PF_OPTION, "format", "Format", 0, ImageFormat.all_format_monikers),
      ],
      [(PF_BOOL, "result", "Whether test passed.", True)],
      plugin_func,
      menu="<Image>/Test")
main()
