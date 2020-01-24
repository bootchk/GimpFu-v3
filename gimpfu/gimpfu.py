#   Gimp-Python - allows the writing of GIMP plug-ins in Python.
#   Copyright (C) 1997  James Henstridge <james@daa.com.au>
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

"""Simple interface for writing GIMP plug-ins in Python.

Instead of worrying about all the user interaction, saving last used
values and everything, the gimpfu module can take care of it for you.
It provides a simple register() function that will register your
plug-in if needed, and cause your plug-in function to be called when
needed.

Gimpfu will also handle showing a user interface for editing plug-in
parameters if the plug-in is called interactively, and will also save
the last used parameters, so the RUN_WITH_LAST_VALUES run_type will
work correctly.  It will also make sure that the displays are flushed
on completion if the plug-in was run interactively.

When registering the plug-in, you do not need to worry about
specifying the run_type parameter.

A typical gimpfu plug-in would look like this:
  from gimpfu import *

  def plugin_func(image, drawable, args):
              # do what plugins do best
  register(
              "plugin_func",
              "blurb",
              "help message",
              "author",
              "copyright",
              "year",
              "My plug-in",
              "*",
              [
                  (PF_IMAGE, "image", "Input image", None),
                  (PF_DRAWABLE, "drawable", "Input drawable", None),
                  (PF_STRING, "arg", "The argument", "default-value")
              ],
              [],
              plugin_func, menu="<Image>/Somewhere")
  main()

The call to "from gimpfu import *" will import all the gimp constants
into the plug-in namespace, and also import the symbols gimp, pdb,
register and main.  This should be just about all any plug-in needs.

You can use any of the PF_* constants below as parameter types, and an
appropriate user interface element will be displayed when the plug-in
is run in interactive mode.  Note that the the PF_SPINNER and
PF_SLIDER types expect a fifth element in their description tuple -- a
3-tuple of the form (lower,upper,step), which defines the limits for
the slider or spinner.

If want to localize your plug-in, add an optional domain parameter to
the register call. It can be the name of the translation domain or a
tuple that consists of the translation domain and the directory where
the translations are installed.
"""

# Since GIMP3 using GI, Python3: here we use "FBC" to denote stuff For Backward Compatibility to old plugins

# Using GI, convention is first letter capital e.g. "Gimp."  FBC we often alias to uncapitalized, e.g. "gimp"
# Aliases in this top level are accessible in plugins that import gimpfu.
# Plugins that import gimpfu additionally MAY use GI, but gimpfu attempts to hide GI.


# v2 exposed to authors? v3, authors must import it themselves
# v2 import math

import sys


import gi
gi.require_version("Gimp", "3.0")
from gi.repository import Gimp


# v3
from gi.repository import Gio
from gi.repository import GLib

# for g_param_spec and properties
# from gi.repository import GObject


# import private implementation
from gimpfu_marshal import Marshal
from gimpfu_procedure import GimpfuProcedure
from gimpfu_exception import *




# Gimp enums exposed to GimpFu authors
# Use "from gimpenums import *" form so author does not need prefix gimpenums.RGB
# TODO retain old module name FBC?
# v2 from gimpenums import *
from gimpfu_enums import *

# GimpFu enums exposed to GimpFu authors e.g. PF_INT
# TODO this also exposes private types
from gimpfu_types import *



# TODO import gimpcolor



'''
alias symbols "gimp" and "pdb" to expose to GimpFu authors
It is not as simple as:
    pdb=Gimp.get_pdb()
    OR from gi.repository import Gimp as gimp
These are adapters. TODO kind of adapters
'''
from gimpfu_pdb import GimpfuPDB
pdb = GimpfuPDB()

from gimpfu_gimp import GimpfuGimp
gimp = GimpfuGimp()

"""
CRUFT
def _define_compatibility_aliases():
    '''
    alias  PDB and Gimp.
    FBC.
    Aliases are uncapitalized.
    Cannot create aliases until after calling Gimp.main(),
    which establishes self as GimpPlugin.
    '''
    print('Aliasing')
    #global gimp
    global pdb

    #gimp = Gimp
    pdb = Gimp.get_pdb()
    assert pdb is not None
"""



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
    print("Warning: GimpFu plugins should not call gettext.install, it is already done.")

