
"""
Runs the dialog for a plugin, showing it's controls.

GUI implemented in Python and GimpFu
"""
class GimpFuControlsRunner():

    @staticmethod
    def run(fuProcedure, gimpProcedure, list_wrapped_args, guiable_formal_params):
        from gimpfu.gui.control_dialog import PluginControlDialog

        nonguiable_actual_args, guiable_actual_args = fuProcedure.split_guiable_actual_args(list_wrapped_args)
        # FuRunner.logger.info(f"in guiable args: {guiable_actual_args}")

        '''
        If you omit this next step, it does not use last_values, instead
        using actual_args, which will be defaults in many cases.
        '''
        # Wrong: config.get_initial_settings(guiable_actual_args)
        # TEMP: this is correct, but not working:
        # TODO what is wrong here???
        # Is the config persistent across changes to the plugin definition?
        # Who handles run with last values?
        # guiable_actual_args = config.get_initial_settings()

        was_canceled, guied_args = PluginControlDialog.show(
            fuProcedure,
            gimpProcedure,
            guiable_actual_args,
            guiable_formal_params)

        return was_canceled, guied_args
