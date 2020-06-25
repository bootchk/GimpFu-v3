
"""
Manages directories of files for testing

Uses system's tmp directory.
Knows where the sample directory is.

Hides those fact from rest of app.
"""

import os
import tempfile
from shutil import copyfile
import logging


class TestDir:

    # must first call create_scratch_temp_dir
    _test_dir = None
    logger = logging.getLogger("TestExportImport.TestDir")


    @classmethod
    def create_new_test_dir(cls):
        # Test dir will change name
        cls._test_dir = tempfile.TemporaryDirectory()
        cls.logger.info(f"Test directory is {cls.name()}")

    @classmethod
    def ensure_test_dir(cls):
        """ Ensure test dir exists, without cleaning. """
        if cls._test_dir is None:
            cls.create_new_test_dir()

    @classmethod
    def create_scratch_temp_dir(cls):
        """ Ensure test dir exists and is scratched (clean) """
        if cls._test_dir is not None:
            # cleanup previous
            cls._test_dir.cleanup()
        # Test dir will change name on every run
        cls.create_new_test_dir()


    @classmethod
    def sample_dir_name(cls):
        """ Name of directory without trailing / """
        # sample files are in dir "in" of the python module
        dir_path = os.path.dirname(os.path.realpath(__file__))
        result = os.path.join(dir_path, "in")
        # print(f"Sample dir: {result}")
        return result


    @classmethod
    def sample_dir(cls):
        directory_name = cls.sample_dir_name()
        directory = os.fsencode(directory_name)
        return directory

    @classmethod
    def sample_path_for_filename(cls, filename):
        # assert filename has extension for format
        result = os.path.join(cls.sample_dir_name(), filename)
        # result = cls.sample_dir_name + "/" + filename
        return result

    @classmethod
    def name(cls):
        """ Return name of test directory. """
        # Or /work/test
        return cls._test_dir.name

    @classmethod
    def test_filename_with_extension(cls, suffix):
        """ Return a path into test directory, str ending in /test.<suffix>

        All test files will be named like /tmp/234342/test.<foo>

        File need not exist yet.
        """
        assert not suffix.startswith('.')
        result = os.path.join(cls.name(), "test" + "." + suffix)
        # print(f"Test path: {result}")
        return result



    @classmethod
    def populate_sample_files(cls):
        """ Scratch the test directory and copy sample files to it.
        Sample file for each format that has no save procedure.
        Copy test/in/sample.<foo> to test/test.<foo>

        Files in test/in named sample.<foo> should have no save procedure.
        Alternatively, we could iterate over the format extensions having no save procedure.
        """
        cls.create_scratch_temp_dir()

        for file in os.listdir(cls.sample_dir()):
             filename = os.fsdecode(file)
             # filepath = os.fspath(file)
             if filename.startswith("sample."):
                 # platform independent path construction
                 # get extension, so we can add it to the copied file
                 extension = os.path.splitext(filename)[1]
                 # assert extension begins with a period
                 suffix = extension.lstrip('.')
                 sample_filepath = os.path.join(cls.sample_dir_name(), filename)
                 cls.logger.info(f"Sample file: {sample_filepath}")
                 copyfile(sample_filepath, cls.test_filename_with_extension(suffix))

        # Ensure a sample file
        filename = cls.test_filename_with_extension("svg")
        assert os.path.isfile(filename)
