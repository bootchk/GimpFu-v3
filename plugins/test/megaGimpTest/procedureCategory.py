

from proceduresDB import ProceduresDB

class ProcedureCategory:
    """
    Knows procedure types and subcategories thereof.

    Unique "type" attribute in pdb.JSON
       "GIMP Extension",
       "GIMP Plug-In",
       "Internal GIMP procedure",
       "Temporary Procedure"
    """

    def isScriptFu(procName):
        return procName.find("script-fu-")==0

    def isPythonFu(procName):
        return procName.find("python-fu-")==0

    def isCPlugin(procName):
        return procName.find("plug-in-")==0

    def isTemporary(procName):
        # Note that all (?) of temporary procedures are omitted later anyway ???
        return ProceduresDB.typeof(procName) == "Temporary Procedure"



    def isPlugin(procName):
        # Relies on procedure canonical names
        # TODO test procedure type?
        # file-foo-save is a plug-in also
        # file-foo-load TODO
        return (procName.find("plug-in-")==0
            or ProcedureCategory.isScriptFu(procName)
            or ProcedureCategory.isPythonFu(procName)
            or ProcedureCategory.isCPlugin(procName)
            or (procName.find("file-")==0
               and procName.find("-save")>0)
            )

    def isDeleting(procName):
        """ We don't test procedures that might delete our test data. """
        return procName.find("-delete")>0

    def isLoadSave(procName):
        """ save/load tested in another plugin testGimpExportImport

        Typically name file-<foo>-save and -load"""
        if (procName.startswith('file')):
            return True
        return False
