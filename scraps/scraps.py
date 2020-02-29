
"""
Cruft from types.def
"""

"""
Cruft: more than necessary, but keep it, it documents how to use GTypes

def try_convert_to_float(proc_name, actual_arg, actual_arg_type, index):
    '''
    Convert the described actual arg to float if is int
    and PDB procedure wants a float (procedure's formal parameter is type float)

    Returns arg, arg_type    possibly converted
    '''
    # require actual_arg_type is a GType

    result_arg = actual_arg
    result_arg_type = actual_arg_type

    print("Actual arg type:", actual_arg_type)

    '''
    GType types are enumerated by constants of GObject.
    E.G. GObject.TYPE_INT is-a GType .
    In GObject docs, see "Constants"
    '''
    if actual_arg_type == GObject.TYPE_INT :    # INT_64 ???
        formal_arg_type = _get_formal_argument_type(proc_name, index)
        if formal_arg_type == GObject.TYPE_FLOAT or formal_arg_type == GObject.TYPE_DOUBLE :
            print("GimpFu: Warning: converting int to float.")
            result_arg = float(actual_arg)
            result_arg_type = GObject.TYPE_DOUBLE

    return result_arg, result_arg_type
"""


"""
@staticmethod
def try_convert_to_str(proc_name, actual_arg, actual_arg_type, index):
    return try_usual_python_conversion(proc_name, actual_arg, actual_arg_type, index, "str")

@staticmethod
def try_convert_to_float(proc_name, actual_arg, actual_arg_type, index):
    return try_usual_python_conversion(proc_name, actual_arg, actual_arg_type, index, "float")
"""


"""
@staticmethod
def try_convert_to_float(proc_name, actual_arg, actual_arg_type, index):
    '''
    Convert the described actual arg to float if is int
    and PDB procedure wants a float
    (procedure's formal parameter is type GObject.TYPE_FLOAT).
    Only converts Python int to float.

    Returns actual_arg, type(actual_arg), possibly converted

    Later, GObject will convert Python types to GTypes.
    '''
    # require type(actual_arg_type) is Python type or a GType

    result_arg = actual_arg
    result_arg_type = actual_arg_type

    print("Actual arg type:", type(actual_arg))

    if type(actual_arg) is int:
        formal_arg_type = Types._get_formal_argument_type(proc_name, index)
        if formal_arg_type is not None:
            print("     Formal arg type ", formal_arg_type.name )
            if Types.is_float_type(formal_arg_type):
                # ??? Tell Gimpfu plugin author their code would be more clear if they used float() themselves
                # ??? Usually the source construct is a literal such as "1" that might better be float literal "1.0"
                print("GimpFu: Suggest: converting int to float.  Your code might be clearer if you use float literals.")
                result_arg = float(actual_arg)  # type conversion
                result_arg_type = type(result_arg)  # i.e. float
        else:
            # Failed to get formal argument type.  Probably too many actual args.
            # Do not convert type.
            do_proceed_error(f"Failed to get formal argument type for index: {index}.")

    # ensure result_arg_type == type of actual_arg OR (type(actual_arg) is int AND result_type_arg == float)
    # likewise for value of result_arg
    print("try_convert_to_float returns ", result_arg, result_arg_type)
    return result_arg, result_arg_type
"""




Cruft from implementation of _create_plugin_procedure_args





'''
A class whose *instances* will have a prop attribute
'''
class PropHolder (GObject.GObject):
    # copied and hacked to remove '-' from Python GTK+ 3 website tutorial
    __gproperties__ = {
        "intprop": (int, # type
                     "integer prop", # nick
                     "A property that contains an integer", # blurb
                     1, # min
                     5, # max
                     2, # default
                     GObject.ParamFlags.READWRITE # flags
                    ),
    }

    def __init__(self):
        GObject.GObject.__init__(self)
        self.int_prop = 2

    def do_get_property(self, prop):
        if prop.name == 'intprop':
            return self.int_prop
        else:
            raise AttributeError('unknown property %s' % prop.name)

    def do_set_property(self, prop, value):
        if prop.name == 'intprop':
            self.int_prop = value
        else:
            raise AttributeError('unknown property %s' % prop.name)







