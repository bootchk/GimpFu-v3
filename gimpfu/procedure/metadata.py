


from gimpfu.message.proceed import  proceed
from gimpfu.message.deprecation import Deprecation

from gimpfu.procedure.formal_params import FuFormalParams
from gimpfu.procedure.type import FuProcedureType

from gimpfu.enums.gimpfu_enums import *  # PF_ enums

import string   # v2 as _string to hide from authors
from inspect import signature
import logging


# v3 _registered_plugins_ is a dictionary of FuProcedureMetadata

class FuProcedureMetadata():
    '''
    Responsibilities:
    1. for sanity checking and fixups to author's declaration.
    2. conveying to Gimp
    3. understands old versus new style registration
    4. understands plugin type (Image, File)
    5. provide utility function letter_check to FuFormalParams class


    This is in the nature of compiling:
       - give warnings
       - or throw exceptions (sanity)
    both of which printed in the console.
    At install time!  Once registered with Gimp, no further warnings.
    Author must delete ~/.config/.../pluginrc to see warnings again.
    '''



    '''
    Since: 3.0 Gimp enforces: Identifiers for procedure names and parameter names:
    Characters from set: '-', 'a-z', 'A-Z', '0-9'.
    v2 allowed "_"
    Gimp will check also.  So redundant, but catch it early.
    '''
    proc_name_allowed = string.ascii_letters + string.digits + "-"
    param_name_allowed = string.ascii_letters + string.digits + "-_"



    '''
    __init__ fixes deprecations
    May raise exceptions
    '''
    def __init__(self,
       name,
       blurb, help, author, copyright,
       date, label, imagetypes,
       plugin_type, params, results,
       function, menu, domain,
       on_query, on_run):

        self.logger = logging.getLogger("GimpFu.FuProcMetadata")

        # Retain name for debugging, but owner of metadata knows the name, not us
        # Rather than make the metadata know the owner of the metadata
        self._name = self.makeProcNamePrefixCanonical(name)

        # Fixup deprecated: Allow string args to be nullable with "None"
        label =self.substitute_empty_string_for_none(label, "label")
        imagetypes = self.substitute_empty_string_for_none(imagetypes, "imagetypes")
        menu = self.substitute_empty_string_for_none(menu, "menupath")

        # wild data, soon to be fixed up
        self.BLURB=blurb
        self.HELP= help
        self.AUTHOR= author
        self.COPYRIGHT=copyright
        self.DATE= date
        self.MENUITEMLABEL= label
        self.IMAGETYPES= imagetypes
        self.PLUGIN_TYPE= plugin_type
        self.RESULTS= results
        self.FUNCTION= function
        self.MENUPATH= menu
        self.DOMAIN= domain
        self.ON_QUERY= on_query
        self.ON_RUN= on_run

        # Retain the old, but not very descriptive, names "params" and "results"
        # IN formal args
        self.params = FuFormalParams(owner_name=self._name)
        for param in params:
             # assert param is a tuple, unpack when passing
             self.params.append(*param)
        # OUT formal args
        # TODO some docs say (type, name, description) but other docs say ...default_value
        # Why would there be a default value for a return value?
        self.results = FuFormalParams(owner_name=self._name)
        for param in results:
             # assert param is a tuple, unpack when passing
             self.results.append(*param)

        '''
        Fix author's mistakes and allow deprecated constructs.
        Generates data into self.
        These are in the nature of patches.
        And hard to maintain.
        '''
        # May not return, throws exceptions
        self._sanity_test_registration()

        self.did_fix_menu = self._deriveMissingMenu()
        self._fix_deprecated_menu()

        '''
        !!! When we insert image params,
        signature registered with Gimp
        differs from signature of run_func.
        '''
        # !!! Pass self as parameter
        self.does_gimpfu_signature_differ_from_gimp_signature = self.params.deriveMissingParams(self)
        # TODO why do we do this twice, consolidate or make cases distinct?
        # One checks for new style registration, the other doesn't???
        if not self.does_gimpfu_signature_differ_from_gimp_signature:
            self.does_gimpfu_signature_differ_from_gimp_signature = self.params.deriveMissingImageParams(self)


    def set_nonguiable_arg_count(self, count):
        self._nonguiable_arg_count = count

    def convey_to_gimp(self, procedure, name):
        ''' convey self to procedure (is-a Gimp.PluginProcedure) '''
        procedure.set_image_types(self.IMAGETYPES);
        procedure.set_documentation (self.BLURB,
                                     self.HELP,
                                     name)

        procedure.set_attribution(self.AUTHOR,
                                  self.COPYRIGHT,
                                  self.DATE)
        """
        Some procedures don't appear in menus.

        GIMP can warn in console for empty menu path,
        but the procedure will still exist.
        TODO is there are result of this call that we can check?

        Why is it called "add", can a procedure be in more than one place in menus?
        """
        if self.MENUPATH != "" :    # TODO or None ?
            procedure.set_menu_label(self.MENUITEMLABEL)
            procedure.add_menu_path (self.MENUPATH)


    def convey_in_args_to_gimp(self, procedure):
        #    ******                                                                 ****
        self.params.convey_to_gimp(procedure, count_omitted_leading_args=self._nonguiable_arg_count, is_in_arg=True)
    def convey_out_args_to_gimp(self, procedure):
        self.results.convey_to_gimp(procedure, count_omitted_leading_args=0, is_in_arg=False)


    '''
    Don't call until metadata initialized and fixed up.
    I.E. we look at fixed up menupath and not at any path that was in label (old style).
    See asserts.
    '''
    @property
    def type(self):
        """ Returns FuProcedureType """
        assert self.MENUPATH is not None
        result = FuProcedureMetadata.type_from_menu_path(self.MENUPATH)
        self.logger.debug(f"{result}")
        return result

    @classmethod
    def type_from_menu_path(cls, menuPath):
        """
        This seems to be the only way to reliably determine
        our notion of type (which tells whether procedure takes a run mode arg)

        Returns FuProcedureType
        """
        if menuPath.startswith("<Image>") :
            result = FuProcedureType.Image
        elif ( menuPath.startswith("<Vectors>")
            or menuPath.startswith("<Layers>")
            or menuPath.startswith("<Palettes>")
            ) :
            #TODO: other gimp_data monikers e.g. Brush
            result = FuProcedureType.Context
        elif menuPath.startswith("<Save>") :
            result = FuProcedureType.Save
        elif menuPath.startswith("<Load>") :
            result = FuProcedureType.Load
        elif menuPath == "" :
            result = FuProcedureType.Other
        else :
            Exception("Could not determine procedure type from menu path")
        return result




    '''
    This only refers to registration with GimpFu.
    Registration with Gimp no longer supports old style?
    I.E. this if FBC.

    Old style:
        denoted by menu path in the label field (must be fixed up)
        first two specfied args (img, drawable) implicit
        run_func formal args includes (img, drawable)
    New style:
        denoted by menu path in the menupath field
        first two specified args (img, drawable) are explicit
           (if the plugin run_func wants them)
        run_func formal args may or may not include (img, drawable)

    Require _deriveMissingMenu() called prior.
    '''
    @property
    def is_old_style_registration(self):
        return self.did_fix_menu

    @property
    def is_new_style_registration(self):
        return not self.is_old_style_registration





    @classmethod
    def fix_underbar(cls, proc_name):
        new_proc_name = proc_name.replace( '_' , '-')
        if (new_proc_name != proc_name):
            Deprecation.say("Underbar in procedure name.")
        return new_proc_name

    @classmethod
    def canonicalize_prefix(cls, proc_name):
        if (not proc_name.startswith("python-") and
            not proc_name.startswith("extension-") and
            not proc_name.startswith("plug-in-") and
            not proc_name.startswith("file-") ):
               result = "python-fu-" + proc_name
               message = f"Procedure name canonicalized to {result}"
               Deprecation.say(message)
        else:
           result = proc_name
        return result


    '''
    public: metadata knows how to fix procedure name
    '''
    def makeProcNamePrefixCanonical(self, proc_name):
        '''
        if given name not canonical, make it so.

        Canonical means having a prefix from a small set,
        so that from the canonical name, PDB browsers know how implemented.

        v2 allowed underbars, i.e. python_, extension_, plug_in_, file_ prefixes.

        Note that prefix python-fu intends to suggest (to browsers of PDB):
        - fu: simplified API i.e. uses GimpFu module
        - python: language is python
        script-fu is similar for Scheme language: simplified API
        You can write a Python language plugin without the simplified API
        and then it is author's duty to choose a canonically prefixed name.
        '''

        # FBC.  Gimp v3 does not allow underbar
        proc_name = FuProcedureMetadata.fix_underbar(proc_name)
        proc_name = FuProcedureMetadata.canonicalize_prefix(proc_name)
        if not self.letterCheck(proc_name, FuProcedureMetadata.proc_name_allowed):
            raise Exception(f"Procedure name: {proc_name} contains illegal characters.")
        return proc_name




    '''
    Utility functions
    '''
    def substitute_empty_string_for_none(self, arg, argname):
        if arg is None:
            Deprecation.say(f"Deprecated: Registered {argname} should be empty string, not None")
            result = ""
        else:
            result = arg
        return result



    def letterCheck(self, str, allowed):
        for ch in str:
            if not ch in allowed:
                return False
        else:
            return True


    '''
    Private methods.
    Fixups to self.  !!! Side effects on self
    '''

    def _fix_deprecated_menu(self):
        """ Fix menu paths deprecated. """
        # require _deriveMissingMenu() called prior

        # Deprecated Since 2.8.
        # No longer the case that they should be in <File>/New as some docs say???
        if self.MENUPATH.startswith("<Toolbox>/Xtns/Languages/Python-Fu") :
            self.MENUPATH = self.MENUPATH.replace("<Toolbox>/Xtns/Languages/Python-Fu", "<Image>/Filters/Extensions")
            Deprecation.say("Replaced menu path <Toolbox>/Xtns/Languages/Python-Fu with: <Image>/Filters/Extensions")
        elif self.MENUPATH.startswith("<Toolbox>/Xtns") :
            self.MENUPATH = self.MENUPATH.replace("<Toolbox>/Xtns", "<Image>/Filters/Extensions")
            Deprecation.say("Replaced menu path <Toolbox>/Xtns with: <Image>/Filters/Extensions")
        elif self.MENUPATH.startswith("<Toolbox>") :
            self.MENUPATH = self.MENUPATH.replace("<Toolbox>", "<Image>")
            Deprecation.say("Replaced menu path <Toolbox> with: <Image>")



    def _deriveMissingMenu(self):
        '''
        if menu is not given, derive it from label
        Ability to omit menu is deprecated, so this is FBC.
        '''
        result = False
        if not self.MENUPATH:
            if self.MENUITEMLABEL:
                # label but no menu. Possible menu path in the label.
                fields = self.MENUITEMLABEL.split("/")
                if fields:
                    self.MENUITEMLABEL = fields.pop()
                    self.MENUPATH = "/".join(fields)
                    result = True
                    Deprecation.say(f"Use the 'menu' parameter instead of passing a full menu path in 'label'.")
                else:
                    # 'label' is not a path, can't derive menu path
                    # TODO will GIMP show it in the GUI in a fallback place?
                    Deprecation.say(f"Simple menu item 'label' without 'menu' path.")
            else:
                # no menu and no label
                # Normal, not a deprecation. Plugin only callable by other plugins
                self.logger.debug(f"No 'menu' and no 'label'.  Plugin {self._name} will not appear in Gimp GUI.")
        else:
            if  self.MENUITEMLABEL:
                # menu and label given
                # Normal, user intends plugin appear in GUI
                pass
            else:
                # menu but no label
                # TODO Gimp will use suffix of 'menu' as 'label' ???
                message = (f" Use the 'label' parameter instead"
                           f"of passing menu item at end of 'menu'.")
                Deprecation.say(message)
        return result






    def _sanity_test_registration(self):
        ''' Quit when detect exceptional results or params. '''

        self.params.sanity_test(self)   # pass self for callback

        for ent in self.RESULTS:
            # ent is tuple
            # TODO a class
            if len(ent) < 3:
                # TODO proceed
                raise Exception( ("result definition must contain at least 3 elements "
                              "(%s given: %s)" % (len(ent), ent)))

            if not isinstance(ent[0], int):
                raise Exception("result must be of integral type")

            if not self.letterCheck(ent[1], self.param_name_allowed):
                # not fatal unless we use it?
                proceed(f"result name '{ent[1]}' contains illegal characters")


    """
    Three different signatures:
       1. formal gimp signature
       2. formal gimpfu signature (from author, in the params list)
       3. formal runfunc signature (from author, in the runfunc itself)

    History:
    In the past, certain arguments could be omitted.
    Thus signatures could differ.
    The epochs are:
       old style registration
       new style registration
       v3 registration

    GimpFu FBC still allows the image params to be omitted from the formal GimpFu parameter spec.
    Gimp v3 enforces that an image type plugin have signature (registered with Gimp) with image params.

    Note that the difference between 1. and 2. is a different but related concern
    from difference between 2. and 3.
    """

    '''
    CRUFT see method in FuProcedure
    def get_guiable_params(self):
        """ Return list of guiable FuFormalParam. """
        return self.params[self._nonguiable_arg_count:]
    '''


    def get_authors_function(self):
        ''' Return author's function AKA the run_func .
        !!! This is not a string, but a callable.
        Because in the author's source, in the registration data,
        the function name is not quoted but is a reference to the function.
        '''
        return self.FUNCTION


    """
    !!! This assumes that author did not define run_func with var args i.e "*args"
    """
    def get_runfunc_arg_count(self):
        sig = signature(self.get_authors_function())
        return len(sig.parameters)



    def does_runfunc_take_nonguiable_args(self, count_guiable_args):
        """ Understands whether we have different signature for run_func.

        One implementation is to determine the cases
        by examining formal signatures.
        Here, we take a more direct approach: introspect the run_func
        to determine the count of parameters.
        If the count of guiable args is less than what the run_func wants,
        assume we need to prefix args with image args passed from Gimp.
        """
        # This is nieve, and doesn't work well.
        # result = self.does_gimpfu_signature_differ_from_gimp_signature


        result = count_guiable_args < self.get_runfunc_arg_count()
        if not result:
            print(">>>>>>>>>>>>Omitting image params to run_func")
        return result
