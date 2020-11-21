This tests what GIMP does with Python packages
re plugin loading.

testPackage/
      __init__.py  (empty)
      foo.py       (empty)
      testPackage.py (empty)
      foo           (script with hashbang)
      readme.txt

Apparently, GIMP requires foo/foo.py

It won't find foo/foo even though foo is a Python script file.

It won't find testPackage/foo.py since
the directory name does not match the file name.

It does find testPackage.py.

It ignores the __init__.py
