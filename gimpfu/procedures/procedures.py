

"""
A container of GimpFuProcedures.

Local to GimpFu.  Gimp.Procedure's correspond, but are separate entities.

Very thin wrapper around dictionary.
Dictionary containing elements of type GimpFuProcedure keyed by procedure name.

Singleton to each session of GimpFu.
Used by gimpfu_top and FuRunner
"""


class FuProcedures:

    # class variable
    _local_registered_procedures = {}

    @classmethod
    def register(cls, procedure):
        # register under its possibly fixuped name, not the Author given name
        cls._local_registered_procedures[procedure.name] = procedure

    @classmethod
    def names(cls):
        return cls._local_registered_procedures.keys()

    @classmethod
    def get_by_name(cls, name):
        return cls._local_registered_procedures[name]