'''
A GO.Property which we will attempt to redecorate
'''
'''
@GObject.Property(type=str,
                  default=None,
                  nick= _("Dummy2"))
def dummy2(self):
'''




# Python property used to create procedure args
# Note we dynamically redecorate it ??

_dummy = ""

#@GObject.Property(type=str,
#                  default=None,
#                  nick= _("Dummy"))
def dummy_getter(self):
    '''Template string property'''
    return self._dummy
    ##return None  # Non-functional getter

##@dummy.setter
def dummy_setter(self, value):
    self._dummy = value







'''
    cruft
    Even if programmed correctly, PyGobject issue 227 says it won't work???
    array = Gimp.GParamSpec.new(1)
    # Gimp.gimp_param_spec_array ('foo', 'bar', 'zed', Gimp.GIMP_PARAM_READWRITE);

    param_spec = Gimp.g_param_spec_int ("spacing",
                                   "spacing",
                                   "Spacing of the brush",
                                   1, 1000, 10,
                                   Gimp.GIMP_PARAM_READWRITE);
    procedure.add_argument(self, param_spec);
    '''

    '''
    All we are  doing is telling Gimp the type of the argument.
    Ideally, we pass Gimp a GParamSpec.
    But PyGobject #227 might say that is broken.
    This is a trick.
    We can use this trick since Gimp is just examining the type and doesn't call the property methods?
    '''

    '''
    Try mangling attributes of property
    '''
    '''
    This doesn't work: it fails to show __gproperties__  as an attribute in dir() ???
    print(dir(GimpFu))
    print(dir(Gimp.PlugIn))
    GimpFu.__gproperties__["myProp"].nick = "newNick"
    procedure.add_argument_from_property(self, "myProp")
    '''

    '''
    # Dynamically create new property
    # default most things
    # the property name (how it is referenced) is "foo"
    foo = GObject.Property(type=str, default='bar')
    print("print(self.foo:)", self.foo)
    #Fail: AttributeError: 'GimpFu' object has no attribute 'foo'

    # C args are:
    # procedure: Gimp.Procedure, a GObject, that owns the property
    # config: GObject on which the property is registered?
    # propname: str that is name of property
    #
    # Since Python, self is passed implicitly as first arg
    procedure.add_argument_from_property(self, "foo")
    # Fails:

    foo = GObject.Property(type=int, default=1)
    procedure.add_argument_from_property(self, "foo")
    '''

    '''
    Try .props

    "Each instance also has a props attribute which exposes all properties as instance attributes:"
    But where is the instance?
    '''
    prop_holder = PropHolder()
    print(prop_holder.props)
    print(prop_holder.props.intprop)




    '''
        print(self.props)
        # <gi._gi.GProps object at 0x7efc9a2e2d90>
        print(self.props.myProp)
        # Fail: AttributeError: 'GimpFu' object has no attribute 'do_get_property'
        print(self.props.myProp.type)
        self.props.myProp.type = int
        print(self.props.myProp.type)
        procedure.add_argument_from_property(self, "myProp")
        '''



        '''
        redecorate a dummy property.
        A decorator is a function (GObject.Property) having a function parameter (dummy).
        The dummy must have the same primitive type (e.g. str) as we redecorate I.E. we can't change the type?
        Goal is to change extra attributes [default, nick] at runtime

        UnboundLocalError: local variable 'dummy' referenced before assignment
        the function being decorated must be in scope i.e. 'self.dummy', not just 'dummy'

        LibGimp-CRITICAL **: 13:14:37.449: gimp_procedure_add_argument_from_property: assertion 'pspec != NULL' failed
        ???
        '''
        # assigned decorated function to class's attributes
        # Not: global dummy
        '''
        When calling Gobject.Property without syntactic sugar "@", args are as shown

        Returns a "descriptor object", of type <property object>
        Make it named "rdummy", an attribute of self (a PluginProcedure) since will be instrospecting self
        '''
        '''
        self.dummy_setter("foo")
        self.rdummy = GObject.Property(getter=self.dummy_getter,
                                  setter=self.dummy_setter,
                                  type=str,
                                  default=None,
                                  nick= _("FooNick"))
        print(self.rdummy)

        procedure.add_argument_from_property(self, "rdummy")

        # attempt to reuse identical property: fails with Gimp error
        # procedure.add_argument_from_property(self, "palette")
        '''
