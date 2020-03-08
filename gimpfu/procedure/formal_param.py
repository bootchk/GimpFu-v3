
class FuFormalParam():


    '''
    Constant class data
    '''
    # Temp hack ???
    from procedure.prop_holder import PropHolder
    prop_holder = PropHolder()
    print("prop_holder.props", prop_holder.props)
    print("prop_holder.props.IntProp:", prop_holder.props.IntProp)



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


    # This just conveys a sequence of undescribed args
    # TODO the intended design of Gimp is to convey types, but this doesn't
    # and the Gimp design is bogus
    def convey_using_static_property(self, procedure):
        """ Use same property over and over to convey. """
        procedure.add_argument_from_property(FuFormalParam.prop_holder, "IntProp")

    # TODO map PF_TYPE to types known to Gimp (a smaller set)
    # use named properties of prop_holder

    def convey_to_gimp(self, procedure):
        """ Convey self as formal arg to GimpProcedure procedure. """
        self.convey_using_static_property(procedure)
