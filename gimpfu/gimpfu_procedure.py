
import string   # v2 as _string to hide from authors

from gimpfu_types import *

'''
Nothing translatable here.
Plugin author should have translated strings in their definition.
'''

'''
GimpFu cache of possibly many plugins registered by a single .py file.
cache: local copy of registration with Gimp.
After registering with Gimp, we could use Gimp's knowledge, but local cache has more information.
Namely, PARAMS have extra information: the kind of control widget for each param.
Dictionary of GimpFuProcedure
'''
'''
_registered_plugins_ = {}
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

    def __init__(self,
                proc_name, blurb, help, author, copyright,
                date, label, imagetypes,
                params, results, function,
                menu, domain, on_query, on_run):
        '''
        Takes data authored by GimpFu author.
        Which is wild, so sanity test.
        Then massage for compatibility.
        Then chunk data into a struct.

        This does NOT create the procedure in Gimp PDB,
        which happens later TODO
        '''
        print ('new GimpfuProcedure', proc_name)

        self._sanity_test_registration(proc_name, params, results)

        # TODO side effects on menu, params according to plugin_type
        # TODO also derives params, rename andParameters
        self._deriveMissingMenu(menu, label, params)

        self.name = self._makeProcNamePrefixCanonical(proc_name)

        '''
        v2 plugin_type = PLUGIN
        v3 plugin_type in local cache always a dummy value
        Gimp enums are not defined yet
        '''
        # TODO this is a hack
        plugin_type = 1

        # TODO rename to ProcedureStruct, f vs F is too subtle
        #_registered_plugins_[proc_name]
        self.metadata = GimpFuProcedure(blurb, help, author, copyright,
                                           date, label, imagetypes,
                                           plugin_type, params, results,
                                           function, menu, domain,
                                           on_query, on_run)




    '''
    def get_first_proc_name():
        # TODO class should implement iterator
        # TODO for key in _registered_plugins_:
        # then return a list

        # return one name
        #TODO this is temp hack, just any one proc_name
        # keys() is not a list. Convert to list, then index

        result = list(_registered_plugins_.keys())[0]
        print("get_first_proc_name", result)
        return result
    '''


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
        procedure.add_menu_path (self.metadata.MENUPATH)


    def convey_procedure_arg_declarations_to_gimp(self, procedure):
        '''
        Convey  to Gimp a declaration of args to the procedure.
        From formal params as recorded in local cache under proc_name
        '''

        '''
        This implementation uses one property on self many times.
        Requires a hack to Gimp, which otherwise refuses to add are many times from same named property.
        '''
        formal_params = self.metadata.PARAMS

        for i in range(len(formal_params)):
            # TODO map PF_TYPE to types known to Gimp (a smaller set)
            # use named properties of prop_holder
            procedure.add_argument_from_property(prop_holder, "intprop")




    '''
    Private methods

    Have self, but don't use it.
    '''


    # TODO this needs review.  Rewrite to a functional style.
    #
    # !!! Side effects on passed parameters
    def _deriveMissingMenu(self, menu, label, params):
        '''
        if menu is not given, derive it from label
        Ability to omit menu is deprecated, so this is FBC.

        Also convenience or compatibility ??? :
        adjust params according to plugin_type
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
                message = ("%s: passing a full menu path in 'label' is "
                           "deprecated, use the 'menu' parameter instead."
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
               print("GimpFu: Warning: Procedure name canonicalized to", new_proc_name)
        return new_proc_name


    def _sanity_test_registration(self, proc_name, params, results):
        ''' Quit when detect exceptional proc_name or params. '''

        '''
        Since: 3.0 Gimp enforces: Identifiers for procedure names and parameter names:
        Characters from set: '-', 'a-z', 'A-Z', '0-9'.
        v2 allowed "_"
        Gimp will check also.  So redundant, but catch it early.
        '''
        def letterCheck(str):
            allowed = string.ascii_letters + string.digits + "-"
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
                # TODO check in range
                exception_str = f"Plugin parameter type {ent[0]} not a valid PF_ enum"
                raise Exception(exception_str)

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
