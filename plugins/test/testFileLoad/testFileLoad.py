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

Cannot create IN test files (no save procedure in Gimp)
so to test load only,
manually create such files in the test directory.

Optionally will omit testing file formats known to crash the test harness.
'''
import os
from gimpfu import *

from image_format import ImageFormat




def create_file_for_filename(image, drawable, format_moniker, filename):
    """ Tell Gimp to create file named: *filename* having format: *format_moniker* from: image, drawable.
    """
    # assert filename already has format's extension
    # typical evaluated string: pdb.file_bmp_save(image, drawable, filename)

    saver_name = ImageFormat.saver_name(format_moniker)

    if ImageFormat.saver_takes_single_drawable(format_moniker):
        arg_string = "(image, drawable, filename)"
    else:
        # has signature image, drawable_count, GObjectArray, filename
        # GimpFu will convert single drawable instance to GObjectArray
        arg_string = "(image, 1, drawable, filename)"

    eval_string = "pdb." + saver_name + arg_string
    print(eval_string)
    eval(eval_string)
    # if the pdb procedure does not exist, this fails quietly and file still not exist



def ensure_test_file(image, drawable, format_moniker):
    """ Ensure exists a file having canonical filename for given format: format_moniker.

    Return canonical filename (like /work/test/test.jpeg)

    If file already exists, return it.
    Else try create, from given image, drawable.

    If file not exist and cannot create it, return None.
    """
    filename = ImageFormat.canned_filename(format_moniker)

    if os.path.isfile(filename):
        # file already exists
        did_saver_run = False
    else:
        create_file_for_filename(image, drawable, format_moniker, filename)
        did_saver_run = True
        # Saver ran but might have failed to create file
        if not os.path.isfile(filename):
            filename = None

    # assert file exists or filename is None
    return filename, did_saver_run


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



def test_file_format(image, drawable, format_moniker):
    """ Test loading and sometimes saving of format_moniker.

    Try create a test file if it does not exist.
    When cannot create show a message
    (when there is no Gimp.PDB.file_foo_save procedure of kind "save")

    Return a string describing result.
    """
    filename, did_saver_run = ensure_test_file(image, drawable, format_moniker)

    if filename is None:
        # gimp.message("File to load doesn't exist and there is no Gimp PDB procedure to create one.")
        if did_saver_run:
            result = "Test file not exist and save procedure failed.)"
        else:
            result = "Test file not exist and no save procedure to create it."
    else:
        test_image = load_file(image, drawable, filename, format_moniker)
        if test_image is not None:
            image_display = pdb.gimp_display_new (test_image)
            # TODO say whether the saver ran
            result = "Passed"
        else:
            result = "Loader failed."
    return result


def test_all_file_formats(image, drawable):
    log = []
    for format_moniker in ImageFormat.all_format_monikers:
        if ImageFormat.excludeFromTests(format_moniker):
            result = "Omitted test."
        else:
            result = test_file_format(image, drawable, format_moniker)
        log.append(format_moniker + ": " + result + "\n")
    print(log)



def plugin_func(image, drawable, run_all, file_format_index):
    """ Run one or all save/load tests of file formats.
    """
    if run_all:
        test_all_file_formats(image, drawable)
    else:
        # get moniker from same list we showed in GUI
        format_moniker = ImageFormat.all_format_monikers[file_format_index]
        result = test_file_format(image, drawable, format_moniker)
        print(f"Test>File save/load: {format_moniker} result: {result}")

    # show the test images we saved/loaded
    gimp.displays_flush()


register(
      "python-fu-test-file-load",
      "Test load and save images of various file formats",
      "No help",
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
