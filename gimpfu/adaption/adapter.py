
#is_test = True
is_test = False

# !!! Can't import Marshal yet, circular

'''
Adapter component of the Wrapper/Adapter pattern.
Wraps an Adaptee that is a Gimp object (usually some subclasses of Item e.g. Layer)
An Adapted object inherits this class.
(Adapted and Adaptee are metaclasses, no instance is-a Adapted or Adaptee.)

Collaborators:
    Marshall:  args to and from Adaptee must be marshalled (wrapped and unwrapped)

Responsibilities:
    delegate a subset of attributes accesses on Adapted to Adaptee
        - property accesses on Adapted => Adaptee getter/setter functions
        - calls to undefined methods of Adapted => calls to Adaptee

    equality of Adapted instances
    copy Adapted instances

    expose the Adaptee instance  and its class_name to Adapted
    catch errors in attribute access

Note that an Adapted class can adapt methods that become calls on Adaptee.
Methods that the Adapted class adapts (specializes.)
The calls that the Adaptor class adapts are generally adapted.

see comments at adapters.image, somewhat similar re dynamic methods

Using the "object adapter" version of the pattern.
Whereby Adapter owns an instance of Adaptee (composition.)
class adapter vs object adapter
   Object adapter: does not inherit Gimp.Image, but owns an instance of it
   Class adapter: multiple inheritance, e.g. GimpfuLayer inherits Gimp.Layer
      I don't know how to wrap Gimp.Layer using metaprogramming dynamically?

TODO enumerate errors it detects

'''

