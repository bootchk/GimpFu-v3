

'''
This is a test case for the adaption techniques used
in the implementation of GimpFu.

IOW it is a much simplfied version of some of the guts of GimpFu
'''






class Adapter():
    def __init__(self, adaptee):
        self._adaptee = adaptee
        _adaptee_callable = None


    def _adaptee_name(self):
        ''' Name by which Gimpfu plugin author knows adaptee e.g. Gimp.Image '''
        return type(self._adaptee).__name__


    def _adapter_func(self, *args):
        print("Adapter._adapter_func called, args:", *args)

        # arg could be a wrapped type, convert to unwrapped type i.e. foreign type
        print("marshal args")

        # call the callable
        # Not sure why we need to use object.__...
        result = object.__getattribute__(self, "_adaptee_callable")(*args)

        # result could be a foreign type, convert to wrapped type, etc.
        print("unmarshal args")
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



    def __getattr__(self, name):
        print("Adapter.__getattr__", name)

        adaptee = self.__dict__['_adaptee']

        # Is name defined by adaptee?
        if hasattr(adaptee, name):
            adaptee_callable = getattr(self.__dict__['_adaptee'], name)
            # Prepare for subsequent call
            object.__setattr__(self, "_adaptee_callable", adaptee_callable)
            result = self._adapter_func
        elif self._is_dynamic_readable_property_name(name):
            result = self._get_dynamic_property_value(name)
        else:
            raise AttributeError(f"Name {name} is not an attribute of {self._adaptee_name()}")
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
            raise AttributeError(f"Name {name} on {self._adaptee_name()} is not assignable, only callable.")
        elif self._is_dynamic_writeable_property_name(name):
            result = self._set_dynamic_property_value(name, value)
        elif self._is_dynamic_readonly_property_name(name):
            raise AttributeError(f"Attempt to assign to readonly attribute '{name}'")
        else:
            '''
            GimpFu itself rarely assigns to Adapted(Adaptee), see above for the only cases
            This must be an error in GimpFu plugin author's code.
            They have instances of Gimpfu's subclasses of Adapter,
            but we disallow assigning attributes to them,
            they could do harm.
            '''
            raise AttributeError(f"Attempt to assign to attribute of Gimpfu Adaptor of {self._adaptee_name()})")
            """
            print("Assigned to Adapted(Adapter) class")
            print("Adapter.__setattr__", name)
            object.__setattr__(self, name, value)
            """

        # assert result is a value, or the callable adapter_func
        return result




class Adaptee():
    '''
    This is the class of some amorphous object to be adapted.
    For example, it could be a GObject Introspected object.
    '''

    '''
    These are properties in the sense that there are no args to getter calls.
    But they are set and get using call syntax.
    '''
    def __init__(self):
      self._othernameRW = "qux"
      self._instance_nameRW = "in_initial"


    def get_filename(self):
      return "foo"

    def get_othernameRO(self):
      # A constant, more or less
      return "zed"

    def get_othernameRW(self):
      return self._othernameRW
    def set_othernameRW(self, arg):
      self._othernameRW = arg

    def get_instance_nameRW(self):
        return self._instance_nameRW
    def set_instance_nameRW(self, arg):
        self._instance_nameRW = arg



    # method whose  [arg, result] both need marshalling
    def adapted_method(self, arg):
      return "bar"



# class AdaptedAdaptee(Adapter, Base):
class AdaptedAdaptee( Adapter):
    '''
    Class that wraps (adapts) class Adaptee
    '''
    def __init__(self, adaptee):
        # Adapter remembers the adaptee instance
        super().__init__(adaptee)


    '''
    Define properties of AdaptedAdaptee
    that map to properties of Adaptee.
    All are instance (not class) properties, since implemented
    using the _adaptee attribute of Adaptee instances.

    !!! The names must match those used in Adaptee.
    '''
    DynamicWriteableAdaptedProperties = ('othernameRW', 'instance_nameRW' )
    DynamicReadOnlyAdaptedProperties = ('othernameRO', )


    # A property defined statically
    # i.e. using code explicit about adaptee name

    @property
    def filename(self):
        print("Adapted property accessed")
        return self._adaptee.get_filename()
    @filename.setter
    def filename(self, dummy):
        # TODO:
        raise RuntimeError("not implemented")

    # A callable that Adapted provides
    def adapted_callable():
         pass



adaptee = Adaptee()
adapted = AdaptedAdaptee(adaptee)

adaptee2 = Adaptee()
adapted2 = AdaptedAdaptee(adaptee2)


# Run tests

print("\nTest normal results\n\n")

# Test call adaptee method directly
print("\nExpect 'foo'")
print(adaptee.get_filename())


# Test access static property of adapted adaptee
print("\nExpect 'Adapted property accessed' ,  'foo' ")
print(adapted.filename)

# Test access dynamic property of adapted adaptee
print("\nExpect 'Adapted property RO accessed' ,  'zed' ")
print(adapted.othernameRO)


# Test [read, write, read] dynamic property of adapted adaptee
print("\nExpect 'Adapted property RW set' ,  'qux', 'changedQux' ")
print(adapted.othernameRW)
adapted.othernameRW = "changedQux"
print(adapted.othernameRW)

# OBSOLETE: all properties are instance properties
# Test crosstalk between adapted class properties
# We wrote othernameRW on first adapted
# Ensure othernameRW on second adapted is also changed
#print("\nExpect 'Instance 2 adapted property RW get' ,  'changedQux' ")
#print(adapted2.othernameRW)


# Test absence of crosstalk between adapted instance properties
# We wrote othernameRW on first adapted
# Ensure othernameRW on second adapted is also changed
print("\nExpect 'Instance 2 adapted instance property RW get' ,  'in_initial', 'in_initial', 'in1', 'in2' ")
# Until set returns an initial value
print(adapted.instance_nameRW)
print(adapted2.instance_nameRW)
adapted.instance_nameRW = "in1"
adapted2.instance_nameRW = "in2"
print(adapted.instance_nameRW)
print(adapted2.instance_nameRW)


# Test access adapted method, through adapter
print("\nExpect: 'marshal args', 'unmarshal args', 'bar' ")
print(adapted.adapted_method("nothing"))

print("\nTest abnormal uses, expect error messages.\n")

print("\nTest attempt write to RO property")
print("Expect: AttributeError: ('Read only property:', 'othernameRO') ")
try:
    adapted.othernameRO = "nothing"
except AttributeError as err:
    print(err)
    pass

print("\nTest attempt to call a property on adaptee")
print("Expect: TypeError: 'str' object is not callable ")
try:
    foo = adapted.instance_nameRW()
except TypeError as err:
    print(err)
    pass

print("\nTest attempt to assign to adaptee callable ")
print("Expect: AttributeError:  Name get_filename on Adaptee is not assignable, only callable. ")
# !!! adaptee is not known to GimpfuPlugin author, only adapted
# but the callable implemented by adaptee
try:
    adaptee.get_filename = 0
except AttributeError as err:
    print(err)
    pass


print("\nTest attempt to assign to adapted callable ")
print("Expect: AttributeError: Attempt to assign to attribute of AdaptedAdaptee")
try:
    adapted.adapted_callable = 0
except AttributeError as err:
    print(err)
    pass


print("\n Completed all tests")
