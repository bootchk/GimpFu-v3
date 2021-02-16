
'''
Define Python symbols for Gimp enums.

Symbols that:
- are aliases of the Gimp enums.
- are shorter, abbreviations of Gimp enums.
- are compatible with GimpFu v2, which also defined a set of symbols.
- are in this module's namespace and can be "from gimpenums.py import *"

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
"Gimp" is in the namespace,
and authors CAN use long names like Gimp.ImageType.RGB_IMAGE.
Also, this module can access the original enum types e.g. Gimp.ImageType

To test: start Gimp.  Filters>Development>Python Console.
>from gimpfu import *
>dir()
That will show you the namespace that authors see.

Implementation note:
The symbols are defined into this module's namespace.
We call modules to generate statements that define the symbols,
but we exec() them here so the symbols are in THIS namespace.
Second argument to exec "globals()" insures definitions in scope COME from global namespace.
It does not ensure that defined symbols go INTO global namespace.
See Python docs for exec()

!!! Do not define functions in this module.
They would remain in the global namespace when GimpFu imports this module.
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
For each enum, in this code, insert a call to ets.defining_statements_for_enum(Gimp.MergeType).
But if you don't have an example from GimpFu v2,
you won't know whether you need a suffix, prefix, or neither.

2) Hand code
Search the GimpFu v2 code for abberant enum definitions.
Insert code to define them.
'''

import gi
gi.require_version("Gimp", "3.0")
from gi.repository import Gimp

from gimpfu.enums.enumTypeSet import EnumTypeSet

import logging

module_logger = logging.getLogger('GimpFu.gimpenums')


"""
TODO open an issue with Gimp:
Gimp names for enum types is inconsistent, not alway FooType, sometimes just Foo.
Usually Foo + [Type, Mode, Range]
"""




ets = EnumTypeSet()

module_logger.info("Defining adulterated backward compatible symbols for Gimp enums")

"""
Define symbols for Gimp enums, for backward compatibility.

Each case is a pattern we divulged by reading GimpFu v2 or plugins using it.

Symbols are adulterated from symbols used in Gimp V3, for backward compatibility.
In other words, Gimp and GimpFu v2 lacked consistency of naming,
and this keeps the inconsistent names.

The patterns:

Pattern                                          Example Gimp type
Suffix: Gimp.FooMode.Bar => BAR_MODE              LayerMode     NORMAL_MODE
Prefix: Gimp.FooMode.Bar => FOO_BAR               RepeatMode    REPEAT_NONE
Prefix: Gimp.FooType.Bar => FOO_BAR               GradientType  GRADIENT_RADIAL
Prefix shorten: Gimp.FooZedType.Bar => FOO_BAR    HistogramChannel HISTOGRAM_VALUE
Prefix plurality change: Gimp.Foos.Bar => FOO_BAR ChannelOps    CHANNEL_OP_REPLACE
Prefix word change: FooType.Bar =>  FOOTION_BAR   RotationType  ROTATE_90
Combination:  ZedFooType.Bar => FOO_BAR           ConvertPaletteType PALLETTE_MONO
"""

# Note we use the dotted name of the Gimp enums

for statement in ets.defining_statements_for_enum(Gimp.LayerMode, suffix='_MODE'):
    exec(statement)
#NORMAL_MODE         = Gimp.LayerMode.NORMAL
#MULTIPLY_MODE       = Gimp.LayerMode.MULTIPLY

for statement in ets.defining_statements_for_enum(Gimp.FillType, suffix='_FILL'):
    exec(statement)
# TODO some wild plugins refer to e.g. FILL_TRANSPARENT, with a prefix
#BACKGROUND_FILL     = Gimp.FillType.BACKGROUND
#WHITE_FILL          = Gimp.FillType.WHITE

for statement in ets.defining_statements_for_enum(Gimp.ChannelOps, prefix='CHANNEL_OP_'):
    exec(statement)
