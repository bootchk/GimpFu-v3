

import logging

module_logger = logging.getLogger('GimpFu.Wrappable')


'''
Knows:

    which Gimp types are wrappable by Gimpfu and vice versa.
    which Gimp attributes are functions
    the class hierarchy of Gimp types (mainly subclasses of Drawable, Item)
'''


# Python idiom for string name of a type
# Gimp.Drawable returns a type, but its name is type.__name__
def get_type_name(instance):
    return get_name_of_type(type(instance))

def get_name_of_type(a_type):
    return a_type.__name__


'''
!!! Keep in correspondence with  wrap() dispatch.
(unwrap is in the adapter)
I.E. to add a wrapper Foo:
 - add Foo.py in adapters/
 - add literals like 'Foo' in three places in this file.

 wrap is symmetrical with unwrap.

 Drawable, Item, are virtual, an Author cannot create instances,
 only instance of subclasses.
'''
# TODO other leaf types, LayerMask etc.
gimp_type_to_wrapper_type_map = {
    'Image':   "GimpfuImage",
    'Layer':   "GimpfuLayer",
    'Display': "GimpfuDisplay",
    'Vectors': "GimpfuVectors",
    'RGB':     "GimpfuRGB",
}

def is_gimpfu_wrappable_name(name):
    result = name in gimp_type_to_wrapper_type_map.keys()
    module_logger.info(f"is_gimpfu_wrappable_name: {name} returns {result}")
    return result

def is_gimpfu_unwrappable_name(name):
    result = name in gimp_type_to_wrapper_type_map.values()
    module_logger.info(f"is_gimpfu_unwrappable_name: {name} returns {result}")
    return result

# TODO rename is_instance_gimpfu_wrappable
def is_gimpfu_wrappable(instance):
    return is_gimpfu_wrappable_name(get_type_name(instance))
def is_gimpfu_unwrappable(instance):
    return is_gimpfu_unwrappable_name(get_type_name(instance))

def wrapper_type_name_for_instance(instance):
    """
    return name of Python type for wrapper (like GimpfuLayer) or None
    """
    name = get_type_name(instance)
    result = gimp_type_to_wrapper_type_map[name]
    module_logger.info(f"wrapper_name_for_instance: {name} returns {result}")
    return result



# TODO rename is_function
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


'''
Taken from "GIMP App Ref Manual>Class Hierarchy"
Note the names are not prefixed with "Gimp."

Authors cannot instantiate Item or Drawable, only their subclasses.
Drawable and Item are virtual base classes.

"Item"  virtual
    "Drawable"  virtual
        "Layer",
           "GroupLayer",
           "TextLayer"
        "Channel",
           "LayerMask",
           "Selection",
    "Vectors"
'''
DrawableTypeNames = (
    "Layer",
       "GroupLayer",
       "TextLayer",
    "Channel",
       "LayerMask",
       "Selection",
)

ItemTypeNames = (
    "Drawable",
    "Vectors"
)

module_logger.info(f"DrawableTypeNames: {DrawableTypeNames}")
module_logger.info(f"ItemTypeNames: {ItemTypeNames}")

# ItemTypeNames = DrawableTypeNames + ("Vectors",)

"""
Test cases:

Single level to Item
Drawable is subclass of Item
Vectors is subclass of Item

Single level to Drawable
Channel is subclass of Drawable

Two levels to Item
Channel is subclass of Item
"""


'''
Instances of 3-tuples and strings
can be considered subclasses of RGB,
since conversion is possible.
'''
ColorTypeNames = (
    "tuple",
    "str"
)


'''
This has these purposes:
- to handle Gimp overly strict about parameter types, it wrongly does not allow a subclass
(Gimp doesn't seem to understand its own class hierarchy)
- to handle None passed (again, Gimp complains)
- to allow conversion from tuple, str to color

Technically, NoneType is a subclass of every type.
But we don't want that here, we deal with it elsewhere.

Strict subclassness: a class is NOT a subclass of itself.
'''
def is_subclass_of_type(instance, super_type):
    # assert super_type is a Python type, having .__name__
    result = False
    super_type_name = get_name_of_type(super_type)
    instance_type_name = get_type_name(instance)
    if super_type_name == instance_type_name:
        result = False    # class is NOT subclass of itself
    elif  super_type_name == 'Drawable':
        result =  instance_type_name in DrawableTypeNames
    elif super_type_name == 'Item':
        result = (instance_type_name in ItemTypeNames or instance_type_name in DrawableTypeNames)
    elif super_type_name == 'RGB':
        result = instance_type_name in ColorTypeNames
    else :
        module_logger.warning(f"is_subclass_of_type, unhandled super_type_name {super_type_name}")

    module_logger.info(f"is_subclass_of_type ( {instance_type_name}, {super_type_name}) returns {result}")

    if result:
        module_logger.debug(f"is_subclass_of_type ( {instance_type_name}, {super_type_name}) returns {result}")
    return result
