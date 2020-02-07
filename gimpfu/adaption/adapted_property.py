

class AdaptedProperty():
    '''
    Understands how to dynamically adapt properties.

    Properties on Adaptee must be called using call syntax (with parens)
    e.g. "foo = adaptee.get_property()" or "property()"
    In the statement dynamically generated by this class.

    Properties on AdaptedAdaptee use non-call syntax (without parens)
    e.g. "foo = adaptedAdaptee.property"
    In the Author's plugin source code.

    An access to an AdaptedProperty is intercepted by the Python __getattr__
    mechanism.

    AdaptedProperty's are defined in AdaptedAdaptee's
    by a property name like "Dynamic..."
    that is a tuple of names of Adaptee properties (sic) that can be
    dynamically adapted.

    Some Adaptee properties cannot be dynamically adapted,
    (because the syntax or semantic differences are too great to be automated.)
    and are instead 'manually' adapted by code in AdaptedAdaptee
    implemented as Python properties i.e. using "@property"
    '''

    '''
    Kinds of adapted properties:
    ReadOnly: get_<property>() defined by adaptee
    Writeable: set_ and get_<property>() defined by adaptee
    True:   <property>() defined by adaptee
    '''

    '''
    Inheritance and AdaptedProperty(s)

    An Adaptee instance inherits from a chain of classes.
    When we ask whether a name is on an instance of adaptee,
    GI must search the chain.

    An AdaptedAdaptee (which defines dynamic properties)
    also inherits from a chain of classes.
    E.g. GimpfuLayer=>GimpfuDrawable=>GimpfuItem.
    Each class may define its own Dynamic... properties,
    but when asked, must return the totaled properties of
    its own class plus its inherited classes.

    (Alternatively we could traverse the MRO)
    '''

    @classmethod
    def is_dynamic_writeable_property_name(cls, instance, name):
        ''' is name a writeable dynamic property on instance? '''
        ''' !!! instance is-a AdaptedAdaptee, not an Adaptee '''

        # raises AttributeError if DynamicWriteableAdaptedProperties not defined by AdaptedAdaptee
        #OLD delegated_property_names = getattr(instance, 'DynamicWriteableAdaptedProperties')
        delegated_property_names = instance.DynamicWriteableAdaptedProperties()
        # ensure delegated_property_names is not None, but could be empty
        return name in delegated_property_names


    @classmethod
    def is_dynamic_readonly_property_name(cls, instance, name):
        # raises AttributeError if DynamicWriteableAdaptedProperties not defined by AdaptedAdaptee
        #OLD delegated_property_names = getattr(instance, 'DynamicReadOnlyAdaptedProperties')
        delegated_property_names = instance.DynamicReadOnlyAdaptedProperties()
        # ensure delegated_property_names is not None, but could be empty
        return name in delegated_property_names



    @classmethod
    def is_dynamic_true_property_name(cls, instance, name):
        ''' Is <name> accessed like <name>() ? '''
        delegated_property_names = instance.DynamicTrueAdaptedProperties()
        return name in delegated_property_names



    @classmethod
    def is_dynamic_readable_property_name(cls, instance, name):
        ''' Is <name> accessed like get_<name>() ? '''
        return (cls.is_dynamic_readonly_property_name(instance, name)
            or cls.is_dynamic_writeable_property_name(instance, name)
            )

    '''
    !!! This does not mean that the callable has arguments.
    When the callable does not have args i.e. <name>(void)
    it is indistinguishable from what we might adapt as a property.
    '''
    @classmethod
    def is_callable_name_on_instance(cls, instance, name):
        ''' Is <name> accessed like <name>() ? '''
        return hasattr(instance, name)





    # Private
    @classmethod
    def _eval_statement_on_adaptee(cls, adaptee, name, prefix = '', setting_value=None):
        '''
        Create and eval() a statement to access a method on adaptee
        that looks like a property i.e. has no args.
        '''

        assert prefix in ("get_", "set_", "")

        # FUTURE rather than trust that DynamicReadOnlyAdaptedProperties is correct,
        # preflight get_name on dictionary of adaptee
        # So we can use a more specific error than AttributeError, e.g. "is not a *property* name"


        # Method on adaptee is like "[get,set]_name"
        # Method on adaptee is a callable having no arguments
        # eval occurs in current context, so formal args are in scope
        print("Adapter: form statement")
        if prefix == 'set_':
            # setStatement is a call with arg
            statement = 'adaptee.set_' + name + '(setting_value)'
        else:
            # is a get (prefix is 'get_') or a read (prefix is '')
            # getStatement is a call without arg
            statement = 'adaptee.' + prefix + name + '()'
        print("AdaptedProperty statement:", statement)
        result = eval(statement)
        print("AdaptedProperty eval result:", result)
        return result


    @classmethod
    def get(cls, adaptee, method_name ):
        ''' Call method_name of adaptee to get a property value. '''
        return cls._eval_statement_on_adaptee(adaptee, method_name, prefix = 'get_')

    @classmethod
    def set(cls, adaptee, method_name, value):
        ''' Call method_name of adaptee to set a property value. '''
        return cls._eval_statement_on_adaptee(adaptee, method_name, prefix = 'set_', setting_value = value)

    @classmethod
    def read(cls, adaptee, method_name ):
        ''' Call method_name of adaptee to get a property value. '''
        return cls._eval_statement_on_adaptee(adaptee, method_name, prefix = '')
