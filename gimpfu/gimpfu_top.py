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

import sys


'''
Expose to authors: GI
GI is also heavily used by GimpFu
'''
import gi

# Require 2.32 for GArray instead of GValueArray
# import GLib before Gimp can import and older version of GLib
# gi.require_version("GLib", "2.32")
from gi.repository import GLib

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp
from gi.repository import Gio
from gi.repository import GObject   # for g_param_spec and properties


# imports  for implementation.  Intended to be private from Authors
from adaption.marshal import Marshal
from procedure.procedure import FuProcedure
from procedure.procedure_config import FuProcedureConfig
from procedure.procedure_creator import FuProcedureCreator

from message.proceed_error import *
from message.deprecation import Deprecation
from message.suggest import Suggest

'''
Initialize logging.
See 'Using logging in multiple modules'
recipe https://docs.python.org/3/howto/logging-cookbook.html#logging-cookbook
'''
import logging
logger = logging.getLogger('GimpFu')

# TODO make the level come from the command line or the environment
logger.setLevel(logging.DEBUG)
#logger.setLevel(logging.WARNING)

# create file handler which logs even debug messages
#fh = logging.FileHandler('spam.log')
#fh.setLevel(logging.DEBUG)
# create console handler with same log level
ch = logging.StreamHandler()
# possible levels are DEBUG, INFO, WARNING, ERROR, CRITICAL
ch.setLevel(logging.DEBUG)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
#fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
#logger.addHandler(fh)
logger.addHandler(ch)



'''
Expose to Authors: Gimp enums
Use "from gimpenums import *" form so author does not need prefix gimpenums.RGB
Name "gimpenums" retained for FBC, some non-GimpFu plugins may import
'''
from gimpenums import *

''' Expose to Authors: v3 GimpFu enums  e.g. PF_INT '''
from gimpfu_enums import *

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


'''
local cache of procedures implemented in the 'Authors source code.
Dictionary containing elements of type GimpFuProcedure
'''
__local_registered_procedures__ = {}



