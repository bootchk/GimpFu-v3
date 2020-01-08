

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
