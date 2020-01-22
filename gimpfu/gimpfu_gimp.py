

import gi
gi.require_version("Gimp", "3.0")
from gi.repository import Gimp
from gi.repository import GObject    # marshalling


# import wrapper classes
from gimpfu_image import GimpfuImage
from gimpfu_layer import GimpfuLayer



class GimpfuGimp():
    '''
    Adaptor to Gimp
    GimpFu defines a symbol "gimp", an instance of this class.
    Its attributes appear to have similar names as the Gimp object (from GI).
    E.G. Gimp.Image vs gimp.Image

    Adaption kinds:
    Some methods are passed straight to Gimp.
    Some methods are passed to wrapper class in Python (constructor methods)
    Some methods are specialized (convenience)

    See gimpfu_pdb, its similar.

    Typical source constructs:
      img = gimp.Image(width, height, RGB)  invoke constructor of Gimp.Layer class, to be wrapped by GimpFu
      gimp.context_push()                   invoking method of Gimp class
      gimp.delete(img)                      specialized method
      gimp.locale_directory                 ???

    Note that Gimp.Layer refers to the Layer class in the Gimp namespace
    while Gimp.context_push invokes a method of the Gimp class.
    I.E. Gimp.Layer is NOT referring to an attribute of the Gimp class.

    Constructs you might imagine, but not seen yet in the wild:
       gimp.Layer.foo                       get attribute of the Gimp.Layer class?
       gimp.Layer.FOO                       get an enum value defined by Gimp.Layer class?
    '''


    def _marshall_args(self, *args):
        '''
        Gather many args into Gimp.ValueArray
        '''
        marshalled_args = Gimp.ValueArray.new(len(args))
        index = 0
        for x in args:
            # TODO convert to GObject
            # GObject.Value(GObject.TYPE_STRING, tmp))
            print("marshall arg")
            print(type(x))

            # !!! Can't assign GObject to python object: marshalled_arg = GObject.Value(Gimp.Image, x)
            # ??? I don't understand why insert() doesn't determine the type of its second argument

            marshalled_args.insert(index, GObject.Value(type(x), x))
            index += 1
        return marshalled_args


    # TODO, not all names are constructors e.g. Image
    # some names are methods of Gimp e.g. Gimp.displays_flush()
    def _adaptor_func(self, *args):
        '''
        run a Gimp constructor method "new"
        for class whose name was used like "gimp.Name()"
        e.g. like call to a class name (as a constructor)
        where class is an attribute of gimp

        Because C++ syntax for creation is Foo.new() whereas Python syntax is Foo()
        '''
        print ("gimp adaptor called, args", args)

        # test

        '''
        # Futz with args that had property semantics in v2
        new_args = []
        for arg in args:
            print("arg type is:", type(arg))
            print(arg.invoke())
            if type(arg) is gi.FunctionInfo:
                print("arg.invoke")
                new_arg = arg.invoke()
            else:
                new_arg = arg
            new_args.append(new_arg)
        '''

        # create name string of method

        # TODO, class_name is misnomer, not every name is a class, some are method names.
        class_name = object.__getattribute__(self, "adapted_gimp_object_name")

        # TEMP  Probably all will be wrapped
        # dispatch on whether object has been wrapped
        if not (class_name in ("Image", "Layer")):
            # TODO this is not right, should be just a method call
            # pass to Gimp constructor
            method_name = "Gimp." + class_name + ".new"
        else:
            # construct a wrapper object of Gimp object
            # e.g. GimpfuFoo, a classname which is a constructor
            method_name = "Gimpfu" + class_name
        print("Calling constructor: ", method_name)

        # eval to get the callable function
        func = eval(method_name)

        '''
        E.G.
        func = Gimp.Image.new
        func = eval("Gimp.Image.new")
        return func(*args)
        return Gimp.Image.new(*args)
        return GimpfuImage(*args)
        '''

        result = func(*args)
        #result = func(*new_args)
        print(result)
        return result



    # Methods and properties offered dynamically.

    def __getattr__(self, name):
    # !!! not def  __getattribute__(self, name):
        '''
        override of Python special method
        Adapts attribute access to become invocation on Gimp object.
        __getattr__ is only called for methods not found on self
        i.e. for methods not defined in this class (non-convenience methods)
        '''
        '''
        Require 'gimp' instance of Gimp object exists.  GimpFu creates it.
        Don't check, would only discover caller is not importing gimpfu.
        '''

        # attribute name e.g. "Image"
        # We don't preflight, e.g. check that it is attribute of Gimp object

        # announce names that are better accessed directly on Gimp, i.e. deprecated syntax
        if name in ("displays_flush", ):

            print(f"gimp.{name} is deprecated, you should use Gimp.{name}")

        '''
        We can't just return attribute of Gimp object:
        "Gimp.__get_attribute__(name)" returns
        AttributeError: 'gi.repository.Gimp' object has no attribute '__get_attribute__'
        Also, we need to mangle "Image()" to "Image.new()"
        '''

        # remember state for soon-to-come call
        self.adapted_gimp_object_name = name

        print("return gimp adaptor func")
        # return adapter function soon to be called
        return object.__getattribute__(self, "_adaptor_func")


    # specialized, convenience

    '''
    These are methods from v2 that we don't intend to deprecate
    since they have actions on the Python side
    that some plugins may require.
    '''


    def delete(self, instance):
        '''
        From PyGimp Reference:
        It deletes the gimp thing associated with the Python object given as a parameter.
        If the object is not an image, layer, channel, drawable or display gimp.delete does nothing.
        '''
        #TODO later
        # For now, assume most programs don't really need to delete,
        # since they are about to exit anyway
        '''
        Maybe:
        delete instance if it is a wrapped class.
        Also deleted the adaptee.
        Gimp.Image.delete() et al says it will not delete
        if is on display (has a DISPLAY) i.e. if Gimp user created as opposed to just the plugin.
        '''
        print("TODO gimp.delete() called")
