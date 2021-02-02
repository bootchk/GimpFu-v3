

import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp

# For GLib.Error()
# ??? Require 2.32 for GArray instead of GValueArray
from gi.repository import GLib

from adaption.marshal import Marshal
from adaption.generic_value import FuGenericValue

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
    def do_formal_and_actual_results_len_match(formal_result, actual_result):
        """
        formal_result is-a Gimp.ValueArray
        Subtract one for status in first element.
        """
        return FuResult.len_actual_result(actual_result) == formal_result.length() - 1


    @staticmethod
    def insertResultOfTypeIntoResultsAt(result, formalType, results, targetIndex):
        """
        Insert an elementary result into a resultArray

        Note resultArray is a Gimp.ValueArray, whose convenience methods
        are only for the values, not for GValues!!!
        This is not correct:
           gvalue = resultArray.index(targetIndex)   does not return a GValue
           gvalue.set_value(item)
        There is no method resultArray.get_type(index)

        The result may be:
        - a primitive,
        - a wrapped Gimp type
        - a list of primitive (FloatArray)
        - a list of wrapped Gimp types (Gimp.ObjectArray)
        GimpFu also allows result primitive to be a convertable type
        e.g. an int where a float is required.
        """
        FuResult.logger.info(f"Required formal type of result: {formalType}")

        unwrappedResult = Marshal.unwrap(result)
        FuResult.logger.info(f"result {targetIndex} of type: {type(unwrappedResult)}")

        # Use our GValue wrapper to do conversions of unwrapped result
        tempGValue = FuGenericValue(unwrappedResult, type(unwrappedResult))
        tempGValue.tryConversionsAndUpcasts(formalType)

        # FuGenericValue owns a Gobject.Value
        # Insert that into the resultArray.
        # resultArray is a Gimp.ValueArray of Gimp.Value.
        # Its not clear whether the resultArray already holds a Gimp.Value
        # nor whether the insert() will fail if the types don't match.
        finalValue = tempGValue.get_gvalue()
        FuResult.logger.info(f"insert final value {finalValue}")
        results.insert(targetIndex, finalValue)


    @staticmethod
    def makeSuccess(procedure, runfuncResult=None):
        """
        Make a result for a PDB procedure, i.e. a GimpValueArray:
        - whose first element is a PDB_STATUS
        - and whose other elements have types matching registered return value types

        Require runfuncResult is some Python object, or None

        status == SUCCESS not imply runfuncResult is not None:
        a procedure returning void returns result==None.
        """
        assert isinstance(procedure, Gimp.Procedure) # !!! Not our GimpProcedure wrapper

        # No GLib.Error when SUCCESS
        # error = FuResult.makeGLibError(Gimp.PDBStatusType.SUCCESS)
        resultArray = procedure.new_return_values(Gimp.PDBStatusType.SUCCESS)
        """
        assert resultArray is-a Gimp.ValueArray, which is NOT a GArray of GValue.
        Length is count of procedure's registered return values plus one for status.
        First item is a status with value taken from error which is type GLib.Error
        Any other items are have None values, until we set them.
        """
        #FuResult.logger.info(f"resultArray is: {resultArray}")
        assert isinstance(resultArray, Gimp.ValueArray)
        #FuResult.logger.info(f"resultArray[0] is: {resultArray.index(0)}")
        assert isinstance(resultArray.index(0), Gimp.PDBStatusType)

        resultSpecs = procedure.get_return_values()
        """
        assert resultSpecs is-a list of GParamSpec.
        assert len(resultSpecs) == len(runfuncResult)
        """

        # see GIR docs for Gimp, section: Structs, item: Gimp.ValueArray
        FuResult.logger.info(f"result length: {resultArray.length()}")

        if not FuResult.do_formal_and_actual_results_len_match(resultArray, runfuncResult):
            FuResult.logger.warning(f"run func returned wrong count of results")
            # TODO make an Exception result rather than return mixed results

            # TODO preflight the procedure formal OUT args versus author's run func return
            # Will Python tell us the types of a callable's results?

        FuResult.logger.info(f"runfuncResult is: {runfuncResult}")

        # TODO a result that is a list should be nested like ((1)) ???
        length = FuResult.len_actual_result(runfuncResult)
        if length >= 1:
            targetIndex = 1  # Start past the status item

            if length >1:
                for item in runfuncResult:
                    formalType = resultSpecs[targetIndex-1].value_type
                    FuResult.insertResultOfTypeIntoResultsAt(item, formalType, resultArray, targetIndex)
                    targetIndex += 1
            else:
                # runfuncResult is elementary, not iterable
                # TODO it could still be a list, where formal result type is array?
                formalType = resultSpecs[0]
                FuResult.insertResultOfTypeIntoResultsAt(runfuncResult, formalType, resultArray, targetIndex, )
        # else void result (except for PDB status)

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
