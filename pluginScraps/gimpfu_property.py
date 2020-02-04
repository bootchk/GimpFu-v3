
class GimpfuProperty(object):
    '''
    A "data descriptor" that sets and returns values on an adaptee.
    '''

    def __init__(self, adaptee, name='var'):

        self.name = name
        self.adaptee = adaptee

    def __get__(self, obj, objtype):
        # objtype not used, but required by descriptor protocol
        print('Retrieving', self.name)
        # Method on adaptee is like "get_name"
        # Method on adaptee is a callable having no arguments
        result = eval("self.adaptee.get_" + self.name + "()")
        return result

    # !!! Set MUST be implemented to make this a 'data descriptor'
    # which affects priority of resolving attributes
    def __set__(self, obj, val):
        raise AttributeError("Read only property")





class GimpfuProperty2(object):
    '''
    A "data descriptor" that sets and returns values on an adaptee.
    '''

    def __init__(self, name='var'):
        self.name = name

    def __get__(self, obj, objtype):
        # objtype not used, but required by descriptor protocol
        print('GimpfuProperty2 Retrieving:', self.name)
        print("obj and type is:", obj, objtype)
        # call the getter of adaptee
        a_adaptee = obj.adaptee()
        # Method on adaptee is like "get_name"
        # Method on adaptee is a callable having no arguments
        statement = "a_adaptee.get_" + self.name + "()"
        print("statement:", statement)
        result = eval(statement)
        print("eval result:", result)
        return result

    # !!! Set MUST be implemented to make this a 'data descriptor'
    # which affects priority of resolving attributes
    def __set__(self, obj, val):
        raise AttributeError("Read only property")
