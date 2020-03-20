

import gi
gi.require_version("Gimp", "3.0")
from gi.repository import Gimp


# absolute from SYSPATH that points to top of gimpfu package
from adaption.adapter import Adapter


'''

Adapts (wraps) Gimp.Image.

Constructor appears in GimpFu plugin code as e.g. : gimp.Image(w, h, RGB)
I.E. an attribute of gimp instance (see aliases/gimp.py.)

In v2, similar concept implemented by pygimp-image.c
Since v3, implemented in Python using GI.

FBC all specialized methods here should match the implementation in pygimp-image.c v2.

Method kinds:
Most have an identical signature method in Gimp.Image. (delegated)
Some have changed signature here, but same action as in Gimp.Image. (convenience)
Some are unique to PyGimp, not present in Gimp.Image. (augment)
    - methods
    - properties (data members)
    TODO do we need to wrap property get/set
'''






class GimpfuImage( Adapter ) :


    '''
    classmethods needed by Adapter

    Notes:
    filename is NOT canonical property of Image, in Gimp v3.  See get_name()
    '''
    @classmethod
    def DynamicWriteableAdaptedProperties(cls):
        return ( 'active_layer', )

    # Name of getter() func is property name prefixed with 'get_'
    @classmethod
    def DynamicReadOnlyAdaptedProperties(cls):
        return ('selection',  'layers', 'vectors')

    # True: name of getter() func is same as name of property
    @classmethod
    def DynamicTrueAdaptedProperties(cls):
        return ('width', 'height', 'base_type')

    # Method name on adaptee is mapped
    @classmethod
    def DynamicMappedMethods(cls):
        return  {
                'disable_undo'         : 'undo_disable',
                'enable_undo'          : 'undo_enable',
                'freeze_undo'          : 'undo_freeze',
                }




    '''
    Constructor exported to s.
    Called internally for existing images as GimpfuImage(None, None, None, adaptee)

    See SO "How to overload __init__ method based on argument type?"
    '''
    def __init__(self, width=None, height=None, image_mode=None, adaptee=None):
        '''Initialize  GimpfuImage from attribute values OR instance of Gimp.Image. '''
        if width is None:
            final_adaptee = adaptee
        else:
            # Gimp constructor named "new"
            print("Calling Gimp.Image.new with width", width)
            final_adaptee = Gimp.Image.new(width, height, image_mode)

        # super is Adaper, and it stores adaptee
        super().__init__(final_adaptee)



    # TODO Not needed ??
    def adaptee(self):
        ''' Getter for private _adaptee '''
        # Handled by super Adaptor
        result = self._adaptee
        print("adaptee getter returns:", result)
        return result




    '''
    WIP
    Overload constructors using class methods.
    # Hidden constructor
    @classmethod
    def fromAdaptee(cls, adaptee):
         "Initialize GimpfuImage from attribute values"

         return cls(data
    '''


    '''
    Specialized methods and properties.
    Reason we must specialize is the comment ahead of each property
    '''


    # Methods


    def _mangle_layer_args(self, layer, parent, position):
        """
        A hack to allow (layer, position) signature,
        which apparently is a very old signature.
        """
        if position == -1 and parent is not None:
            # swap passed parent into the position arg
            result = (layer, None, parent)
        else:
            result = (layer, parent, position)
        return result


    # Reason: allow optional args
    def insert_layer(self, layer, parent=None, position=-1):
        print("insert_layer called")

        layer, parent, position = self._mangle_layer_args(layer, parent, position)
        # Note that first arg "image" to Gimp comes from self
        success = self._adaptee.insert_layer(layer.unwrap(), parent, position)
        if not success:
            raise Exception("Failed insert_layer")

    # Reason: allow optional args, rename
    def add_layer(self, layer, parent=None, position=-1):
        print("add_layer called")
        layer, parent, position = self._mangle_layer_args(layer, parent, position)
        success = self._adaptee.insert_layer(layer.unwrap(), parent, position)
        if not success:
            raise Exception("Failed add_layer")



    '''
    Properties
    '''

    """
    # CRUFT, is a dynamic read-only property now
    @property
    def vectors(self):
        # avoid circular import, import when needed
        from adaption.marshal import Marshal

        unwrapped_list = self._adaptee.get_vectors()
        result_list = Marshal.wrap_args(unwrapped_list)
        return result_list
    """



    """
    !!! This is not correct, since get_file() can return None.
    file = self._adaptee.get_file()
    # assert file is-a Gio.File
    result = file.get_path()
    """
    @property
    def filename(self):
        '''
        Returns string that is path to file the image was saved to.
        Returns "Untitled" if image not loaded from file, or not saved.
        '''
        # print("GimpfuImage.filename get called")
        # sic Image.get_name returns a filepath
        result = self._adaptee.get_name()
        return result
