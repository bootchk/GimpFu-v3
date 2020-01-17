
import gi
gi.require_version("Gimp", "3.0")
from gi.repository import Gimp



class Compat():
    '''
    Knows backward compatibility.

    And other hacky workarounds of limitations in Gimp
    ???
    '''

    def make_compatible_proc_name(name):
        '''
        1.  transliterate: names in PDB use hyphen for underbar
        2.  translate deprecated names
        '''
        hyphenized_name = name.replace( '_' , '-')

        # see Gimp commit  233ac80d "script-fu: port all scripts to the new gimp-drawable-edit functions "
        # 'gimp-threshold' : 'gimp-drawable-threshold',  needs param2 channel, and values in range [0.0, 1.0]
        deprecated_names_map = {
            "gimp-edit-fill" : "gimp-drawable-edit-fill",

        }

        if hyphenized_name in deprecated_names_map:
            result = deprecated_names_map[hyphenized_name]
            # TODO print new name
            print("GimpFu: Warning: Translating deprecated pdb name:", hyphenized_name)
        else:
            result = hyphenized_name

        '''
        if hyphenized_name == "gimp-edit-fill":
            result = "gimp-drawable-edit-fill"
        elif hyphenized_name == 'gimp-threshold':
            print("Deprecated pdb name:", hyphenized_name)
            result = 'gimp-drawable-threshold'
        else:
            result = hyphenized_name
        '''

        return result


    # TODO move this to marshal

    '''
    Seems like need for upcast is inherent in GObj.
    But probably Gimp should be doing most of the upcasting,
    so that many plugs don't need to do it.
    '''
    def try_upcast_to_drawable(arg):
        '''
        When type(arg) is subclass of Gimp.Drawable, up cast to Gimp.drawable
        and return new type, else return original type.

        Require arg a GObject (not wrapped)
        '''
        # idiom for class name
        print("Attempt up cast type", type(arg).__name__ )
        # Note the names are not prefixed with Gimp ???
        if type(arg).__name__ in ("Channel", "Layer"):  # TODO more subclasses
            result = Gimp.Drawable
        else:
            result = type(arg)
        print("upcast result:", result)
        return result
