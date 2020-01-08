

import gi
gi.require_version("Gimp", "3.0")
from gi.repository import Gimp


class GimpfuPDB():
    '''
    Adaptor to Gimp.PDB
    GimpFu promises a symbol pdb that acts like the pdb, with attributes of Gimp.PDB.

    GimpFu creates one instance named "pdb"
    TODO enforce singleton, but GimpFu user doesn't even imagine this class exists.

    FBC
    Problems it solves:

    1) We can't just "pdb = Gimp.get_pdb()" at gimpfu import time
    because Gimp.main() hasn't been called yet
    (which would create the PDB instance and establish self type is GimpPlugin).
    Such code would bind "pdb" to None, forever, since that is the way import works.

    Alternatively, we could require a plugin's "func" to always first call pdb = Gimp.get_pdb().
    But that is new boilerplate for GimpFu authors, and not backward compatible.

    2) PyGimp v2 made an object for pdb some other way???? TODO
    '''

    '''
    Implementation:
    Adaptor pattern.
    Override special method __get_attribute__.

    OLD to return attribute of Gimp.PDB.
    In other words, forward attribute access to Gimp.PDB.
    (when attribute is a function, subsequent invocation is on Gimp.PDB )

    NEW Assume each get_attribute is immediately followed by a call.
    We don't check for callable().
    Each valid get_attribute() returns an interceptor func.
    The interceptor func marshalls arguments for a call to PDB.run_procedure()

    Some get_attributes ARE attributes on Gimp.PDB e.g. run_procedure().
    We let those pass through, with mangling of procedure name and args?

    Errors:

    Raise if cannot get a reference to Gimp.PDB
    (when this is called before Gimp.main() has been called.)

    No set attribute allowed.
    The PDB (known by alias "pdb") can only be called, it has no data members.
    But we don't warn, and the effect would be to add attributes to an instance of this class.
    '''

    def __init__ (self):
        self.adaptee = None

    # @classmethod
    def _adaptor(self, args):
        ''' run a PDB procedure whose name was used like "pdb.name()" e.g. like a method call of pdb object '''
        print ("adaptor called, args", args)
        # TODO marshall into Gimp.ValueArray
        Gimp.get_pdb().run_procedure( object.__getattribute__(self, "adapted_proc_name"), args )


    def  __getattribute__(self, name):
        # idiomatic avoid infinite recursion when accessing non-forwarded attributes of self
        # super is "object".  Alternatively: super().__getattribute__()
        # note adapteeValue is local
        adapteeValue = object.__getattribute__(self, "adaptee")
        if adapteeValue is None:
            # First call, cache empty
            adapteeValue = Gimp.get_pdb()
            # cache it
            self.adaptee = adapteeValue
            print("adapteeValue: ", adapteeValue)

        #  adapteeValue might still be None

        if adapteeValue is None:
            # TODO better error message
            # main() calls Gimp.main() to create PDB and establishes GimpFu type is GimpPlugin
            raise Exception("Gimpfu: pdb accessed before calling main()")
        else:
            # TODO leave some calls unadapted, direct to PDB

            mangledName = name.replace( '_' , '-')

            if Gimp.get_pdb().procedure_exists(mangledName):
                # todo return an adaptor function
                print("return adaptor")
                # remember state for soon-to-come call of _adaptor
                self.adapted_proc_name = mangledName
                return object.__getattribute__(self, "_adaptor")
            else:
                # TODO print name
                raise Exception("GimpFu: unknown pdb procedure")

            # will raise AttributeError for names that are not defined by GimpPDB
            return adapteeValue.__getattribute__(mangledName)
