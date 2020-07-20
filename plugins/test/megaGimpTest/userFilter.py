

from procedureCategory import ProcedureCategory


class UserFilter:
    """ Understands user choice of tests """

    _shouldTestScriptFu = False
    _shouldTestPythonFu = False
    _shouldTestCPlugin = False
    _shouldTestExportImport = False
    _shouldTestTemporary = False
    _shouldTestOther = False

    def setChoices(shouldTestScriptFu,
                   shouldTestPythonFu,
                   shouldTestCPlugin,
                   shouldTestExportImport,
                   shouldTestTemporary,
                   shouldTestOther):
        UserFilter._shouldTestScriptFu = shouldTestScriptFu
        UserFilter._shouldTestPythonFu = shouldTestPythonFu
        UserFilter._shouldTestCPlugin = shouldTestCPlugin
        UserFilter._shouldTestExportImport = shouldTestExportImport
        UserFilter._shouldTestTemporary = shouldTestTemporary
        UserFilter._shouldTestOther = shouldTestOther

    """
    Divide tests into exclusive subsets.
    User chooses from among subsets.
    """
    def userWantsTest(procedure_name):
        result = True
        if   ProcedureCategory.isScriptFu(procedure_name):
            if not UserFilter._shouldTestScriptFu :
                result = False
        if   ProcedureCategory.isPythonFu(procedure_name):
            if not UserFilter._shouldTestPythonFu :
                result = False
        if   ProcedureCategory.isCPlugin(procedure_name):
            if not UserFilter._shouldTestCPlugin :
                result = False
        elif ProcedureCategory.isLoadSave(procedure_name):
            if not UserFilter._shouldTestExportImport :
                result = False
        elif ProcedureCategory.isTemporary(procedure_name):
            if not UserFilter._shouldTestTemporary :
                result = False
        else:
            """
            Other will be: Temporary and Internal and Extension
            and anything not named properly
            TODO allow choice of Temporary or Internal
            """
            if not UserFilter._shouldTestOther:
                result = False
        return result
