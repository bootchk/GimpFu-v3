
from adaption.compatibility import get_name_map_for_adaptee_class

from adapted_call_sequencer import AdaptedCallSequencer



class Adapter():
    '''
    Wrapper/Adapter pattern.

    This is Adapter component of the pattern.

    Adaptee is a Gimp object (usually some subclasses of Item e.g. Layer)

    Using the "object adapter" version of the pattern.
    Whereby Adapter owns an instance of Adaptee (composition.)

    see comments at adapters.image, somewhat similar re dynamic methods


    class adapter vs object adapter
       Object adapter: does not inherit Gimp.Image, but owns an instance of it
       Class adapter: multiple inheritance, e.g. GimpfuLayer inherits Gimp.Layer
          I don't know how to wrap Gimp.Layer using metaprogramming dynamically?
    '''

    def __init__(self, adaptee):
        self._adaptee = adaptee
        self._adaptee_callable = None


    def __eq__(self, other):
         '''
         Override equality.
         Two wrapper instances are equal if:
         - both wrappers of adaptee
         - AND their adaptee's are equal.

         Require self and other both Adapters, ow exception.
         I.E. not general purpose equality such as: Layer instance == int instance
         '''
         try:
             # Compare ID's or names instead?
             # Could use public unwrap() for more generality
             return self._adaptee == other.unwrap()
         except AttributeError:
             print("GimpFu can't compare types ", type(self), type(other))
             raise



    def unwrap(self):
        ''' Return inner object, of a Gimp type, used when passing args back to Gimp'''
        print("unwrap to", self._adaptee)
        return self._adaptee


    # TODO lots of cruft Here

    '''
    copy() was implemented in v2, but I am not sure it went through the __copy__ mechanism.
    Anyway, a  uses layer.copy().
    That invokes the copy() method, defined here.

     __copy__ is invoked by copy module i.e. copy.copy(foo)
    Any copy must be deep, to copy adaptee implemented by Gimp.
    To allow authors to use the copy module,
    we should override __copy__ and __deepcopy__ also.
    Such MUST call gimp to copy the adaptee.
    TODO

    See SO "How to override the copy/deepcopy operations for a Python object?"
    This is a hack of that answer code.
    '''

    # TODO just Marshal.wrap() ??? Would work if self has no attributes not computed from adaptee
    def copy(self):
        """
        OLD
        ''' Deep copy wrapper, with cloned adaptee'''
        cls = self.__class__
        result = cls.__new__(cls)
        result.__dict__.update(self.__dict__)

        '''
        clone _adaptee
        v2 called run_procedure()
        Here we use Gimp.Layer.copy() directly???
        '''
        adaptee_clone = self._adaptee.copy()
        setattr(result, "_adaptee", adaptee_clone)
        """
        from gimpfu_marshal import Marshal
        adaptee_clone = self._adaptee.copy()
        result =  Marshal.wrap(adaptee_clone)

        print("Copy: ", adaptee_clone, " into result ",  result)
        return result

    '''
    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memo))
        return result
    '''




    def _adaptor_func(self, *args):
        print("Adaptor._adaptor_func called, args:", *args)
        #

        # TODO marshal args

        # call the callable
        # Not sure why we need to use object.__...
        result = object.__getattribute__(self, "_adaptee_callable")(*args)

        AdaptedCallSequencer.end_call()

        # TODO marshal result
        return result



    # Methods and properties offered dynamically.
    # __getattr__ is only called for methods not found on self

    def __getattr__(self, name):
        '''
        Since name not found on self (i.e. not wrapped) return name found on adaptee.

        When name is callable: returns a callable.
        Which source code will soon call using "()" notation.

        When name is data member:
        Ordinary Python source would return value.
        !!! adaptee has no property semantics.
        So any source that attempts this ( "name" without "()" )
        is an error in the source code (in the GimpFu language.)

        !!! This does not preclude public,direct access to _adaptee, use unwrap()
        '''
        # assert _adaptee is a Gimp object (and a GObject)

        adapted_class_name = type(self.__dict__['_adaptee']).__name__
        name_map = get_name_map_for_adaptee_class(adapted_class_name)
        latest_name = name_map[name]
        # ensure latest_name == name OR latest_name has been adapted
        # KeyError means need add class_name to map_map in gimpfu_compatibility, etc.

        '''
        !!! Getting an object of type functionInfo ?? on the adaptee.
        If the author does not subsequently call it,
        it is probably an error, since the Gimp adaptee has no property attributes.
        We can't check here whether the result will be called.
        We can check later when passing args to Gimp: none should be of type functionInfo
        since Gimp rarely passes function pointers,
        especially not to the PDB.

        Possibly this could be a missing convenience function in GimpFu implementation,
        which DOES provide properties.
        Especially since GimpFu often provides convenience functions with the same symbol
        as the underlying callable on the adaptee.
        e.g. "foo = drawable.is_alpha"
        is_alpha is a callable on adaptee Drawable,
        but GimpFu provides convenience property "is_alpha"
        '''

        '''
        getattr() is builtin (not special method) that gets arg1's attribute named arg2
        Here arg1 is the adaptee.
        '''
        try:
            adaptee_callable = getattr(self.__dict__['_adaptee'], latest_name)
        except AttributeError:
            print("attribute error in Adapter.__getattr__, names:", name, latest_name)
            print("type(self)")
            print(type(self))
            print("self.__dir__")
            print(self.__dir__)
            print("dir(type(self))")
            print(dir(type(self)))
            print("dir(self)")
            print(dir(self))
            raise

        '''
        FUTURE catch AttributeError and mangle the name in a canonical way
        to get the Gimp name.
        That would not work for Python properties
        (say 'foo=img.filename' => 'foo.img.get_filename()')
        because the source phrase has no parens,
        and we can't turn this attribute access into a call??
        '''


        print("Adaptor.adaptee_callable:", adaptee_callable)

        # Not sure why we must use object, but fails otherwise
        object.__setattr__(self, "_adaptee_callable", adaptee_callable)

        # Record original name from author's source (in author's namespace), not latest_name (in Gimp namespace)
        # This throws if another call was started.
        AdaptedCallSequencer.start_call(name)

        '''
        We don't just return the callable,
        because we need to wrap the args,
        So return an interceptor func.
        '''
        return self._adaptor_func

        """
        OLD just return the callable
        print("__getattr__ result", result)
        return result
        """




    def __setattr__(self, name, value):
        # TODO Exception: Gimp has no properties that can be set without call syntax
        if name in ('_adaptee',):
            self.__dict__[name] = value
        else:
            setattr(self.__dict__['_adaptee'], name, value)

    def __delattr__(self, name):
        delattr(self.__dict__['_adaptee'], name)
