
'''
GimpFu is an interpreter of a language.

The language includes statements (or phrases) from:
- Python language
- Gimp language
-   GI Gimp
-   PDB
- GimpFu (i.e. symbols and methods defined by GimpFu)

This module handles certain errors in interpretation
returned mostly at points of contact with Gimp.
Referred to as proceedErrors.
GimpFu can continue past proceedErrors,
so that more errors can be detected in one interpretation run.
ProceedErrors are in the nature of GimpFu API or Gimp API errors.

These are NOT ProceedErrors:
   - errors in Python syntax in the GimpFu author's code
   - severe GimpFu API errors (not calling register(), main())
These raise Python Exceptions that terminate the plugin.

The GimpFu code, when it discovers a proceedError() at a statement,
attempts to continue i.e. to proceed,
returning for example None for results of the erroneous statement.
Any following statements may generate spurious proceedErrors.

The results of a plugin (on the Gimp state, e.g. open image)
after a proceedError can be very garbled.
Usually Gimp announces this fact.
Any effects on existing images should still be undoable.

This behaviour is helpful when you are first developing a plugin.
Or porting a v2 plugin.

FUTURE this behaviour is configurable to raise an exception instead of proceeding.
'''



def proceedError(message):
    print(">>>>GimpFu continues past error:", message)
    print(">>>>The first error may cause more, spurious errors.")
