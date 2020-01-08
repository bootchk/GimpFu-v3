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


import string as _string
import math
import sys


import gi

# alias Gimp as gimp FBC
# TODO, later

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp
from gi.repository import Gimp as gimp


# v3
from gi.repository import Gio
from gi.repository import GLib
# for g_param_spec
from gi.repository import GObject


from gimpfu_types import *


# TODO import gimpcolor

# TODO from gimpenums import *


# alias Gimp.PGB as pdb

# This not working, fails assert
#pdb = GimpFu.get_pdb()
#if pdb is None:
#    print(Gimp.pdb_error())
#assert pdb is not None
from gimpfu_pdb import GimpfuPDB

pdb = GimpfuPDB()

#gimp = None

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




# Python 3 ugettext() is deprecated, use gettext() which also returns unicode
import gettext
t = gettext.translation("gimp30-python", Gimp.locale_directory, fallback=True)
_ = t.gettext

#class error(RuntimeError): pass
#class CancelError(RuntimeError): pass


'''
GimpFu cache of possibly many plugins registered by a single .py file.
cache: local copy of registration with Gimp.
After registering with Gimp, we could use Gimp's knowledge, but local cache has more information.
Namely, PARAMS have extra information: the kind of control widget for each param.
Dictionary of GimpFuProcedure
'''
_registered_plugins_ = {}


def deriveMissingMenu(menu, label, params):
    '''
    if menu is not given, derive it from label
    Ability to omit menu is deprecated, so this is FBC.
    '''
    need_compat_params = False
    if menu is None and label:
        fields = label.split("/")
        if fields:
            label = fields.pop()
            menu = "/".join(fields)
            need_compat_params = True

            import warnings
            #TODO proc_name undefined
            message = ("%s: passing the full menu path for the menu label is "
                       "deprecated, use the 'menu' parameter instead"
                       % (proc_name))
            warnings.warn(message, DeprecationWarning, 3)

        if need_compat_params:   # v2 and plugin_type == PLUGIN:
            file_params = [(PDB_STRING, "filename", "The name of the file", ""),
                           (PDB_STRING, "raw-filename", "The name of the file", "")]

            if menu is None:
                pass
            elif menu.startswith("<Load>"):
                params[0:0] = file_params
            elif menu.startswith("<Image>") or menu.startswith("<Save>"):
                params.insert(0, (PDB_IMAGE, "image", "Input image", None))
                params.insert(1, (PDB_DRAWABLE, "drawable", "Input drawable", None))
                if menu.startswith("<Save>"):
                    params[2:2] = file_params


def makeProcNamePrefixCanonical(proc_name):
    '''
    if given name not canonical, make it so.

    Canonical means having a prefix from a small set,
    so that from the canonical name, PDB browsers know how implemented.

    v2 allowed underbars, i.e. python_, extension_, plug_in_, file_ prefixes.
    TODO FBC, transliterate _ to -

    Note that prefix python-fu intends to suggest (to browsers of PDB):
    - fu: simplified API i.e. uses GimpFu module
    - python: language is python
    script-fu is similar for Scheme language: simplified API
    You can write a Python language plugin without the simplified API
    and then it is author's duty to choose a canonically prefixed name.
    '''
    if (not proc_name.startswith("python-") and
        not proc_name.startswith("extension-") and
        not proc_name.startswith("plug-in-") and
        not proc_name.startswith("file-") ):
           proc_name = "python-fu-" + proc_name


