This directory is about a Author's
declarations and definitions of PDB procedures *in GimpFu*.
That is, what the author's code declares in run_func() and in register().
GimpFu in turn declares into the PDB.
IOW, this is an abstraction or wrapper of the
declarations that the PDB holds.
The classes here are about the current procedure(s) being defined and declared,
by the Author, in the current Python source file that GimpFu is processing.

For example, the class FuProcedureMetadata
knows the metadata for a FuProcedure
but *does not ask the PDB for it*.
Instead, it *conveys* the metadata to the PDB.

Another example.
File procedure/procedure.py defines class FuProcedure.
Not the same as class GimpProcedure defined in gimppdb/gimprocedure.py.
Not the same as the class Gimp.Procedure defined by C code in GIMP.
