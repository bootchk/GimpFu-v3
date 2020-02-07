

class AdaptedProperty():
    '''
    Understands how to dynamically adapt properties.

    Properties on Adaptee must be called using call syntax (with parens)
    e.g. "foo = adaptee.get_property()" or "property()"

    Properties on AdaptedAdaptee use non-call syntax (without parens)
    e.g. "foo = adaptedAdaptee.property"

    An access to an AdaptedProperty is intercepted by the Python __getattr__
    mechanism.

    AdaptedProperty's are defined in AdaptedAdaptee's
    by a property name like "Dynamic..."
    that is a tuple of names of Adaptee properties (sic) that can be
    dynamically adapted.

    Some Adaptee properties cannot be dynamically adapted,
    and are instead adapted by code in AdaptedAdaptee
    implemented as Python properties i.e. using "@property"
    '''

    @classmethod
    def is_dynamic_writeable_property_name(cls, instance, name):
        ''' is name a writeable dynamic property on instance? '''
        ''' !!! instance is-a AdaptedAdaptee, not an Adaptee '''

        # raises AttributeError if DynamicWriteableAdaptedProperties not defined by AdaptedAdaptee
        delegated_property_names = getattr(instance, 'DynamicWriteableAdaptedProperties')
        # ensure delegated_property_names is not None, but could be empty
        return name in delegated_property_names


    @classmethod
    def is_dynamic_readonly_property_name(cls, instance, name):
        # raises AttributeError if DynamicWriteableAdaptedProperties not defined by AdaptedAdaptee
        delegated_property_names = getattr(instance, 'DynamicReadOnlyAdaptedProperties')
        # ensure delegated_property_names is not None, but could be empty
        return name in delegated_property_names


    @classmethod
    def is_dynamic_readable_property_name(cls, instance, name):
        return cls.is_dynamic_readonly_property_name(instance, name) or cls.is_dynamic_writeable_property_name(instance, name)





    # Private
    @classmethod
    def _eval_statement_on_adaptee(cls, adaptee, name, get_or_set, setting_value=None):
        assert get_or_set in ("get", "set")

        # FUTURE rather than trust that DynamicReadOnlyAdaptedProperties is correct,
        # preflight get_name on dictionary of adaptee
        # So we can use a more specific error than AttributeError, e.g. "is not a *property* name"


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


    @classmethod
    def get(cls, adaptee,method_name ):
        ''' Call method_name of adaptee to get a property value. '''
        return cls._eval_statement_on_adaptee(adaptee, method_name, 'get')

    @classmethod
    def set(cls, adaptee, method_name, value):
        ''' Call method_name of adaptee to set a property value. '''
        return cls._eval_statement_on_adaptee(adaptee, method_name, 'set', value)
