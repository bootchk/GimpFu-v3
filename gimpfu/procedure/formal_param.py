
import gi
from gi.repository import GObject
gi.require_version("Gimp", "3.0")
from gi.repository import Gimp

from gimpfu.enums.gimpfu_enums import *

from gimpfu.procedure.extras import Extras
from gimpfu.procedure.prop_holder_factory import PropHolderFactory

from gimpfu.message.proceed import proceed

import logging


'''
Inherits GObject.Object so we can install properties.
'''
class FuFormalParam(GObject.Object):
    """
    A formal parameter of a plugin.
    Formal (generic description) versus actual (specific value).

    This is parallel to Gimp's similar concept.
    Gimp keeps formal parameters as properties of the plugin.
    Gimp constructs actual parameters to runs of a plugin
    from the formal parameters and the state of the GUI
    i.e. on "run with last values" the actual params are from saved prior run

    Knows how to convey to Gimp.

    For now, this one class suffices for IN and OUT formal params.
    IN params should have a non-null default value.
    OUT params (return values) should not have a default value,
    but we store None for them anyway.
    And don't enforce things properly.
    """

    """
    OLD is working now?

    For now, conveyance is broken:
    all it accomplishes is to tell Gimp the count of parameters
    (and not the types and defaults: we tell Gimp every formal parameter is an int)
    and elsewhere GimpFu ignores actual parameters passed.
    This temporarily suffices for testing GimpFu.
    """


    '''
    Constant class data
    '''
    # Temp hack ???
    from gimpfu.procedure.prop_holder import PropHolder
    prop_holder = PropHolder()
    #self.logger.debug("prop_holder.props", prop_holder.props)
    #self.logger.debug("prop_holder.props.IntProp:", prop_holder.props.IntProp1)

    prop_holder_factory = PropHolderFactory()


    def __init__(self, pf_type, label, desc, default_value=None, extras = [] ):

        # not allow none default, our conveyance methods choke
        if default_value is None:
            default_value = 0

        self.PF_TYPE= pf_type
        self.LABEL= label
        self.DESC= desc
        self.DEFAULT_VALUE= default_value
        self.EXTRAS = extras
        # EXTRAS defaults to empty list or ???  [None]  Python 3.7

        self.logger = logging.getLogger("GimpFu.FuFormalParam")


    def __repr__(self):
        """ Not a true repr. """
        return f"PF: {str(self.PF_TYPE)} DESC:{self.DESC} EXTRAS:{str(self.EXTRAS)}"


    @property
    def tooltip_text(self):
        # Remove accelerator markers from tooltips
        return self.DESC.replace("_", "")

    @property
    def label(self):
        """
        v2 LABEL was used.
        v2 LABEL typically, but not required, matches run_func actual arg name.
        v2 LABEL was a Python symbol (no whitespace or -, allow _ )

        Since v3, LABEL is now a gproperty name and can't have spaces.
        Use DESC instead.
        Which means the tooltip is the same as the label, for GimpFu v3.
        Gimp allows a separate tooltip????
        """
        return self.DESC

    @property
    def gimp_name(self):
        """ Return a name suiting Gimp/GObject requirement for property name:
        alphanumeric only, no (space, _, -).

        Implementation: Use LABEL, suitably altered.
        GimpFu v2 did NOT require LABEL to be a Python symbol (merely a convention.)
        GimpFu allows almost any string.
        We allow, and fixup: (space, -, _) but not (tab)
        """

        result = self.LABEL.replace("_", "")
        result = result.replace("-", "") # fixup
        result = result.replace(" ", "") # fixup
        return result


    '''
    Cruft
    def _get_property_name_to_convey(self):
       """ Returns the name of property.
       All attribues of property do not match properties of self.
       For now, the type may match, but not the default.
       """
       if True:
           # TEMP # HACK:
           # Use same property over and over to convey.
           result = "IntProp1"
       else:
           # get a property from a pool to convey.
           type = self._get_type()
           result = FuFormalParam.prop_holder.next_prop_name(type)
       # OR build a dynamic property that describes self
       return result
   '''

    def _set_property_attributes_to_match_self(self, prop_name):
         """
         Put self attributes in property attributes.
         """
         # TODO when Pygobject is fixed
         # FuFormalParam.prop_holder.set_property(prop_name, self.DEFAULT_VALUE)    # default value
         pass


    """
    Choices of implementation. Most of this is cruft, and might change in the future.

    Static property implementation uses one property on self many times.
    Requires a hack to Gimp, which otherwise refuses to add arg many times from same named property.

    The essential problem is that GObject GParamSpec is not fully implemented.
    Gimp has an alternative implementation that adds args from GParamSpec.
    But that can't be used because of broken PyGObject.

    Gimp has an alternative implementation to add args from property.
    But GimpFu doesn't know the properties ahead of time (like a GI implemented plugin does.)
    The best solution here is to create the properties dynamically,
    and tell Gimp to add args from those dynamically created properties.
    """
    # This just conveys a sequence of undescribed args
    # TODO the intended design of Gimp is to convey types, but this doesn't
    # and the Gimp design is bogus
    def convey_using_static_property(self, procedure):
        """ Convey self to Gimp.
        Gimp wants All of self's attributes, or just type, default, limits?
        """

        prop_name = self._get_property_name_to_convey()
        self._set_property_attributes_to_match_self(prop_name)
        procedure.add_argument_from_property(FuFormalParam.prop_holder, prop_name)


    def convey_using_dynamic_property(self, procedure, index):
        """  Convey attributes of self to Gimp using a new created property.
        """
        param_spec = GObject.param_spec_int ("spacing",
                                       "spacing",
                                       "Spacing of the brush",
                                       1, 1000, 10,
                                       GObject.ParamFlags.READWRITE)
                                       # Gimp.GIMP_PARAM_READWRITE);
        self.install_property(index, param_spec)
        # Yields TypeError: argument pspec: Expected GObject.ParamSpec, but got gobject.GParamSpec
        procedure.add_argument_from_property(self, "spacing")


    def convey_using_dynamic_class_property(self, procedure, is_in_arg):
        """ convey self implemented using a short-lived instance having one property.

        Gimp docs say the instance should be a 'config' but it only needs to be any GObject
        """
        type = self._get_type()
        default = self.mangle_default()
        min, max = Extras.derive_min_max_from_extras(self.PF_TYPE, self.EXTRAS)
        property_name = self.gimp_name

        # OLD
        # produce an instance having a property with an arbitrary name, of given type
        # instance, property_name = FuFormalParam.prop_holder_factory.produce(type, default, min, max)

        # produce an instance having a property with the given attributes
        instance = FuFormalParam.prop_holder_factory.produce(property_name, type, default, min, max)

        """
        Call Gimp.Procedure.add_argument_from_property()
        That should return a GObject.ParamSpec.
        It does not seem to return None on an error.
        There are common errors:
           1. LibGimp warns if property of same name already exists.
           2. ??? later get _gimp_gp_param_def_to_param_spec: GParamSpec type 'GParamBoxed' is not handled
              for a layer property ??? TODO

        1. occurs if author chooses a name that is already a stock property name e.g. 'image'
        """

        self.logger.info(f"convey_using_dynamic_class_property, name: {property_name} ")
        if is_in_arg:
            paramspec = procedure.add_argument_from_property(instance, property_name)
            self.logger.debug(f"Paramspec for conveyed property: {paramspec}")
            assert(paramspec is not None)
        else:
            procedure.add_return_value_from_property(instance, property_name)

        #instance and property go out of scope i.e. they were short-lived

        # ensure the property was conveyed
        # TODO this is not correct, a formal arg was conveyed.  procedure.get_property(property_name)


    def convey_to_gimp(self, procedure, index, is_in_arg):
        """ Convey self as part of the signature of a GimpProcedure procedure.
        is_in_arg: whether formal arg is IN (an arg) or OUT (a return value)
        """
        self.logger.debug(f"convey_to_gimp: {self}")
        # TODO choice of implementation
        #self.convey_using_static_property(procedure)
        self.convey_using_dynamic_class_property(procedure, is_in_arg)
        #self.convey_using_dynamic_property(procedure, index)


    # TODO not necessary because Gimp accepts properties without defaults?
    # TODO but catch string valued literals for default value here?
    def mangle_default(self):
        """ Create Gimp types for certain defaults.
        PyGObject creates GObject types for most defaults.
        E.G. GimpFu allows tuples and string for Gimp.RGB
        """
        # TODO this crashes, and is not necessary
        if self.PF_TYPE in (PF_COLOR, PF_COLOUR):
            # result = FuColor.color_from_python_type(self.DEFAULT_VALUE)
            # TODO get the repr string for the author's given default value
            result = "Gimp.RGB()"
        else:
            result = self.DEFAULT_VALUE
        return result


    def _get_type(self):
        ''' Python type to represent self. '''
        result = map_PF_TYPE_to_python_type[self.PF_TYPE]

        # special case FBC
        if self.PF_TYPE == PF_RADIO and isinstance(self.DEFAULT_VALUE, str):
            # author intends string valued radio buttons
            result = str
        self.logger.info(f"_get_type: {result}")
        return result


