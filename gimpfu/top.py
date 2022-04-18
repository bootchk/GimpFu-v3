#   GimpFu - Lets you write GIMP plug-ins in Python, with a simple API.
#   Copyright (C) 1997  James Henstridge <james@daa.com.au>
#   Copyright (C) 2020  Lloyd Konneker <konnekerl@gmail.com>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.


"""
Simple interface to write GIMP plug-ins in Python.
An alternative is to use GObject Introspection and not import GimpFu.

GimpFu provides a simpler API, only two methods:
   register() to register your plug-in
   main() to enter the machinery for plugins when your plugin is executed.

Gimp will call your plug-in function as needed.
Gimp will also show a dialog to let a user edit plug-in
parameters when a user invokes your plug-in interactively.
Gimp will also save the last used parameters, so a user can
"Repeat" or "Reshow" your filters with those saved parameters.
Gimp will also flush displays so the user sees the plugin results
when a user runs your plug-in interactively.
All these features are provided by Gimp, whether or not you use GimpFu,
since Gimp 3.

The register() function of GimpFu is similar to the Gimp methods
for registering a plugin, but simplified.

A typical gimpfu plug-in would look like this:
  from gimpfu import *

  def plugin_func(image, drawable, arg):
              # do what plugins do best
              pass

  register(
              "plugin-name",
              "blurb",
              "help message",
              "author",
              "copyright",
              "year",
              N_("My plug-in menu label..."),
              "*",
              [
                  (PF_IMAGE, "image", "Input image", None),
                  (PF_DRAWABLE, "drawable", "Input drawable", None),
                  (PF_STRING, "arg", "a_argument", "default-value")
              ],
              [],
              plugin_func,
              menu="<Image>/Somewhere"
          )

  main()

The call to "from gimpfu import *" imports gimp constants
into the plug-in namespace, and also imports the symbols: gimp, pdb,
register and main.  This should be just about all any plug-in needs.

Use any of the PF_* constants as parameter types.
They denote the kind of user interface control for the plugin's dialog box.
The PF_SPINNER and PF_SLIDER types expect a fifth element in their description tuple -- a
3-tuple of the form (lower,upper,step), which defines the valid limits for
the setting.

All the strings in the example are your choices, following these guidelines:
"plugin-name" should use hyphens.
GimpFu will canonicalize the name (make it meet standards) before registering it
(the example yields actual name "python-fu-plugin-name".)
Argument names ("image", etc.) should not use spaces.
They do not need to match the names of the formal parameters of the "plugin_func".
Parameter descriptions should match the formal parameters in number.
The symbol plugin_func can be anything but must be a valid Python identifier.
The menu label should follow common conventions: first letter capitalized and
using trailing "...." to denote a dialog will open.
The menu path string (e.g. "<Image>/Somewhere"): the prefix must be from a small
set defined elsewhere, and the suffix "Somewhere" is optional:
your choice to make a new sub-menu.
Omitting the menu path description is deprecated (highly discouraged).
"*" denotes image_types the plugin will accept, from a small set:
"RGB", "RGBA", "RGB*", "GRAY", "GRAYA", "GRAY*"

TODO or a tuple???
TODO return values.
TODO domain

To localize your plug-in, add an optional domain parameter to
the register call. It can be the name of the translation domain or a
tuple that consists of the translation domain and the directory where
the translations are installed.  Then use N_() to surround GUI strings
that should be translated, as in the example.
"""

"""
Notations used in the comments:

"FBC" denotes 'For Backward Compatibility' of v2 plugins

'Author' denotes a writer of plugins, not a programmer of this code
"""

"""
This is a discusssion about what we import and expose in the Author's namespace.
An author uses "from gimpfu import *" which gets everything here.
!!! By design, we limit what we expose.
These are judgement calls, and may change.
FBC we may expose more than we would if a complete redesign.

We expose the GimpFu API: (consider these as keywords, or primary phrases)
   - register()
   - main()
   - pdb and gimp instances (aliases)
   - GimpFu enums (e.g. PF_)
   - GimpFu aliases for Gimp enums (e.g. )
   - i18n methods (gettext)

We do NOT expose:  (Authors must import themselves)
- GI, but Author's plugins MAY use GI.  GimpFu heavily uses GI.
- math i.e. "import math" although v2 did

TODO should warn(), fail() be in the API?  gimp.message will already work.
TODO v2 import gimpcolor
TODO v2 class error(RuntimeError): pass
TODO v2 class CancelError(RuntimeError): pass
"""