#CHANNEL_OP_REPLACE  = Gimp.ChannelOps.REPLACE

for statement in ets.defining_statements_for_enum(Gimp.GradientType, prefix='GRADIENT_'):
    exec(statement)
#GRADIENT_RADIAL     = Gimp.GradientType.RADIAL

for statement in ets.defining_statements_for_enum(Gimp.RepeatMode, prefix='REPEAT_'):
    exec(statement)
#REPEAT_NONE         = Gimp.RepeatMode.NONE

for statement in ets.defining_statements_for_enum(Gimp.HistogramChannel, prefix='HISTOGRAM_'):
    exec(statement)
#HISTOGRAM_VALUE      = Gimp.HistogramChannel.VALUE

for statement in ets.defining_statements_for_enum(Gimp.MaskApplyMode, prefix='MASK_'):
    exec(statement)
#MASK_APPLY           = Gimp.MaskApplyMode.APPLY

# New to v3, or possibly since 2.8
# Prefix and suffix?  ADD_ALPHA_TRANSFER_MASK seen in feather_paste.py
for statement in ets.defining_statements_for_enum(Gimp.AddMaskType, prefix='ADD_MASK_'):
    exec(statement)
# ADD_MASK_SELECTION = Gimp.AddMaskType.SELECTION

for statement in ets.defining_statements_for_enum(Gimp.HueRange, prefix='HUE_RANGE_'):
    exec(statement)
# HUE_RANGE_ALL = Gimp.HueRange.ALL

# TODO this is a guess, find a test case in the wild
for statement in ets.defining_statements_for_enum(Gimp.DesaturateMode, prefix='DESATURATE_'):
    exec(statement)
# DESATURATE_LIGHNTESS = Gimp.DesaturateMode.LIGHTNESS

# For image conversions

for statement in ets.defining_statements_for_enum(Gimp.ConvertDitherType, prefix='DITHER_'):
    exec(statement)
# scale conversion
# DITHER_NONE = Gimp.ConvertDitherType.None

for statement in ets.defining_statements_for_enum(Gimp.ConvertPaletteType, prefix='PALETTE_'):
    exec(statement)
# mode conversion
# PALETTE_MONO = Gimp.ConvertPaletteType.MONO

for statement in ets.defining_statements_for_enum(Gimp.RotationType, prefix='ROTATE_'):
    exec(statement)
# ROTATE_90 = Gimp.RotationType.90




module_logger.info("Defining unadulterated backward compatible symbols for Gimp enums")

"""
Define unadulterated  symbols for Gimp enums.
For a limited set that GimpFu v2 defined.

Not adulterated, same symbol as used in Gimp V3.
But an abbreviation (not in dot notation.)
"""

for statement in ets.defining_statements_for_enum(Gimp.SizeType):
    exec(statement)
# PIXELS = Gimp.SizeType.PIXELS,     POINTS
for statement in ets.defining_statements_for_enum(Gimp.MergeType):
    exec(statement)
# Layer merge types
# FLATTEN_IMAGE = Gimp.MergeType.FLATTEN_IMAGE

for statement in ets.defining_statements_for_enum(Gimp.ImageBaseType):
    exec(statement)
# ImageBaseType is superset of ImageType, i.e. RGB => RGB, RGBA, etc.
#RGB                 = Gimp.ImageBaseType.RGB  # GRAY, INDEXED

for statement in ets.defining_statements_for_enum(Gimp.ImageType):
    exec(statement)
#RGB_IMAGE           = Gimp.ImageType.RGB_IMAGE


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

for statement in ets.defining_statements_for_unchecked_enums():
    exec(statement)


"""
Finally, del superflous symbols from namespace of this module.
"""
del ets
del module_logger
del EnumTypeSet



# Cruft exploring how to get enum names from properties of enum class
#for bar in foo:
#for bar in foo.props:
#for bar in foo.list_properties():
#    print(bar)
