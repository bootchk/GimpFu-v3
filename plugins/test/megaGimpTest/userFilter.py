

from megaGimpTestUtils import *


class UserFilter:
    """ Understands user choice of tests """

    _shouldTestScriptFu = False
    _shouldTestExportImport = False
    _shouldTestOther = False

    def setChoices(shouldTestScriptFu, shouldTestExportImport, shouldTestOther):
        UserFilter._shouldTestScriptFu = shouldTestScriptFu
        UserFilter._shouldTestExportImport = shouldTestExportImport
        UserFilter._shouldTestOther = shouldTestOther

    """
    Divide tests into exclusive subsets.
    User chooses from among subsets.
    """
    def userWantsTest(procedure_name):
        result = True
        if   isScriptFu(procedure_name):
            if not UserFilter._shouldTestScriptFu :
                result = False
        elif isLoadSave(procedure_name):
            if not UserFilter._shouldTestExportImport :
                result = False
        else:
            if not UserFilter._shouldTestOther:
                result = False
        return result