"""
The GimpFu API:
   - register()
   - main()
   - fail()
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
    # register under its possibly fixed name, not the given name
    __local_registered_procedures__[gf_procedure.name] = gf_procedure

    # !!! Have not conveyed to Gimp yet


# A primary phrase in GimpFu language
def main():
    """This should be called after registering the plug-in."""
    # v2:   gimp.main(None, None, _query, _run)
    logger.info('GimpFu main called')
    Gimp.main(GimpFu.__gtype__, sys.argv)


# A primary phrase in GimpFu language
def fail(msg):
    """Display an error message and quit"""
    Gimp.message(msg)
    raise Exception(msg)



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


def _try_run_func(proc_name, function, args, display):
    '''
    Run the plugin's run_func with args, catching exceptions.
    Return result of run_func.

    This is always non-headless (interactive.)
    But not require an image open.
    Show dialog on exception.
    '''
    try:
        result = function(*args)
    except:
        # Show dialog here, or pass exception string back to Gimp???
        from gui.exception_dialog import ExceptionDialog

        if display:
            ExceptionDialog.show(proc_name, display)

        exc_str, exc_only_str = ExceptionDialog.create_exception_str()

        logger.critical(f"{exc_str}, {exc_only_str}")
        result = None
        # TODO either pass exc_str back so Gimp shows in dialog,
        # or reraise so Gimp shows a generic "plugin failed" dialog
        # or show our own dialog above
        raise
    return result







def _interact(procedure, list_gvalues_all_args, config):
    '''
    Show GUI when guiable args, then execute run_func.
    Progress will show in Gimp window, not dialog window.

    Returns (was_canceled, (results of run_func or None))
    '''
    logger.info(f"_interact, {procedure}, {list_gvalues_all_args}")

    # get name from instance of Gimp.Procedure
    proc_name = procedure.get_name()

    # TODO assume first arg is likely an image
    # display = Display.get(proc_name, list_gvalues_all_args[0])

    from gui.display import Display
    display = Display.get_window(proc_name)

    # get FuProcedure from local cache by name
    gf_procedure = __local_registered_procedures__[proc_name]

    function = gf_procedure.metadata.FUNCTION

    wrapped_in_actual_args = Marshal.wrap_args(list_gvalues_all_args)

    guiable_formal_params =  gf_procedure.guiable_formal_params

    """
    CRUFT from implementation where dialog executed run_script
    guiable_formal_params =  gf_procedure.guiable_formal_params
    nonguiable_actual_args, guiable_actual_args = gf_procedure.split_guiable_actual_args(wrapped_in_actual_args)

    # effectively a closure, partially bound to function, nonguiable_actual_args
    # passed to show_plugin_dialog to be executed after dialog
    def run_script(guiable_actual_args):
        # guiable_actual_args may have been altered by the GUI from earlier values
        nonlocal function
        nonlocal nonguiable_actual_args

        wrapped_run_args = gf_procedure.join_nonguiable_to_guiable_args(nonguiable_actual_args,  guiable_actual_args)
        logger.info("wrapped_run_args", wrapped_run_args)
        '''
        invoke Authors func on unpacked args
        !!! Authors func never has run_mode, Gimpfu hides need for it.
        '''
        result = function(*wrapped_run_args)
        return result
    """



    if len(guiable_formal_params) == 0:
        # Just execute, don't open ControlDialog, but display ExceptionDialog
        logger.info("no guiable parameters")
        was_canceled = False
        # !!! no gui can change the in_args
        result = _try_run_func(proc_name, function, wrapped_in_actual_args, display)
    else:
        # create GUI from guiable formal args, let user edit actual args

        #TODO duplicate??
        gf_procedure.on_run()

        from gui.control_dialog import PluginControlDialog

        '''
        v2
        # executes run_script if not canceled, returns tuple of run_script result
        was_canceled, result = gimpfu_dialog.show_plugin_dialog(
            procedure,
            guiable_actual_args,
            guiable_formal_params, run_script)
        '''
        nonguiable_actual_args, guiable_actual_args = gf_procedure.split_guiable_actual_args(wrapped_in_actual_args)

        '''
        If you omit this next step, it does not use last_values, instead
        using actual_args, which will be defaults in many cases.
        '''
        # Wrong: config.get_initial_settings(guiable_actual_args)
        # TEMP: this is correct, but not working:  guiable_actual_args = config.get_initial_settings()

        was_canceled, guied_args = PluginControlDialog.show(
            procedure,
            guiable_actual_args,
            guiable_formal_params)
        if not was_canceled :

            config.set_changed_settings(guied_args)

            # update incoming guiable args with guied args
            wrapped_run_args = gf_procedure.join_nonguiable_to_guiable_args(nonguiable_actual_args, guied_args)
            logger.info(f"Wrapped args to run_func, {wrapped_run_args}" )

            # !!! with args modified since passed in
            result = _try_run_func(proc_name, function, wrapped_run_args, display)
        else:
            # Don't save any gui changes to args
            result = None
            pass

    return was_canceled, result





'''
Since 3.0, changed the signature of _run():
- parameters not in one tuple
- type of 'procedure' parameter is GimpImageProcedure, not str.
v2, most parameters were in one tuple.

XXXNow the first several are mandatory and do not need to be declared when registering.
XXXIn other words, formerly their declarations were boilerplate, repeated often for little practical use.

Since 3.0,
when the plugin procedure is of type Gimp.ImageProcedure
the parameter actual_args only contains arguments special to given plugin instance,
and the first two args (image and drawable) are passed separately.

!!! The args are always as declared when procedure created.
It is only when they are passed to the procedure that they are grouped
in different ways (some chunked into a Gimp.ValueArray)

Also formerly the first argument was type str, name of proc.
Now it is of C type GimpImageProcedure or Python type ImageProcedure

!!! Args are Gimp types, not Python types
'''
def _run_imageprocedure(procedure, run_mode, image, drawable, original_args, data):
    ''' Callback from Gimp.

    GimpFu wrapper of the Authors "main" function, aka run_func
    '''

    logger.info(f"_run_imageprocedure , {procedure}, {run_mode}, {image}, {drawable}, {original_args}")
    # logger.info("_run_imageprocedure count original_args", original_args.length())

    '''
    Create GimpValueArray of *most* args.
    !!! We  pass GimpValueArray of Gimp types to lower level methods.
    That might change when the lower level methods are fleshed out to persist values.
    *most* means (image, drawable, *original_args), but not run_mode!
    '''
    list_gvalues_all_args = Marshal.prefix_image_drawable_to_run_args(original_args, image, drawable)

    _run(procedure, run_mode, image, list_gvalues_all_args, original_args, data)



def _run_context_procedure(procedure, original_args, data):
    ''' Callback from Gimp for a Gimp.Procedure class of procedure.

    For a procedure invoked from a context menu, operating on an instance of "Gimp data" e.g. Vectors, Brush, ...

    GimpFu wrapper of the Authors "main" function, aka run_func

    The signature is as defined by Gimp C code.
    '''
    logger.info(f"_run_context_procedure , {procedure}, {original_args}, {data}")

    '''
    Rearrange args to fit _run()
    '''
    list_gvalues_all_args = Marshal.convert_gimpvaluearray_to_list_of_gvalue(original_args)
    # assert is (runmode, image, <Gimp data object>)

    # GimpFu always hides run mode, delete first element
    list_gvalues_all_args.pop(0)

    # this type of procedure always NONINTERACTIVE
    run_mode = Gimp.RunMode.NONINTERACTIVE

    # TODO this type of procedure always passed image in the first element of GimpValueArray
    image = list_gvalues_all_args[0]

    _run(procedure, run_mode, image, list_gvalues_all_args, original_args, data)



def _run(procedure, run_mode, image, list_gvalues_all_args, original_args, data):
    '''
    Understands run_mode.
    Different ways to invoke procedure batch, or interactive.

    Hides run_mode from Authors.
    I.E. their run_func signature does not have run_mode.

    require procedure is-a Gimp.Procedure.
    require original_arges is-a Gimp.ValueArray.
    require list_gvalues_all_args is a list of GValues
    '''
    # args have already been marshalled into native types
    assert isinstance(list_gvalues_all_args, list)

    # To get the Python name of a Gimp.Procedure method,
    # see gimp/libgimp/gimpprocedure.h, and then remove the prefix gimp_procedure_
    name = procedure.get_name()

    logger.info(f"_run: {name}, {run_mode}, {list_gvalues_all_args}")
    '''
    list_gvalues_all_args are one-to-one with formal params.
    list_gvalues_all_args may include some args that are not guiable (i.e. image, drawable)
    '''

    # get local GimpFuProcedure
    gf_procedure = __local_registered_procedures__[name]

    isBatch = (run_mode == Gimp.RunMode.NONINTERACTIVE)
    '''
    Else so-called interactive mode, with GUI dialog of params.
    Note that the v2 mode RUN_WITH_LAST_VALS is obsolete
    since Gimp 3 persists settings, i.e. actual arg values can be from last invocation.
    If not from last invocation, they are the formal parameter defaults.
    '''

    func = gf_procedure.get_authors_function()

    config = FuProcedureConfig(procedure, len(list_gvalues_all_args)-2 )
    config.begin_run(image, run_mode, original_args)

    if isBatch:
       try:
           # invoke func with unpacked args.  Since Python3, apply() gone.
           # TODO is this the correct set of args? E.G. Gimp is handling RUN_WITH_LAST_VALS, etc. ???
           result = func(*list_gvalues_all_args)
           # TODO add result values
           final_result = procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())
       except:
           final_result = procedure.new_return_values(Gimp.PDBStatusType.EXECUTION_ERROR, GLib.Error())
    else:
       # pass list of args

       '''
       Not enclosed in try:except: since then you don't get a good traceback.
       Any exceptions in showing a dialog are hard programming errors.
       Any exception in executing the run_func should be shown to user,
       either by calling our own dialog or by calling a Gimp.ErrorDialog (not exist)
       or by passing the exception string back to Gimp.
       '''
       was_canceled, result = _interact(procedure, list_gvalues_all_args, config)
       if was_canceled:
           final_result = procedure.new_return_values(Gimp.PDBStatusType.CANCEL, GLib.Error())
           config.end_run(Gimp.PDBStatusType.CANCEL)
       else:
           # TODO add result values to Gimp  procedure.add_return_value ....
           # trigger Gimp create all return values from this status and prior add_return_value
           final_result = procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())
           config.end_run(Gimp.PDBStatusType.SUCCESS)
       """
       OLD above was enclosed in try
       try:
       except Exception as err:
           '''
           Probably GimpFu module programming error (e.g. bad calls to GTK)
           According to GLib docs, should be a warning, since this is not recoverable.
           But it might be author programming code (e.g. invalid PARAMS)
           '''
           do_proceed_error(f"Exception opening plugin dialog: {err}")
           final_result = procedure.new_return_values(Gimp.PDBStatusType.EXECUTION_ERROR, GLib.Error())
       """

    '''
    Make visible any alterations to user created images.
    GimpFu promises to hide the need for this.
    '''
    Gimp.displays_flush()   # !!! Gimp, not gimp

    did_suggest_or_deprecate = Suggest.summarize()
    did_suggest_or_deprecate = did_suggest_or_deprecate or Deprecation.summarize()

    if did_suggest_or_deprecate:
        # TODO make this go to the status bar, not a dialog
        # Gimp.message("See console for suggestions and deprecations.")
        pass

    if summarize_proceed_errors():
        fail("GimpFu detected errors.  See console for a summary.")

    # ensure final_result is type GimpValueArray
    return final_result


'''
v2
def _run(proc_name, params):
    run_mode = params[0]
    func = _registered_plugins_[proc_name][10]

    if run_mode == RUN_NONINTERACTIVE:
        return apply(func, params[1:])

    script_params = _registered_plugins_[proc_name][8]

    min_args = 0
    if len(params) > 1:
        for i in range(1, len(params)):
            param_type = _obj_mapping[script_params[i - 1][0]]
            if not isinstance(params[i], param_type):
                break

        min_args = i

    if len(script_params) > min_args:
        start_params = params[:min_args + 1]

        if run_mode == RUN_WITH_LAST_VALS:
            default_params = _get_defaults(proc_name)
            params = start_params + default_params[min_args:]
        else:
            params = start_params
    else:
       run_mode = RUN_NONINTERACTIVE

    if run_mode == RUN_INTERACTIVE:
        try:
            res = _interact(proc_name, params[1:])
        except CancelError:
            return
    else:
        res = apply(func, params[1:])

    gimp.displays_flush()

    return res
'''








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
        keys = __local_registered_procedures__.keys()

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
        gf_procedure = __local_registered_procedures__[name]

        # pass all the flavors of wrapped_run_funcs
        procedure = FuProcedureCreator.create(self, name, gf_procedure, _run_imageprocedure, _run_context_procedure)

        # ensure result is-a Gimp.Procedure
        return procedure