"""
Log this top level, because Gimp gives uninformative "wire error" when Python crashes.

The most common error is to call a Gimp method before Gimp.main() is called.
Then Gimp fails assert that GIMP_IS_PLUGIN(PLUGIN)
i.e. that the plugin as called Gimp.main() and initialized the Gimp variable "PLUGIN"
"""
# TODO should this be exposed? Rename to gimpfuLogger so name clash less likely
from gimpfu.logger.logger import FuLogger
logger = FuLogger.getGimpFuLogger()


"""
TODO see PEP 562 module __getattr__
Define __getattr__ for this module to warn of deprecated enums
"""

'''
Expose to Authors in global namespace:
   abbreviated and backward compatible symbols Gimp enums
   GimpFu enums
   more, abbreviated symbols for Gimp.Enum classes (some for backward compatibility)
All defined enum symbols are upper case, without dot notation.

TODO Use "from gimpenums import *" form so author does not need prefix gimpenums.RGB
Name "gimpenums" retained for FBC, some non-GimpFu plugins may "from gimpenums import *"
'''
logger.info("defining backward compatible, deprecated enums")
from gimpfu.enums.backward_enums import *

logger.info("defining GimpFu enums e.g. PF_INT ")
from gimpfu.enums.gimpfu_enums import *

logger.info("defining short names of long names of Gimp enum types e.g. HSV_COLOR_MODE")
from gimpfu.enums.gimpenums import *
"""
At one time the above crashed on Alpine but not on Ubuntu.
with assertion GIMP_IS_PLUGIN(PLUGIN) fail.
May be a race to create plugin, or maybe I just hacked improperly on Alpine.
"""




'''
Expose to Authors : alias symbols "gimp" and "pdb"
It is not as simple as:
    pdb=Gimp.get_pdb()
    OR from gi.repository import Gimp as gimp
These are adapters.

Using GI, convention is first letter capital e.g. "Gimp."
"Gimp" symbol is NOT equivalent to the "gimp" symbol,
but they have similar methods/attributes.
'''
logger.info("defining pdb and gimp aliases")
from gimpfu.aliases.pdb import GimpfuPDB
pdb = GimpfuPDB()

from gimpfu.aliases.gimp import GimpfuGimp
gimp = GimpfuGimp()




logger.info("Initializing i18n")
'''
localization, i18n

Here the call to gettext.install installs an alias _() into built-in scope (global.)

If instead a plugin author wants to internationalize their plugin,
or a module of their plugin,
they might use this code in their modules:
    t = gettext.translation("myPlugin", Gimp.locale_directory(), fallback=True)
    _ = t.gettext

See docs/internationalization.txt.
'''
import gettext
gettext.install("gimp30-python", Gimp.locale_directory())

logger.warning(f"translations for domain gimp30-python in {Gimp.locale_directory()}")


# v2 defined this.  FBC, keep it in v3.
# But most plugins that use it are probably not doing runtime localization.
def N_(message):
    return message



'''
# Warn v2 authors
# Signature that will catch gettext older versions
def override_gettext_install(name, locale, **kwargs):
    logger.info("Warning: GimpFu plugins should not call gettext.install, it is already done.")

gettext.install = override_gettext_install
'''


'''
Register locally with GimpFu, not with Gimp.

Each Authors source may contain many calls to register(), i.e. many procedures.
'''
def register(proc_name, blurb, help, author, copyright,
            date, label, imagetypes,
            params, results, function,
            menu=None, domain=None, on_query=None, on_run=None):
    """ GimpFu method that registers a plug-in. May be called many times from same source file."""

    logger.info(f"register() called with: {proc_name}")
    from gimpfu.procedure.procedure import FuProcedure
    from gimpfu.procedures.procedures import FuProcedures

    gf_procedure = FuProcedure(proc_name, blurb, help, author, copyright,
                            date, label, imagetypes,
                            params, results, function,
                            menu, domain, on_query, on_run)

    FuProcedures.register(gf_procedure)

    # !!! Have not conveyed to Gimp yet


def main():
    """Authors should call this after register()."""
    logger.info('main() called')

    # Late imports so not in Author's namespace
    import sys
    import gi
    gi.require_version("Gimp", "3.0")
    from gi.repository import Gimp
    from gimpfu.plugin import FuPlugin

    # !!! Pass a GType which is a GObject class defining a plugin, that Gimp will instantiate.
    Gimp.main(FuPlugin.__gtype__, sys.argv)
    """
    Gimp will register this plugin in the PDB,
    and eventually call the registered Author's "function"
    the so-called "run func" when this plugin is invoked.
    The actual method that Gimp will call is
    a method of FuRunner (see runner.py)
    which interposes between Gimp and Author's "function".
    """

logger.info("Done with import from top")
