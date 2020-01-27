
import string   # v2 as _string to hide from authors


import sys

# Insure all warnings (deprecation and user) will be printed
if not sys.warnoptions:
    import warnings
    warnings.simplefilter("default") # Change the filter in this process



from gimpfu_types import *  # GimpFuProcedure only?

from gimpfu_exception import  do_proceed_error

'''
Nothing translatable here.
Plugin author should have translated strings in their definition.
'''

'''
GimpFu keeps a local copy of what was registered with Gimp.
After registering with Gimp, we could use Gimp's knowledge, but local cache has more information.
Namely, PARAMS have extra information: the kind of control widget for each param.
'''
'''
!!! When this is called, the PDB_ enums are not defined, use PF_ enums.
And pdb and gimp symbols are not defined.
'''

# Temp hack ???
from prop_holder import PropHolder

prop_holder = PropHolder()
print(prop_holder.props)
print(prop_holder.props.intprop)





class GimpfuProcedure():
    '''
    Understands and wraps Gimp procedure.

    GimpFu procedure is slightly different from Gimp PluginProcedure.
    This hides the differences.
    Differences:
       plugin_type not required of GimpFu author
    '''

    '''
    Responsible for sanity checking and fixups to author's declaration.
    This is in the nature of compiling:
       - give warnings
       - or throw exceptions (sanity)
    both of which printed in the console.
    At install time!  Once registered with Gimp, no further warnings.
    Author must delete ~/.config/.../pluginrc to see warnings again.
    '''
    def _deprecation(self, message):
        ''' wrapper of warnings.warn() that fixpoints the parameters. '''
        # stacklevel=2 means print two lines, including caller's info
        warnings.warn(message, DeprecationWarning, stacklevel=2)


    def __init__(self,
                proc_name, blurb, help, author, copyright,
                date, label, imagetypes,
                params, results, function,
                menu, domain, on_query, on_run):
        '''
        Takes data authored by GimpFu author.
        Which is wild, so sanity test.
        Then chunk data into self.
        Fix self for compatibility with Gimp.

        This does NOT create the procedure in Gimp PDB, which happens later.
        '''
        print ('new GimpfuProcedure', proc_name)

        # May not return, throws exceptions
        self._sanity_test_registration(proc_name, params, results)

        '''
        v2 plugin_type = PLUGIN
        v3 plugin_type in local cache always a dummy value
        Gimp enums are not defined yet.
        Other types are EXTENSION, INTERNAL, TEMPORARY
        but no type comes from the author
        and the type is not used anywhere else in GimpFu,
        so what is the purpose?
        '''
        # TODO this is a hack
        plugin_type = 1


        self.name = self._makeProcNamePrefixCanonical(proc_name)

        # TODO rename to ProcedureStruct, f vs F is too subtle
        self.metadata = GimpFuProcedure(blurb, help, author, copyright,
                                           date, label, imagetypes,
                                           plugin_type, params, results,
                                           function, menu, domain,
                                           on_query, on_run)

        '''
        Fix author's mistakes and allow deprecated constructs.
        Generates data into self.metadata.
        These are in the nature of patches.
        And hard to maintain.
        '''

        self._did_fix_menu = self._deriveMissingMenu()
        self._deriveMissingParams()
        '''
        !!! When we insert image params,
        signature registered with Gimp
        differs from signature of run_func.
        '''
        self._did_insert_image_params = self._deriveMissingImageParams()



    '''
    Methods that understand what parameters are guiable.
    '''

    @property
    def guiable_formal_params(self):
        # computable property
        if self.is_a_imageprocedure_subclass:
            # slice off prefix of formal param descriptions (i.e. image and drawable)
            # leaving only descriptions of GUI-time params
            result = self.metadata.PARAMS[2:]
        else:
            # is LoadProcedure
            result = self.metadata.PARAMS

        print("guiable_formal_params:", result)
        return result


    def split_guiable_actual_args(self, actual_args):   # list => list, list
        ''' Split actual_args by whether they are user changeable in GUI '''
        '''
        Actual args are those of the plugin,
        and passed by Gimp.
        Only some are guiable,
        and only some are passed to run_func
        (when we inserted image and drawable)
        '''
        """
        Cruft?
        if self.is_a_imageprocedure_subclass:
            # slice off prefix of formal param descriptions (i.e. image and drawable)
            # leaving only descriptions of GUI-time params
            guiable = actual_args[2:]
            nonguiable = actual_args[:2]
        else:
            # is LoadProcedure
            guiable = actual_args
            nonguiable = []
        """
        '''
        !!! Signature in Gimp includes leading run_mode.
        But GimpFu signature does not.
        So this splits off leading image and drawable
        '''
        nonguiable = actual_args[:2]
        guiable    = actual_args[2:]

        return nonguiable, guiable


    def join_nonguiable_to_guiable_args(self, nonguiable, guiable):
        '''
        Understands whether we have different signature for run_func '''
        if self._did_insert_image_params:
            # nonguiable args in signature of both plugin and run_func
            result = guiable
        else:
            # nonguiable args in signature of plugin but not the run_func
            result = nonguiable + guiable
        return result



    '''
    Methods re class of procedure.

    Knows how to determine the subclass from attributes of the metadata.

    Each subclass has a run_func with a different signature prefix.
    E.G. an ImageProcedure signature must start like: (image, drawable, ...)

    This is the inheritance:
    Gimp.Procedure
       Gimp.FileProcedure
           Gimp.LoadProcedure
       Gimp.ImageProcedure

    '''

    @property
    def is_a_imageprocedure_subclass(self):
        '''
        An ImageProcedure must have signature (Image, Drawable, ...)
        and a non-null IMAGETYPES
        TODO could be stricter, i.e. check args prefix is image and drawable
        '''
        # not empty string is True
        return self.metadata.IMAGETYPES

    @property
    def is_a_imagelessprocedure_subclass(self):
        '''
        A imageless procedure (Gimp.Procedure) has empty IMAGETYPEs.
        The signature CAN be (Image, Drawable) but need not be.



        A imageless procedure is always enabled in Gimp GUI (doesn't care about imagetypes)
        and might not take an existing image, instead creating one.
        '''
        return not self.is_a_imageprocedure_subclass

    """
    TODO is_a_loadprocedure_subclass
    A LoadProcedure usually installs to menu File>, but need not.
    For example some plugins that install to menu Filter>Render
    just create a new image.
    """







    """
    def get_metadata(self):
        ''' Return metadata authored by GimpFu author. '''
        return _registered_plugins_[proc_name]
    """


    def get_authors_function(self):
        ''' Return function authored by GimpFu author. '''
        return self.metadata.FUNCTION


    '''
    Conveyance methods
    '''

    def convey_metadata_to_gimp(self, procedure):
        '''
        understands GimpProcedure methods

        procedure is-a Gimp.PluginProcedure
        '''
        # WAS _registered_plugins_[name]
        procedure.set_image_types(self.metadata.IMAGETYPES);
        procedure.set_documentation (self.metadata.BLURB,
                                     self.metadata.HELP,
                                     self.name)
        procedure.set_menu_label(self.metadata.MENUITEMLABEL)
        procedure.set_attribution(self.metadata.AUTHOR,
                                  self.metadata.COPYRIGHT,
                                  self.metadata.DATE)
        # TODO apparently GIMP can declare error (see console)
        # TODO is there are result of this call that we can check?
        procedure.add_menu_path (self.metadata.MENUPATH)


    def convey_procedure_arg_declarations_to_gimp(self, procedure, count_omitted_leading_args):
        '''
        Convey  to Gimp a declaration of args to the procedure.
        From formal params as recorded in local cache under proc_name
        '''

        '''
        This implementation uses one property on self many times.
        Requires a hack to Gimp, which otherwise refuses to add are many times from same named property.
        '''
        formal_params = self.metadata.PARAMS

        for i in range(count_omitted_leading_args, len(formal_params)):
            # TODO map PF_TYPE to types known to Gimp (a smaller set)
            # use named properties of prop_holder
            procedure.add_argument_from_property(prop_holder, "intprop")




    '''
    Private methods.
    Fixups to self.
    '''


    # TODO this needs review.  Rewrite to a functional style.
    #
    # !!! Side effects on passed parameters
    def _deriveMissingMenu(self):
        '''
        if menu is not given, derive it from label
        Ability to omit menu is deprecated, so this is FBC.
        '''
        result = False
        if self.metadata.MENUPATH is None:
            if self.metadata.MENUITEMLABEL:
                # label but no menu. Possible menu path in the label.
                fields = self.metadata.MENUITEMLABEL.split("/")
                if fields:
                    self.metadata.MENUITEMLABEL = fields.pop()
                    self.metadata.MENUPATH = "/".join(fields)

                    result = True

                    message = (f"{self.name}: Use the 'menu' parameter instead"
                               f" of passing a full menu path in 'label'.")
                    self._deprecation(message)
                else:
                    # 'label' is not a path, can't derive menu path
                    message = f"{self.name}: Simple menu item 'label' without 'menu' path."
                    # TODO will GIMP show it in the GUI in a fallback place?
                    self._deprecation(message)
            else:
                # no menu and no label
                # Normal, user intends to create plugin only callable by other plugins
                message = (f"{self.name}: No 'menu' and no 'label'."
                           f"Plugin will not appear in Gimp GUI.")
                # Not really a deprecation, a UserWarning??
                self._deprecation(message)
        else:
            if  self.metadata.MENUITEMLABEL:
                # menu and label given
                # Normal, user intends plugin appear in GUI
                pass
            else:
                # menu but no label
                # TODO Gimp will use suffix of 'menu' as 'label' ???
                message = (f"{self.name}: Use the 'label' parameter instead"
                           f"of passing menu item at end of 'menu'.")
                self._deprecation(message)
        return result





    def _deriveMissingParams(self):
        ''' FBC Add missing params according to plugin type. '''

        '''
        FBC.
        In the distant past, an author could specify menu like <Load>
        and not provide a label
        and not provide the first two params,
        in which case GimpFu inserts two params.
        Similarly for other cases.
        '''
        # v2 if self._did_fix_menu and plugin_type == PLUGIN:
        # require _deriveMissingMenu called earlier
        if not self._did_fix_menu:
            return

        file_params = [(PF_STRING, "filename", "The name of the file", ""),
                       (PF_STRING, "raw-filename", "The name of the file", "")]

        if self.metadata.MENUPATH is None:
            pass
        elif self.metadata.MENUPATH.startswith("<Load>"):
            self.metadata.PARAMS[0:0] = file_params
            message = f"{self.name}: Fixing two file params for Load plugin"
            self._deprecation(message)
        elif self.metadata.MENUPATH.startswith("<Image>") or self.metadata.MENUPATH.startswith("<Save>"):
            self.metadata.PARAMS.insert(0, (PF_IMAGE, "image", "Input image", None))
            self.metadata.PARAMS.insert(1, (PF_DRAWABLE, "drawable", "Input drawable", None))
            message = f"{self.name}: Fixing two image params for Image or Save plugin"
            self._deprecation(message)
            if self.metadata.MENUPATH.startswith("<Save>"):
                self.metadata.PARAMS[2:2] = file_params
                message = f"{self.name}: Fixing two file params for Save plugin"
                self._deprecation(message)


    def _deriveMissingImageParams(self):
        '''
        Some plugins declare they are <Image> plugins,
        but don't have first two params equal to (image, drawable),
        and have imagetype == "" (menu item enabled even if no image is open).
        And then Gimp refuses to create procedure
        (but does create an item in pluginrc!)
        E.G. sphere.py

        So we diverge the signature of the plugin from the signature of the run_func.
        The GimpFu plugin author might be unaware, unless they explore,
        or try to call the PDB procedure from another PDB procedure.
        '''
        result = False
        # if missing params (never there, or not fixed by earlier patch)
        # TODO if params are missing altogether
        if ( self.metadata.MENUPATH.startswith("<Image>")
            and self.metadata.PARAMS[0][0] != PF_IMAGE
            and self.metadata.PARAMS[1][0] != PF_DRAWABLE
            ):
            self.metadata.PARAMS.insert(0, (PF_IMAGE, "image", "Input image", None))
            self.metadata.PARAMS.insert(1, (PF_DRAWABLE, "drawable", "Input drawable", None))
            message = f"{self.name}: Fixing two image params for Image plugin"
            self._deprecation(message)
            result = True
        return result







    def _makeProcNamePrefixCanonical(self, proc_name):
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
        new_proc_name = proc_name
        if (not proc_name.startswith("python-") and
            not proc_name.startswith("extension-") and
            not proc_name.startswith("plug-in-") and
            not proc_name.startswith("file-") ):
               new_proc_name = "python-fu-" + proc_name
               message = f"Procedure name canonicalized to {new_proc_name}"
               self._deprecation(message)
        return new_proc_name


    def _sanity_test_registration(self, proc_name, params, results):
        ''' Quit when detect exceptional proc_name or params. '''

        '''
        Since: 3.0 Gimp enforces: Identifiers for procedure names and parameter names:
        Characters from set: '-', 'a-z', 'A-Z', '0-9'.
        v2 allowed "_"
        Gimp will check also.  So redundant, but catch it early.
        '''
        proc_name_allowed = string.ascii_letters + string.digits + "-"
        param_name_allowed = string.ascii_letters + string.digits + "-_"

        def letterCheck(str, allowed):
            for ch in str:
                if not ch in allowed:
                    return False
            else:
                return True

        # TODO transliterate "_" to "-" FBC

        if not letterCheck(proc_name, proc_name_allowed):
            raise Exception("procedure name contains illegal characters")

        for ent in params:
            if len(ent) < 4:
                raise Exception( ("parameter definition must contain at least 4 "
                              "elements (%s given: %s)" % (len(ent), ent)) )

            if not isinstance(ent[0], int):
                # TODO check in range
                exception_str = f"Plugin parameter type {ent[0]} not a valid PF_ enum"
                raise Exception(exception_str)

            if not letterCheck(ent[1], param_name_allowed):
                # Not fatal since we don't use it, args are a sequence, not by keyword
                # But Gimp may yet complain.
                do_proceed_error(f"parameter name '{ent[1]}'' contains illegal characters")

        for ent in results:
            if len(ent) < 3:
                raise Exception( ("result definition must contain at least 3 elements "
                              "(%s given: %s)" % (len(ent), ent)))

            if not isinstance(ent[0], int):
                raise Exception("result must be of integral type")

            if not letterCheck(ent[1], param_name_allowed):
                # not fatal unless we use it?
                do_proceed_error(f"result name '{ent[1]}' contains illegal characters")
