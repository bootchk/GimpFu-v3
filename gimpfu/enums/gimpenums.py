
'''
Define Python symbols for Gimp enums.

Symbols that:
- are aliases of the Gimp enums.
- are shorter, abbreviations of Gimp enums.
- are compatible with GimpFu v2, which also defined a set of symbols.

Convenience for authors (save typing.)
And for backward compatibility.

In GimpFu, enums are named like RGB_IMAGE.
- Capitalized.
- With underbar character.

Examples:
GimpFu's RGB_IMAGE is an alias for introspected Gimp.ImageType.RGB_IMAGE
GimpFu's NORMAL_MODE is an alias for Gimp.LayerMode.NORMAL
   (note that the GimpFu name has suffix "_MODE")

Usually the names used in Gimp are the same as used in GimpFu v2 (except for prefix or suffix).
But there are some abberations from that rule.

GimpFu enums:
- most are generated programatically from introspected Gimp enums.
- some are defined statically, FBC: (sometimes deprecated or obsolete)
  see backward_enums.py


!!! Since we have already "from gi.repository import Gimp",
the machinery (PyGObject?) already put the enums in the namespace,
just with long names like Gimp.ImageType.RGB_IMAGE
We can crudely search the namespace.
'''

'''
TODO Warn about deprecated symbols.
A deprecated symbol is used by v2 plugins
but no longer has a corresponding Gimp enum.
Do not warn about symbol that are now moot.
A moot symbol is one used by v2 plugins,
but only in GimpFu methods that are adapted.
TODO think about this some more


FIXME
=====

GimpFu v2 see gimpenumsmodule.c
It creates a Python module named _gimpenums.

It uses PyGObject, has a different code structure.
This should use that code, just update it to not be C.



The process for writing this module
===================================
1) Generate automagically
In an API doc for Gimp generated from its .gir:
scroll to the 'Other section'
where enums are described.
(But the section also includes some constants that are not enums.)
Most enums are name like:
- Gimp.FooType
- Gimp.ChannelOps
- Gimp.FooMode
For each enum, in this code, insert a call to wrangler.define_symbols_for_enum(Gimp.MergeType).
But if you don't have an example from GimpFu v2,
you won't know whether you need a suffix, prefix, or neither.

2) Hand code
Search the GimpFu v2 code for abberant enum definitions.
Insert code to define them.
'''

import gi
gi.require_version("Gimp", "3.0")
from gi.repository import Gimp

from enums.enumTypeSet import EnumWrangler

import logging

module_logger = logging.getLogger('GimpFu.gimpenums')


"""
TODO open an issue with Gimp:
Gimp names for enum types is inconsistent, not alway FooType, sometimes just Foo.
Usually Foo + [Type, Mode, Range]
"""



def define_enums_into_global_namespace():

    wrangler = EnumWrangler()

    module_logger.info("Defining adulterated backward compatible symbols for Gimp enums")
    define_backward_enums(wrangler)

    module_logger.info("Defining unadulterated backward compatible symbols for Gimp enums")
    define_backward_abbreviations(wrangler)

    """
    Straight, unadulterated definition as an abbreviation.
    No suffix or prefix.
    For all that we have not already defined for backward compatibility.
    TODO or for all,
    i.e. define both PALLETTE_MONO and MONO

    This is controversial.
    Why should we clutter up the namespace?

    Possibly we need to do it in a certain order.
    For example, Gimp.ImageBaseType and Gimp.ImageType have conflicts,
    would try to define the same abbreviations for different enum values.
    """
    module_logger.info("Defining more abbreviations for Gimp enums")
    wrangler.define_symbols_for_unchecked_enums()


