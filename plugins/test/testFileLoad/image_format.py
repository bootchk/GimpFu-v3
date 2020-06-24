

from gimpfu import *   # pdb and enums for mode conversions




"""
Understands Gimp capabilities re image file formats.

Moniker: name embedded in save/load procedure.

Understands and hides:
- Moniker is not always the same as file format extension.
- save and load procedure names not always named canonically e.g. file_moniker_save
- signatures differ among save and load procedures
- formats can be: save-only, load-only, or load-or-save
- formats omitted from testing, usually known bad

To find sample test files, see filestar.com or search github.
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

    """
    Process for determining which extensions are supported.

    1) Run Gimp and open the PDB browser, search for "-load" and "-save" and "file-" etc.
    2) Run Gimp and use File>Open and File>Export and choose the option ""

    Notes:
    file-gex-load is an extension loader, not an image loader
    Gimp uses "jpeg" but this plugin does not detect .jpg files.
    """

    """
    Aberrant cases, where load/save procedure moniker not have extension embedded in name
    Loader is named canonically but extension not embedded in name
    Example: sunras is file-sunras-load but extensions are many e.g. .sun, .ras, etc.
    Example: openraster is file-openraster-load but extension is ora
    """
    map_moniker_to_extension = {
    "sunras"     : "ras",
    "openraster" : "ora",    # or .sun, etc.
    "rgbe"       : "hdr",
    "colorxhtml" : "xhtml",
    "csource"    : "c",    # C source
    "header"     : "h",     # C header source
    "html-table" : "html",
    "faxg3"      : "g3",
    }


    # moniker classes by loader signature
    two_arg_file_formats = ("pdf", )
    one_arg_file_formats = ( "bmp", "bz2", "cel", "dds", "dicom", "faxg3", "fits", "fli",
                        "gbr", "gif", "gih", "gz",
                        "hgt", "ico", "jpeg", "openraster",
                        "pat", "pcx", "pix", "png", "pnm", "psd", "psp",
                        "raw", "rgbe", "sgi", "sunras", "svg",
                        "tga", "tiff", "xbm",
                        "xcf", "xmc", "xwd", "xz")
    no_loader_formats = ("colorxhtml", "csource", "exr", "header", "html_table",
                        "pbm", "pfm", "pgm", "ppm", )

    # !!! Note procedure is named file-html-table_save, but we transliterate - to _ since this is Python GimpFu

    # formats whose save procedure take (drawable) and not (num_drawabled, GimpObjectArray of drawables)
    single_drawable_save_formats = ( )

    # formats which Gimp can load but not save.
    no_saver_formats = ("faxg3", "hgt", "psp", "svg")
    # faxg3 fax  .g3
    # hgt "height" or elevation maps NASA SRTM  Gimp only supports SRTM-1 and SRTM-3 variants
    # psp Paintshop pro (ancient, not later than Paintshop6, say pre 2005, later format extension is .pspimage Gimp Issue #493)
    # svg scalable vector graphics

    # Savers that require image of specific mode:
    # gif, indexed color
    # flic, indexed or gray

    # loader named non-canonically
    # handled in code below, not metadata
    # rgbe is file-load-rgbe
    # xcf is gimp-xcf-load

    # TODO unknown i.e. using magic is gimp-file-load

    # TODO also test thumbs???

    # Note that no_saver_formats are not included, since they are in the loader_formats
    all_format_monikers = two_arg_file_formats + one_arg_file_formats + no_loader_formats

    # formats whose saver requires downmode image
    # to mode indexed or less
    downmode_to_BW_formats = ("gif", "flic", "xbm")
    # remove alpha i.e. flatten
    downmode_to_sans_alpha_formats = ("dicom", "fits")
    # TODO restrict image size xmc



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
    Understands what modes some formats require.

    TODO extract to ModeConverter class
    """
    def compatible_mode_image(format_moniker, image, drawable):
        """ Return a down-moded image of mode that moniker accepts.  """
        if format_moniker in ImageFormat.downmode_to_BW_formats :
            print("Down moding to B&W")
            # format requires indexed.  Convert to lowest common denominator: one-bit B&W mono
            # TODO convert only xbm to B&W, convert others to pallete
            new_image = pdb.gimp_image_duplicate(image)
            # TODO defaults not working
            pdb.gimp_image_convert_indexed(new_image, DITHER_NONE, PALETTE_MONO, 0, False, False, "foo")
            new_drawable = pdb.gimp_image_get_active_layer(new_image)
            result = new_image, new_drawable
        # TODO flic requires indexed or gray but fails on B&W ?
        elif format_moniker in ImageFormat.downmode_to_sans_alpha_formats:
            # format requires without alpha
            if pdb.gimp_drawable_has_alpha(drawable):
                print("Down moding to sans alpha")
                # TODO copy  image, get alpha channel, remove it
                new_image = pdb.gimp_image_duplicate(image )
                # new_drawable = pdb.gimp_get_active_layer(image)
                pdb.gimp_image_flatten(new_image)
                new_drawable = pdb.gimp_image_get_active_layer(new_image)
                result = new_image, new_drawable
            else:
                result = image, drawable
        #TODO xmc save restricted to 256 pixel wide
        else:
            result = image, drawable
        return result

        """
        elif format_moniker in ("xbm",):
            # 1 bit indexed
            # TODO
            result = image, drawable
        """
