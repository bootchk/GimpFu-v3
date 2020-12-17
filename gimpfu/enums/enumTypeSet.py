

import gi
gi.require_version("Gimp", "3.0")
from gi.repository import Gimp
# !!! We use Gimp in exec'd statements

from enums.gimpType import GimpType

import logging




class EnumWrangler():
    """
    Knows how to put enum types defined by Gimp into the Python global namespace.

    Checks them off.
    Knows which are not checked off.
    """

    def __init__(self):
        self.logger = logging.getLogger("GimpFu.EnumWrangler")
        self.checked = {}
        for name in GimpType.list_gimp_enums():
            self.checked[name] = False


    def checkOff(self, name):
        # assert name is dotted name
        self.checked[name] = True


    def unchecked_names(self):
        """ Return dotted names for enum types not handled yet. """
        result = []
        for name in self.checked:
            # assert is dotted name
            if self.checked[name] == False:
                result.append(name)
        self.logger.info(f"unchecked_names {result}")    # TODO info
        return result


    def define_symbols_for_unchecked_enums(self):
        for name in self.unchecked_names():
            # assert name is short name
            try:
                enum_gtype = GimpType.type_from_short_name(name)
                self.define_symbols_for_enum(enum_gtype)
            except Exception as err:
                self.logger.critical(f"Exception: {err}")
                pass



    def define_symbols_for_enum(self, enum, prefix="", suffix=""):
        '''
        Define into the GimpFu Python global namespace:
        all the constants defined by enum.
        Require enum is a Gimp type.
        enum is-a class.  type(enum) == 'type'

        Also, for backward compatibility, prefix and suffix with given strings.
        Prepend with prefix, or suffend with suffix, where not None.
        Note there was not much consistency in v2: some prefixed, some suffixed.

        This is metaprogramming.
        We are not directly defining the names in this Python text,
        we are inserting the names into the namespace (i.e. dir ).

        Example:
        enum is Gimp.HistogramChannel
        Statements:
            global CLIP_TO_IMAGE
            CLIP_TO_IMAGE = Gimp.MergeType.CLIP_TO_IMAGE
        '''

        self.logger.debug(f"define_symbols_for_enum {enum}")
        # prints: <class 'gi.repository.Gimp.LayerMode'>

        enum_class_name = GimpType.dotted_name_of_type(enum)

        self.checkOff(enum_class_name)

        # search the names in the dir of the enum
        for attribute in dir(enum):
            # Crudity: assume anything upper case is what we want.
            if attribute.isupper():
                defined_name = prefix + attribute + suffix
                defining_statement = defined_name + " = " + enum_class_name + "." + attribute
                # !!! a reference to Gimp is in the defining_statement, must import Gimp
                #print(defining_statement)

                # Ensure its not already in the global namespace
                if defined_name in globals():
                    self.logger.info(f"Not overwriting enum symbol already in globals: {enum_class_name} {defined_name}")
                else:
                    self.logger.debug(f"Defining in globals: {defined_name}")

                # Second argument insures definition goes into global namespace
                # See Python docs for exec()
                exec(defining_statement, globals())
