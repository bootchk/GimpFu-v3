
import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp

from adaption.marshal import Marshal
from adaption.types import Types

from adaption.value_array import FuValueArray
from adaption.generic_value import FuGenericValue

from message.proceed_error import proceed

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
    Gimp also persists ProcedureConfig across Gimp sessions,
    so that next time a user uses a plugin, the initial dialog settings match
    the last use of the dialog in the last session of Gimp.

    The algebra of calls is:
        <create a procedure and register its args>
        FuProcedureConfig(),
        begin_run(),
        [get_initial_settings(), <show dialog()>, set_changed_settings()],
        end_run()

    A FuProcedureConfig owns (wraps) a Gimp.ProcedureConfig.
    A ProcedureConfig owns a GimpValueArray, will get() and set() it.
    """


    def __init__(self, gimpfu_procedure, procedure, length):
        self._gf_procedure = gimpfu_procedure
        self._procedure = procedure
        self._config = procedure.create_config()
        # Save length, Gimp.ProcedureConfig does not expose it
        # assert length is len(guiable args) ???
        self._length = length
        # Hack, try + 2
        #self._length = length + 2

        self.logger = logging.getLogger("GimpFu.FuProcConfig")
        self.logger.debug(f"__init__, length: {length}")



    def begin_run(self, image, run_mode, args):
        """ Tell Gimp to set self with last values when run_mode is interactive.

        Side effects on self.  Args is unchanged.
        Later, use get_initial_settings().
        """
        # require args is-a GValueArray

        """
        See despeckle.c.  Apparently, you can/should call begin_run no matter the mode.
        When you call end-run, you will just pass a config that is unchanged by a dialog.

        if run_mode == Gimp.RunMode.NONINTERACTIVE:
            return

        TODO what if this procedure is called by another procedure,
        does that change the settings?
        """

        '''
        args is either:
        - values for case: passed from a caller
        - default values (at registration time) for case: invoked interactively
        '''
        self._config.begin_run (image, run_mode, args)


    #OLD Abandoned because of difficulties with getting matching types for GValueArray
    def _get_values_using_config_get_values(self):
        """
        Implementation: Gimp.ProcedureConfig.get_values is not a getter() but takes mutable arg
        Must pass a GimpValueArray of same length as self,
        having GTypes that match formal params
        """
        # TODO magic number 3 accounts for runmode, image, drawable
        # magic number 1 allows for first element *procedure* returned by get_values()
        value_array = FuValueArray.get_empty_gvalue_array(self._length + 1)
        # TODO the types of the GValues must match the types of the registered args
        # and the first type must match the type Gimp.Procedure ?
        self._config.get_values(value_array)

        # hack off first element, the *procedure*
        value_array.remove(0)

        # assert is same size as can be passed to set_values()
        return value_array

    def _get_property_value(self, name):
        """ Get value of property of self.

        Catching exceptions with fixup and proceed.
        """
        self.logger.debug(f"_get_property_value name: {name}")
        try:
            result = self._config.get_property(name)
        except TypeError:
            """ Usually property not exist.
            Because failed to convey args to Gimp.
            Because of current limitations of patches to Gimp.
            "GParamBoxed is not handled"

            Temporarily:
            Most often it the property is type Gimp.RGB for 'color' arg/property,
            so patch it.
            But also the property type may be Gimp.Image and others, unfixed.

            Permanently: return arbitrary GValue so we can proceed.
            """
            proceed(f"GimpFu failed to register with Gimp property name: {name}.")
            if name == 'color':
                result = FuGenericValue.new_rgb_value()
            else:
                result = FuGenericValue.new_int_gvalue()
        # ensure result is-a GValue
        return result




    def _get_values_using_config_properties(self):
        """
        Return GValueArray of values for *guiable* arguments/properties

        A Gimp.ProcedureConfig has property for each *guiable* arg of procedure.

        Code derived from gimp/plug-ins/common/despeckle.c, which accesses config properties
        not in a batch, but just whenever dialog widgets have events.

        Implementation: GimpFuProcedure knows GimpFu's metadata for procedure.
        Iterate over GimpFu metadata, since ProcedureConfig has extra property "procedure"
        """
        length = len(self._gf_procedure.guiable_formal_params)
        result = Gimp.ValueArray.new(length)
        for formal_param in self._gf_procedure.guiable_formal_params :
            name = formal_param.gimp_name
            value = self._get_property_value(name)
            # assert value is-a GValue
            result.append(value)
        return result



    def _get_values(self):
        """ Get current values out of self. """
        return self._get_values_using_config_properties()



    def get_initial_settings(self):
        """ Returns wrapped values from self, to be passed as initial (last) values to a dialog. """

        value_array = self._get_values()

        # Assert config length > 0.  Should not be called unless there one or more guiable args.
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
        """ Put last values of users_args (guiable) into self. """
        # require users_args is list of Python typed elements, for guiable args
        self.logger.info(f"set_changed_settings, length: {self._length}, len users_args: {len(users_args)}")

        # DEBUG
        aux_args = self._procedure.get_aux_arguments()
        self.logger.info(f"length aux_args: {len(aux_args)}")
        self.logger.info(f"aux_args: {aux_args}")
        args = self._procedure.get_arguments()
        self.logger.info(f"length args: {len(args)}")
        self.logger.info(f"args: {args}")
        # DEBUG, get properties of ProcedureConfig
        # FAIL: print(self._procedure.type_name_from_class())
        print(self._config.list_properties())

        """
        Get the current values in the Gimp.ProcedureConfig.
        The values are still what existed when Gimp invoked the plugin.
        """
        value_array = self._get_values()

        # assert value_array same size as registered args
        # and is appropriate length for set_values()

        # Fill with user's values
        # !!! users_args is NOT prefixed with (runmode, image, drawable)

        configurable_args_values = users_args
        dest_index = 0

        for value in configurable_args_values:
            self.logger.info(f"changed setting at index: {dest_index} to value: {value}")
            self._set_value_at_index(value_array, value, dest_index)
            dest_index += 1

        self._config.set_values(value_array)


    def end_run(self, is_success):
        self._config.end_run (Gimp.PDBStatusType.SUCCESS)
