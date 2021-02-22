Each file defines a Python class that adapts a corresponding Gimp class.

One-to-one.
They have the same class hierarchy as Gimp classes.
They all have super class Adapter.

Possibly there could be a abstract base class for all.
For now, comments are scattered around the classes.

Code near the top is similar (since they all inherit Adapter.)
E.G. it defines the adapted properties of the class.

Code near the bottom is specialized.
Mostly FBC.
E.G. define methods that GimpFu v2 defined that are not in Gimp itself.

Process to add an adapter:
  copy an <adapter>.py
  modify it:
    change name
    change properties according to GimpFu v2 documents
    change the new method according to GimpFu v3 documents

  import it into adatption/marshal.py
