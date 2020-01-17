'''
Types defined by GimpFu.
And methods to alias some Gimp types into GimpFu namespace.

The aliases:
- gimp
- pdb
These cannot be defined until after Gimp is imported

!!! To get in the importers namespace, use "from gimpfu_types import *"
'''

from collections import namedtuple



'''
v3 At import time, we don't have access to Gimp types yet.  Define PF enum without them.
PF_TYPES eum (sic) is used in actual parameters to register(), before the plugin is registered.
We don't need mapping to Gimp.GimpPDB types until register() executes.
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




# v3 _registered_plugins_ is a dictionary of namedtuple
# declare struct type "Procedure"
GimpFuProcedure = namedtuple("GimpFuProcedure", [ 'BLURB', 'HELP', 'AUTHOR', 'COPYRIGHT',
   'DATE', 'MENUITEMLABEL', 'IMAGETYPES', 'PLUGIN_TYPE',
   'PARAMS', 'RESULTS', 'FUNCTION', 'MENUPATH', 'DOMAIN', 'ON_QUERY', 'ON_RUN' ])

GimpFuFormalParam = namedtuple("GimpFuFormalParam",
    [ 'PF_TYPE', 'LABEL', 'DESC', 'DEFAULT_VALUE', 'EXTRAS' ],
    defaults = [None])  # EXTRAS defaults to None.  Python 3.7

'''
from enum import Enum
# @unique
class FieldIndex(Enum):
  BLURB = 0,
'''
