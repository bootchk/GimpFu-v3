

import gi
gi.require_version("Gimp", "3.0")
from gi.repository import Gimp

from gimpfu.procedure.type import FuProcedureType

"""
Knows how to create a procedure in Gimp.

Implements some of the simplifications of GimpFu re implicit parameters.

Collaborates with:
  FuProcedure
  Gimp
  GimpFu top
"""


class FuProcedureCreator:

    @classmethod
    def _create_gimp_procedure(cls, procedure_type, plugin, name, gf_procedure, wrapped_run_func):
        """ Create basic Gimp.Procedure or a subclass as given in procedure_type

        Creation common to all subclasses.
        Note that Gimp has this class hierarchy:
        Gimp.Procedure
            Gimp.ImageProcedure
            Gimp.LoadProcedure
            Gimp.SaveProcedure
        !!! But not Gimp.VectorsProcedure etc.
        GimpFu creates a Vectors procedure by conveying the proper set of args (runmode, image, vectors)
        """
        # assert procedure-type is class (constructor) Gimp.Procedure or subclass e.g. Gimp.ImageProcedure

        procedure = procedure_type.new(plugin,
                                        name,
                                        Gimp.PDBProcType.PLUGIN,
                                        wrapped_run_func, # wraps Author's run_func
                                        None)
        gf_procedure.set_wrapped_procedure(procedure)
        gf_procedure.convey_metadata_to_gimp()
        gf_procedure.convey_return_value_declarations_to_gimp()

        # !!! Caller must also convey args
        return procedure



    @classmethod
    def _create_image_procedure(cls, plugin, name, gf_procedure, wrapped_run_func):
        """ Create a Gimp.ImageProcedure. """

        procedure = cls._create_gimp_procedure(Gimp.ImageProcedure, plugin, name, gf_procedure, wrapped_run_func)
        '''
        ImageProcedure:
        Gimpfu does not convey run_mode param.
        Gimpfu does not convey first two formal args.
        Those are the "standard" args, automatic in Gimp.
        Gimpfu only conveys the "extra" args.

        !!! When Gimp calls the run() callback, it passes (runmode, image, drawable, extra_args)
        TODO move these comments to where the call lands.
        Author's run_func takes img, drw as first two params
        Gimpfu massages image, drawable, otherArgArray (but omits run_mode) into args to run_func
        '''
        gf_procedure.set_nonguiable_arg_count(2)
        gf_procedure.convey_procedure_guiable_arg_declarations_to_gimp()
        return procedure


    @classmethod
    def _create_context_procedure(cls, plugin, name, gf_procedure, wrapped_run_func):
        # !!! Pass the type Gimp.Procedure, which we will new(),
        # and then to the instance we convey specialized args
        procedure = cls._create_gimp_procedure(Gimp.Procedure, plugin, name, gf_procedure, wrapped_run_func)

        '''
        Gimp plugin operating on a gimp-data instance requires (runmode, image, gimp_data)
        '''
        gf_procedure.convey_runmode_arg_declaration_to_gimp()
        # Author formally declared params (image, <gimp_data>, guiable_args)
        gf_procedure.set_nonguiable_arg_count(0)    # TODO 0, 1 ???
        gf_procedure.convey_procedure_guiable_arg_declarations_to_gimp()
        return procedure

    @classmethod
    def _create_other_procedure(cls, plugin, name, gf_procedure, wrapped_run_func):
        procedure = cls._create_gimp_procedure(Gimp.Procedure, plugin, name, gf_procedure, wrapped_run_func)
        '''
        Gimp plugin operating out of the blue (no image or other object)
        requires ( just the declared args)
        '''
        # Author formally declared params (guiable_args)
        gf_procedure.set_nonguiable_arg_count(0)    # TODO 0, 1 ???
        gf_procedure.convey_procedure_guiable_arg_declarations_to_gimp()
        return procedure


    @classmethod
    def create(cls, plugin, name, gf_procedure,
       wrapped_image_run_func,
       wrapped_context_run_func,
       wrapped_other_run_func):
        '''
        Create and return a subclass of Gimp.Procedure, from GimpFuProcedure.

        <plugin> is-a Gimp.PlugIn, may create many procedures

        Dispatch on the locally determined kind
        e.g. by the menu path and by the signature of the formal args.
        And use a different wrapped_run_runc for each subclass.
        '''
        if gf_procedure.type == FuProcedureType.Image:
            procedure =  cls._create_image_procedure(plugin, name, gf_procedure, wrapped_image_run_func)
        elif gf_procedure.type == FuProcedureType.Context:
            procedure =  cls._create_context_procedure(plugin, name, gf_procedure, wrapped_context_run_func)
        elif gf_procedure.type == FuProcedureType.Other:
            procedure =  cls._create_other_procedure(plugin, name, gf_procedure, wrapped_other_run_func)
        else:
            # TODO Better message, since this error depends on authored code
            # TODO preflight this at registration time.
            raise Exception("Unknown procedure type")
        # ensure result is-a Gimp.Procedure
        return procedure

        """
                logger.info("Create imageless procedure")
                procedure = Gimp.Procedure.new(plugin,
                                                name,
                                                Gimp.PDBProcType.PLUGIN,
                                                _run_imagelessprocedure, 	# wrapped plugin method
                                                None)
                gf_procedure.convey_metadata_to_gimp(procedure)

                gf_procedure.convey_runmode_arg_declaration_to_gimp(procedure)
                gf_procedure.convey_procedure_arg_declarations_to_gimp(
                    procedure,
                    count_omitted_leading_args=0)
            else:
        """

        """
        # TODO different plug_type LoadProcedure for loaders???
        elif gf_procedure.is_a_loadprocedure_subclass :
            procedure = Gimp.LoadProcedure.new(plugin,
                                            name,
                                            Gimp.PDBProcType.PLUGIN,
                                            _run_loadprocedure, 	# wrapped plugin method
                                            None)
        """
