
'''
Define Python symbols for Gimp enums.

These are aliases.
Convenience for GimpFu plugin authors.

hack, just the ones reference by clothify
and not real values

If nothing else, enumerate them all here.
Probably should automate it,
if the names used in Gimp are the same (except for prefix)
Probably there are some abberations.
'''

import gi
gi.require_version("Gimp", "3.0")
from gi.repository import Gimp

RGB = 1
RGB_IMAGE  = Gimp.ImageType.RGB_IMAGE
NORMAL_MODE = 1
BACKGROUND_FILL = 1
MULTIPLY_MODE = 1
