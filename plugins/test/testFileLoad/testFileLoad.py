#!/usr/bin/env python3
# lkk add hashbang

'''
A Gimp plugin that:
- tests PDB procedures that save and load image files

!!! See ImageFormat in image_format.py which hides many vagaries of the PDB.

Depends on specific test directory existing.
Does NOT depend on test files existing.
You can empty the test directory, and it can create test files (using save procedure)
(effectively testing both save and load procedures.)

When this plugin cannot create IN test files (since there is no save procedure in Gimp)
you can still test loading but
you must manually create such files in the test directory.

Optionally will omit testing file formats known to crash the test harness.

Some format loader/savers have defaulted args that are not tested.
I.E. this does not understand the details about a format,
and does not stress test all possibilities for a format.
I.E. only does basic sanity test: creates or reads a file.
Does not compare resulting images or files with known good result images or files.

You should first open an image.
Typically image is of a sophisticated mode, and has alpha.
The image is then repeatedly saved in test formats, and reloaded.
This plugin automatically down converts mode for some formats.
This plugin automatically removes alpha for some formats.
IOW this plugin tries hard to make a minimal conversion succeed.

You should first open an unsophisticated mode image, say gray or 1-bit B&W.
This plugin does NOT yet up convert mode.
'''
import os
from gimpfu import *

from image_format import ImageFormat


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
    print(eval_string)
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
    else:
      raise Exception(f"Not implemented loader args case: {format_moniker}")

    # GimpFu will convert filename to GFile for first arg
    test_image = eval("pdb." + loader_name + arg_string)
    return test_image




def ensure_test_file(image, drawable, format_moniker):
    """ Ensure exists a file having canonical filename for given format: format_moniker.

    Return canonical filename (like /work/test/test.jpeg)

    If file already exists, return filename.
    Else try create, from given image, drawable.

    Return whether save_procedure ran, and whether it succeeded.
    """
    filename = ImageFormat.canned_filename(format_moniker)

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

    result =  format_result(format_moniker, did_saver_run, did_saver_pass,  did_loader_run, did_loader_pass)
    return result


def test_all_file_formats(image, drawable):
    log = []
    for format_moniker in ImageFormat.all_format_monikers:
        if ImageFormat.excludeFromTests(format_moniker):
            result = f"{format_moniker}: Omitted test."
        else:
            result = test_file_format(image, drawable, format_moniker)
        # append line to logger
        log.append(result)

    print("testFileLoad summary of 'Test All' ")
    for line in log: print(line)
    # This is a GimpFu plugin so other GimpFu messages may precede or follow, and might be pertinent



def plugin_func(image, drawable, run_all, file_format_index):
    """ Run one or all save/load tests of file formats.
    """
    if run_all:
        test_all_file_formats(image, drawable)
    else:
        # get moniker from same list we showed in GUI
        format_moniker = ImageFormat.all_format_monikers[file_format_index]
        result = test_file_format(image, drawable, format_moniker)
        print(f"Test>File save/load: {result}")

    # show the test images we saved/loaded
    gimp.displays_flush()


register(
      "python-fu-test-file-load",
      "Test load and/or save images of various file formats",
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
      [],
      plugin_func,
      menu="<Image>/Test")
main()
