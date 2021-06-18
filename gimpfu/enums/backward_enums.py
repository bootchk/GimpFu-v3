"""
FBC (for backward compatibility)

Put certain symbols for constants into global namespace.

These are cases that the code that defines Gimp enums can't handle.
That is, they don't seem to fit any pattern that can be done programatically.
They date from the early days of Gimp and GimpFu.

These are evaluated at import time, generally from the top module.
The order of importing this is important so you don't overwrite any more recently defined enums.

Note that we access Gimp gir but don't call any Gimp methods,
which will fail until we call Gimp.main()
"""


import gi
gi.require_version("Gimp", "3.0")
from gi.repository import Gimp


# TODO put these in a list and warn of deprecated use by defining __getattr__ on top module


# TODO this is a don't care, because GimpFu adapts all functions that use it??
FG_BG_RGB_MODE      = 1999

# TODO not sure this is correct
FG_BUCKET_FILL      = Gimp.FillType.FOREGROUND
BG_BUCKET_FILL      = Gimp.FillType.BACKGROUND

# Note that even in Gimp2, COLOR_MODE meant HSL_COLOR, not HSV
SATURATION_MODE = Gimp.LayerMode.HSV_SATURATION
HUE_MODE        = Gimp.LayerMode.HSV_HUE
COLOR_MODE = Gimp.LayerMode.HSL_COLOR
VALUE_MODE = Gimp.LayerMode.HSV_VALUE




# Rest is WIP

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

"""
TRUE and FALSE are obsolete in GimpFu v3.
The following code from GimpFu v2 has problems.

from adaption.deprectated_constant import _DeprecatedConstant

TRUE = _DeprecatedConstant(True, 'gimpenums.TRUE', 'True')
FALSE = _DeprecatedConstant(False, 'gimpenums.FALSE', 'False')

del _DeprecatedConstant
"""