def register(proc_name, blurb, help, author, copyright, date, label,
             imagetypes, params, results, function,
             menu=None, domain=None, on_query=None, on_run=None):
    """GimpFu method that registers a plug-in."""

    print ('register', proc_name)

    # First sanity check the data

    '''
    Since: 3.0 Gimp enforces: Identifiers for procedure names and parameter names:
    Characters from set: '-', 'a-z', 'A-Z', '0-9'.
    v2 allowed "_"
    Gimp will check also.  So redundant, but catch it early.
    '''
    def letterCheck(str):
        allowed = _string.ascii_letters + _string.digits + "-"
        for ch in str:
            if not ch in allowed:
                return 0
        else:
            return 1

    # TODO transliterate "_" to "-" FBC

    if not letterCheck(proc_name):
        raise Exception("procedure name contains illegal characters")

    for ent in params:
        if len(ent) < 4:
            raise Exception( ("parameter definition must contain at least 4 "
                          "elements (%s given: %s)" % (len(ent), ent)) )

        if not isinstance(ent[0], int):
            raise Exception("parameters must be of integral type")

        if not letterCheck(ent[1]):
            raise Exception("parameter name contains illegal characters")

    for ent in results:
        if len(ent) < 3:
            raise Exception( ("result definition must contain at least 3 elements "
                          "(%s given: %s)" % (len(ent), ent)))

        if not isinstance(ent[0], int):
            raise Exception("result must be of integral type")

        if not letterCheck(ent[1]):
            raise Exception("result name contains illegal characters")

    # v2 plugin_type = PLUGIN

    deriveMissingMenu(menu, label, params)

    makeProcNamePrefixCanonical(proc_name)

    # v3 plugin_type in local cache always a dummy value
    # Gimp enums are not defined yet
    plugin_type = 1

    _registered_plugins_[proc_name] = GimpFuProcedure(blurb, help, author, copyright,
                                       date, label, imagetypes,
                                       plugin_type, params, results,
                                       function, menu, domain,
                                       on_query, on_run)



# TODO still needed in v3?  Not a virtual method of GimpPlugin anymore?
def _query():
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


def _interact(procedure, stock_args, actualArgs):
    print("interact called")

    proc_name = procedure.get_name()
    fu_procedure = _registered_plugins_[proc_name]
    formal_params = fu_procedure.PARAMS
    function = fu_procedure.FUNCTION
    on_run = fu_procedure.ON_RUN

    # effectively a closure, partially bound to stock_args
    def run_script(run_params):
        nonlocal stock_args
        # TEMP attempt to get pdb into scope
        # nonlocal function

        print("run_script")
        print("pdb before run_script", pdb)
        params = stock_args + tuple(run_params)
        #TODO _set_defaults(proc_name, params)
        # invoke on unpacked args
        return function(*params)

    # slice off prefix of formal param descriptions (i.e. image and drawable)
    # leaving only descriptions of GUI-time params
    formal_guiable_params = formal_params[len(stock_args):]

    print(formal_guiable_params)
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

        import gimpfu_widgets

        print("Call show_plugin_dialog")
        # executes run_script if not canceled, returns tuple of run_script result
        return gimpfu_widgets.show_plugin_dialog(procedure, actualArgs, formal_params, run_script)


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

    # see gimp/libgimp/gimpprocedure.h, and then remove the prefix gimp_procedure_

    name = procedure.get_name()

    isBatch = (run_mode == Gimp.RunMode.NONINTERACTIVE)
    ## TODO can't find enum isRunWithLastValues = (run_mode == Gimp.RunMode.RUN_WITH_LAST_VALS)
    # else so-called interactive mode, with GUI dialog of params

    print("Name is ", name)	# procedure.name)
    func = _registered_plugins_[name].FUNCTION

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

    _define_compatibility_aliases()
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
       except:
           final_result = procedure.new_return_values(Gimp.PDBStatusType.EXECUTION_ERROR, GLib.Error())

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

def N_(message):
    return message




'''
A class whose *instances* will have a prop attribute

Class has one property of each type.
Properties used only for their type.
In calls to set_args_from_property
'''
class PropHolder (GObject.GObject):
    # copied and hacked to remove '-' from Python GTK+ 3 website tutorial
    __gproperties__ = {
        "intprop": (int, # type
                     "integer prop", # nick
                     "A property that contains an integer", # blurb
                     1, # min
                     5, # max
                     2, # default
                     GObject.ParamFlags.READWRITE # flags
                    ),
    }

    def __init__(self):
        GObject.GObject.__init__(self)
        self.int_prop = 2

    def do_get_property(self, prop):
        if prop.name == 'intprop':
            return self.int_prop
        else:
            raise AttributeError('unknown property %s' % prop.name)

    def do_set_property(self, prop, value):
        if prop.name == 'intprop':
            self.int_prop = value
        else:
            raise AttributeError('unknown property %s' % prop.name)