gettext.install = override_gettext_install
'''

# v2 cruft
#class error(RuntimeError): pass
#class CancelError(RuntimeError): pass


'''
local cache of procedures implemented in the GimpFu author's source code.
Dictionary containing elements of  type GimpFuProcedure
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

'''
Register locally, not with Gimp.

Each GimpFu plugin author's source may contain many calls to register.
'''
def register(proc_name, blurb, help, author, copyright,
            date, label, imagetypes,
            params, results, function,
            menu=None, domain=None, on_query=None, on_run=None):
    """ GimpFu method that registers a plug-in. May be called many times from same source file."""

    print("register ", proc_name)

    gf_procedure = GimpfuProcedure(proc_name, blurb, help, author, copyright,
                            date, label, imagetypes,
                            params, results, function,
                            menu, domain, on_query, on_run)
    __local_registered_procedures__[proc_name] = gf_procedure

    # !!! Have not conveyed to Gimp yet


def main():
    """This should be called after registering the plug-in."""
    # v2:   gimp.main(None, None, _query, _run)
    print('GimpFu main called\n')
    Gimp.main(GimpFu.__gtype__, sys.argv)


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

'''
TODO replace this with gimp_procedure_config

def _get_defaults(proc_name):
    import gimpshelf

    (blurb, help, author, copyright, date,
     label, imagetypes, plugin_type,
     params, results, function, menu, domain,
     on_query, on_run) = _registered_plugins_[proc_name]

    key = "python-fu-save--" + proc_name

    if gimpshelf.shelf.has_key(key):
        return gimpshelf.shelf[key]
    else:
        # return the default values
        return [x[3] for x in params]

def _set_defaults(proc_name, defaults):
    import gimpshelf

    key = "python-fu-save--" + proc_name
    gimpshelf.shelf[key] = defaults
'''




def _interact(procedure, actual_args):
    print("_interact called", procedure, actual_args)

    # get name from instance of Gimp.Procedure
    proc_name = procedure.get_name()

    # get GimpfuProcedure from container by name
    gf_procedure = __local_registered_procedures__[proc_name]

    formal_params = gf_procedure.metadata.PARAMS
    function = gf_procedure.metadata.FUNCTION
    on_run = gf_procedure.metadata.ON_RUN

    wrapped_actual_args = Marshal.wrap_args(actual_args)

    guiable_formal_params =  gf_procedure.guiable_formal_params
    nonguiable_actual_args, guiable_actual_args = gf_procedure.split_guiable_actual_args(wrapped_actual_args)


    # effectively a closure, partially bound to function, nonguiable_actual_args
    # passed to show_plugin_dialog to be executed after dialog
    def run_script(guiable_actual_args):
        # guiable_actual_args may have been altered by the GUI from earlier values
        nonlocal function
        nonlocal nonguiable_actual_args

        wrapped_run_args = gf_procedure.join_args_to_run_args(nonguiable_actual_args,  guiable_actual_args)
        '''
        invoke author's func on unpacked args
        !!! author's func never has run_mode, Gimpfu hides need for it.
        '''
        return function(*wrapped_run_args)

        """
        CRUFT
        nonlocal wrapped_stock_args
        # TEMP attempt to get pdb into scope
        # nonlocal function

        print("run_script called with pdb", pdb)

        # TODO is this correct?
        # Is the procedure an image consumer?
        # If first param is image, prepend
        # TODO add class GimpfuPlugin that hides all this magic
        # if formal_params[0].PF_TYPE != PF_IMAGE:
        if formal_params[0][0] == PF_IMAGE:
            params = wrapped_stock_args + tuple(run_params)
        else:
             params = tuple(run_params)

        #TODO _set_defaults(proc_name, params)

        # invoke on unpacked args
        return function(*params)
        """


    if len(guiable_formal_params) == 0:
        #Just execute, don't open dialog.
        print("no guiable parameters")
        # Since no GUI, was_canceled always false
        result = (false, run_script(wrapped_actual_args))
    else:
        # create GUI from guiable formal args, let user edit actual args

        #TODO duplicate??
        # on_run only called when GUI??
        if on_run:
            print("Call on_run")
            on_run()

        import gimpfu_dialog

        print("Call show_plugin_dialog")
        # executes run_script if not canceled, returns tuple of run_script result
        result = gimpfu_dialog.show_plugin_dialog(procedure, guiable_actual_args, guiable_formal_params, run_script)
        # TODO save the changed settings i.e. new defaults

    return result


