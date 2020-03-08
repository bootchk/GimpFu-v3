
from procedure.formal_param import FuFormalParam
from gimpfu_enums import *  # PF_ enums
from message.deprecation import Deprecation


class FuFormalParams():
    '''
    A set of FuFormalParams.

    Distinct from the other metadata.

    Responsibilities:
    - keep a list of FuFormalParams
    - fixups on self
    - convey self to Gimp
    '''

    '''
    Constant class data
    '''
    file_params = [FuFormalParam(PF_STRING, "filename", "The name of the file", ""),
                   FuFormalParam(PF_STRING, "raw-filename", "The name of the file", "")]
    image_param = FuFormalParam(PF_IMAGE, "image", "Input image", None)
    drawable_param = FuFormalParam(PF_DRAWABLE, "drawable", "Input drawable", None)





    def __init__(self):
        self.PARAMS= []

    def append(self, *args):
        self.PARAMS.append(FuFormalParam(*args))


    def sanity_test(self, metadata):
        for param in self.PARAMS:
            """
            TODO
            if len(ent) < 4:
                raise Exception( ("parameter definition must contain at least 4 "
                              "elements (%s given: %s)" % (len(ent), ent)) )
            """

            if not isinstance(param.PF_TYPE, int):
                # TODO check in range
                exception_str = f"Plugin parameter type {param.PF_TYPE} not a valid PF_ enum"
                raise Exception(exception_str)


            # Common mistake is a space in the LABEL
            param.LABEL = param.LABEL.replace( ' ' , '_')

            if not metadata.letterCheck(param.LABEL, metadata.param_name_allowed):
                # Not fatal since we don't use it, args are a sequence, not by keyword
                # But Gimp may yet complain.
                # TODO transliterate space to underbar
                do_proceed_error(f"parameter name '{param.LABEL}'' contains illegal characters")


    def deriveMissingParams(self, metadata):
        ''' FBC Add missing params according to plugin type. '''

        '''
        FBC.
        In the distant past, an author could specify menu like <Load>
        and not provide a label
        and not provide the first two params,
        in which case GimpFu inserts two params.
        Similarly for other cases.
        '''
        # v2 if self.did_fix_menu and plugin_type == PLUGIN:
        # require _deriveMissingMenu called earlier
        if metadata.is_new_style_registration:
            # specified params are explict, requires no fixup
            return

        if metadata.is_load_procedure_type:
            # insert into slice
            self.PARAMS[0:0] = FuFormalParams.file_params
            message = f" Fixing two file params for Load plugin"
            Deprecation.say(message)
        elif metadata.is_image_procedure_type or metadata.is_save_procedure_type:
            self.PARAMS.insert(0, FuFormalParams.image_param)
            self.PARAMS.insert(1, FuFormalParams.drawable_param)
            message = f" Fixing two image params for Image or Save plugin"
            Deprecation.say(message)
            if metadata.is_save_procedure_type:
                self.PARAMS[2:2] = file_params
                message = f" Fixing two file params for Save plugin"
                Deprecation.say(message)
        #print(self.PARAMS)


    def deriveMissingImageParams(self, metadata):
        '''
        Some plugins declare they are <Image> plugins,
        but don't have first two params equal to (image, drawable),
        and have imagetype == "" (menu item enabled even if no image is open).
        And then Gimp refuses to create procedure
        (but does create an item in pluginrc!)
        E.G. sphere.py

        So we diverge the signature of the plugin from the signature of the run_func.
        The author might be unaware, unless they explore,
        or try to call the PDB procedure from another PDB procedure.

        TODO after we are done, the count of args to run_func
        and the count of formal parameters (PARAMS) should be the same.
        Can we count the formal parameters of run_func?
        '''

        result = False
        # if missing params (never there, or not fixed by earlier patch)
        # TODO if params are missing altogether
        if ( metadata.is_image_procedure_type
            and self.PARAMS[0].PF_TYPE != PF_IMAGE
            and self.PARAMS[1].PF_TYPE != PF_DRAWABLE
            ):
            self.PARAMS.insert(0, FuFormalParams.image_param)
            self.PARAMS.insert(1, FuFormalParams.drawable_param)
            message = f" Fixing two image params for Image plugin"
            Deprecation.say(message)
            result = True
        return result


    def convey_to_gimp(self, procedure, count_omitted_leading_args, prefix_with_run_mode):
        ''' convey self to Gimp '''
        '''
        Convey  to Gimp a declaration of args to the procedure.

        This implementation uses one property on self many times.
        Requires a hack to Gimp, which otherwise refuses to add are many times from same named property.
        '''

        if prefix_with_run_mode :
            pass
            # WIP
            # procedure.add_argument_from_property(prop_holder, "intprop")

        for i in range(count_omitted_leading_args, len(self.PARAMS)):
            self.PARAMS[i].convey_to_gimp(procedure)