prop_holder = PropHolder()
print(prop_holder.props)
print(prop_holder.props.intprop)



# lkk rest is my hack trying to understand
'''
GimpFu is subclass of Gimp.Plugin.
At runtime, only methods of such a subclass (or procedures called from methods)
have access to Gimp and its PDB.

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
    # not used
    __gproperties__ = {
        # nick, blurb, default
        "myProp": (str,
                 _("myPropNick"),
                 _("myPropBlurb"),
                 _("myPropDefaultValue"),
                 GObject.ParamFlags.READWRITE)
    }


    ## Private specialization methods for GimpFu

    def _set_procedure_metadata(self, procedure, name):
        '''
        Convey local plugin metadata to Gimp
        '''
        procedure.set_image_types(_registered_plugins_[name].IMAGETYPES);
        procedure.set_documentation (N_(_registered_plugins_[name].BLURB),
                                     _registered_plugins_[name].HELP,
                                     name)
        procedure.set_menu_label(N_(_registered_plugins_[name].MENUITEMLABEL))
        procedure.set_attribution(_registered_plugins_[name].AUTHOR,
                                  _registered_plugins_[name].COPYRIGHT,
                                  _registered_plugins_[name].DATE)
        procedure.add_menu_path (_registered_plugins_[name].MENUPATH)


    def _create_plugin_procedure_args(self, procedure, proc_name ):
        '''
        Add (i.e. declare to Gimp) args to plugin procedure
        from formal params as recorded in local cache under proc_name
        '''

        '''
        This implementation uses one property on self many times.
        Requires a hack to Gimp, which otherwise refuses to add are many times from same named property.
        '''
        formal_params = _registered_plugins_[proc_name].PARAMS

        for i in range(len(formal_params)):
            # TODO map PF_TYPE to types known to Gimp (a smaller set)
            # use named properties of prop_holder
            procedure.add_argument_from_property(prop_holder, "intprop")



    ## GimpPlugIn virtual methods ##
    def do_query_procedures(self):
        self.set_translation_domain("Gimp30-python",
                                    Gio.file_new_for_path(Gimp.locale_directory()))

        # return all proc_names from local cache
        #TODO this is temp hack, just any one proc_name
        # keys() is not a list. Convert to list, then index
        # TODO for key in _registered_plugins_:
        return [ list(_registered_plugins_.keys())[0] ]


    '''
    Gimp calls this back when the GimpFu plugin calls main(), which calls Gimp.main().
    Thus it should execute AFTER the GimpFu plugin calls register().
    Until now, the GimpFu plugin is only registered in the local cache, and not registered with Gimp.

    The filename arg is name of the source file, not necessarily the same as given in register(name,...)
    '''
    def do_create_procedure(self, filename):

        # filename not otherwise used
        print ('create procedure(s) from file: ', filename, " .py")

        '''
        Register with Gimp all the locally registered plugins.
        '''
        for key in _registered_plugins_:
           procedure = Gimp.ImageProcedure.new(self,
                                            key,
                                            Gimp.PDBProcType.PLUGIN,
                                            _run, 	# wrapped plugin method
                                            None)
           self._set_procedure_metadata(procedure, key)
           self._create_plugin_procedure_args(procedure, key)

        # TODO, we created and registered many, we return only the last one??
        # Is creating many legal to Gimp 3?
        return procedure


# alias Gimp.PGB as pdb
# This not working, fails assert
#pdb = Gimp.get_pdb()
#assert pdb is not None
#pdb = GimpFu.get_pdb()
#if pdb is None:
#    print(Gimp.pdb_error())
