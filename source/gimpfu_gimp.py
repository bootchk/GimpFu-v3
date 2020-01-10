

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

    See gimpfu_pdb, its similar.
    '''

    # TODO some me


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

        class_name = object.__getattribute__(self, "adapted_gimp_object_name")

        # TEMP  Probably all will be wrapped
        # dispatch on whether object has been wrapped
        if not (class_name in ("Image", "Layer")):
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




    def  __getattribute__(self, name):
        '''
        override of Python special method
        Adapts attribute access to become invocation on Gimp object.
        '''
        '''
        Require Gimp object exists.  GimpFu creates it.
        Don't check, would only discover caller is not importing gimpfu.
        '''

        # attribute name e.g. "Image"
        # We don't preflight, e.g. check that it is attribute of Gimp object

        '''
        We can't just return attribute of Gimp object:
        "Gimp.__get_attribute__(name)" returns
        AttributeError: 'gi.repository.Gimp' object has no attribute '__get_attribute__'
        Also, we need to mangle "Image()" to "Image.new()"
        '''

        print("return gimp adaptor")
        # remember state for soon-to-come call
        self.adapted_gimp_object_name = name

        # return intercept function soon to be called
        return object.__getattribute__(self, "_adaptor_func")
