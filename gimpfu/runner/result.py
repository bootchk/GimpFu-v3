

import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp

# For GLib.Error()
# ??? Require 2.32 for GArray instead of GValueArray
from gi.repository import GLib

import logging
from collections.abc import Iterable



class FuResult():
    """
    Knows how to make a result for a plugin (a PDB procedure).

    Test cases:
    - procedure returning void (almost any plugin)
    - procedure failing
    - procedure canceled
    - procedure returning single value (Test>Return Int...  in test/returnInt)
    - procedure returning many values  (Test>Return two Int...  in test/returnInt)

    Most plugins only have side effects on Gimp resource e.g. images and return void.
    """

    logger = logging.getLogger('GimpFu.FuResult')

    # TODO For a Python exception in GimpFu, we return status EXECUTION_ERROR.
    # We should put more into the GLib.Error
    # for the case where we were called by another plugin,
    # i.e. propagate the error message as far as we can.
    # The caller will also fail, but with just "EXECUTION_ERROR" unless we do.
    # ????

    @staticmethod
    def makeGLibError(status):
        """
        Make a GLib error.
        It carries more information into a result?
        The message?
        Gimp.Procedure.new_return_values() takes one.
        """
        if status == Gimp.PDBStatusType.SUCCESS:
            result = GLib.Error()
        else:
            # Seems wierd that a "literal" is a Glib.Error
            quark = GLib.quark_from_string("GimpFu")
            result = GLib.Error.new_literal( quark, "foo", 0 )
        FuResult.logger.info(f"makeGLibError result: {result}")
        return result


    @staticmethod
    def make(procedure, status, runfunc_result=None):
        """
        Make a result for a PDB procedure, i.e. a GimpValueArray:
        - whose first element is a PDB_STATUS
        - and whose other elements have types matching registered return value types

        Require status is-a Gimp.PDBStatusType
        Require runfunc_result is some Python object, or None

        status == SUCCESS not imply runfunc_result is not None:
        a procedure returning void returns result==None.
        """

        error = FuResult.makeGLibError(status)
        resultArray = procedure.new_return_values(status, error) # GLib.Error())
        """
        assert resultArray is-a GimpValueArray
        of size corresponding to count of procedure's registered return values
        whose first item is a status with given value
        but whose any other items are arbitrary or default values?
        """
        FuResult.logger.info(f"resultArray is: {resultArray}")

        if (status == Gimp.PDBStatusType.SUCCESS):
            FuResult.logger.info(f"runfunc_result is: {runfunc_result}")
            if runfunc_result is not None:
                targetItem = 1  # Start past the status item

                if isinstance(runfunc_result, Iterable):
                    for item in runfunc_result:
                        resultArray.insert(targetItem, item)
                        targetItem += 1
                else:
                    # runfunc_result is elementary, not iterable
                    resultArray.insert(targetItem, runfunc_result)
                    # Note this is not correct:
                    #gvalue = resultArray.index(targetItem)
                    #gvalue.set_value(item)
        else:
            """
            Else assert the resultArray has a valid status.
            Don't care what any other values are, Gimp will ignore them.
            """
            pass

        assert isinstance(resultArray, Gimp.ValueArray)
        FuResult.logger.info(f"resultArray is: {resultArray}")
        return resultArray
