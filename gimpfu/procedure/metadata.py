
import string   # v2 as _string to hide from authors

from message.proceed_error import  do_proceed_error
from message.deprecation import Deprecation

from procedure.formal_params import FuFormalParams

from gimpfu_enums import *  # PF_ enums


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
       blurb, help, author, copyright,
       date, label, imagetypes,
       plugin_type, params, results,
       function, menu, domain,
       on_query, on_run):

        label =FuProcedureMetadata.substitute_empty_string_for_none(label, "label")
        imagetypes = FuProcedureMetadata.substitute_empty_string_for_none(imagetypes, "imagetypes")
        menu = FuProcedureMetadata.substitute_empty_string_for_none(menu, "menupath")

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

        self.params = FuFormalParams()
        for param in params:
             # assert param is a tuple, unpack when passing
             self.params.append(*param)

        '''
        Fix author's mistakes and allow deprecated constructs.
        Generates data into self.
        These are in the nature of patches.
        And hard to maintain.
        '''
        # May not return, throws exceptions
        self._sanity_test_registration()

        self.did_fix_menu = self._deriveMissingMenu()

        self.params.deriveMissingParams(self)   # pass self as metadata
        '''
        !!! When we insert image params,
        signature registered with Gimp
        differs from signature of run_func.
        '''
        self.did_insert_image_params = self.params.deriveMissingImageParams(self)



    def convey_to_gimp(self, procedure, name):
        ''' convey self to procedure (is-a Gimp.PluginProcedure) '''
        procedure.set_image_types(self.IMAGETYPES);
        procedure.set_documentation (self.BLURB,
                                     self.HELP,
                                     name)
        procedure.set_menu_label(self.MENUITEMLABEL)
        procedure.set_attribution(self.AUTHOR,
                                  self.COPYRIGHT,
                                  self.DATE)
        # TODO apparently GIMP can declare error (see console)
        # TODO is there are result of this call that we can check?
        procedure.add_menu_path (self.MENUPATH)




    '''
    Don't call these until metadata initialized and fixed up.
    I.E. we look at fixed up menupath and not at any path that was in label (old style).
    See asserts.
    '''
    @property
    def is_image_procedure_type(self):
        assert self.MENUPATH is not None
        return self.MENUPATH.startswith("<Image>")

    @property
    def is_save_procedure_type(self):
        assert self.MENUPATH is not None
        return self.MENUPATH.startswith("<Save>")

    @property
    def is_load_procedure_type(self):
        assert self.MENUPATH is not None
        return self.MENUPATH.startswith("<Load>")



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
        print(f"Procedure name: {proc_name}")
        return proc_name




    '''
    Utility functions
    '''
    def substitute_empty_string_for_none(arg, argname):
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

                    message = (f" Use the 'menu' parameter instead"
                               f" of passing a full menu path in 'label'.")
                    Deprecation.say(message)
                else:
                    # 'label' is not a path, can't derive menu path
                    message = f" Simple menu item 'label' without 'menu' path."
                    # TODO will GIMP show it in the GUI in a fallback place?
                    Deprecation.say(message)
            else:
                # no menu and no label
                # Normal, user intends to create plugin only callable by other plugins
                message = (f" No 'menu' and no 'label'."
                           f"Plugin will not appear in Gimp GUI.")
                # TODO Not really a deprecation, a UserWarning??
                Deprecation.say(message)
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
                do_proceed_error(f"result name '{ent[1]}' contains illegal characters")
