
import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp
gi.require_version('GimpUi', '3.0')
from gi.repository import GimpUi


"""
Runs the dialog for a plugin.

GUI implemented in Gimp

Gimp is capable of displaying a dialog for a Gimp.Procedure.
It takes a ProcedureConfig.
Before the dialog run, ProcedureConfig contains initial values for widgets.
After the dialog run, ProcedureConfig contains values the user chose.

Taken from foggify.py
"""


def get_values_from_config(config):
    # assert config is a FuProcedureConfig
    values = []
    # get args from properties of config
    # TODO for loop
    values.append( config.get_property('color') )
    return values




class GimpControlsRunner():

    @staticmethod
    def run(fuProcedure, gimpProcedure, config):     # , list_wrapped_args, guiable_formal_params):

        """
        assert config is a FuProcedureConfig which wraps a Gimp.ProcedureConfig
        Is initialized for the given gimpProcedure
        and config.begin_run(image, run_mode, args) has been called
        """

        GimpUi.init('foo1') # TODO what is this string?

        procedureDialog = GimpUi.ProcedureDialog.new(gimpProcedure,
            config._config,       # pass the wrapped config
            fuProcedure.name )    # title of dialog is the name of the plugin
        procedureDialog.fill(None)   # ???

        # run() returns True if OK was chosen, else Cancel was chosen.
        was_canceled = not procedureDialog.run()
        procedureDialog.destroy()

        # assert (not canceled) => the config contains the user's choice of control values from the dialog
        users_chosen_control_values = []
        if not was_canceled :
            users_chosen_control_values = config.get_list_of_wrapped_values()

        # ensure returned values is a list of Python primitives or wrapped Gimp objects
        return was_canceled, users_chosen_control_values
