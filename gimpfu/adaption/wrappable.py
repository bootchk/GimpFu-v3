

'''
Knows:

    which Gimp types are wrappable by Gimpfu and vice versa.
    which Gimp attributes are functions
    which Gimp types are subclasses of Drawable
'''

'''
Keep these in correspondence with each other,
and with wrap() dispatch.
(unwrap is in the adapter)
I.E. to add a wrapper Foo:
 - add Foo.py in adapters/
 - add literals like 'Foo' in three places in this file.
'''



def is_gimpfu_wrappable_name(name):
    return name in ('Image', 'Layer', 'Display', 'Vectors')


def get_gimp_type_name(instance):
    return type(instance).__name__


def is_gimpfu_wrappable(instance):
    return is_gimpfu_wrappable_name(get_gimp_type_name(instance))


def is_gimpfu_unwrappable( instance):
    return type(instance).__name__ in ("GimpfuImage", "GimpfuLayer", "GimpfuDisplay", "GimpfuVectors")


def is_wrapped_function(instance):
    ''' Is the instance a gi.FunctionInfo? '''
    '''
    Which means an error earlier in the author's source:
    accessing an attribute of adaptee as a property instead of a callable.
    Such an error is sometimes caught earlier by Python
    when author dereferenced the attribute
    (e.g. when used as an int, but not when used as a bool)
    but when first dereference is when passing to PDB, we catch it.
    '''
    return type(instance).__name__ in ('gi.FunctionInfo')


def is_subclass_of_drawable(instance):
    # Note the names are not prefixed with Gimp ???
    # These taken from "GIMP App Ref Manual>Class Hierarchy"
    # !!! Technically, NoneType is a subclass of every type?? But we don't want that here.
    return  get_gimp_type_name(instance) in (
        "Layer",
           "GroupLayer",
           "TextLayer"
        "Channel",
           "LayerMask",
           "Selection",
         "Vectors"
        )
