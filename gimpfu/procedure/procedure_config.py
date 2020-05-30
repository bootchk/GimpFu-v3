
import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp

from adaption.marshal import Marshal
from adaption.types import Types
from adaption.generic_value import FuGenericValue

import logging


class FuProcedureConfig():
    """
    Wraps Gimp.ProcedureConfig

    A ProcedureConfig is a set of settings for a plugin.
    It remembers "last values."
    Before a user interaction (GUI dialog), the settings initialize the dialog control's values.
    After a user interaction, a ProcedureConfig is updated with changed settings.
    Gimp persists a ProcedureConfig.
    Gimp sends a ProcedureConfig in a run() call when Gimp invokes the plugin.
    The plugin returns a ProcedureConfig to Gimp after run() is completed.

    The algebra of calls is:
        FuProcedureConfig(),
        begin_run(),
        [get_initial_settings(), <show dialog()>, set_changed_settings()],
        end_run()

    A FuProcedureConfig owns (wraps) a Gimp.ProcedureConfig.
    A ProcedureConfig owns a GimpValueArray, will get() and set() it.
    """

    def __init__(self, procedure, length):
        self._procedure = procedure
        self._config = procedure.create_config()
        # Save length, Gimp.ProcedureConfig does not expose it
        self._length = length

        self.logger = logging.getLogger("GimpFu.FuProcedureConfig")


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


    # TODO move this to FuValueArray
    def _get_empty_value_array(self):
        assert self._length > 0
        # pass length as prealloc
        value_array = Gimp.ValueArray.new(self._length)
        # a new GimpValueArray always has length 0
        assert value_array.length() == 0

        for i in range(0, self._length) :
            # This generates TypeError: unknown type (null) later???
            # Although docs say this creates an uninitialized GValue
            # value_array.append(None)
            gen_value = FuGenericValue.new_int_gvalue()
            value_array.append(gen_value)
        assert value_array.length() == self._length
        return value_array


    def get_initial_settings(self):
        """ Returns wrapped values from self, to be passed as initial (last) values to a dialog. """

        # ProcedureConfig.get_values is not a getter() but takes arg
        # Must pass a GimpValueArray of same length as self
        value_array = self._get_empty_value_array()

        self._config.get_values(value_array)
        # Require non-empty config returns non-empty values
        assert value_array.length() > 0

        values_list = Types.convert_gimpvaluearray_to_list_of_gvalue(value_array)
        wrapped_arg_list = Marshal.wrap_args(values_list)
        # assert values_list is a list of GValues, not prefixed with image, drawable

        """
        cruft
        for value in args:
            print(f"last value to setting {arg}")
            arg = self._set_value_at_index(arg, index-2)
        """
        return wrapped_arg_list



    '''
    !!! you can't assign a GValue to a variable, PyGObject unmarshals it

    array.index(index-2) = arg => SyntaxError: can't assign to function call
    '''
    def _set_value_at_index(self, array, value, index):
        """ Set the value of the GValue at index of self """
        '''
        GimpValueArray lacks a setter, must remove and insert.
        '''
        # require value is-a GValue
        array.remove(index)
        array.insert(index, value)



    def set_changed_settings(self, args):
        """ Put last values of args into self. """
        # require args is list of Python types for guiable args
        # TODO:
        self.logger.info("set_changed_settings called")

        array = Gimp.ValueArray.new(0)
        self._config.get_values(array)

        # !!! args is prefixed with (image, drawable) i.e. has more elements than self
        index = 2
        for arg in args:
            self.logger.info(f"changed setting at index: {index} to value: {arg}")
            self._set_value_at_index(array, arg, index-2)
            index += 1

        self._config.set_values(array)


    def end_run(self, is_success):
        self._config.end_run (Gimp.PDBStatusType.SUCCESS)