def define_backward_enums(wrangler):
    """
    Define symbols for Gimp enums, for backward compatibility.

    Each case is a pattern we divulged from reading
    GimpFu v2 or plugins using it.

    Symbols are adulterated from symbols used in Gimp V3, for backward compatibility.

    The patterns:

    Pattern                                          Example Gimp type
    Suffix: Gimp.FooMode.Bar => BAR_MODE              LayerMode     NORMAL_MODE
    Prefix: Gimp.FooMode.Bar => FOO_BAR               RepeatMode    REPEAT_NONE
    Prefix: Gimp.FooType.Bar => FOO_BAR               GradientType  GRADIENT_RADIAL
    Prefix shorten: Gimp.FooZedType.Bar => FOO_BAR    HistogramChannel HISTORRAM_VALUE
    Prefix plurality change: Gimp.Foos.Bar => FOO_BAR ChannelOps    CHANNEL_OP_REPLACE
    Prefix word change: FooType.Bar =>  FOOTION_BAR   RotationType  ROTATE_90
    Combination:  ZedFooType.Bar => FOO_BAR           ConvertPaletteType PALLETTE_MONO
    """

    # Note we use the dotted name of the Gimp enums

    wrangler.define_symbols_for_enum(Gimp.LayerMode, suffix='_MODE')
    #NORMAL_MODE         = Gimp.LayerMode.NORMAL
    #MULTIPLY_MODE       = Gimp.LayerMode.MULTIPLY

    wrangler.define_symbols_for_enum(Gimp.FillType, suffix='_FILL')
    # TODO some wild plugins refer to e.g. FILL_TRANSPARENT, with a prefix
    #BACKGROUND_FILL     = Gimp.FillType.BACKGROUND
    #WHITE_FILL          = Gimp.FillType.WHITE

    wrangler.define_symbols_for_enum(Gimp.ChannelOps, prefix='CHANNEL_OP_')
    #CHANNEL_OP_REPLACE  = Gimp.ChannelOps.REPLACE

    wrangler.define_symbols_for_enum(Gimp.GradientType, prefix='GRADIENT_')
    #GRADIENT_RADIAL     = Gimp.GradientType.RADIAL

    wrangler.define_symbols_for_enum(Gimp.RepeatMode, prefix='REPEAT_')
    #REPEAT_NONE         = Gimp.RepeatMode.NONE

    wrangler.define_symbols_for_enum(Gimp.HistogramChannel, prefix='HISTOGRAM_')
    #HISTOGRAM_VALUE      = Gimp.HistogramChannel.VALUE

    wrangler.define_symbols_for_enum(Gimp.MaskApplyMode, prefix='MASK_')
    #MASK_APPLY           = Gimp.MaskApplyMode.APPLY

    # New to v3, or possibly since 2.8
    # Prefix and suffix?  ADD_ALPHA_TRANSFER_MASK seen in feather_paste.py
    wrangler.define_symbols_for_enum(Gimp.AddMaskType, prefix='ADD_MASK_')
    # ADD_MASK_SELECTION = Gimp.AddMaskType.SELECTION

    wrangler.define_symbols_for_enum(Gimp.HueRange, prefix='HUE_RANGE_')
    # HUE_RANGE_ALL = Gimp.HueRange.ALL

    # TODO this is a guess, find a test case in the wild
    wrangler.define_symbols_for_enum(Gimp.DesaturateMode, prefix='DESATURATE_')
    # DESATURATE_LIGHNTESS = Gimp.DesaturateMode.LIGHTNESS

    # For image conversions

    wrangler.define_symbols_for_enum(Gimp.ConvertDitherType, prefix='DITHER_')
    # scale conversion
    # DITHER_NONE = Gimp.ConvertDitherType.None

    wrangler.define_symbols_for_enum(Gimp.ConvertPaletteType, prefix='PALETTE_')
    # mode conversion
    # PALETTE_MONO = Gimp.ConvertPaletteType.MONO

    wrangler.define_symbols_for_enum(Gimp.RotationType, prefix='ROTATE_')
    # ROTATE_90 = Gimp.RotationType.90




def define_backward_abbreviations(wrangler):
    """
    Define unadulterated  symbols for Gimp enums.
    For a limited set that GimpFu v2 defined.

    Not adulterated, same symbol as used in Gimp V3.
    But an abbreviation (not in dot notation.)
    """

    wrangler.define_symbols_for_enum(Gimp.SizeType)
    # PIXELS = Gimp.SizeType.PIXELS,     POINTS
    wrangler.define_symbols_for_enum(Gimp.MergeType)
    # Layer merge types
    # FLATTEN_IMAGE = Gimp.MergeType.FLATTEN_IMAGE

    wrangler.define_symbols_for_enum(Gimp.ImageBaseType)
    # ImageBaseType is superset of ImageType, i.e. RGB => RGB, RGBA, etc.
    #RGB                 = Gimp.ImageBaseType.RGB  # GRAY, INDEXED

    wrangler.define_symbols_for_enum(Gimp.ImageType)
    #RGB_IMAGE           = Gimp.ImageType.RGB_IMAGE







# Cruft exploring how to get enum names from properties of enum class
#for bar in foo:
#for bar in foo.props:
#for bar in foo.list_properties():
#    print(bar)
