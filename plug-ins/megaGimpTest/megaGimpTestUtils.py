"""
Utilities for plugin megaTestGimp
"""

def isPlugin(procName):
    # Relies on procedure canonical names
    return (procName.find("plug-in-")==0
        or procName.find("script-fu-")==0
        or procName.find("python-fu-")==0
        )



def shouldTestProcedure(procName):
    """ Decides to NOT test certain procedures. """
    # Plugins already excluded
    # Those that are interactive, open windows and hang test waiting on user Input

    # !!! Not test self, infinite recursion
    if procName in ("python-fu-mega-test-gimp"):
        return False

    # !!! If we quit, testing stops
    if procName in ("gimp-quit"):
        return False

    # !!! This opens a dialog that locks GUI
    if procName in ("plug-in-busy-dialog"):
        return False

    """
    Special cases.
    Some open windows, impeding lights-out testing.
    We *can* test them interactively, optionally.  TODO

    Others are known bad actors.
    """
    if procName in (
       "plug-in-animationplay",
       "python-fu-console",
       # ??? These are opening windows despite run mode NONINTERACTIVE ???
       # TODO explore whether that is a bug
       "plug-in-script-fu-console",
       "plug-in-script-fu-text-console",
       "plug-in-unit-editor",
       "plug-in-screenshot",
       "plug-in-metadata-viewer",
       # Known bad actors?  Seems to lock the test, with many Gtk errors
       "plug-in-metadata-editor",
       "plug-in-plug-in-details",
       # ??
       "extension-script-fu",
       #
       "goat-exercise-lua",
       "goat-exercise-python",
       # temporary procedures, author Itkin
       "gimp-palette-export-text",
       "gimp-palette-export-css",
       "gimp-palette-export-java",
       "gimp-palette-export-php",
       "gimp-palette-export-python",
       #
       "file-print-gtk",
       # help, author ???
       "gimp-help-using-web",
       "gimp-help-using-photography",
       "gimp-help-concepts-usage",
       "gimp-help-using-selections",
       "gimp-help-concepts-paths",
       "gimp-help-using-simpleobjects",
       "gimp-help-using-fileformats",
       "gimp-help-using-docks",
        ):
        result = False
    else:
        result = True
    return result

# Not used?
def printPDBError(testStmt):
    """
    megaGimpTest is-a GimpFu plugin, so pdb is defined,
    but get_last_error() is not *in* the PDB, only a method of the pdb.
    Hence we call Gimp.get_pdb().

    PDB is stateful on errors so we can get the last error until we call the next PDB procedure.

    error_str = Gimp.get_pdb().get_last_error()
    print(f"Error string from pdb procedure execution: {error_str}")
    if error_str != 'success':
    """

    """
    GimpFu continues past exceptions on PDB procedures.
    also has already printed an error like "Error: Gimp PDB execution error: <foo>"
    But that mechanism doesn't print the stmt.
    """
    print(f"Error executing {testStmt}")
