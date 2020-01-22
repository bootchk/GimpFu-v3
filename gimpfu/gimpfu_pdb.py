

import gi
gi.require_version("Gimp", "3.0")
from gi.repository import Gimp
from gi.repository import GObject    # marshalling

from gimpfu_marshal import Marshal
from gimpfu_compatibility import Compat


class GimpfuPDB():
    '''
    Adaptor to Gimp.PDB
    GimpFu defines a symbol "pdb", an instance of this class.
    Its attributes appear to have similar names as procedures in the Gimp.PDB.

    GimpFu v2 also allowed access using index notation.
    Obsolete? not supported here yet.

    GimpFu creates one instance named "pdb"
    TODO enforce singleton, but GimpFu plugin author doesn't even imagine this class exists.

    FBC
    Problems it solves:

    1) We can't just "pdb = Gimp.get_pdb()" at gimpfu import time
    because Gimp.main() hasn't been called yet
    (which would create the PDB instance and establish self type is GimpPlugin).
    Such code would bind "pdb" to None, forever, since that is the way import works.
    Besides, the object returned by Gimp.get_pdb() is the PDB manager,
    not having a method for each procedure IN the PDB.

    Alternatively, we could require a plugin's "func" to always first call pdb = Gimp.get_pdb().
    But that is new boilerplate for GimpFu authors, and not backward compatible.

    2) PyGimp v2 made an object for pdb some other way???? TODO
    '''

    '''
    Implementation:

    See:
    1)"Adaptor pattern"
    2) Override "special method" __get_attribute__.
    3) "intercept method calls"
    4) "marshalling" args.

    An author's access (on right hand side) of an attribute of this class (instance "pdb")
    is adapted to run a procedure in the PDB.
    Requires all accesses to attributes of pdb are function calls (as opposed to get data member.)
    Each valid get_attribute() returns an interceptor func.
    The interceptor func marshalls arguments for a call to PDB.run_procedure()
    and returns result of run_procedure()

    ???Some get_attributes ARE attributes on Gimp.PDB e.g. run_procedure().
    We let those pass through, with mangling of procedure name and args?

    Notes:

    Since we override __getattribute__, use idiom to avoid infinite recursion:
    call super to access self attributes without recursively calling overridden __getattribute__.
    super is "object".  Alternatively: super().__getattribute__()

    Errors:

    Exception if cannot get a reference to PDB
    (when this is called before Gimp.main() has been called.)

    Exception if attribute name not a procedure of PDB

    No set attribute should be allowed, i.e. author use pdb on left hand side.
    The PDB (known by alias "pdb") can only be called, it has no data members.
    But we don't warn, and the effect would be to add attributes to an instance of this class.
    Or should we allow set attribute to mean "store a procedure"?
    '''



    def _marshall_args(self, proc_name, *args):
        '''
        1. Gather many args into Gimp.ValueArray and return it.

        2. Optionally prefix args with run mode
        GimpFu feature: hide run_mode from calling author

        3. Unwrap wrapped arguments so all args are GObjects

        4. Hacky upcast???

        5. float(args) as needed
        '''

        # TODO python-fu- ??
        if proc_name.startswith('plug-in-'):
            marshalled_args = Gimp.ValueArray.new(len(args)+1)
            marshalled_args.insert(0, Gimp.RunMode.NONINTERACTIVE)  # no GUI
            index = 1
        else:
            marshalled_args = Gimp.ValueArray.new(len(args))
            index = 0


        for x in args:
            ## GObject.Value(GObject.TYPE_STRING, tmp))
            ## print("marshall arg:", x )

            go_arg, go_arg_type = Marshal.unwrap_arg(x)

            # All args need conversion, don't assume any arg does NOT need conversion
            # A procedure definition can have float arg in anywhere in args
            go_arg, go_arg_type = Marshal.try_convert_to_float(proc_name, go_arg, go_arg_type, index)

            # !!! Can't assign GObject to python object: marshalled_arg = GObject.Value(Gimp.Image, x)
            # Must pass directly to insert()

            # ??? I don't understand why GObject.Value() doesn't determine the type of its second argument
            # unless GObject.Value() does some sort of casting

            marshalled_args.insert(index, GObject.Value(go_arg_type, go_arg))
            index += 1
        return marshalled_args


    def _adaptor_func(self, *args):
        ''' run a PDB procedure whose name was used like "pdb.name()" e.g. like a method call of pdb object '''
        print ("pdb adaptor called, args", args)
        # !!! Must unpack args before passing to _marshall_args
        # !!! avoid infinite recursion
        proc_name = object.__getattribute__(self, "adapted_proc_name")

        inner_result = Gimp.get_pdb().run_procedure( proc_name ,
                                     object.__getattribute__(self, "_marshall_args")(proc_name, *args) )

        # pdb is stateful for errors, i.e. gets error from last invoke, and resets on next invoke
        error_str = Gimp.get_pdb().get_last_error()
        if error_str != 'success':   # ??? GIMP_PDB_SUCCESS
            raise Exception(error_str)

        # TODO unmarshall result?
        # Low priority: all PDB calls have side_effects, but don't return objects?
        return inner_result




    def  __getattribute__(self, name):
        '''
        Adapts attribute access to become invocation of PDB procedure.

        Override of Python special method.
        The more common purpose of such override is to compute the attribute,
        or get it from an adaptee.
        '''

        '''
        Require that GimpFu plugin author previously called main()
        which calls Gimp.main() to create PDB and establish GimpFu type is GimpPlugin
        '''
        if Gimp.get_pdb() is None:
            raise Exception("Gimpfu: pdb accessed before calling main()")
        else:
            # TODO leave some calls unadapted, direct to PDB
            # ??? e.g. run_procedure ???, recursion ???

            '''
            Handle hyphens, and deprecated names.
            '''
            mangled_proc_name = Compat.make_compatible_proc_name(name)
            # OLD object.__getattribute__(self, "_make_compatible_proc_name")(name)

            if Gimp.get_pdb().procedure_exists(mangled_proc_name):
                print("return _adaptor_func for pdb.", mangled_proc_name)
                # remember state for soon-to-come call
                self.adapted_proc_name = mangled_proc_name
                # return intercept function soon to be called
                return object.__getattribute__(self, "_adaptor_func")
            else:
                exception_string = f"GimpFu: unknown pdb procedure {mangled_proc_name}"
                raise Exception( exception_string )

            # OLD
            # will raise AttributeError for names that are not defined by GimpPDB
            # return adapteeValue.__getattribute__(mangled_proc_name)