def _pack(actual_args, arg1=None, arg2=None):
    '''
    return a list [arg1, arg2, *actual_args]
    Where:
        actual_args is-a Gimp.ValueArray
        arg1, arg2 are optional GObjects
    '''

    args = []
    if arg1:
        args.append(arg1)
    if arg2:
        args.append(arg2)

    len = actual_args.length()   # !!! not len(actual_args)
    for i in range(len):
        gvalue = actual_args.index(i)
        # Python can handle the gvalue, we don't need to convert to Python types
        # assuming we have imported gi
        args.append(gvalue)
    # ensure result is-a list, but might be empty
    return args



'''
Since 3.0, signature of _run() has changed.
Formerly, most parameters were in one tuple.

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
def _run_imageprocedure(procedure, run_mode, image, drawable, actual_args, data):
    ''' GimpFu wrapper of the author's "main" function, aka run_func '''

    print("_run_imageprocedure ", procedure, run_mode, image, drawable, actual_args)

    '''
    create GimpValueArray of *most* args
    !!! We  pass GimpValueArray types to lower level methods.
    That might change when the lower level methods are fleshed out to persist values.
    *most* means (image, drawable, *actual_args), but not run_mode!
    '''
    all_args = _pack(actual_args, image, drawable)
    """
    cruft
    # from gimpfu_array import GimpfuValueArray
    # GimpfuValueArray
    gf.prepend(image)
    stock_args = (image, drawable)
    all_args = stock_args +  tuple(*actual_args)
    """

    _run(procedure, run_mode, all_args, data)


def _run_imagelessprocedure(procedure, run_mode, actual_args, data):
    ''' GimpFu wrapper of the author's "main" function, aka run_func '''
    print("_run_loadprocedure ", procedure, run_mode, actual_args)
    all_args = _pack(actual_args)
    _run(procedure, run_mode, all_args, data)


