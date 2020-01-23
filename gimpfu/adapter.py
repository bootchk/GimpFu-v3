
from gimpfu_compatibility import image_name_map





class Adapter():
    '''
    Wrapper/Adapter pattern.

    This is Adapter component of the pattern.

    Adaptee is a Gimp object (usually some subclasses of Item e.g. Layer)

    Using the "object adapter" version of the pattern.
    Whereby Adapter owns an instance of Adaptee (composition.)

    see comments at gimpfu_image, somewhat similar re dynamic methods


    class adapter vs object adapter
       Object adapter: does not inherit Gimp.Image, but owns an instance of it
       Class adapter: multiple inheritance, e.g. GimpfuLayer inherits Gimp.Layer
          I don't know how to wrap Gimp.Layer using metaprogramming dynamically?
    '''

    def __init__(self, adaptee):
        self._adaptee = adaptee


    def __eq__(self, other):
         '''
         Override equality.
         Two wrapper instances are equal if their adaptee's are equal.

         Require self and other both wrappers.
         Otherwise, raise exception.
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
    Anyway, a GimpFu author uses layer.copy().
    That invokes the copy() method, defined here.

     __copy__ is invoked by copy module i.e. copy.copy(foo)
    Any copy must be deep, to copy attribute _adaptee.
    To allow Gimpfu plugin authors to use the copy module,
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





    # Methods and properties offered dynamically.
    # __getattr__ is only called for methods not found on self

    def __getattr__(self, name):
        '''
        Since name not found on self (i.e. not wrapped)
        return name found on adaptee.

        When name is callable, returns a callable which is soon to be called.
        When name is data member, returns value.
        
        !!! This does not preclude public,direct access to _adaptee, use unwrap()
        '''
        # assert _adaptee is a Gimp object (and a GObject)

        # TODO ideally this class would not know the adaptee classes
        # map deprecated names, dispatch on class of adaptee
        # TODO Layer, etc.
        if type(self.__dict__['_adaptee']).__name__ == "Image":
            latest_name = image_name_map[name]
        else:
            latest_name = name

        return getattr(self.__dict__['_adaptee'], latest_name)


    def __setattr__(self, name, value):
        if name in ('_adaptee',):
            self.__dict__[name] = value
        else:
            setattr(self.__dict__['_adaptee'], name, value)

    def __delattr__(self, name):
        delattr(self.__dict__['_adaptee'], name)
