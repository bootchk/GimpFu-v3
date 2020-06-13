'''
A test Gimp plugin
that:
- tests pdb procedures that load files named file_foo_load()

!!! All should be named according to a forumula.
!!! They have different signatures.

Depends on specific test directory existing.
Does NOT depend on test files existing.
You can empty the test directory, and it will create test files
(effectively testing both save and load procedures.)
'''
import os
from gimpfu import *

"""
These tuples separate file formats into classes
according to signature of file save/load procedures.

Some have defaulted args that are not tested.
"""

# For aberrant cases, where loader not have extension embedded in name
map_format_to_extension = {
"sunras" : "ras",
"openraster" : "ora"    # or .sun, etc.
}

two_arg_file_formats = ("pdf", )
one_arg_file_formats = ( "bmp", "bz2", "dds", "dicom", "fits", "fli", "gbr",
                    "gif", "gih", "gz", "ico", "jpeg", "pat", "pcx", "pix",
                    "png", "pnm", "psd", "raw", "sgi",
                    "tga", "tiff", "xbm", "xmc", "xwd", "xz")
# where the file extension is not embedded in the loader name
noncanonical_ext_file_formats = ("sunras", "openraster")

# TODO "cel" )
# TODO "faxg3", "gex", "hgt", "psp", "svg" has no save procedure, thus we cannot create
# TODO Gimp names use "jpeg" so we won't open .jpg files.
# TODO rgbe is file-load-rgbe, named non-canonically
# TODO sunras is file-sunras-load but extensions are many e.g. .sun, .ras, etc.
# TODO ora is file-openraster-load
# TODO xcf is gimp-xcf-load
# TODO unknown i.e. using magic is gimp-file-load

# TODO also thumbs???

all_file_formats = two_arg_file_formats + one_arg_file_formats + noncanonical_ext_file_formats

def create_test_filename_for_format(file_format_name):
    return "/work/test/test." + file_format_name

def create_file_for_filename(image, drawable, loader_name, filename):
    """ Tell Gimp to create file of given: filename having format: file_format_name from: image, drawable. """
    # like: pdb.file_bmp_save(image, drawable, filename)
    # TODO is actually saver_name
    eval("pdb.file_" + loader_name + "_save(image, drawable, filename)")
    # if the pdb procedure does not exist, this fails quietly and file still not exist


def ensure_test_file(image, drawable, loader_name, file_format_name):
    """ Ensure exists a file having canonical filename of given format: file_format_name.

    Return canonical filename (like /work/test/test.jpeg)

    If file already exists, return it.
    Else try create, from given image, drawable.

    If file not exist and cannot create it, return None.
    """
    filename = create_test_filename_for_format(file_format_name)
    if not os.path.isfile(filename):
        # pass loader_name, not file_format_name
        create_file_for_filename(image, drawable, loader_name, filename)
    if not os.path.isfile(filename):
        filename = None
        # raise Exception(f"Could not create test file for format: {file_format_name}.")
    print(f"Test file: {filename}")
    return filename


def load_file(image, drawable, loader_name, file_format_name):
    """ Tell Gimp to load test file of given file_format_name.

    Return new image.

    File need not exist.
    Will try create file from image, drawable
    """
    filename = ensure_test_file(image, drawable, loader_name, file_format_name)
    if filename is None:
        image = None
    else:
        # Like test_pdb.file_jpeg_load(filename)
        image = eval("pdb.file_" + loader_name + "_load(filename)")
    return image


def plugin_func(image, drawable, file_format_index):
    """ Attempt to load test file of given format.

    Try create the file if it does not exist.
    If cannot create (when there is no Gimp.PDB.file_foo_save procedure of kind "save")
    show a message.
    """

    # get name from same list we showed in GUI
    file_format_name = all_file_formats[file_format_index]

    if file_format_name in two_arg_file_formats :
        # load procedure has args (GFile, str) e.g. pdf
        filename = ensure_test_file(image, drawable, file_format_name)
        if filename is None:
            test_image = None
        else:
            # GimpFu will convert filename to GFile
            test_image =  pdb.file_pdf_load(filename, filename)
    elif file_format_name in one_arg_file_formats :
        # load procedure has args (GFile)
        # loader name is canonical with file_format_name embedded
        test_image = load_file(image, drawable, file_format_name, file_format_name)
    elif file_format_name in noncanonical_ext_file_formats :
        # load procedure has args (GFile)
        # get file ext from dictionary
        file_ext = map_format_to_extension[file_format_name]
        test_image = load_file(image, drawable, file_format_name, file_ext )
    else:
      raise Exception("Not implemented format case")

    if test_image is not None:
        image_display = pdb.gimp_display_new (test_image)
    else:
        gimp.message("File to load doesn't exist and there is no Gimp PDB procedure to create one.")
        # OR other errror?
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
          (PF_OPTION, "format", "Format", 0, all_file_formats),
      ],
      [],
      plugin_func,
      menu="<Image>/Test")
main()
