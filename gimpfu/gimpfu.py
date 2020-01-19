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
# for g_param_spec
from gi.repository import GObject


# import private implementation
from gimpfu_marshal import Marshal
from gimpfu_procedure import GimpfuProcedure




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



gf_procedure = None


def register(proc_name, blurb, help, author, copyright,
            date, label, imagetypes,
            params, results, function,
            menu=None, domain=None, on_query=None, on_run=None):
    """ GimpFu method that registers a plug-in. """

    print("register ", proc_name)
    # TODO put in iterable container
    global gf_procedure
    gf_procedure = GimpfuProcedure(proc_name, blurb, help, author, copyright,
                            date, label, imagetypes,
                            params, results, function,
                            menu, domain, on_query, on_run)



# TODO still needed in v3?  Not a virtual method of GimpPlugin anymore?
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

def _wrap_stock_args(stock_args):
    '''
    Return tuple of wrapped incoming arguments.
    I.E. create Gimpfu wrappers for Gimp GObject's
    '''
    # TODO Marshal may be wrapping a Gimp.Drawable as GimpfuLayer  ???
    return (Marshal.wrap(stock_args[0]),
            Marshal.wrap(stock_args[1]))



def _interact(procedure, stock_args, actualArgs):
    print("interact called")

    proc_name = procedure.get_name()
    # fu_procedure = GimpfuProcedure.get_metadata(proc_name)
    formal_params = gf_procedure.metadata.PARAMS
    function = gf_procedure.metadata.FUNCTION
    on_run = gf_procedure.metadata.ON_RUN

    wrapped_stock_args = _wrap_stock_args(stock_args)

    # effectively a closure, partially bound to stock_args
    # passed to show_plugin_dialog to be executed after dialog
    def run_script(run_params):
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

    # slice off prefix of formal param descriptions (i.e. image and drawable)
    # leaving only descriptions of GUI-time params
    formal_guiable_params = formal_params[len(stock_args):]

    print("guiable formal params:", formal_guiable_params)
    if len(formal_guiable_params) == 0:
         print("no guiable parameters")
         # Since no GUI, was_canceled always false
         return false, run_script([])
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
        return gimpfu_dialog.show_plugin_dialog(procedure, actualArgs, formal_params, run_script)


def unpackActualArgs(actualArgs):
   # actualArgs is Gimp type ValueArray
   pass



'''
Since 3.0, signature of _run() has changed.
Formerly, most parameters were in one tuple.
Now the first several are mandatory and do not need to be declared when registering.
In other words, formerly their declarations were boilerplate, repeated often for little practical use.
Since 3.0 the parameter actualArgs only contains arguments special to given plugin instance.

Also formerly the first argument was type str, name of proc.
Now it is of C type GimpImageProcedure or Python type ImageProcedure

!!! Args are Gimp types, not Python types
'''
def _run(procedure, run_mode, image, drawable, actualArgs, data):

    # assert type of actualArgs is Gimp.ValueArray.  Thus has non-Python methods, only GI methods.
    print(actualArgs)
    #name = actualArgs.index(0)
    print (actualArgs.length())

    # To get the Python name of a Procedure method,
    # see gimp/libgimp/gimpprocedure.h, and then remove the prefix gimp_procedure_

    name = procedure.get_name()

    isBatch = (run_mode == Gimp.RunMode.NONINTERACTIVE)
    ## TODO can't find enum isRunWithLastValues = (run_mode == Gimp.RunMode.RUN_WITH_LAST_VALS)
    # else so-called interactive mode, with GUI dialog of params

    print("Name is ", name)	# procedure.name)
    func = gf_procedure.get_authors_function()


    # catenate standard args and special args into list
    # !!! Low level Gimp plugin procedures take first arg "run_mode", GimpFu hides it
    # TODO finalArgs = (image, drawable) + unpackActualArgs(actualArgs)
    # TEMP just use the first actualArgs
    #finalArgs = (image, drawable, actualArgs.index(0))
    # TODO this is in a mess, understand the original better.
    '''
    I think actualArgs could be LAST_VALS,
    Need to pass them to batch.
    Need to pass them to interact, which should init widgets to those values.
    Can actualArgs be a prefix of formal parameters?
    '''
    stock_args = (image, drawable)

    # CRUFT? _define_compatibility_aliases()
    assert pdb is not None
    print("pdb outside", pdb)

    if isBatch:
       try:
           # invoke func with unpacked args.  Since Python3, apply() gone.
           # TODO is this the correct set of args?
           result = func(*stock_args)
           # TODO add result values
           final_result = procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())
       except:
           final_result = procedure.new_return_values(Gimp.PDBStatusType.EXECUTION_ERROR, GLib.Error())
    else:
       # pass list of args
       try:
           was_canceled, result = _interact(procedure, stock_args, actualArgs)
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


    # assert final_result is type GimpValueArray
    return final_result

