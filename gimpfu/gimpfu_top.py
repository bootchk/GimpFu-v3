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
An alternative is to use GObject Introspection
and a template plugin that does not import GimpFu.

GimpFu provides a simple register() function that registers your plug-in.

Gimp will call your plug-in function as needed.
Gimp will also show a dialog to let a user edit plug-in
parameters when a user invokes your plug-in interactively.
Gimp will also save the last used parameters, so a user can
"Repeat" or "Reshow" your filters with those saved parameters.
Gimp will also flush displays so the user sees the plugin results
when a user runs your plug-in interactively.
All these features are provided by Gimp, whether or not you use GimpFu,
since Gimp 3.

When registering the plug-in, you need not specify the run_type parameter.

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

# Using GI, convention is first letter capital e.g. "Gimp."
# FBC GimpFu provides uncapitalized aliases in the namespace: "gimp" and "pdb"

# GimpFu attempts to hide GI, but GimpFu plugins MAY also use GI.


# Expose to Authors: math.  v2 did? v3, Authors must import it themselves
# v2 import math

#print("gimpfu_top begin imports")
import sys


'''
Expose to authors: GI
GI is also heavily used by GimpFu
'''
import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp
from gi.repository import Gio
# from gi.repository import GObject   # for g_param_spec and properties


# imports  for implementation.  Intended to be private from Authors
from runner.runner import FuRunner
from procedure.procedure import FuProcedure
from procedure.procedure_creator import FuProcedureCreator
from procedures.procedures import FuProcedures



from logger.logger import FuLogger
logger = FuLogger.get_logger()



'''
Expose to Authors: Gimp enums
Use "from gimpenums import *" form so author does not need prefix gimpenums.RGB
Name "gimpenums" retained for FBC, some non-GimpFu plugins may import
'''
# cases not handled programatically
from enums.backward_enums import *

# cases handled programatically
from enums.gimpenums import define_enums_into_global_namespace
define_enums_into_global_namespace()

''' Expose to Authors: GimpFu enums e.g. PF_INT '''
from enums.gimpfu_enums import *

# v2 import gimpcolor



'''
Expose to Authors : alias symbols "gimp" and "pdb" to
It is not as simple as:
    pdb=Gimp.get_pdb()
    OR from gi.repository import Gimp as gimp
These are adapters.
'''
from aliases.pdb import GimpfuPDB
pdb = GimpfuPDB()

from aliases.gimp import GimpfuGimp
gimp = GimpfuGimp()




# localization, i18n

# Python 3 ugettext() is deprecated, use gettext() which also returns unicode
import gettext
'''
This does not seem to export to the plugin, but maybe we should not.
This works for this module only.
See Python gettext documentation.
Should we install _ locally, or globally?
Note that this module itself has no translated strings (yet)

t = gettext.translation("gimp30-python", Gimp.locale_directory, fallback=True)
# similar as gettext.install(): put _() in namespace
_ = t.gettext
'''

gettext.install("gimp30-python", Gimp.locale_directory,)

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

# v2 cruft
#class error(RuntimeError): pass
#class CancelError(RuntimeError): pass




"""
The GimpFu API:
   - register()
   - main()
   - pdb instance
   - gimp instance
"""
# TODO should warn() be in the API?  gimp.message will already work.

'''
Register locally with GimpFu, not with Gimp.

Each Authors source may contain many calls to register(), i.e. many procedures.
'''
# A primary phrase in GimpFu language
def register(proc_name, blurb, help, author, copyright,
            date, label, imagetypes,
            params, results, function,
            menu=None, domain=None, on_query=None, on_run=None):
    """ GimpFu method that registers a plug-in. May be called many times from same source file."""

    logger.info(f"register procedure: {proc_name}")

    gf_procedure = FuProcedure(proc_name, blurb, help, author, copyright,
                            date, label, imagetypes,
                            params, results, function,
                            menu, domain, on_query, on_run)

    FuProcedures.register(gf_procedure)

    # !!! Have not conveyed to Gimp yet


# A primary phrase in GimpFu language
def main():
    """This should be called after registering the plug-in."""
    # v2:   gimp.main(None, None, _query, _run)
    logger.info('GimpFu main called')
    Gimp.main(GimpFu.__gtype__, sys.argv)

# TODO fail() is primary phrase???



