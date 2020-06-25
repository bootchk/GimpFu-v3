
import logging

from gimpfu import *   # pdb and enums for mode conversions


logger = logging.getLogger("TestExportImport.ImageFormat")

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

    """
    Exclude formats from test all
    Where we know they fail and want to test everything else.
    You can still test individually, just not using "test all"
    Especially when they crash the *test plugin*, not just return error from PDB call.
    Some may enter the debugger and wait on user interaction.

    Reasons are subject to change.
    They are snapshots in time for a given state of Gimp development.
    Reasons given may be wrong.
    When bugs in Gimp are fixed, remove these reasons.
    Any tester can alter this temporarily.
    Should permanently remove a line when issue is closed.
    """
    map_omission_to_reason = {
        "cel"        : "Known crash",
        "openraster" : "Known to crash in Python load/save procedure",
        "gih"        : "Known crash, waiting on GimpParamStringArray implementation.",
        "colorxhtml" : "Known to crash in Python load/save procedure",
        "csource"    : "Docs say won't run non-interactively",
        "psp"        : "Can't locate a sample of this ancient format"
    }

    # procedures not named canonically file-<foo>-[load,save]
    # Python names, with underbar
    map_moniker_to_loader_name = {
    "rgbe" : "file_load_rgbe",
    "xcf"  :  "gimp_xcf_load",
    }
    map_moniker_to_saver_name = {
    "rgbe" : "file_save_rgbe",
    "xcf"  :  "gimp_xcf_save",
    }


    # moniker classes by loader signature
    # fli requires two extra args
    three_arg_file_formats = ("fli", )
    # pdf signature is (filename, filename as a password?)
    two_arg_file_formats = ("pdf", )
    one_arg_file_formats = ( "bmp", "bz2", "cel", "dds", "dicom", "faxg3", "fits",
                        "gbr", "gif", "gih", "gz",
                        "hgt", "ico", "jpeg", "openraster",
                        "pat", "pcx", "pix", "png", "pnm", "psd", "psp",
                        "raw", "rgbe", "sgi", "sunras", "svg",
                        "tga", "tiff", "xbm",
                        "xcf", "xmc", "xwd", "xz")
    # Gimp can save but not load
    no_loader_formats = ("colorxhtml", "csource", "exr", "header", "html_table",
                        "pbm", "pfm", "pgm", "ppm", )

    # !!! Note procedure is named file-html-table_save, but we transliterate - to _ since this is Python GimpFu

    # formats whose save procedure take (drawable) and not (num_drawables, GimpObjectArray of drawables)
    single_drawable_save_formats = ( )

    # formats which Gimp can load but not save.
    no_saver_formats = ("faxg3", "hgt", "psp", "svg")
    # faxg3 fax  .g3
    # hgt "height" or elevation maps NASA SRTM  Gimp only supports SRTM-1 and SRTM-3 variants
    # psp Paintshop pro (ancient, not later than Paintshop6, say pre 2005, later format extension is .pspimage Gimp Issue #493)
    # svg scalable vector graphics

    # TODO unknown format i.e. using magic is gimp-file-load

    # TODO also test thumbs???

    # All formats that can be tested.
    # Note that no_saver_formats are not included, since they are in the loader_formats
    all_format_monikers = two_arg_file_formats + one_arg_file_formats + no_loader_formats + three_arg_file_formats

    """
    formats whose saver requires downmode image
    Here "downmode" encompasses any of: lower the mode, remove alpha, scale down
    """
    # to mode indexed or less
    downmode_to_BW_formats = ("gif", "fli", "xbm")
    downmode_to_gray_formats = ("")
    # remove alpha i.e. flatten
    downmode_to_sans_alpha_formats = ("dicom", "fits")
    # xmc handles at most 256 pixels
    downmode_to_small_size_formats = ("xmc", )



    def excludeFromTests(format_moniker):
        return format_moniker in ImageFormat.map_omission_to_reason.keys()

    def get_reason_for_omission(format_moniker):
        return ImageFormat.map_omission_to_reason[format_moniker]

    def get_extension(format_moniker):
        """ Return extension for format_moniker"""

        if format_moniker in ImageFormat.map_moniker_to_extension.keys():
            result = ImageFormat.map_moniker_to_extension[format_moniker]
        else:
            # extension same as moniker
            result = format_moniker
        return result


    """
    Knows name of PDB save  and load procedures.
    """
    def exists_loader(format_moniker):
        return not format_moniker in ImageFormat.no_loader_formats

    def exists_saver(format_moniker):
        return not format_moniker in ImageFormat.no_saver_formats



    def saver_name(format_moniker):
        if format_moniker in ImageFormat.map_moniker_to_saver_name.keys():
            result = ImageFormat.map_moniker_to_saver_name[format_moniker]
        else:
            result = "file_" + format_moniker + "_save"
        return result

    def loader_name(format_moniker):
        if format_moniker in ImageFormat.map_moniker_to_loader_name.keys():
            result = ImageFormat.map_moniker_to_loader_name[format_moniker]
        else:
            result = "file_" + format_moniker + "_load"
        return result



    """
    Knows signatures of format.
    """
    def has_two_arg_loader(format_moniker):
        return format_moniker in ImageFormat.two_arg_file_formats
    def has_one_arg_loader(format_moniker):
        return format_moniker in ImageFormat.one_arg_file_formats
    def has_three_arg_loader(format_moniker):
        return format_moniker in ImageFormat.three_arg_file_formats

    def saver_takes_single_drawable(format_moniker):
        return format_moniker in ImageFormat.single_drawable_save_formats




    """
    Down moding.
    Understands what modes some formats require.

    TODO extract to ModeConverter class
    """
    def compatible_mode_image(format_moniker, image, drawable):
        """ Return a down-moded image of mode that format requires.

        Image is to-be-saved.
        TODO xmc appears to save any image, but won't load its own dogfood.
        """
        if format_moniker in ImageFormat.downmode_to_BW_formats :
            logger.info("Down moding to mode indexed B&W")
            # format requires indexed.  Convert to lowest common denominator: one-bit B&W mono
            # TODO convert only xbm to B&W, convert others to pallete
            new_image = pdb.gimp_image_duplicate(image)
            # TODO defaults not working
            pdb.gimp_image_convert_indexed(new_image, DITHER_NONE, PALETTE_MONO, 0, False, False, "foo")
            new_drawable = pdb.gimp_image_get_active_layer(new_image)
            result = new_image, new_drawable
        elif format_moniker in ImageFormat.downmode_to_gray_formats:
            logger.info("Down moding to mode gray")
            new_image = pdb.gimp_image_duplicate(image)
            pdb.gimp_image_convert_grayscale(new_image)
            new_drawable = pdb.gimp_image_get_active_layer(new_image)
            result = new_image, new_drawable
        elif format_moniker in ImageFormat.downmode_to_sans_alpha_formats:
            # format requires without alpha
            if pdb.gimp_drawable_has_alpha(drawable):
                logger.info("Down moding to sans alpha")
                new_image = pdb.gimp_image_duplicate(image )
                # flatten removes alpha channel
                pdb.gimp_image_flatten(new_image)
                new_drawable = pdb.gimp_image_get_active_layer(new_image)
                result = new_image, new_drawable
            else:
                result = image, drawable
        elif format_moniker in ImageFormat.downmode_to_small_size_formats:
            logger.info("Down moding to 256 pixels")
            # !!! 256 is the total, i.e. 16x16
            new_image = pdb.gimp_image_duplicate(image )
            pdb.gimp_image_scale(new_image, 16, 16)
            new_drawable = pdb.gimp_image_get_active_layer(new_image)
            result = new_image, new_drawable
        else:
            # format can be any mode, can have alpha, can be any size
            result = image, drawable
        return result

        """
        elif format_moniker in ("xbm",):
            # 1 bit indexed
            # TODO
            result = image, drawable
        """