def _run(procedure, run_mode, actual_args, data):
    '''
    Understands run_mode.
    Different ways to invoke procedure batch, or interactive.

    Hides run_mode from GimpFu authors.
    I.E. their run_func signature does not have run_mode.

    require procedure is-a Gimp.Procedure.  All args are GObjects.
    require actual_args is-a Gimp.ValueArray.  Thus has non-Python methods, only GI methods.
    e.g. actual_args.length(), NOT len(actual_args)
    '''
    assert isinstance(actual_args, list)

    # To get the Python name of a Gimp.Procedure method,
    # see gimp/libgimp/gimpprocedure.h, and then remove the prefix gimp_procedure_
    name = procedure.get_name()

    print("_run ", name, run_mode, actual_args)
    '''
    actual_args are one-to-one with formal params.
    actual_args may include some args that are not guiable (i.e. image, drawable)
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

    # CRUFT? _define_compatibility_aliases()
    assert pdb is not None
    print("pdb outside", pdb)

    if isBatch:
       try:
           # invoke func with unpacked args.  Since Python3, apply() gone.
           # TODO is this the correct set of args?
           result = func(*actual_args)
           # TODO add result values
           final_result = procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())
       except:
           final_result = procedure.new_return_values(Gimp.PDBStatusType.EXECUTION_ERROR, GLib.Error())
    else:
       # pass list of args
       try:
           was_canceled, result = _interact(procedure, actual_args)
           if was_canceled:
               final_result = procedure.new_return_values(Gimp.PDBStatusType.CANCEL, GLib.Error())
           else:
               # TODO add result values to Gimp  procedure.add_result ....
               final_result = procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())
       except Exception as err:
           '''
           Probably GimpFu module programming error (e.g. bad calls to GTK)
           According to GLib docs, should be a warning, since this is not recoverable.
           But it might be GimpFu plugin author programming code (e.g. invalid PARAMS)
           '''
           print("Exception opening plugin dialog: {0}".format(err))
           final_result = procedure.new_return_values(Gimp.PDBStatusType.EXECUTION_ERROR, GLib.Error())

    '''
    Make any alterations to user created images visible.
    GimpFu promises to hide the need for this.
    '''
    Gimp.displays_flush()   # !!! Gimp, not gimp

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
See header comments for type Gimp.Plugin.

A plugin must define (but not instantiate) a subclass of Gimp.Plugin.
GimpFu is a subclass of Gimp.Plugin.
At runtime, only methods of such a subclass have access to Gimp and its PDB.

GimpFu is wrapper.
Has no properties itself.
More generally (unwrapped) properties  represent params (sic arguments) to ultimate plugin.

_run() above wraps author's "function" i.e. ultimate plugin method,
which is referred to as "run_func" here and in Gimp documents.
'''
class GimpFu (Gimp.PlugIn):

    """
    cruft
    @classmethod
    def get_pdb(cls):
        return Gimp.get_pdb();
    """


    """
    ## Parameters ##
    # Long form: create attribute which is dictionary of GProperty
    # class attribute ??
    # not used by GimpFu
    __gproperties__ = {
        # nick, blurb, default
        "myProp": (str,
                 _("myPropNick"),
                 _("myPropBlurb"),
                 _("myPropDefaultValue"),
                 GObject.ParamFlags.READWRITE)
    }
    """



    ## GimpPlugIn virtual methods ##
    '''
    Called at install time,
    OR when ~/.config/GIMP/2.99/pluginrc (a cache of installed plugins) is being recreated.
    '''
    def do_query_procedures(self):
        print("do_query_procedures")

        # TODO Why set the locale again?
        # Maybe this is a requirement documented for class Gimp.Plugin????
        self.set_translation_domain("Gimp30-python",
                                    Gio.file_new_for_path(Gimp.locale_directory()))

        # return list of all procedures implemented in the GimpFu plugin author's source code
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
    Thus the GimpFu plugin is GimpFu register'ed in the local cache.
    It also was registered with Gimp (at installation time.)
    '''
    def do_create_procedure(self, name):

        print ('do_create_procedure: ', name)

        # We need the kind of plugin, and to ensure the passed name is know to us
        gf_procedure = __local_registered_procedures__[name]

        # TODO different plug_type LoadProcedure for loaders???
        '''
        Create subclass of Gimp.Procedure dispatching
        on the locally determined kind i.e. by the signature of the formal args.
        And use a different wrapper _run for each subclass.
        '''

        # TEMP hack, always a GimpImageProcedure
        procedure = Gimp.ImageProcedure.new(self,
                                name,
                                Gimp.PDBProcType.PLUGIN,
                                _run_imageprocedure, 	# wrapped plugin method
                                None)
        """
        if gf_procedure.is_a_imageprocedure_subclass :
            procedure = Gimp.ImageProcedure.new(self,
                                            name,
                                            Gimp.PDBProcType.PLUGIN,
                                            _run_imageprocedure, 	# wrapped plugin method
                                            None)
        elif gf_procedure.is_a_imagelessprocedure_subclass :
            print("Create imageless procedure")
            procedure = Gimp.Procedure.new(self,
                                            name,
                                            Gimp.PDBProcType.PLUGIN,
                                            _run_imagelessprocedure, 	# wrapped plugin method
                                            None)
        else:
            # TODO Better message, since this error depends on authored code
            # TODO preflight this at registration time.
            raise Exception("Unknown subclass of Gimp.Procedure")
        """

        gf_procedure.convey_metadata_to_gimp(procedure)
        gf_procedure.convey_procedure_arg_declarations_to_gimp(procedure)

        # ensure result is-a Gimp.Procedure
        return procedure

"""
elif gf_procedure.is_a_loadprocedure_subclass :
    procedure = Gimp.LoadProcedure.new(self,
                                    name,
                                    Gimp.PDBProcType.PLUGIN,
                                    _run_loadprocedure, 	# wrapped plugin method
                                    None)
"""