class Adapter():

    def __init__(self, adaptee):
        self._adaptee = adaptee
        self._adaptee_callable = None


    '''
    Expose adaptee and its class_name.
    '''
    def unwrap(self):
        ''' Return inner object, of a Gimp type, used when passing args back to Gimp'''
        print("unwrap to", self._adaptee)
        return self._adaptee

    @property
    def adaptee_class_name(self):
        ''' Class name by which Gimpfu plugin author knows adaptee class e.g. Gimp.Image '''
        return type(self._adaptee).__name__



    '''
    Equality and copy
    '''
    def __eq__(self, other):
         '''
         Override equality.
         Two Adapted instances are equal if:
         - both same superclass of Adapter
         - AND their adaptee's are equal.

         Require self and other both inherit Adapter, ow exception.
         I.E. not general purpose equality such as: Layer instance == int instance
         '''
         try:
             # Compare ID's or names instead?
             # Could use public unwrap() for more generality
             return self._adaptee == other.unwrap()
         except AttributeError:
             print("Adaptor can't compare types ", type(self), type(other))
             raise



    '''
    copy() method on AdaptedAdaptee instance.
    Source code like: fooAdapted.copy().
    Copy() is deep, to copy the instance and its owned adaptee.

    This is NOT __copy__
     __copy__ is invoked by copy module i.e. copy.copy(foo)
    To allow Gimpfu plugin authors to use the copy module,
    we should override __copy__ and __deepcopy__ also.
    Such MUST call gimp to copy the adaptee.
    TODO

    See SO "How to override the copy/deepcopy operations for a Python object?"
    This is a hack of that answer code.
    Gimp adaption:
    copy() was implemented in v2, but I am not sure it went through the __copy__ mechanism.

    TODO just Marshal.wrap() ??? Would work if self has no attributes not computed from adaptee
    '''

    def copy(self):
         """ Copy an Adapted instance. """

         # require Adaptee implements copy()

         # Marshall knows how to wrap self in AdaptedAdaptee, e.g. GimpfuLayer
         if is_test:
             from mock.marshal import Marshal
         else:
             from adaption.marshal import Marshal

         '''
         clone _adaptee
         v2 called run_procedure()
         Here we use Adaptee.copy() directly
         Exception if Adaptee does not implement copy()
         '''
         adaptee_clone = self._adaptee.copy()

         # Create Adapted instance
         result =  Marshal.wrap(adaptee_clone)

         print(f"Copy: {adaptee_clone} into copy of Adapted instance {result}")
         return result





    '''
    Private
    '''

    def _adapter_func(self, *args):
        ''' intercepts calls to previously accessed attribute '''

        print("Adapter._adapter_func called, args:", *args)

        # arg could be a wrapped type, convert to unwrapped type i.e. foreign type
        print("marshal args")
        # TODO

        # call the callable
        # Not sure why we need to use object.__...
        result = object.__getattribute__(self, "_adaptee_callable")(*args)

        # result could be a foreign type, convert to wrapped type, etc.
        print("unmarshal args")
        # TODO

        return result


    def _is_dynamic_writeable_property_name(self, name):
        # raises AttributeError if DynamicWriteableAdaptedProperties not defined by AdaptedAdaptee
        delegated_property_names = getattr(self, 'DynamicWriteableAdaptedProperties')
        # ensure delegated_property_names is not None, but could be empty
        return name in delegated_property_names

    def _is_dynamic_readonly_property_name(self, name):
        # raises AttributeError if DynamicWriteableAdaptedProperties not defined by AdaptedAdaptee
        delegated_property_names = getattr(self, 'DynamicReadOnlyAdaptedProperties')
        # ensure delegated_property_names is not None, but could be empty
        return name in delegated_property_names

    def _is_dynamic_readable_property_name(self, name):
        return self._is_dynamic_readonly_property_name(name) or self._is_dynamic_writeable_property_name(name)




    def _eval_statement_on_adaptee(self, adaptee, name, get_or_set, setting_value=None):
        assert get_or_set in ("get", "set")

        # Method on adaptee is like "[get,set]_name"
        # Method on adaptee is a callable having no arguments
        # eval occurs in current context, so formal args are in scope
        print("Adapter: form statement")
        if get_or_set == 'set':
            # set statement is a call with arg
            statement = 'adaptee.set_' + name + '(setting_value)'
        else:
            # get statement is a call without arg
            statement = 'adaptee.get_' + name + '()'
        print("AdaptedProperty statement:", statement)
        result = eval(statement)
        print("AdaptedProperty eval result:", result)
        return result


    def _get_dynamic_property_value(self, name):
        ''' Call method of adaptee to get a property value. '''
        adaptee = self.__dict__['_adaptee']
        return self._eval_statement_on_adaptee(adaptee, name, 'get')

    def _set_dynamic_property_value(self, name, value):
        ''' Call a method of adaptee to set a property value. '''
        adaptee = self.__dict__['_adaptee']
        return self._eval_statement_on_adaptee(adaptee, name, 'set', value)





    '''
    __getattr and __setattr that adapt attributes: delegate to adaptee
    '''

    def __getattr__(self, name):
        print("Adapter.__getattr__", name)

        '''
        require self is AdaptedAdaptee i.e. defines class variable that lists properties
        i.e. implements virtual properties of ABC AdaptedAdaptee.
        Use this idiom to avoid infinite recursion.
        '''
        assert object.__getattribute__(self, 'DynamicReadOnlyAdaptedProperties')
        assert object.__getattribute__(self, 'DynamicWriteableAdaptedProperties')

        adaptee = self.__dict__['_adaptee']

        # Is name a callable defined by adaptee?
        if hasattr(adaptee, name):
            adaptee_callable = getattr(self.__dict__['_adaptee'], name)
            # Prepare for subsequent call
            object.__setattr__(self, "_adaptee_callable", adaptee_callable)
            result = self._adapter_func
        elif self._is_dynamic_readable_property_name(name):
            result = self._get_dynamic_property_value(name)
        else:
            raise AttributeError(f"Name {name} is not an attribute of {self.adaptee_class_name}")
        # assert result is a value, or the callable adapter_func
        return result



    def __setattr__(self, name, value):
        ''' Attempt to assign to name. '''

        '''
        Special case: implementation of Adapter assigns to the few attributes of itself.
        '''
        if name in ('_adaptee', '_adaptee_callable'):
            object.__setattr__(self, name, value)
            return

        '''
        All other cases should be GimpFu plugin authors attempts to assign
        to attributes of an instance of Adapted(Adapter).
        '''

        adaptee = self.__dict__['_adaptee']

        # Is name defined by adaptee?
        if hasattr(adaptee, name):
            # Adaptee's have no assignable attributes, only callables ????
            raise AttributeError(f"Name {name} on {self.adaptee_class_name} is not assignable, only callable.")
        elif self._is_dynamic_writeable_property_name(name):
            result = self._set_dynamic_property_value(name, value)
        elif self._is_dynamic_readonly_property_name(name):
            raise AttributeError(f"Attempt to assign to readonly attribute '{name}'")
        else:
            '''
            Gimpfu plugin author is attempting to assign a new attribute
            to a class of the adaption mechanism (e.g. an instance that inherits Adaptor.)
            See above for the only internal attributes of Adaptor.
            This must be an error in GimpFu plugin author's code.
            They have instances of Gimpfu's subclasses of Adapter,
            but we disallow assigning attributes to them, they could do harm.
            Instead they should use local variables.
            '''
            raise AttributeError(f"Attempt to assign to attribute: {name} of Gimpfu Adaptor of: {self.adaptee_class_name})")
            """
            print("Assigned to Adapted(Adapter) class")
            print("Adapter.__setattr__", name)
            object.__setattr__(self, name, value)
            """

        # assert result is a value, or the callable adapter_func
        return result