"""
CRUFT
# TODO still needed in v3?  Not a virtual method of Gimp.Plugin anymore?
def _query():
    raise Exception("v2 method _query called.")
    for plugin in _registered_plugins_.keys():
        (blurb, help, author, copyright, date,
         label, imagetypes, plugin_type,
         params, results, function, menu, domain,
         on_query, on_run) = _registered_plugins_[plugin]

        def make_params(params):
            return [(_type_mapping[x[0]],
                     x[1],
                     _string.replace(x[2], "_", "")) for x in params]

        params = make_params(params)
        # add the run mode argument ...
        params.insert(0, (PDB_INT32, "run-mode",
                                     "The run mode { RUN-INTERACTIVE (0), RUN-NONINTERACTIVE (1) }"))

        results = make_params(results)

        if domain:
            try:
                (domain, locale_dir) = domain
                Gimp.domain_register(domain, locale_dir)
            except ValueError:
                Gimp.domain_register(domain)

        # TODO convert plugin_type type
        # always PLUGIN i.e. filter
        Gimp.install_procedure(plugin, blurb, help, author, copyright,
                               date, label, imagetypes, plugin_type,
                               params, results)

        if menu:
            Gimp.menu_register(plugin, menu)
        if on_query:
            on_query()
"""









'''
See header comments for type Gimp.Plugin in Gimp docs or Gimp C code.

A plugin must define (but not instantiate) a subclass of Gimp.Plugin.
GimpFu is a subclass of Gimp.Plugin.
At runtime, only methods of such a subclass have access to Gimp and its PDB.

GimpFu is wrapper.
Has no properties itself.
More generally (unwrapped) properties  represent params (sic arguments) to ultimate plugin.

_run() above wraps Authors "function" i.e. ultimate plugin method,
which is referred to as "run_func" here and in Gimp documents.

All methods are invoked (callbacks) from Gimp.
Callbacks occur:
- at Gimp startup: do_query_procedures() and do_create_procedure()
- at Gimp execution time:  the <run method chain>
   - when user interacts with Gimp GUI (INTERACTIVE)
   - when another plugin calls a plugin (NONINTERACTIVE)

 The <run method chain>:
    Gimp invokes the run_func registered for the procedure.
    That is some method that Gimpfu has registered such as _run_imageprocedure.
    Thus the call chain is:  Gimp => _run_imageprocedure() or similar => _run()  => <the Authors function>()
    The middle two are wrappers of the Authors function, and manipulate the args for GimpFu purposes.

TODO: Gimp calls all methods from C code using GI after starting the Gimp interpreter?

TODO: why do we not provide concrete implementation of virtual methods: init_procedures() and quit() ?
'''

class GimpFu (Gimp.PlugIn):

    # See prop_holder.py for GProperty stuff

    ## GimpPlugIn virtual methods ##
    '''
    Called at install time,
    OR when ~/.config/GIMP/2.99/pluginrc (a cache of installed plugins) is being recreated.
    '''
    def do_query_procedures(self):
        logger.info("do_query_procedures")

        # TODO Why set the locale again?
        # Maybe this is a requirement documented for class Gimp.Plugin????
        self.set_translation_domain("Gimp30-python",
                                    Gio.file_new_for_path(Gimp.locale_directory()))

        # return list of all procedures implemented in the Authors source code
        # For testing: result =[ gf_procedure.name, ]
        keys = FuProcedures.names()

        # Ensure result is GLib.List () (a Python list suffices) but keys is not a list in Python 3
        result = list(keys)

        return result


    '''
    "run-mode"

    Gimp docs says that Gimp calls this back when plugin is executed.
    ??? But it seems to be called back at installation time also,
    once per call of do_query_procedures.

    In the GimpFu source code: at a call to main(), which calls Gimp.main(), which calls back.
    Thus in the source code AFTER the calls to GimpFu register().
    Thus the GimpFu plugin is GimpFu registered in the local cache.
    It also was registered with Gimp (at installation time.)
    '''


    def do_create_procedure(self, name):

        logger.info (f"do_create_procedure: {name}")

        # We need the kind of plugin, and to ensure the passed name is know to us
        gf_procedure = FuProcedures.get_by_name(name)

        # pass all the flavors of wrapped_run_funcs
        procedure = FuProcedureCreator.create(self, name, gf_procedure, FuRunner.run_imageprocedure, FuRunner.run_context_procedure)

        # ensure result is-a Gimp.Procedure
        return procedure
