
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
For each enum, in this code, insert a call to define_symbols_for_enum(Gimp.MergeType).
But if you don't have an example from GimpFu v2,
you won't know whether you need a suffix, prefix, or neither.

2) Hand code
Search the GimpFu v2 code for abberant enum definitions.
Insert code to define them.
'''

import gi
gi.require_version("Gimp", "3.0")
from gi.repository import Gimp

import logging

module_logger = logging.getLogger('GimpFu.gimpenums')


'''
# TODO:

code a static list of Gimp enum type names e.g. ("Gimp.ImageType",)

for each
    introspect to get list of symbols in the enum type (is that possible?)
    mangle symbol (get the upper case suffix, sometimes suffix it with "_MODE")
    define a Python symbol having the mangled name
    (meta programming, use eval? or just chunk in __dict__)
    e.g. eval("RGB_IMAGE = Gimp.ImageType.RGB_IMAGE")
'''


def list_gimp_enums():
    """ Return a list of Gimp enum short names.
    Its a libgimp function.
    """
    names, count_names = gimp.enums_get_type_names()
    return names


def get_long_enum_name(enum):
    """ Return long name of the short name of a Gimp enum type.

    e.g. short_name is 'MergeType', long_name is 'Gimp.MergeType'
    """
    short_name = enum.__name__
    # Qualify with Gimp namespace
    long_name = "Gimp." + short_name
    # print("Enum name: ", long_name)
    return long_name


"""
TODO we could check that a symbol is not already defined before we define it.
"""

def define_symbols_for_enum(enum, prefix="", suffix=""):
    '''
    Define into the GimpFu Python global namespace:
    all the constants defined by enum.
    Require enum is a Gimp type.
    enum is-a class.  type(enum) == 'type'

    Also, for backward compatibility, prefix and suffix with given strings.
    Prepend with prefix, or suffend with suffix, where not None.
    Note there was not much consistency in v2: some prefixed, some suffixed.

    This is metaprogramming.
    We are not directly defining the names in this Python text,
    we are inserting the names into the namespace (i.e. dir ).

    Example:
    enum is Gimp.HistogramChannel
    Statements:
        global CLIP_TO_IMAGE
        CLIP_TO_IMAGE = Gimp.MergeType.CLIP_TO_IMAGE
    '''
    #print(enum, type(enum))
    enum_class_name = get_long_enum_name(enum)
    # search the names in the dir of the enum
    for attribute in dir(enum):
        # Crudity: assume anything upper case is what we want.
        if attribute.isupper():
            defining_statement = prefix + attribute + suffix + " = " + enum_class_name + "." + attribute
            #print(defining_statement)
            # Second argument insures definition goes into global namespace
            # See Python docs for exec()
            # TODO check its not already in the global namespace
            exec(defining_statement, globals())

    # TODO check off the Gimp enums we aliased, log any we didn't.


module_logger.info("defining enums...")





"""
'''
Cruft
Iterate over dir(enum type)
Use any upper case attributes as constants
define into the current namespace
by exec()'ing appropriate statement string
'''
# Gimp.DodgeBurnType
foo = Gimp.HistogramChannel
#print(foo)
#print(dir(foo))
for attribute in dir(foo):
    if attribute.isupper():
        statement = "HISTOGRAM_" + attribute + " = Gimp.HistogramChannel." + attribute
        #print(statement)
        exec(statement)
"""

"""
TODO open an issue with Gimp:
Gimp names for enum types is inconsistent, not alway FooType, sometimes just Foo.
"""

def define_backward_enums_programatically():
    """
    Each case is a pattern that we manually divulged from reading
    GimpFu v2 or plugins using it.
    """
    define_symbols_for_enum(Gimp.MergeType)
    # Layer merge types
    # FLATTEN_IMAGE = Gimp.MergeType.FLATTEN_IMAGE

    define_symbols_for_enum(Gimp.ImageBaseType)
    # ImageBaseType is superset of ImageType, i.e. RGB => RGB, RGBA, etc.
    #RGB                 = Gimp.ImageBaseType.RGB  # GRAY, INDEXED

    define_symbols_for_enum(Gimp.ImageType)
    #RGB_IMAGE           = Gimp.ImageType.RGB_IMAGE

    define_symbols_for_enum(Gimp.LayerMode, suffix='_MODE')
    #NORMAL_MODE         = Gimp.LayerMode.NORMAL
    #MULTIPLY_MODE       = Gimp.LayerMode.MULTIPLY

    define_symbols_for_enum(Gimp.FillType, suffix='_FILL')
    # TODO some wild plugins refer to e.g. FILL_TRANSPARENT, with a prefix
    #BACKGROUND_FILL     = Gimp.FillType.BACKGROUND
    #WHITE_FILL          = Gimp.FillType.WHITE

    define_symbols_for_enum(Gimp.ChannelOps, prefix='CHANNEL_OP_')
    #CHANNEL_OP_REPLACE  = Gimp.ChannelOps.REPLACE

    define_symbols_for_enum(Gimp.GradientType, prefix='GRADIENT_')
    #GRADIENT_RADIAL     = Gimp.GradientType.RADIAL

    define_symbols_for_enum(Gimp.RepeatMode, prefix='REPEAT_')
    #REPEAT_NONE         = Gimp.RepeatMode.NONE

    define_symbols_for_enum(Gimp.HistogramChannel, prefix='HISTOGRAM_')
    #HISTOGRAM_VALUE      = Gimp.HistogramChannel.VALUE

    define_symbols_for_enum(Gimp.MaskApplyMode, prefix='MASK_')
    #MASK_APPLY           = Gimp.MaskApplyMode.APPLY

    # New to v3, or possibly since 2.8
    # Prefix and suffix?  ADD_ALPHA_TRANSFER_MASK seen in feather_paste.py
    define_symbols_for_enum(Gimp.AddMaskType, prefix='ADD_MASK_')
    # ADD_MASK_SELECTION = Gimp.AddMaskType.SELECTION

    define_symbols_for_enum(Gimp.SizeType)
    # PIXELS = Gimp.SizeType.PIXELS,     POINTS

    define_symbols_for_enum(Gimp.HueRange, prefix='HUE_RANGE_')
    # HUE_RANGE_ALL = Gimp.HueRange.ALL

    # TODO this is a guess, find a test case in the wild
    define_symbols_for_enum(Gimp.DesaturateMode, prefix='DESATURATE_')
    # DESATURATE_LIGHNTESS = Gimp.DesaturateMode.LIGHTNESS

    # For image conversions

    define_symbols_for_enum(Gimp.ConvertDitherType, prefix='DITHER_')
    # scale conversion
    # DITHER_NONE = Gimp.ConvertDitherType.None

    define_symbols_for_enum(Gimp.ConvertPaletteType, prefix='PALETTE_')
    # mode conversion
    # PALETTE_MONO = Gimp.ConvertPaletteType.MONO

    define_symbols_for_enum(Gimp.RotationType, prefix='ROTATE_')
    # ROTATE_90 = Gimp.RotationType.90


# Cruft exploring how to get enum names from properties of enum class
#for bar in foo:
#for bar in foo.props:
#for bar in foo.list_properties():
#    print(bar)
