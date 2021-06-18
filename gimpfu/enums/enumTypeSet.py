

import gi
gi.require_version("Gimp", "3.0")
from gi.repository import Gimp
# !!! We use Gimp in exec'd statements

from gimpfu.enums.gimpType import GimpType

import logging





class EnumTypeSet():
    """
    Knows the set of enum types defined in Gimp.
    Know how to generate statements to define symbols for the enumerated values.
    To help put enum types defined by Gimp into a Python global namespace.

    Checks them off.
    Knows which are not checked off.
    Wraps a dictionary.
    """

    def __init__(self):
        self.logger = logging.getLogger("GimpFu.EnumTypeSet")
        # !!! voluminous, so enable logging separately from GIMPFU_DEBUG
        # CRITICAL suppresses warnings about overwriting enums
        self.logger.setLevel(logging.CRITICAL)
        #self.logger.setLevel(logging.INFO)

        self.logger.info("GimpFu.EnumTypeSet.init")

        # Map from short, upper case enum name to its enum type.
        self.defined_enums = {}

        # map from GimpType of an enum to a boolean
        self.checked = {}
        for short_name in GimpType.list_gimp_enums():
            # assert name is a short name
            assert not "." in short_name
            self.checked[short_name] = False


    def checkOff(self, name):
        # assert name is short name
        assert not "." in name
        self.checked[name] = True


    def unchecked_names(self):
        """ Return dotted names for enum types not handled yet. """
        result = []
        for name in self.checked:
            # assert is dotted name
            if self.checked[name] == False:
                result.append(name)
        self.logger.info(f"unchecked_names {result}")
        return result

    def is_defined(self, enum_class_name, name):
        """ Side effect is keep separate list of defined enums. """
        result = name in self.defined_enums.keys()
        if result:
            self.logger.warning(f"Not overwriting: {enum_class_name} {name}, already defined: {self.defined_enums[name]} ")
        else:
            self.logger.debug(f"Defining enum: {name}")
            self.defined_enums[name] = enum_class_name
        return result


    """
    Methods that understand Python syntax for defining symbols.
    """
    def defining_statement_for_symbol(self, defined_name, enum_class_name, attribute):
        """
        Returns a string that is a Python statement that defines a symbol.

        Of form: defined_name = enum_class_name.attribute

        This will only be in the Python global namespace in case the caller execs it in main Python module.
        """
        result = defined_name + " = " + enum_class_name + "." + attribute
        self.logger.debug(f"enum defining_statement: {result}")
        return result

    """
    !!! This is complicated.
    globals()["foo"]=bar means the symbol goes into the namespace of the module that execs it,
    even if exec'ed inside a function of that module.
    But it does not put the symbol in the namespace of the top module,
    unless this module is imported into the top module
    and thus this statement execed at import time of the top module.
    """
    def defining_statement_for_global_symbol(self, defined_name, enum_class_name, attribute):
        """
        Returns a string that is a Python statement that defines a *global* symbol.

        Of form: > globals()["ADDITION_MODE"] = Gimp.LayerMode.ADDIITON <

        This will put the symbol in the Python global namespace
        even if the caller execs it inside a function.
        """
        result = 'globals()["' + defined_name + '"] = ' + enum_class_name + '.' + attribute
        self.logger.debug(f"defining_statement: {result}")
        return result


    # Generator
    # Note this calls the generator below, which checks for names already in globals
    def defining_statements_for_unchecked_enums(self):
        """ Return defining statements for all enumerated values in all unchecked enum types. """
        for name in self.unchecked_names():
            # assert name is short name
            try:
                enum_gtype = GimpType.type_from_short_name(name)
                for statement in self.defining_statements_for_enum(enum_gtype):
                    yield statement
            except Exception as err:
                self.logger.critical(f"Exception: {err}")
                pass


    # Generator
    def defining_statements_for_enum(self, enum, prefix="", suffix=""):
        '''
        Generate statements that will define
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
            CLIP_TO_IMAGE = Gimp.MergeType.CLIP_TO_IMAGE
            or globals()["CLIP_TO_IMAGE"] = Gimp.MergeType.CLIP_TO_IMAGE
        '''

        self.logger.debug(f"define_symbols_for_enum {enum}")
        # prints: <class 'gi.repository.Gimp.LayerMode'>

        enum_class_name = GimpType.dotted_name_of_type(enum)
        enum_short_name = GimpType.short_name_of_dotted_name(enum_class_name)
        self.checkOff(enum_short_name)

        # search the names in the dir of the enum type
        for attribute in dir(enum):
            # Crudity: assume anything upper case is what we want.
            if attribute.isupper():
                # Form a name like RGB_WHITE_ENUM
                defined_name = prefix + attribute + suffix

                # !!! alternative is: defining_statement_for_global_symbol
                defining_statement = self.defining_statement_for_symbol(defined_name, enum_class_name, attribute)
                # !!! a reference to Gimp is in the defining_statement, must import Gimp

                # Skip defining statements for names already in the global namespace
                # if not is_defined_in_top_globals(enum_class_name, defined_name):
                if not self.is_defined(enum_short_name, defined_name):
                    yield(defining_statement)

                """
                Depending on which method is called to make the statement,
                the statement by itself might not put the symbol in the global namespace,
                but might depend on the caller exec'ing the statement in the top module.
                (not just the global namespace of this or some other module).

                Note we don't exec the statement here.

                Note that : exec(defining_statement, globals()) doesn't put the symbol
                in the global namespace, only passes globals() to the exec method.
                """
            else:
                # Log is almost useless since it includes all the __dunders__ and functions
                # self.logger.warning(f"GIMP enum name not uppper case: {attribute}")
                pass