"""
PF_TYPE enumerates a larger type
that specifies widget kind and format of extras.
"""

"""
Map PF_TYPE >> python type or Gimp type
Many to one.
!!! We return a string for Gimp types, not an instance of Type.

This is not entirely accurate.
v2 allowed PF_RADIO to be str or int type.
See special case

!!! If there are aliases, put only one here.
"""
map_PF_TYPE_to_python_type = {
    # fundamental types, with simple look-and-feel widgets
    PF_INT8:      int,
    PF_INT16:     int,
    PF_INT32:     int,
    PF_INT:       int,
    PF_FLOAT:     float,
    PF_STRING:    str,
    PF_VALUE:     int,
    PF_TEXT:      str,
    PF_BOOL:      int,
    # Gimp types, with chooser widgets, often Gimp widgets
    PF_COLOR:     "Gimp.RGB",  # tuple?
    PF_COLOUR:    "Gimp.RGB",
    PF_ITEM:      "Gimp.Item",
    PF_DISPLAY:   "Gimp.Display",
    PF_IMAGE:     "Gimp.Image",
    PF_LAYER:     "Gimp.Layer",
    PF_CHANNEL:   "Gimp.Channel",
    PF_DRAWABLE:  "Gimp.Drawable",
    PF_VECTORS:   "Gimp.Vectors",
    # constrained (by EXTRAS) fundamental types,
    # but with sophisticated look-and feel widgets
    # that do the constraining
    # PF_TOGGLE is alias for PF_BOOL
    PF_SLIDER:    float,
    PF_SPINNER:   float,
    # PF_ADJUSTMENT is alias for SPINNER
    PF_OPTION:    int,
    PF_RADIO:     int,
    # Gimp resource objects, identified by name of type str
    # !!! No Gimp type.
    # Sophisticated look-and_feel widgets provided by Gimp
    # Widgets all have .get_<foo> methods returning str
    PF_BRUSH:     str,
    PF_FONT:      str,
    PF_GRADIENT:  str,
    PF_PALETTE:   str,
    PF_PATTERN:   str,

    PF_FILE:      str,  # ??? GFile?
    PF_FILENAME:  str,
    PF_DIRNAME:   str,

    # Arrays of primitives (fixed size elements)
    PF_INT8ARRAY:          "Gimp.Uint8Array",    # ??? GObject.Array or GimpParamSpecUInt8Array
    PF_INT32ARRAY:         "Gimp.Int32Array",
    # PF_INTARRAY:           "Gimp.Array",
    PF_FLOATARRAY:         "Gimp.FloatArray",

    # Arrays of pointers to variable size elements
    # GIMP v2 used "Gimp.StringArray", GIMP v3 uses GStrv, a GLib type
    # PyGObject will bind a Python list to GStrv
    PF_STRINGARRAY:        list,    # "GStrv",

    # Arrays of pointers (fixed size) to Gimp objects
    # TODO how does this cross the wire protocol?
    PF_GIMP_OBJECT_ARRAY:  "Gimp.ObjectArray",
    PF_GIMP_RGB_ARRAY:     "Gimp.RGBArray",

    # Gimp.ValueArray  Only used to receive args and return values
    # No plugin author can use.
}
