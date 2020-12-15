'''
PF_foo enums defined by GimpFu.

These constants describe parameter types AND GUI widget types.
Used in args to register(), before the plugin is registered.
We don't need mapping to Gimp.GimpPDB types (if any) until register() executes.

There is no longer any correspondence to similar enums/constants that GIMP might define.

FBC.  This may eventually go away.

!!! To get in the Authors namespace, gimpfu_top executes "from gimpfu_enums import *"
Remember everything here is evaluated and goes into the global namespace.

v3 At import time, we don't have access to Gimp types yet.  Define PF enum without them.

We don't use Python 3 enum class FBC.
'''
PF_INT8        = 1
PF_INT16       = 2
PF_INT32       = 3
PF_INT         = 4
PF_FLOAT       = 5
PF_STRING      = 6
PF_VALUE       = 7
#PF_INT8ARRAY   = PDB_INT8ARRAY
#PF_INT16ARRAY  = PDB_INT16ARRAY
#PF_INT32ARRAY  = PDB_INT32ARRAY
#PF_INTARRAY    = PF_INT32ARRAY
#PF_FLOATARRAY  = PDB_FLOATARRAY
#PF_STRINGARRAY = PDB_STRINGARRAY
PF_COLOR       = 8
PF_COLOUR      = 9
PF_ITEM        = 10
PF_DISPLAY     = 11
PF_IMAGE       = 12
PF_LAYER       = 13
PF_CHANNEL     = 14
PF_DRAWABLE    = 15
PF_VECTORS     = 16
#PF_SELECTION   = PDB_SELECTION
#PF_BOUNDARY    = PDB_BOUNDARY
#PF_PATH        = PDB_PATH
#PF_STATUS      = PDB_STATUS
PF_TOGGLE      = 1000
PF_BOOL        = PF_TOGGLE
PF_SLIDER      = 1001
PF_SPINNER     = 1002
PF_ADJUSTMENT  = PF_SPINNER
PF_FONT        = 1003
PF_FILE        = 1004
PF_BRUSH       = 1005
PF_PATTERN     = 1006
PF_GRADIENT    = 1007
PF_RADIO       = 1008
PF_TEXT        = 1009
PF_PALETTE     = 1010
PF_FILENAME    = 1011
PF_DIRNAME     = 1012
PF_OPTION      = 1013


'''
from enum import Enum
# @unique
class FieldIndex(Enum):
  BLURB = 0,
'''
