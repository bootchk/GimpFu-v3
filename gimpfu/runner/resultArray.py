import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp

from gi.repository import GObject


class FuResultArray():
    """
    An array of results for a plugin (a PDB procedure).

    Thin wrapper on Gimp.ValueArray
    specialized for results.
    Special: the first element is a status.

    This works around the issue that Gimp.ValueArray.index
    returns the value field instead of a GObject.Value.

    Strategy here is to append.
    """

    def __init__(self, preAllocedLength):
        ''' Initialize a wrapped Gimp.ValueArray with a success status. '''
        self._array = Gimp.ValueArray.new(preAllocedLength+1)
        # assert length is zero, but allocated for status and return values
        assert self._array.length() == 0

        self._array.append(GObject.Value(Gimp.PDBStatusType, Gimp.PDBStatusType.SUCCESS))

    def append(self, gvalue):
        """ Append given gvalue into self.

        In Python, you can (but usually should not) still use the gvalue.
        When you change it, it will change the one in self._array.

        !!! We don't use GObject.Value.copy() because it only copies the value field
        (not the type field.)
        """
        self._array.append(gvalue)
        # ensure length has increased

    def getWrappedValueArray(self):
        return self._array
