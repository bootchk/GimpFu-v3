

from procedure.metadata import FuProcedureMetadata


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





class FuProcedure():
    '''
    Understands and wraps Gimp procedure.

    GimpFu procedure is slightly different from Gimp PluginProcedure.
    This hides the differences.
    Differences:
       plugin_type not required of
       certain procedure parameters not required of
       FBC fixes Author use of deprecated stuff

    Also understands:
     - what parameters are guiable.
     - how to convey to Gimp the specs for a procedure
     - types of procedure
    '''




    def __init__(self,
                proc_name, blurb, help, author, copyright,
                date, label, imagetypes,
                params, results, function,
                menu, domain, on_query, on_run):
        '''
        Takes metadata authored by .
        Which is wild, so sanity test.

        Fix self for compatibility with Gimp.

        This does NOT create the procedure in Gimp PDB, which happens later.
        '''
        print ('new FuProcedure', proc_name)

        '''
        v2 plugin_type = PLUGIN
        v3 plugin_type in local cache always a dummy value
        Gimp enums are not defined yet.
        Other types are EXTENSION, INTERNAL, TEMPORARY
        but no type comes from the author
        and the type is not used anywhere else in GimpFu,
        so what is the purpose?
        '''
        # TODO a hack, Gimpfu never use plugin_type?
        plugin_type = 1

        self.metadata = FuProcedureMetadata(blurb, help, author, copyright,
                                        date, label, imagetypes,
                                        plugin_type, params, results,
                                        function, menu, domain,
                                        on_query, on_run)

        # name is not part of metadata, but is the key
        # and metadata knows how to make it canonical
        self.name = self.metadata.makeProcNamePrefixCanonical(proc_name)



    '''
    Methods that understand what parameters are guiable.
    '''

    @property
    def guiable_formal_params(self):
        # computable property
        if self.is_a_imageprocedure_subclass:
            # slice off prefix of formal param descriptions (i.e. image and drawable)
            # leaving only descriptions of GUI-time params
            result = self.metadata.params.PARAMS[2:]
        else:
            # is LoadProcedure
            result = self.metadata.params.PARAMS

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
        if self.metadata.did_insert_image_params:
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
        The signature CAN be (Image, Drawable)? but usually is not.

        A imageless procedure is always enabled in Gimp GUI (doesn't care about imagetypes)
        and might not take an existing image, instead creating one.
        '''
        result = (self.metadata.IMAGETYPES is None) or (self.metadata.IMAGETYPES == "")
        return result
    """
    TODO is_a_loadprocedure_subclass
    A LoadProcedure usually installs to menu File>, but need not.
    For example some plugins that install to menu Filter>Render
    just create a new image.
    """


    """
    def get_metadata(self):
        ''' Return metadata authored by . '''
        return _registered_plugins_[proc_name]
    """


    def get_authors_function(self):
        ''' Return function authored by . '''
        return self.metadata.FUNCTION


    '''
    Conveyance methods
    '''

    def convey_metadata_to_gimp(self, procedure):
        self.metadata.convey_to_gimp(procedure, self.name);

    def convey_runmode_arg_declaration_to_gimp(self, procedure):
        procedure.add_argument_from_property(prop_holder, "RunmodeProp")


    def convey_procedure_arg_declarations_to_gimp(self,
        procedure,
        count_omitted_leading_args=0,
        prefix_with_run_mode=False):

        # TODO metadata.params should be hidden
        self.metadata.params.convey_to_gimp(procedure, count_omitted_leading_args, prefix_with_run_mode);
