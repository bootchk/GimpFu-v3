


"""
Understands image file formats.

Moniker: name embedded in save/load procedure.

Understands and hides:
- Moniker is not always the same as file format extension.
- save and load procedure names not always named canonically e.g. file_moniker_save
- signatures differ among save and load procedures
"""
class ImageFormat:
    """
    These tuples separate file formats into classes
    according to signature of file save/load procedures.

    Some have defaulted args that are not tested.
    """

    # Exclude formats from test
    # Where we know they crash the plugin and want the plugin to test everything else
    excluded_from_test = ("openraster")

    # For aberrant cases, where load procedure name not have extension embedded in name
    map_moniker_to_extension = {
    "sunras" : "ras",
    "openraster" : "ora"    # or .sun, etc.
    }

    # separate moniker classes by loader signature
    two_arg_file_formats = ("pdf", )
    one_arg_file_formats = ( "bmp", "bz2", "dds", "dicom", "fits", "fli", "gbr",
                        "gif", "gih", "gz", "ico", "jpeg", "openraster", "pat", "pcx", "pix",
                        "png", "pnm", "psd", "raw", "sgi", "sunras",
                        "tga", "tiff", "xbm", "xmc", "xwd", "xz")

    # formats whose save procedure take (num_drawables int, drawable GimpObjectArray)
    single_drawable_save_formats = ( )
    # "bmp", "bz2", "dds", "dicom", "gz", "pdf")



    # TODO "cel" )
    # TODO "faxg3", "gex", "hgt", "psp", "svg" has no save procedure, thus we cannot create
    # TODO Gimp names use "jpeg" so we won't open .jpg files.
    # loader named non-canonically
    # TODO rgbe is file-load-rgbe,
    # TODO xcf is gimp-xcf-load
    # loader named semi-canonically but extension not embedded in name
    # TODO sunras is file-sunras-load but extensions are many e.g. .sun, .ras, etc.
    # TODO ora is file-openraster-load

    # TODO unknown i.e. using magic is gimp-file-load

    # TODO also thumbs???

    all_format_monikers = two_arg_file_formats + one_arg_file_formats

    def excludeFromTests(format_moniker):
        return format_moniker in ImageFormat.excluded_from_test

    def canned_filename(format_moniker):
        # TODO aberrant cases
        # TODO extension from format_moniker
        if format_moniker in ImageFormat.map_moniker_to_extension.keys():
            extension = ImageFormat.map_moniker_to_extension[format_moniker]
        else:
            # extension same as moniker
            extension = format_moniker
        result = "/work/test/test." + extension
        print(f"Test file: {result}")
        return result


    """
    Knows name of PDB save  and load procedures.
    """
    def saver_name(format_moniker):
        # TODO aberrant cases
        return "file_" + format_moniker + "_save"

    def loader_name(format_moniker):
        # TODO aberrant cases
        """
        elif ImageFormat.has_noncanonical_loader(format_moniker):
            format_moniker in noncanonical_ext_file_formats :
            # load procedure has args (GFile)
            # get file ext from dictionary
            file_ext = map_format_to_extension[format_moniker]
            test_image = load_file(image, drawable, format_moniker, file_ext )
        """
        return "file_" + format_moniker + "_load"


    """
    Knows signatures of format.
    """
    def has_two_arg_loader(format_moniker):
        return format_moniker in ImageFormat.two_arg_file_formats
    def has_one_arg_loader(format_moniker):
        return format_moniker in ImageFormat.one_arg_file_formats

    def saver_takes_single_drawable(format_moniker):
        return format_moniker in ImageFormat.single_drawable_save_formats
