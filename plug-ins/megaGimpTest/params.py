

from testLog import TestLog




"""
functions to generate paramstrings for PDB procedures

param strings will be eval'ed
"""


def appendParameter(paramString, parameter):
    # trailing comma will be OK to Python
    result = paramString + parameter + ','
    return result


def generateQuotedIntegerLiteral():
    """ Choose an integer with certain testing goals e.g. stress test or not.

    0 is out of range for many tested procedures
    1 tests the least
    """
    return '1'


def generateParamString(procName, inParamList,  image, drawable):
    # TODO why GParam and GimpParam ??
    result = "("
    for aType in inParamList:
        if aType == "GimpParamString" or aType == "GParamString" :
            # often the name of an item
            result = appendParameter(result, '"foo"')
        elif aType == "GParamInt" :
            result = appendParameter(result, generateQuotedIntegerLiteral())
        elif aType == "GParamUInt" :
            # TODO this does not suffice.  Change gimpfu to cast to GParamUint
            result = appendParameter(result, generateQuotedIntegerLiteral())
        elif aType == "GParamUChar" :
            # GParamUChar usually used as an int-valued enum, often True/False
            # TODO this does not suffice.  Change gimpfu to cast to GParamUint
            result = appendParameter(result, generateQuotedIntegerLiteral())
        elif aType == "GParamDouble" :
            result = appendParameter(result, '1.0003')
        elif aType == "GParamBoolean" :
            # bool is int ??
            result = appendParameter(result, generateQuotedIntegerLiteral())
        elif aType == "GimpParamItem" :
            # Item is superclass of Drawable, etc.
            # Use a convenient one
            result = appendParameter(result, 'drawable')
        elif aType == "GParamEnum" or aType == "GimpParamEnum" :
            # enums are ints
            result = appendParameter(result, generateQuotedIntegerLiteral())
        elif aType == "GimpParamImage" :
            # reference a symbol in Python context at time of eval
            result = appendParameter(result, 'image')
        elif aType == "GimpParamDrawable" :
            # reference a symbol in Python context at time of eval
            result = appendParameter(result, 'drawable')
        elif aType == "GimpParamLayer" :
            # reference a symbol in Python context at time of eval
            # assert drawable is-a Layer
            result = appendParameter(result, 'drawable')
        elif aType == "GimpParamRGB" :
            # a 3-tuple suffices
            result = appendParameter(result, '(12, 13, 14)')
        elif aType == "GimpParamFloatArray" :
            # a 4-tuple often suffices
            result = appendParameter(result, '(1.0, 1.0, 5.0, 5.0)')

        # TODO more types
        # TODO GimpParamParasite
        # GimpParamUInt8Array
        # GimpParamChannel
        # GParamObject usually a file
        # GimpParamUnit
        # GimpParamVectors
        # GParamUChar
        else:
            # some type we don't handle, abandon
            TestLog.say(f"unhandled type {aType} for {procName}")
            return ""

    result = result + ')'
    return result
