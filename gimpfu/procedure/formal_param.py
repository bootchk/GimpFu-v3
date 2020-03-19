

import gi
from gi.repository import GObject

from gimpfu_enums import *



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
    from procedure.prop_holder import PropHolder
    prop_holder = PropHolder()
    print("prop_holder.props", prop_holder.props)
    print("prop_holder.props.IntProp:", prop_holder.props.IntProp1)



    def __init__(self, pf_type, label, desc, default_value, extras = [] ):
        self.PF_TYPE= pf_type
        self.LABEL= label
        self.DESC= desc
        self.DEFAULT_VALUE= default_value
        self.EXTRAS = extras
        # EXTRAS defaults to empty list or ???  [None]  Python 3.7


    def __repr__(self):
        """ Not a true repr. """
        return str("PF: " + str(self.PF_TYPE) + self.DESC)


    @property
    def tooltip_text(self):
        # Remove accelerator markers from tooltips
        return self.DESC.replace("_", "")

    @property
    def label(self):
        """
        v2 LABEL was used.
        v2 LABEL typically, but not required, matches run_func actual arg name.

        Since v3, LABEL is now a gproperty name and can't have spaces.
        Use DESC instead.
        Which means the tooltip is the same as the label, for GimpFu v3.
        Gimp allows a separate tooltip????
        """
        return self.DESC

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
           type = map_PF_TYPE_to_type[self.PF_TYPE]
           result = FuFormalParam.prop_holder.next_prop_name(type)
       # OR build a dynamic property that describes self
       return result

    def _set_property_attributes_to_match_self(self, prop_name):
         """
         Put self attributes in property attributes.
         """
         # TODO when Pygobject is fixed
         # FuFormalParam.prop_holder.set_property(prop_name, self.DEFAULT_VALUE)    # default value
         pass



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


    def convey_to_gimp(self, procedure, index):
        """ Convey self as formal arg to GimpProcedure procedure. """
        # TODO get dynamic property to work
        self.convey_using_static_property(procedure)
        #self.convey_using_dynamic_property(procedure, index)


"""
PF_TYPE >> python type or Gimp type
Many to one.
PF_TYPE enumerates widget kind.
"""
map_PF_TYPE_to_type = {
    PF_INT8:      int,
    PF_INT16:     int,
    PF_INT32:     int,
    PF_INT:       int,
    PF_FLOAT:     float,
    PF_STRING:    str,
    PF_VALUE:     int,
    PF_COLOR:     int,  # tuple?
    PF_COLOUR:    int,
    PF_ITEM:      int,
    PF_DISPLAY:   int,
    PF_IMAGE:     int,
    PF_LAYER:     int,
    PF_CHANNEL:   int,
    PF_DRAWABLE:  int,
    PF_VECTORS:   int,
    PF_TOGGLE:    int,
    PF_BOOL:      int,
    PF_SLIDER:    float,
    PF_SPINNER:   float,
    PF_ADJUSTMENT: int,
    PF_FONT:      str,
    PF_FILE:      str,  # ??? GFile?
    PF_BRUSH:     int,
    PF_PATTERN:   int,
    PF_GRADIENT:  int,
    PF_RADIO:     int,
    PF_TEXT:      str,
    PF_PALETTE:   int,
    PF_FILENAME:  str,
    PF_DIRNAME:   str,
    PF_OPTION:    int,
}
