

import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp

from gi.repository import GLib  # For GLib.Error()
from gi.repository import GObject

from gimpfu.adaption.marshal import Marshal
from gimpfu.adaption.generic_value import FuGenericValue
from gimpfu.runner.resultArray import FuResultArray

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
    def lenActualResult(actual_result):
        """ Length of a Python instance that is None, a single item, or a sequence.
        A Python func can return a tuple.
        """
        # TODO this is wrong
        if actual_result is None:
            result = 1
        elif isinstance(actual_result, Iterable) and not isinstance(actual_result, str):
            result = len(actual_result)
        else :
            result = 1
        return result

    @staticmethod
    def doFormalAndActualResultsLenMatch(formalResultLength, actual_result):
        """
        Is the length of the result of the run_func OK?

        Note that a single result of None is wrong only when the procedure
        declared it would return more than one value.
        In Python, there is no concept of a procedure that returns no value whatsoever.
        A run_func returning None matches a PDB procedure returning no values.

        In Gimp, there is no general concept of a value that is not nullable.
        When None is a result, we do conversions to e.g. -1
        to indicate that a None was returned
        (where we can reasonably infer the value should be not nullable. )

        formalResultLength is-a unsigned int
        Subtract one for status in first element.
        """
        # TODO this is wrong
        return FuResult.lenActualResult(actual_result) == formalResultLength


    @staticmethod
    def setResultOfTypeIntoResults(result, formalType, results):
        """
        Set a result into a FuResultArray

        The result may be:
        - a primitive,
        - a wrapped Gimp type
        - a list of primitive (FloatArray)
        - a list of wrapped Gimp types (Gimp.ObjectArray)

        GimpFu allows result primitive to be a convertable type
        e.g. an int where a float is required.
        Try conversions here to achieve formalType if possible.
        """
        FuResult.logger.info(f"Required formal type of result: {formalType}")

        unwrappedResult = Marshal.unwrap(result)
        FuResult.logger.info(f"result of type: {type(unwrappedResult)}")

        # Use our GValue wrapper to do conversions of unwrapped result
        tempGValue = FuGenericValue(unwrappedResult, type(unwrappedResult))
        tempGValue.tryConversionsAndUpcasts(formalType)

        finalValue = tempGValue.get_gvalue()
        FuResult.logger.info(f"final value {finalValue}")

        """
        OLD
        destValue = results.index(targetIndex)
        print(type(destValue))
        assert isinstance(destValue, GObject.Value)
        # Copy converted value from our GValue into destination GValue in result
        finalValue.copy(destValue)
        """
        results.append(finalValue)


    """
    Notes on new_return_values()

    Returns a Gimp.ValueArray,
    which is-a array of GObject.Value (aka GValue in C aka "generic value")
    Length is count of procedure's registered return values plus one for status.
    First item is a status (type Gimp.PDBStatusType)
    Any other items are GObject.Value
    - whose value is Nones, until we set them,
    - whose type is the type the procedure registered
      (a GObject.Value knows its own type.)
    See GIR docs for Gimp:
    - section: Structs, item: Gimp.ValueArray
    - section: Classes, item: Gimp.Procedure
    """

    @staticmethod
    def makeSuccess(procedure, runfuncResult=None):
        """
        Make a result for a PDB procedure, as described above

        Require runfuncResult is some Python object, or None

        status == SUCCESS not imply runfuncResult is not None:
        Since this is Python, the run_func for a PDB procedure declared returning void
        returns result==None.

        Check for wrong count of results from runfunc.
        Check runfunc actual result types match declared formal types,
        after trying to convert/upcast.
        """
        assert isinstance(procedure, Gimp.Procedure) # !!! Not our GimpProcedure wrapper
        FuResult.logger.info(f"procedure: {procedure.get_name()}, runfuncResult is: {runfuncResult}")
        # FuResult.logger.info(f"result length: {resultArray.length()}")

        # Get formal specs
        resultSpecs = procedure.get_return_values()
        """
        assert resultSpecs is-a list of GParamSpec.
        assert len(resultSpecs) == len(runfuncResult)
        """
        formalLength = len(resultSpecs)
        FuResult.logger.info(f"length formal results is: {formalLength}")

        if not FuResult.doFormalAndActualResultsLenMatch(formalLength, runfuncResult):
            return FuResult.makeWrongLengthReturned(procedure)

        """
        OLD
        # No need to make a GLib.Error when SUCCESS
        # Not:  error = FuResult.makeGLibError(Gimp.PDBStatusType.SUCCESS)
        resultArray = procedure.new_return_values(Gimp.PDBStatusType.SUCCESS)
        FuResult.logger.info(f"out result length: {resultArray.length()}")
        """
        resultArray = FuResultArray(formalLength)

        # Gimp.ValueArray.index is broken and returns the GValue.value, not the GValue

        # TODO a single result that is a list should be nested like ((1)) ???
        # We must contain the result before this so we know it is always a sequence

        if formalLength == 0:
            # procedure declared returning void
            # assert we already checked that actual result was None
            # ensure status is set to "SUCCESS"
            return resultArray

        # Put actual results into resultArray

        # TODO ensure runFuncResult is an iterable, always iterate
        length = FuResult.lenActualResult(runfuncResult)
        if length > 0:
            index = 0
            for item in runfuncResult:
                formalType = resultSpecs[index].value_type
                FuResult.setResultOfTypeIntoResults(item, formalType, resultArray)
                index += 1
        else:
            # runfuncResult is elementary, not iterable
            # TODO it could still be a list, where formal result type is array?
            formalType = resultSpecs[0].value_type
            FuResult.setResultOfTypeIntoResults(runfuncResult, formalType, resultArray)

        # This log conveys little info
        #FuResult.logger.info(f"resultArray is: {resultArray}")
        return resultArray.getWrappedValueArray()




    @staticmethod
    def makeBad(procedure, status, message) :
        """
        Make return values for "not success".

        status is type Gimp.PDBStatusType
        message is a string
        """
        error = FuResult.makeGLibError(status, message)
        resultArray = procedure.new_return_values(Gimp.PDBStatusType.EXECUTION_ERROR, error)
        # ensure resultArray is-a Gimp.ValueArray whose first element is a GLib.Error??
        # ensure length of resultArray is length the procedure formal declared ???
        return resultArray


    # Convenience methods on makeBad

    @staticmethod
    def makeException(procedure, err_message) :
        return FuResult.makeBad(procedure, Gimp.PDBStatusType.EXECUTION_ERROR, err_message)

    @staticmethod
    def makeCancel(procedure) :
        return FuResult.makeBad(procedure, Gimp.PDBStatusType.CANCEL, "User canceled.")

    @staticmethod
    def makeWrongLengthReturned(procedure) :
        return FuResult.makeBad(procedure, Gimp.PDBStatusType.EXECUTION_ERROR,
            "Runfunc returned wrong count of results.")
