This tests what GIMP does with Python packages
re plugin loading.

testPackage/
      __init__.py  (empty)
      foo.py       (contains plugin code)
      testPackage.py (contains plugin code)
      foo           (script with hashbang)
      readme.txt

Apparently, GIMP requires <foo>/<foo>.py

It won't find testPackage/foo even though foo is a Python script file.

It won't find testPackage/foo.py since
the directory name does not match the file name.

It does find testPackage/testPackage.py.

It ignores the __init__.py