'''
TODO in progress
    if isBatch:
        finalArgs = (run_mode, image, drawable, actualArgs)
        return apply(func, finalArgs)

    formalParams = _registered_plugins_[procedure].PARAMS

    # Count actual arguments whose type is correct
    min_args = 0
    if len(actualArgs) > 1:
        for i in range(1, len(actualArgs)):
            param_type = _obj_mapping[formalParams[i - 1][0]]
            if not isinstance(actualArgs[i], param_type):
                break

        min_args = i

    if len(formalParams) > min_args:
        start_params = actualArgs[:min_args + 1]

        if run_mode == RUN_WITH_LAST_VALS:
            default_actualArgs = _get_defaults(proc_name)
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

    Gimp.displays_flush()

    return res
'''

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

def main():
    """This should be called after registering the plug-in."""
    # v2
    # gimp.main(None, None, _query, _run)
    # v3
    print('main called\n')
    Gimp.main(GimpFu.__gtype__, sys.argv)

def fail(msg):
    """Display an error message and quit"""
    Gimp.message(msg)
    raise Exception(msg)












# lkk rest is my hack trying to understand
'''
GimpFu is subclass of Gimp.Plugin.
At runtime, only methods of such a subclass have access to Gimp and its PDB.

GimpFu is wrapper.
Has no properties itself.
More generally (unwrapped) properties  represent params (sic arguments) to ultimate plugin.

_run() above wraps author's "function" i.e. ultimate plugin method
'''
class GimpFu (Gimp.PlugIn):

    @classmethod
    def get_pdb(cls):
        return Gimp.get_pdb();



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




    ## GimpPlugIn virtual methods ##
    def do_query_procedures(self):
        print("do_query_procedures")
        self.set_translation_domain("Gimp30-python",
                                    Gio.file_new_for_path(Gimp.locale_directory()))

        # TODO return all proc_names
        # return [ GimpfuProcedure.get_first_proc_name(), ]
        return [ gf_procedure.name, ]


    '''
    Gimp calls this back when the GimpFu plugin calls main(), which calls Gimp.main().
    Thus it should execute AFTER the GimpFu plugin calls register().
    Until now, the GimpFu plugin is only registered in the local cache, and not registered with Gimp.

    The filename arg is name of the source file, not necessarily the same as given in register(name,...)
    '''
    def do_create_procedure(self, filename):

        # filename not otherwise used
        # Gimp is passing filename as if there is only one procedure to be implemented in a file.
        # and the name is "procedure" without a 's'
        print ('create procedure(s) from file: ', filename, " .py")

        '''
        Register with Gimp all the locally registered plugins.
        '''
        # TODO GimpFuProcedure iterator
        # for key in _registered_plugins_:

        # TODO different plug_type LoadProcedure for loaders???

        procedure = Gimp.ImageProcedure.new(self,
                                        gf_procedure.name,
                                        Gimp.PDBProcType.PLUGIN,
                                        _run, 	# wrapped plugin method
                                        None)
        gf_procedure.convey_metadata_to_gimp(procedure)
        gf_procedure.convey_procedure_arg_declarations_to_gimp(procedure)

        # TODO, we created and registered many, we return only the last one??
        # Is creating many legal to Gimp 3?

        return procedure
