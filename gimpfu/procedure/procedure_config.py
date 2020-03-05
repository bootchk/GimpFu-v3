
import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp




class FuProcedureConfig():
    """
    Wraps Gimp.ProcedureConfig

    The algebra of calls is: FuProcedureConfig(), begin_run(), [<show dialog()>, set_changed_settings()], end_run()
    """

    def __init__(self, procedure):
        self._procedure = procedure
        self._config = procedure.create_config()
        self._args_gvalue_array = None

    def begin_run(self, image, run_mode, args):
        """ Tell Gimp the arg values before any settings changes. """
        # require args is-a GValueArray
        self._args_gvalue_array = args
        self._config.begin_run (image, run_mode, args)

    def set_changed_settings(self, args):
        """ Put last values of args into self. """
        # require args is list of Python types for guiable args
        # TODO:
        print("***************set_changed_settings NOT IMPLEMENTED")

        # !!! args is prefixed with (image, drawable) i.e. has more elements than _args_gvalue_array
        index = 2
        for arg in args:
            print(f"changed setting {arg}")
            # !!! you can't assign a GValue to a variable, PyGObject unmarshals it
            # foo = index()
            # IOW, index() returns a GValue that you must call immediately,
            # without assigning the GValue index().set
            # TODO still not resolved.
            # self._args_gvalue_array.index(index-2) = arg => SyntaxError: can't assign to function call
            self._args_gvalue_array.index(index-2) = arg
            # TODO remove, then reinsert

        self._config.set_values(self._args_gvalue_array)
        pass

    def end_run(self, is_success):
        self._config.end_run (Gimp.PDBStatusType.SUCCESS)
