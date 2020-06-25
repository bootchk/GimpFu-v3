


class AllTestResult(dict):
    """
    Records a test result for a set of formats.

    Used for:
    - a reference, good result
    - result of test instances at a particular time, condition of Gimp
    Then comparing two for equality yields  an overall result for "test all formats"

    A dictionary:
    keyed by format_moniker
    value is a tuple (saver_result, loader_result)

    Each saver/loader result in ("Pass", "Fail", "NoTest", "Omit")
    NoTest means did not test:
      save: because no save procedure exists or file already exists
      load: because save procedure failed or (no save procedure and no sample file)
    """

    def __init__(self):
        super().__init__(self)




from image_format import ImageFormat

class KnownGoodAllTestResult:
    """
    Known good results, by format and for "test all"

    Assumes correct setup: test directory emptied.
    """

    def _create_known_good_all_test_result():
        """ The known good result depends on unique starting condition: empty test directory. """

        result = AllTestResult()

        for format_moniker in ImageFormat.all_format_monikers:
            if ImageFormat.excludeFromTests(format_moniker):
                result[format_moniker] = ("Omit", "Omit")
            else:
                if format_moniker in ImageFormat.no_saver_formats:
                    result[format_moniker] = ("NoTest", "Pass")
                elif format_moniker in ImageFormat.no_loader_formats:
                    result[format_moniker] = ("Pass", "NoTest")
                else:
                    result[format_moniker] = ("Pass", "Pass")

        return result

    # class variable
    # the gold standard for "test all"
    # must follow definition of _create method
    known_good_all_test_result = _create_known_good_all_test_result()

    def expected_result(format_moniker):
        """ Ideal test result for an individual format when setup is correct and Gimp is working. """
        # print(KnownGoodAllTestResult.known_good_all_test_result)
        return KnownGoodAllTestResult.known_good_all_test_result[format_moniker]
