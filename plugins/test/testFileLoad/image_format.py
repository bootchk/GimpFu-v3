

from gimpfu import *   # pdb and enums for mode conversions

"""
Understands Gimp capabilities re image file formats.

Moniker: name embedded in save/load procedure.

Understands and hides:
- Moniker is not always the same as file format extension.
- save and load procedure names not always named canonically e.g. file_moniker_save
- signatures differ among save and load procedures
- formats can be: save-only, load-only, or load-or-save
"""
class ImageFormat:
    """
    This class data is metadata about file formats
    and the signature of file save/load procedures.

    This was derived manually.
    It could be automated by querying the PDB ?
    """

    # TODO heif plugin? was in 2.10.2

    # Exclude formats from test all
    # Where we know they crash the test plugin and want the plugin to test everything else
    # You can still test individually, just not using "test all"
    excluded_from_test = ("cel", "openraster", "gih", "colorxhtml" )


    # Aberrant cases, where load/save procedure moniker not have extension embedded in name
    # loader named canonically but extension not embedded in name
    # sunras is file-sunras-load but extensions are many e.g. .sun, .ras, etc.
    # openraster is file-openraster-load but extension is ora
    map_moniker_to_extension = {
    "sunras"     : "ras",
    "openraster" : "ora",    # or .sun, etc.
    "rgbe"       : "hdr",
    "colorxhtml" : "xhtml",
    "csource"    : "c",    # C source
    "header"     : "h",     # C header source
    "html-table" : "html",
    }
    #  "exr", "pbm", "pfm", "pgm", "ppm", )


    # moniker classes by loader signature
    two_arg_file_formats = ("pdf", )
    one_arg_file_formats = ( "bmp", "bz2", "cel", "dds", "dicom", "fits", "fli", "gbr",
                        "gif", "gih", "gz", "ico", "jpeg", "openraster", "pat", "pcx", "pix",
                        "png", "pnm", "psd", "raw", "rgbe", "sgi", "sunras",
                        "tga", "tiff", "xbm", "xcf", "xmc", "xwd", "xz")
    no_loader_formats = ("colorxhtml", "csource", "exr", "header", "html_table",
                        "pbm", "pfm", "pgm", "ppm", )

    # !!! Note procedure is named file-html-table_save, but we transliterate - to _ since this is Python GimpFu

    # formats whose save procedure take (drawable) and not (num_drawabled, GimpObjectArray of drawables)
    single_drawable_save_formats = ( )

    no_saver_formats = ("faxg3", "gex", "hgt", "psp", "svg")

    # Savers that require image of specific mode:
    # gif, indexed color
    # flic, indexed or gray
    # TODO

    # TODO Gimp names use "jpeg" so we won't open .jpg files.

    # loader named non-canonically
    # handled in code below, not metadata
    # rgbe is file-load-rgbe
    # xcf is gimp-xcf-load

    # TODO unknown i.e. using magic is gimp-file-load

    # TODO also thumbs???


    all_format_monikers = two_arg_file_formats + one_arg_file_formats + no_loader_formats + no_saver_formats


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
    def exists_loader(format_moniker):
        return not format_moniker in ImageFormat.no_loader_formats

    def exists_saver(format_moniker):
        return not format_moniker in ImageFormat.no_saver_formats


    def saver_name(format_moniker):
        # abberations
        if format_moniker == "rgbe":
            return "file_save_rgbe"
        elif format_moniker == "xcf":
            return "gimp_xcf_save"
        else:
            # canonical
            return "file_" + format_moniker + "_save"

    def loader_name(format_moniker):
        # aberrations
        if format_moniker == "rgbe":
            return "file_load_rgbe"
        elif format_moniker == "xcf":
            return "gimp_xcf_save"
        else:
            # canonical
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

    """
    Down moding.
    Understands what modes some format_monikers require.

    TODO extract to ModeConverter class
    """
    def compatible_mode_image(format_moniker, image, drawable):
        """ Return a down-moded image of mode that moniker accepts.  """
        if format_moniker in ("gif", "flic") :
            # indexed.  Convert to one-bit B&W mono
            new_image = pdb.gimp_image_duplicate(image)
            # TODO defaults not working
            pdb.gimp_image_convert_indexed(new_image, DITHER_NONE, PALETTE_MONO, 0, False, False, "foo")
            new_drawable = pdb.gimp_image_get_active_layer(new_image)
            result = new_image, new_drawable
        elif format_moniker in ("dicom", "fits"):
            # no alpha
            if pdb.gimp_drawable_has_alpha(drawable):
                # TODO copy  image, get alpha channel, remove it
                new_image = pdb.gimp_image_duplicate(image )
                # new_drawable = pdb.gimp_get_active_layer(image)
                pdb.gimp_image_flatten(new_image)
                new_drawable = pdb.gimp_image_get_active_layer(new_image)
                result = new_image, new_drawable
            else:
                result = image, drawable
        elif format_moniker in ("xbm",):
            # 1 bit indexed
            # TODO
            result = image, drawable
        else:
            result = image, drawable
        return result
