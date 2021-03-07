'''
PF_ enums defined by GimpFu.

These constants describe parameter types AND GUI widget types.
Used in args to register(), before the plugin is registered.
We don't need mapping to Gimp.GimpPDB types (if any) until register() executes.

There is no longer any correspondence to similar enums/constants that GIMP might define.
The values are arbitrary, you can reorder/renumber them.
No plugin should persist values of this enum.

FBC.  This may eventually go away.
GIMP itself may define a similar enum.

!!! To get in the Authors namespace, gimpfu_top executes "from gimpfu_enums import *"
Remember everything here is evaluated and goes into the global namespace.

v3 At import time, we don't have access to Gimp types yet.  Define PF enum without them.

We don't use Python 3 enum class FBC.

See also _edit_map dictionary in gui/widget_factory.py

We define aliases, FBC, so that old scripts may continue to work.
The GimpFu code should use the non-alias, so the aliases can be deleted later.
The GimpFu code cannot check that an author used an alias, without parsing the script.
'''
PF_INT8        = 1  # Should be UINT8 or PF_CHAR
PF_INT16       = 2  # Should be obsolete, not supported in Gimp?
PF_INT32       = 3  # Should be obsolete, same as PF_INT
PF_INT         = 4
PF_FLOAT       = 5
PF_STRING      = 6
PF_BOOL        = 7
PF_VALUE       = 8  # ??? Meaning ???

PF_COLOR       = 9
PF_COLOUR      = PF_COLOR   # FBC, an alias

# gimp ephemeral object related, integer ID valued?

# No widgets, for return values only
PF_ITEM        = 10
PF_DISPLAY     = 11

PF_IMAGE       = 12
PF_LAYER       = 13
PF_CHANNEL     = 14
PF_DRAWABLE    = 15
PF_VECTORS     = 16

# vestiges of v2, what are they?
#PF_SELECTION   = PDB_SELECTION
#PF_BOUNDARY    = PDB_BOUNDARY
#PF_PATH        = PDB_PATH
#PF_STATUS      = PDB_STATUS

PF_TOGGLE      = PF_BOOL    # alias, same widget

# float valued
PF_SLIDER      = 1001
PF_SPINNER     = 1002
PF_ADJUSTMENT  = PF_SPINNER  # alias, same widget

# integer valued, different widgets
PF_RADIO       = 1010  # radio button group
PF_OPTION      = 1011  # pulldown menu i.e. combobox

# TODO PF_ENUM, integer valued, widget is a Gimp.EnumComboBox,
# extras is a Gimp enum gtype?

# different widget for a PF_STRING
PF_TEXT        = 1020

# file related
PF_FILE        = 1100   # GFile valued ?
PF_FILENAME    = 1101   # string valued ?
PF_DIRNAME     = 1102

# gimp resource related, resources are named with strings
PF_FONT        = 1200
PF_BRUSH       = 1201
PF_PATTERN     = 1202
PF_GRADIENT    = 1203
PF_PALETTE     = 1204

# Arrays.  GimpFu has no widgets for these.  Only to declare types of return values.

# PF_INTARRAY Obsolete.  Could be an alias for INT32 FBC, but it was never defined in v2
# PF_INT16ARRAY  was never defined in v2, and won't be implemented in v3
# No plugin can return Gimp.ParamArray or Gimp.ParamObjectArray ???

PF_INT8ARRAY   = 1300
PF_INT32ARRAY  = 1301
PF_FLOATARRAY  = 1302
PF_STRINGARRAY = 1303
PF_GIMP_OBJECT_ARRAY = 1304   # Array of Gimp objects
PF_GIMP_RGB_ARRAY    = 1305   # Array of Gimp RGB objects (colors)


'''
Cruft to use Python enum enforcing uniqueness
from enum import Enum
# @unique
class FieldIndex(Enum):
  BLURB = 0,
'''
