"""
Utilities for plugin megaTestGimp

"""
from procedureCategory import ProcedureCategory



def shouldTestProcedure(procName):
    """ Decides to NOT test certain procedures.

    Generally, any that prevent lights-out testing.
    Reasons:
    - infinite recursion
    - quitting
    - interactive, open windows and hang test waiting on user Input
    - delete test objects (they should be run last)
    """

    if ProcedureCategory.isDeleting(procName):
        return False

    # We will test load/save if user requests it.
    # But better to use plugin testGimpExportImport
    # OLD if isLoadSave(procName):
    #    return False

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

    Others are known bad actors, usually they hang or take too long.
    """
    if procName in (
       # TODO why are these excluded?
       "plug-in-animationplay",
       "python-fu-console",
       # ??? These are opening windows despite run mode NONINTERACTIVE ???
       # TODO explore whether that is a bug
       "plug-in-script-fu-console",
       "plug-in-script-fu-text-console",
       "plug-in-unit-editor",
       "plug-in-screenshot",
       "plug-in-metadata-viewer",
       # Hang, with many Gtk errors
       "plug-in-metadata-editor",
       "plug-in-plug-in-details",
       # Hang, without error messages
       "script-fu-ripply-anim",
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
       # Spawn a browser, which could be tested, does not stop test.
       # This one takes a URL parameter, but also throws missing run-mode
       # since we pass runmode to every 'plug-in-'
       "plug-in-web-browser",
       # Bookmarks.  Authors Henrik Brix Andersen or Roman Joost or A. Prokoudine
       # These all use plug-in-web-browser, and Gimp throws "operation not supported"
       # meaning they cannot be called procedurally
       "gimp-online-main-web-site",
       "gimp-online-docs-web-site",
       "gimp-online-developer-web-site",
       "gimp-online-wiki",
       "gimp-online-bugs-features",
       "gimp-online-roadmap",
       # gimp-web
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
