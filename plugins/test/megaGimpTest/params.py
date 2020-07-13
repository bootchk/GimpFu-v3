

from testLog import TestLog
from stats import TestStats



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
            # a 3-tuple suffices, GimpFu marshals to a Gimp.RGB
            result = appendParameter(result, '(12, 13, 14)')
        elif aType == "GimpParamFloatArray" :
            # a 4-tuple often suffices
            # TODO  prefixed with len ?? result = appendParameter(result, '4, (1.0, 1.0, 5.0, 5.0)')
            result = appendParameter(result, '(1.0, 1.0, 5.0, 5.0)')
        elif aType == "GimpParamVectors" :
            # refer to test harness object
            result = appendParameter(result, 'fooVectors')
        elif aType == "GParamObject" :
            # Usually a GFile
            # refer to test harness object
            result = appendParameter(result, 'fooFile')
        elif aType == "GimpParamObjectArray" :
            """
            Usually an array of Gimp.Drawable.
            The signature of many procedures changed in 3.0 to take: n_drawables, drawables
            Refer to "drawable", since GimpFu will convert to GimpParamDrawableArray automatically.
            However, this depends on the int for n_drawables being 1.
            """
            result = appendParameter(result, 'drawable')

        # TODO more types
        # GimpParamParasite
        # GimpParamUInt8Array 10
        # GimpParamChannel 12
        # GimpParamUnit 13
        # GimpParamVectors 23
        # GimpParamDisplay 2
        # GimpParamStringArray
        else:
            # some type we don't handle, omit test
            TestStats.sample("omit for param type")
            TestStats.sample(f"omit for param type: {aType}")

            TestLog.say(f"unhandled type {aType} for {procName}")
            return ""

    result = result + ')'
    return result
