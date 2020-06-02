
import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp

# For GLib.Error()
# ??? Require 2.32 for GArray instead of GValueArray
from gi.repository import GLib


from procedure.procedure_config import FuProcedureConfig
from procedures.procedures import FuProcedures

from adaption.marshal import Marshal

from message.proceed_error import *
from message.deprecation import Deprecation
from message.suggest import Suggest

import logging


"""
Understands how to run a GimpFu procedure
from Gimp's callback to the registered run function.

Hides:
- adaption of signatures
- GimpFu's hiding of runmode
- GimpFu's messaging

Class was developed to extract code formerly in gimpfu_top
"""

class FuRunner:

    logger = logging.getLogger('GimpFu.FuRunner')

    @staticmethod
    def _try_run_func(proc_name, function, args, display):
        '''
        Run the plugin's run_func with args, catching exceptions.
        Return result of run_func.

        This is always non-headless (interactive.)
        But not require an image open.
        Show dialog on exception.
        '''
        try:
            result = function(*args)
        except:
            # Show dialog here, or pass exception string back to Gimp???
            from gui.exception_dialog import ExceptionDialog

            if display:
                ExceptionDialog.show(proc_name, display)

            exc_str, exc_only_str = ExceptionDialog.create_exception_str()

            FuRunner.logger.critical(f"{exc_str}, {exc_only_str}")
            result = None
            # TODO either pass exc_str back so Gimp shows in dialog,
            # or reraise so Gimp shows a generic "plugin failed" dialog
            # or show our own dialog above
            raise
        return result







    @staticmethod
    def _interact(procedure, list_gvalues_all_args, config):
        '''
        Show GUI when guiable args, then execute run_func.
        Progress will show in Gimp window, not dialog window.

        Returns (was_canceled, (results of run_func or None))
        '''
        FuRunner.logger.info(f"_interact, {procedure}, {list_gvalues_all_args}")

        # get name from instance of Gimp.Procedure
        proc_name = procedure.get_name()

        # TODO assume first arg is likely an image
        # display = Display.get(proc_name, list_gvalues_all_args[0])

        from gui.display import Display
        display = Display.get_window(proc_name)

        gf_procedure = FuProcedures.get_by_name(proc_name)

        function = gf_procedure.metadata.FUNCTION

        wrapped_in_actual_args = Marshal.wrap_args(list_gvalues_all_args)

        guiable_formal_params =  gf_procedure.guiable_formal_params

        """
        CRUFT from implementation where dialog executed run_script
        guiable_formal_params =  gf_procedure.guiable_formal_params
        nonguiable_actual_args, guiable_actual_args = gf_procedure.split_guiable_actual_args(wrapped_in_actual_args)

        # effectively a closure, partially bound to function, nonguiable_actual_args
        # passed to show_plugin_dialog to be executed after dialog
        def run_script(guiable_actual_args):
            # guiable_actual_args may have been altered by the GUI from earlier values
            nonlocal function
            nonlocal nonguiable_actual_args

            wrapped_run_args = gf_procedure.join_nonguiable_to_guiable_args(nonguiable_actual_args,  guiable_actual_args)
            FuRunner.logger.info("wrapped_run_args", wrapped_run_args)
            '''
            invoke Authors func on unpacked args
            !!! Authors func never has run_mode, Gimpfu hides need for it.
            '''
            result = function(*wrapped_run_args)
            return result
        """



        if len(guiable_formal_params) == 0:
            # Just execute, don't open ControlDialog, but display ExceptionDialog
            FuRunner.logger.info("no guiable parameters")
            was_canceled = False
            # !!! no gui can change the in_args
            result = FuRunner._try_run_func(proc_name, function, wrapped_in_actual_args, display)
        else:
            # create GUI from guiable formal args, let user edit actual args

            #TODO duplicate??
            gf_procedure.on_run()

            from gui.control_dialog import PluginControlDialog

            '''
            v2
            # executes run_script if not canceled, returns tuple of run_script result
            was_canceled, result = gimpfu_dialog.show_plugin_dialog(
                procedure,
                guiable_actual_args,
                guiable_formal_params, run_script)
            '''
            nonguiable_actual_args, guiable_actual_args = gf_procedure.split_guiable_actual_args(wrapped_in_actual_args)

            '''
            If you omit this next step, it does not use last_values, instead
            using actual_args, which will be defaults in many cases.
            '''
            # Wrong: config.get_initial_settings(guiable_actual_args)
            # TEMP: this is correct, but not working:
            print(guiable_actual_args)
            guiable_actual_args = config.get_initial_settings()
            print(guiable_actual_args)

            was_canceled, guied_args = PluginControlDialog.show(
                procedure,
                guiable_actual_args,
                guiable_formal_params)
            if not was_canceled :

                config.set_changed_settings(guied_args)

                # update incoming guiable args with guied args
                wrapped_run_args = gf_procedure.join_nonguiable_to_guiable_args(nonguiable_actual_args, guied_args)
                FuRunner.logger.info(f"Wrapped args to run_func, {wrapped_run_args}" )

                # !!! with args modified since passed in
                result = FuRunner._try_run_func(proc_name, function, wrapped_run_args, display)
            else:
                # Don't save any gui changes to args
                result = None
                pass

        return was_canceled, result



    """
    These are the main exposed methods.

    Registered with Gimp as the run_func of Gimp procedures.
    """

    '''
    Since 3.0, changed the signature of _run():
    - parameters not in one tuple
    - type of 'procedure' parameter is GimpImageProcedure, not str.
    v2, most parameters were in one tuple.

    XXXNow the first several are mandatory and do not need to be declared when registering.
    XXXIn other words, formerly their declarations were boilerplate, repeated often for little practical use.

    Since 3.0,
    when the plugin procedure is of type Gimp.ImageProcedure
    the parameter actual_args only contains arguments special to given plugin instance,
    and the first two args (image and drawable) are passed separately.

    !!! The args are always as declared when procedure created.
    It is only when they are passed to the procedure that they are grouped
    in different ways (some chunked into a Gimp.ValueArray)

    Also formerly the first argument was type str, name of proc.
    Now it is of C type GimpImageProcedure or Python type ImageProcedure

    !!! Args are Gimp types, not Python types
    '''
    @staticmethod
    def run_imageprocedure(procedure, run_mode, image, drawable, original_args, data):
        ''' Callback from Gimp.

        GimpFu wrapper of the Authors "main" function, aka run_func
        '''

        FuRunner.logger.info(f"run_imageprocedure , {procedure}, {run_mode}, {image}, {drawable}, {original_args}")

        '''
        Create GimpValueArray of *most* args.
        !!! We  pass GimpValueArray of Gimp types to lower level methods.
        That might change when the lower level methods are fleshed out to persist values.
        *most* means (image, drawable, *original_args), but not run_mode!
        '''
        list_gvalues_all_args = Marshal.prefix_image_drawable_to_run_args(original_args, image, drawable)

        result = FuRunner._run_procedure_in_mode(procedure, run_mode, image, list_gvalues_all_args, original_args, data)
        # ensure result is-a GValueArray whose first element is a PDB_STATUS
        # and whose other elements have types matching registered return value types
        return result



    @staticmethod
    def run_context_procedure(procedure, original_args, data):
        ''' Callback from Gimp for a Gimp.Procedure class of procedure.

        For a procedure invoked from a context menu, operating on an instance of "Gimp data" e.g. Vectors, Brush, ...

        GimpFu wrapper of the Authors "main" function, aka run_func

        The signature is as defined by Gimp C code.
        '''
        FuRunner.logger.info(f"run_context_procedure , {procedure}, {original_args}, {data}")

        '''
        Rearrange args to fit _run_procedure_in_mode()
        '''
        list_gvalues_all_args = Marshal.convert_gimpvaluearray_to_list_of_gvalue(original_args)
        # assert is (runmode, image, <Gimp data object>)

        # GimpFu always hides run mode, delete first element
        list_gvalues_all_args.pop(0)

        # this type of procedure always NONINTERACTIVE
        run_mode = Gimp.RunMode.NONINTERACTIVE

        # TODO this type of procedure always passed image in the first element of GimpValueArray
        image = list_gvalues_all_args[0]

        result = FuRunner.FuRunner._run_procedure_in_mode(procedure, run_mode, image, list_gvalues_all_args, original_args, data)
        return result



    @staticmethod
    def _run_procedure_in_mode(procedure, run_mode, image, list_gvalues_all_args, original_args, data):
        '''
        Understands run_mode.
        Different ways to invoke procedure batch, or interactive.

        Hides run_mode from Authors.
        I.E. their run_func signature does not have run_mode.

        require procedure is-a Gimp.Procedure.
        require original_arges is-a Gimp.ValueArray.
        require list_gvalues_all_args is a list of GValues
        '''
        # args have already been marshalled into native types
        assert isinstance(list_gvalues_all_args, list)

        # To get the Python name of a Gimp.Procedure method,
        # see gimp/libgimp/gimpprocedure.h, and then remove the prefix gimp_procedure_
        name = procedure.get_name()

        FuRunner.logger.info(f"_run_procedure_in_mode: {name}, {run_mode}, {list_gvalues_all_args}")
        '''
        list_gvalues_all_args are one-to-one with formal params.
        list_gvalues_all_args may include some args that are not guiable (i.e. image, drawable)
        '''

        gf_procedure = FuProcedures.get_by_name(name)

        isBatch = (run_mode == Gimp.RunMode.NONINTERACTIVE)
        '''
        Else so-called interactive mode, with GUI dialog of params.
        Note that the v2 mode RUN_WITH_LAST_VALS is obsolete
        since Gimp 3 persists settings, i.e. actual arg values can be from last invocation.
        If not from last invocation, they are the formal parameter defaults.
        '''

        func = gf_procedure.get_authors_function()

        """
        The ProcedureConfig should have length equal to ????
        original_args is-a GimpValueArray
        """
        # config = FuProcedureConfig(procedure, len(list_gvalues_all_args)-2 )
        config = FuProcedureConfig(procedure, original_args.length() )
        config.begin_run(image, run_mode, original_args)

        if isBatch:
           try:
               # invoke func with unpacked args.  Since Python3, apply() gone.
               # TODO is this the correct set of args? E.G. Gimp is handling RUN_WITH_LAST_VALS, etc. ???
               result = func(*list_gvalues_all_args)
               # TODO add result values
               final_result = procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())
           except:
               final_result = procedure.new_return_values(Gimp.PDBStatusType.EXECUTION_ERROR, GLib.Error())
        else:
           # pass list of args

           '''
           Not enclosed in try:except: since then you don't get a good traceback.
           Any exceptions in showing a dialog are hard programming errors.
           Any exception in executing the run_func should be shown to user,
           either by calling our own dialog or by calling a Gimp.ErrorDialog (not exist)
           or by passing the exception string back to Gimp.
           '''
           was_canceled, result = FuRunner._interact(procedure, list_gvalues_all_args, config)
           if was_canceled:
               final_result = procedure.new_return_values(Gimp.PDBStatusType.CANCEL, GLib.Error())
               config.end_run(Gimp.PDBStatusType.CANCEL)
           else:
               # TODO add result values to Gimp  procedure.add_return_value ....
               # trigger Gimp create all return values from this status and prior add_return_value
               final_result = procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())
               config.end_run(Gimp.PDBStatusType.SUCCESS)
           """
           OLD above was enclosed in try
           try:
           except Exception as err:
               '''
               Probably GimpFu module programming error (e.g. bad calls to GTK)
               According to GLib docs, should be a warning, since this is not recoverable.
               But it might be author programming code (e.g. invalid PARAMS)
               '''
               do_proceed_error(f"Exception opening plugin dialog: {err}")
               final_result = procedure.new_return_values(Gimp.PDBStatusType.EXECUTION_ERROR, GLib.Error())
           """

        '''
        Make visible any alterations to user created images.
        GimpFu promises to hide the need for this.
        '''
        Gimp.displays_flush()   # !!! Gimp, not gimp

        did_suggest_or_deprecate = Suggest.summarize()
        did_suggest_or_deprecate = did_suggest_or_deprecate or Deprecation.summarize()

        if did_suggest_or_deprecate:
            # TODO make this go to the status bar, not a dialog
            # Gimp.message("See console for suggestions and deprecations.")
            pass

        if summarize_proceed_errors():  # side effect is writing to console
            """ Gimpfu proceeded past earlier exceptions.
            Display a dialog.
            Then raise a final exception.
            """
            msg = "GimpFu detected errors.  See console for a summary."
            Gimp.message(msg)
            raise Exception(msg)


        # ensure final_result is type GimpValueArray
        return final_result


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
