
"""
Manages directories of files for testing

Uses system's tmp directory.
Knows where the sample directory is.

Hides those fact from rest of app.
"""

import os
import tempfile
from shutil import copyfile


class TestDir:

    # must first call create_scratch_temp_dir
    _test_dir = None

    @classmethod
    def create_scratch_temp_dir(cls):
        if cls._test_dir is not None:
            # cleanup previous
            cls._test_dir.cleanup()
        # Test dir will change name on every run
        cls._test_dir = tempfile.TemporaryDirectory()
        print(f"Test directory is {cls.name()}")

    @classmethod
    def sample_dir_name(cls):
        """ Name of directory without trailing / """
        # TODO from Python pwd ???
        return "/work/test/in"

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
        """ Return a path into test directory, str ending in /test

        All test files will be named like /tmp/234342/test.<foo>

        File should not exist yet.
        """
        result = os.path.join(cls.name(), "test" + "." + suffix)
        # result = "/work/test/test"
        print(f"Test path: {result}")
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
                 # TODO platform independent path construction
                 # get the extension, so we can add it to the copied file
                 extension = os.path.splitext(filename)[1]
                 # print(directory_name, filename, root_and_extension[1])
                 sample_filepath = cls.sample_dir_name() + "/" + filename
                 copyfile(sample_filepath, cls.test_filename_with_extension(extension))
