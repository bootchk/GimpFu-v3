

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
    def makeGLibError(status, message=""):
        """
        Make a GLib error.
        It carries more information into a result?
        Gimp.Procedure.new_return_values() takes one.
        """
        FuResult.logger.info(f"makeGLibError for status: {status}")
        if status == Gimp.PDBStatusType.SUCCESS:
            # ??? creates an empty but valid GLib.Error ????
            result = GLib.Error()
        else:
            # Seems wierd that a "literal" is a Glib.Error
            quark = GLib.quark_from_string("GimpFu")
            result = GLib.Error.new_literal( quark, message, 0 )
        assert isinstance(result, GLib.Error)
        # a GLib.Error seems to have a good repr() method
        # i.e. prints a tuple (domain string, message string, code numeric )
        FuResult.logger.info(f"makeGLibError result: {result}")
        return result


    @staticmethod
    def len_actual_result(actual_result):
        """ Length of a Python instance that is None, a single item, or a sequence. """
        if actual_result is None:
            result = 0
        elif isinstance(actual_result, Iterable) and not isinstance(actual_result, str):
            result = len(actual_result)
        else :
            result = 1
        return result

    @staticmethod
    def do_formal_and_actual_results_match(formal_result, actual_result):
        """
        formal_result is-a Gimp.ValueArray
        Subtract one for status in first element.
        """
        return FuResult.len_actual_result(actual_result) == formal_result.length() - 1



    @staticmethod
    def makeSuccess(procedure, runfunc_result=None):
        """
        Make a result for a PDB procedure, i.e. a GimpValueArray:
        - whose first element is a PDB_STATUS
        - and whose other elements have types matching registered return value types

        Require runfunc_result is some Python object, or None

        status == SUCCESS not imply runfunc_result is not None:
        a procedure returning void returns result==None.
        """


        # No GLib.Error when SUCCESS
        # error = FuResult.makeGLibError(Gimp.PDBStatusType.SUCCESS)
        resultArray = procedure.new_return_values(Gimp.PDBStatusType.SUCCESS)
        """
        assert resultArray is-a GValueArray (GimpValueArray?).
        Length is count of procedure's registered return values plus one for status.
        First item is a status with value taken from error which is type GLib.Error
        Any other items are arbitrary or default values, until we set them.
        """
        #FuResult.logger.info(f"resultArray is: {resultArray}")
        assert isinstance(resultArray, Gimp.ValueArray)
        #FuResult.logger.info(f"resultArray[0] is: {resultArray.index(0)}")
        assert isinstance(resultArray.index(0), Gimp.PDBStatusType)

        # see GIR docs for Gimp, section: Structs, item: Gimp.ValueArray
        FuResult.logger.info(f"result length: {resultArray.length()}")

        if not FuResult.do_formal_and_actual_results_match(resultArray, runfunc_result):
            FuResult.logger.warning(f"run func returned wrong count or type of results")
            # TODO make an Exception result rather than return mixed results
            # TODO preflight the procedure formal args versus run func args

        FuResult.logger.info(f"runfunc_result is: {runfunc_result}")
        length = FuResult.len_actual_result(runfunc_result)
        if length >= 1:
            targetItem = 1  # Start past the status item

            if length >1:
                for item in runfunc_result:
                    resultArray.insert(targetItem, item)
                    targetItem += 1
            else:
                # runfunc_result is elementary, not iterable
                resultArray.insert(targetItem, runfunc_result)
                # Note this is not correct:
                #gvalue = resultArray.index(targetItem)
                #gvalue.set_value(item)

        assert isinstance(resultArray, Gimp.ValueArray)
        # This log conveys little info
        #FuResult.logger.info(f"resultArray is: {resultArray}")
        return resultArray


    @staticmethod
    def makeException(procedure, err_message) :
        error = FuResult.makeGLibError(Gimp.PDBStatusType.EXECUTION_ERROR, err_message)
        resultArray = procedure.new_return_values(Gimp.PDBStatusType.EXECUTION_ERROR, error)
        return resultArray

    @staticmethod
    def makeCancel(procedure) :
        pdbStatus = Gimp.PDBStatusType.CANCEL
        error = FuResult.makeGLibError(pdbStatus, "User canceled.")
        resultArray = procedure.new_return_values(pdbStatus, error)
        return resultArray
