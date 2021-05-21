"""
Test a procedure that takes StringArray

Plugin has no GUI.  GimpFu does not yet implement a widget for entering many strings.
"""

from gimpfu import *

def called_plugin_func(image, drawable, strings):

    for string in strings:
        print(f"String is: {string}")

def calling_plugin_func(image, drawable):

    # PyGObject will convert list of strings to GStrv
    pdb.python_fu_test_take_string_array(image, drawable, ["foo", "bar"])


# takes a string array
register(
      "python-fu-test-take-string-array",
      "blurb",
      "help message",
      "author",
      "copyright",
      "year",
      "",   # No menu item
      "*",
      [
          (PF_IMAGE, "image", "Input image", None),
          (PF_DRAWABLE, "drawable", "Input drawable", None),
          (PF_STRINGARRAY, "strings", "A sequence of strings", None),
      ],
      [],
      called_plugin_func,
      menu="<Image>/Test")

# calls a proc that takes a string array
register(
      "python-fu-test-call-with-string-array",
      "blurb",
      "help message",
      "author",
      "copyright",
      "year",
      "Call PDB proc that takes string array...",
      "*",
      [
          (PF_IMAGE, "image", "Input image", None),
          (PF_DRAWABLE, "drawable", "Input drawable", None),
      ],
      [],
      calling_plugin_func,
      menu="<Image>/Test")
main()
