
import gi
gi.require_version("Gimp", "3.0")
from gi.repository import Gimp

from gimppdb.gimpprocedure import GimpProcedure


import logging




class GimpPDB:
    """ Thin wrapper around the Gimp PDB.

    For introspection of the PDB.

    !!! Distinct from GimpfuPDB.
    This is not an Adapter, an Author does not use this,
    only the GimpFu implementation uses it.
    See aliases/pdb for the adapter used by Authors, see class GimpfuPDB
    """

    logger = logging.getLogger("GimpFu.GimpPDB")

    def get_procedure_by_name(proc_name):
        """ Returns Gimp.Procedure for procname, else None.

        The returned type is GimpProcedure, a GimpFu type,
        not Gimp.Procedure, a Gimp type.
        """
        result = Gimp.get_pdb().lookup_procedure(proc_name)
        if result is not None:
            # wrap
            result = GimpProcedure(result)
        GimpPDB.logger.info(f"get_procedure_by_name returns {result}")
        return result
