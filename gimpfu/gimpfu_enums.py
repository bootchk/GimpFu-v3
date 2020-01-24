
'''
Define Python symbols for Gimp enums.

These are aliases.
Convenience for GimpFu plugin authors.

TODO Warn about deprecated symbols.
A deprecated symbol is used by v2 plugins
but no longer has a corresponding Gimp enum.
Do not warn about symbol that are now moot.
A moot symbol is one used by v2 plugins,
but only in GimpFu methods that are adapted.
TODO think about this some more

TODO hack, just the ones reference by clothify, not real values

If nothing else, enumerate them all here.
Probably should automate it,
if the names used in Gimp are the same (except for prefix)
Probably there are some abberations.
'''

import gi
gi.require_version("Gimp", "3.0")
from gi.repository import Gimp

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


# ImageBaseType is superset of ImageType, i.e. RGB => RGB, RGBA, etc.
RGB = Gimp.ImageBaseType.RGB  # GRAY, INDEXED

RGB_IMAGE           = Gimp.ImageType.RGB_IMAGE

NORMAL_MODE         = Gimp.LayerMode.NORMAL
MULTIPLY_MODE       = Gimp.LayerMode.MULTIPLY

BACKGROUND_FILL     = Gimp.FillType.BACKGROUND
WHITE_FILL          = Gimp.FillType.WHITE

CHANNEL_OP_REPLACE  = Gimp.ChannelOps.REPLACE

# TODO this is a don't care, because GimpFu adapts all functions that use it??
FG_BG_RGB_MODE      = 1999

GRADIENT_RADIAL     = Gimp.GradientType.RADIAL

# TODO not sure this is correct
BG_BUCKET_FILL      = Gimp.FillType.BACKGROUND

REPEAT_NONE         = Gimp.RepeatMode.NONE

"""
from v2 plugin/pygimp/gimpenums-types.defs, which is perl script??
GIMP_FOREGROUND_FILL")
'("background-fill" "GIMP_BACKGROUND_FILL")
'("white-fill" "GIMP_WHITE_FILL")
'("transparent-fill" "GIMP_TRANSPARENT_FILL")
'("pattern-fill" "GIMP_PATTERN_FILL")
"""

# Not work Gimp.BucketFillMode.BG

# How to to this manually
# see /usr/local/share/gir-1.0/gimp<>.gir
# find apropos typename.  Use the short name (appears lower case, like "background") ???

'''
GIMP_BUCKET_FILL_FG,      /*< desc="FG color fill" >*/
  GIMP_BUCKET_FILL_BG,      /*< desc="BG color fill" >*/
  GIMP_BUCKET_FILL_PATTERN
'''
