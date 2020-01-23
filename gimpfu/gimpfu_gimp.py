

import gi
gi.require_version("Gimp", "3.0")
from gi.repository import Gimp
from gi.repository import GObject    # marshalling


# import wrapper classes
from gimpfu_image import GimpfuImage
from gimpfu_layer import GimpfuLayer

from gimpfu_compatibility import gimp_name_map


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

    # TODO extract to Marshal
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



    """
    If experience shows this would be helpful,
    resurrect it.
    For now, just wrap all methods that have signaturge changes.

    def _adapt_signature(self, name, *args):
        # HACK: more generality for adapt signatures
        '''
        Some funcs have args that changed in Gimp.

        Returns a tuple
        '''
        print("_adapt_signature", name, args)
        if name is "set_background":
            # TODO create a color
            # TEMP return a constant color
            color = Gimp.RGB()
            color.parse_name("orange", 6)
            args = [color,]
            result = (color,)
        else:
            result = args
    """



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
        dot_name = object.__getattribute__(self, "adapted_gimp_object_name")


        # Is a GimpFu wrapper object?
        if dot_name in ("Image", "Layer"):
            '''
            The source phrase is like "layer=gimp.Layer(foo)"
            Construct a wrapper object of Gimp object
            e.g. GimpfuLayer, a GimpFu classname which is a constructor.
            Args to wrapper are in GimpFu notation.
            Constructor will in turn call Gimp.Layer constructor.
            '''
            callable_name = "Gimpfu" + dot_name
            print("Calling constructor: ", callable_name)
        else:
            '''
            The source phrase is like 'gimp.context_push()'
            I.E. a method call on the (Gimp instance? or library?)
            Note that some method calls on the Gimp,
            e.g. gimp.delete(foo) are wrapped and intercepted earlier.
            '''
            callable_name = "Gimp." + gimp_name_map[dot_name]


        # eval to get the callable
        func = eval(callable_name)

        '''
        TODO crufty comments
        E.G.
        func = Gimp.Image.new
        func = eval("Gimp.Image.new")
        return func(*args)
        return Gimp.Image.new(*args)
        return GimpfuImage(*args)
        '''

        # new_args = self._adapt_signature(dot_name, args)
        # result = func(*new_args)

        # Call Gimp
        '''
         TODO but keep going if exception
        # often the plugin is not checking errors,
        # beneficial duto find the next error
        '''
        result = func(*args)
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
        Also, we need to mangle "Image()"
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


    def set_background(self, r, g=None, b=None):
        '''
        Changed:
           name
           signature was adapted in PyGimp v2, also here v3
        '''
        # method is overloaded, with optional args
        if g is None:
            # r is-a Gimp.Color already
            color = r
        else:
            color = Gimp.RGB()
            color.set(float(r), float(g), float(b), )

        # call Gimp instead of PDB
        Gimp.context_set_background(color)


    # Changed in Gimp commit 233ac80d
    def gimp_edit_blend(self, mask, blend_mode, layer_mode,
           gradient1, gradient2, gradient3, gradient4,
           truthity1, truthity2,
           int1, int2,
           truthity3,
           x1, y1, x2, y2):
        '''
        One to many.
        !!! We are calling instance of self.
        '''
        gimp.gimp_context_set_gradient_fg_bg_rgb()   # was blend_mode
        # TODO should dispatch blend_mode to different context calls?

        # Note discarded some args
        gimp.gimp_drawable_edit_gradient_fill( mask,
           gradient1, gradient3,
           truthity2, int1, int2, truthity3,
           x1, y1, x2, y2)
