
import gi
gi.require_version("Gimp", "3.0")
from gi.repository import Gimp


class GimpPDB:
    """ Thin wrapper around the Gimp PDB.

    !!! Distinct from GimpfuPDB.
    This is not an adapter, an Author does not use this,
    only the GimpFu implementation uses it.
    See aliases/pdb for the adapter used by Authors, see class GimpfuPDB
    """

    def get_procedure_by_name(proc_name):
        """ Returns Gimp.Procedure for procname, else None. """
        return Gimp.get_pdb().lookup_procedure(proc_name)


# Gimp.procedure
