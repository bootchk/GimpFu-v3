
from collections.abc import Mapping


'''
Knows backward compatibility for Gimp changes.
Gimp versions infrequently:
    rename functions  (most often)
    condense many functions into one
    migrate functions from one class to another

And other hacky workarounds of limitations in Gimp
???
'''




class GimpFuMap(Mapping):
    '''
    A wrapper around dictionary.
    Read-only, wraps a static dictionary.
    I.E. access uses dictionary syntax:  new_name = compat[name]

    Subclasses may do additional alterations to name.

    Implemented by inheriting ABC collections.Mapping,
    which is also read-only
    '''

    def __init__(self, map):
        # replace wrapped dict
        self.__dict__ = map

    '''
    Implement abstract methods of Mapping
    '''
    def __getitem__(self, key):
        '''
        CRUX:
        If the key is not in the wrapped dictionary, return unmapped key
        And print a warning.
        '''
        # TODO implement with except KeyError: would be faster?
        if key in self.__dict__.keys():
            # TODO use warning module
            print("GimpFu: Warning: Translating deprecated name:", key)
            return self.__dict__[key]
        else:
            return key



    def __iter__(self):
        raise NotImplementedError("Compat iterator.")
    def __len__(self):
        raise NotImplementedError("Compat len()")

    '''
    Not required by ABC.
    '''
    def __repr__(self):
        return 'GimpFuMap'
        """
        TODO use this snippet
        '''echoes class, id, & reproducible representation in the REPL'''
        return '{}, D({})'.format(super(D, self).__repr__(),
                                  self.__dict__)
        """


class GimpFuPDBMap(GimpFuMap):
    '''
    Specialize GimpFuMap for the Gimp PDB.

    Alter all mapped names: transliterate
    The names in the PDB use hyphens, which Python does not allow in symbols.
    Super() will proceed to map deprecated names.
    '''
    def __getitem__(self, key):
        hyphenized_key = key.replace( '_' , '-')
        # !!! The map must use hyphenated strings
        return super().__getitem__(hyphenized_key)




# see Gimp commit  233ac80d "script-fu: port all scripts to the new gimp-drawable-edit functions "
# 'gimp-threshold' : 'gimp-drawable-threshold',  needs param2 channel, and values in range [0.0, 1.0]

pdb_renaming = {
    "gimp-edit-fill" : "gimp-drawable-edit-fill",
}

gimp_renaming = {}

# TODO maybe these become undo_renaming i.e. calls to Gimp.Undo.disable?
image_renaming = {
    'disable_undo' : "undo_disable",
}


'''
One map for each Gimp object that GimpFu wraps
'''
pdb_name_map = GimpFuPDBMap(pdb_renaming);
gimp_name_map = GimpFuMap(gimp_renaming);
image_name_map = GimpFuMap(image_renaming);
# todo layer, etc
