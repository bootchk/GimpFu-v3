
import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp

from adaption.marshal import Marshal
from adaption.types import Types

from adaption.value_array import FuValueArray

import logging


class FuProcedureConfig():
    """
    Wraps Gimp.ProcedureConfig

    A ProcedureConfig is a set of settings for a plugin.
    It remembers "last values."
    Before a user interaction (GUI dialog), the settings initialize the dialog control's values.
    After a user interaction, a ProcedureConfig is updated with changed settings.
    Gimp sends a ProcedureConfig in a run() call when Gimp invokes the plugin.
    The plugin returns a ProcedureConfig to Gimp after run() is completed.

    Gimp persists a ProcedureConfig for a procedure.
    Persists it at least over a Gimp session,
    so that the user can "Repeat" or "Re-show" a plugin
    and it will use the persisted settings (the last values.)
    ??? Does Gimp persist across Gimp sessions?

    The algebra of calls is:
        <create a procedure and register its args>
        FuProcedureConfig(),
        begin_run(),
        [get_initial_settings(), <show dialog()>, set_changed_settings()],
        end_run()

    A FuProcedureConfig owns (wraps) a Gimp.ProcedureConfig.
    A ProcedureConfig owns a GimpValueArray, will get() and set() it.
    """

    # TODO something broken, Gimp throws n_psecs == n_values....

    def __init__(self, procedure, length):
        self._procedure = procedure
        self._config = procedure.create_config()
        # Save length, Gimp.ProcedureConfig does not expose it
        # assert length is len(guiable args) ???
        self._length = length
        # Hack, try + 2
        #self._length = length + 2

        self.logger = logging.getLogger("GimpFu.FuProcedureConfig")
        self.logger.debug(f"__init__, length: {length}")


    """
    @property
    def length():
    """

    def begin_run(self, image, run_mode, args):
        """ Tell Gimp to set self with last values when run_mode is interactive.

        Side effects on self.  Args is unchanged.
        Later, use get_initial_settings().
        """
        # require args is-a GValueArray

        """
        TODO, do we need to check runmode, or does Gimp check it and do nothing?
        """
        if run_mode == Gimp.RunMode.NONINTERACTIVE:
            return

        '''
        args is either:
        - values for case: passed from a caller
        - default values (at registration time) for case: invoked interactively
        '''
        self._config.begin_run (image, run_mode, args)


    def _get_values(self):
        """ Get current values out of self.

        Implementation: Gimp.ProcedureConfig.get_values is not a getter() but takes mutable arg
        Must pass a GimpValueArray of same length as self
        """
        # TODO magic number 3 accounts for runmode, image, drawable
        value_array = FuValueArray.get_empty_gvalue_array(self._length + 3)
        self._config.get_values(value_array)
        return value_array


    def get_initial_settings(self):
        """ Returns wrapped values from self, to be passed as initial (last) values to a dialog. """

        value_array = self._get_values()

        self._config.get_values(value_array)
        # Require non-empty config returns non-empty values
        assert value_array.length() > 0

        values_list = Types.convert_gimpvaluearray_to_list_of_gvalue(value_array)
        wrapped_arg_list = Marshal.wrap_args(values_list)
        # assert values_list is a list of GValues, not prefixed with image, drawable


        return wrapped_arg_list



    '''
    !!! you can't assign a GValue to a variable, PyGObject unmarshals it

    array.index(index-2) = arg => SyntaxError: can't assign to function call
    '''
    def _set_value_at_index(self, array, value, index):
        """ Set the value of the GValue at index of array """
        '''
        GimpValueArray lacks a setter, must remove and insert.
        '''
        # require value is-a GValue
        # require array is-a Gimp.ValueArray
        array.remove(index)
        array.insert(index, value)



    def set_changed_settings(self, users_args):
        """ Put last values of users_args into self. """
        # require users_args is list of Python typed elements, for guiable args
        # TODO:
        self.logger.info(f"set_changed_settings, length: {self._length}, len users_args: {len(users_args)}")

        # DEBUG
        aux_args = self._procedure.get_aux_arguments()
        self.logger.info(f"length aux_args: {len(aux_args)}")
        self.logger.info(f"aux_args: {aux_args}")
        args = self._procedure.get_arguments()
        self.logger.info(f"length args: {len(args)}")
        self.logger.info(f"args: {args}")

        """
        Get the current values in the Gimp.ProcedureConfig.
        The values are what existed when Gimp invoked the plugin.
        """
        value_array = self._get_values()

        # Fill with user's values, offset appropriately
        # !!! users_args is NOT prefixed with (runmode, image, drawable)
        configurable_args_values = users_args
        dest_index = 3

        for value in configurable_args_values:
            self.logger.info(f"changed setting at index: {dest_index} to value: {value}")
            self._set_value_at_index(value_array, value, dest_index)
            dest_index += 1

        self._config.set_values(value_array)


    def end_run(self, is_success):
        self._config.end_run (Gimp.PDBStatusType.SUCCESS)
