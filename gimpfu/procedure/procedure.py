

from procedure.metadata import FuProcedureMetadata
from procedure.prop_holder import PropHolder
from procedure.type import FuProcedureType

import logging

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
    Understands GimpFu local representation of a plugin procedure,
    the one(s) being defined by the current Author's source.

    Does NOT wrap Gimp.Procedure, only knows how to create one, for the current source

    FuProcedure is slightly different from Gimp.Procedure.
    This hides the differences.
    Differences:
       plugin_type not required of
       certain procedure parameters not required of
       FBC fixes Author use of deprecated stuff

    Also understands:
     - what parameters are guiable.
     - how to convey to Gimp:
     -- the specs for a procedure
     -- the return values for a procedure
     - types of procedure
     - the callbacks for the plugin: function, on_query, on_run


    Note that FuProcedure does not understand last values, see FuProcedureConfig
    '''




    def __init__(self,
                proc_name, blurb, help, author, copyright,
                date, label, imagetypes,
                params, results, function,
                menu, domain, on_query, on_run):

        self.logger = logging.getLogger("GimpFu.FuProcedure")

        '''
        Takes metadata created by plugin Author .
        Which is wild, so sanity test.

        Fix self for compatibility with Gimp.

        This does NOT create the procedure in Gimp PDB, which happens later.
        '''
        self.logger.info (f"new instance: {proc_name}")

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
    def set_nonguiable_arg_count(self, count):
        self.metadata.set_nonguiable_arg_count(count)

    # TODO: not used uniformly, see FuFormalParams.get_guiable_params
    # TODO magic number 2 below duplicated elsewhere, should be in one place
    @property
    def guiable_formal_params(self):
        # computable property
        # TODO and image_type is not empty
        if self.type == FuProcedureType.Image:
            # slice off prefix of formal param descriptions (i.e. image and drawable)
            # leaving only descriptions of GUI-time params
            result = self.metadata.params.PARAMS[2:]
        elif (self.type == FuProcedureType.Load
            or self.type == FuProcedureType.Other):
            # all params guiable
            result = self.metadata.params.PARAMS
        else:
            Exception("Unhandled procedure type in guiable_formal_params()")

        self.logger.info(f"has guiable_formal_params: {result}")
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
        """ Possibly join args """
        if self.metadata.does_runfunc_take_nonguiable_args(len(guiable)):
            result = nonguiable + guiable
        else:
            result = guiable
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

    ''' Delegate: Metatdata knows the type of procedure. '''
    @property
    def type(self):  return self.metadata.type


    """
    OLD
    '''
    An ImageProcedure must have signature (Image, Drawable, ...)
    and a non-null IMAGETYPES
    TODO could be stricter, i.e. check args prefix is image and drawable
    '''
    # not empty string is True
    return self.metadata.IMAGETYPES
    """

    """
    Cruft
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

    """
    TODO is_a_loadprocedure_subclass
    A LoadProcedure usually installs to menu File>, but need not.
    For example some plugins that install to menu Filter>Render
    just create a new image.
    """


    def get_authors_function(self):
        result = self.metadata.get_authors_function()
        self.logger.debug(f"func: {result}")
        return result



    '''
    Conveyance methods
    '''
    def set_wrapped_procedure(self, procedure):
        """ Set the Gimp.Procedure that self wraps. """
        self._wrapped_gimp_procedure = procedure

    # all conveyance methods require set_wrapped_procedure() was called prior

    def convey_metadata_to_gimp(self):
        self.metadata.convey_to_gimp(self._wrapped_gimp_procedure, self.name);

    def convey_runmode_arg_declaration_to_gimp(self):
        self.logger.debug("convey run mode")

        # get an instance that has a RunmodeProp
        prop_holder = PropHolder()

        # Gimp.Procedure will add args from named properties of any given instance
        self._wrapped_gimp_procedure.add_argument_from_property(prop_holder, "RunmodeProp")


    def convey_procedure_guiable_arg_declarations_to_gimp(self ):
        self.metadata.convey_in_args_to_gimp(self._wrapped_gimp_procedure)


    def convey_return_value_declarations_to_gimp(self):
        """ Declare to Gimp return value types of this plugin procedure. """
        self.metadata.convey_out_args_to_gimp(self._wrapped_gimp_procedure)
        # self.logger.warning("convey_return_value_declarations_to_gimp NOT IMPLEMENTED")
        # procedure.add_return_value_from_property(self, "new-palette")

    '''
    callbacks
    '''

    def on_run(self):
        if self.metadata.ON_RUN:
            self.logger.info("on_run called")
            a_callback = self.metadata.ON_RUN
            a_callback()

    #TODO: on_query


    '''
    Cruft
    def convey_last_values(self, guiable_args):
        """ Tell Gimp to shelve user's latest choices of settings. """

        """
        Implementation notes:
        None of the current Python plugins do this.
        See the .c plugins for example code.
        The best example is plug-ins/common/despeckle.c
        """
        self.logger.info("convey_last_values NOT IMPLEMENTED")
        config = self._wrapped_gimp_procedure.create_config()
        self.logger.info(config)
        ## assert config is type Gimp.ProcedureConfig, having properties same as args of procedure
    '''
