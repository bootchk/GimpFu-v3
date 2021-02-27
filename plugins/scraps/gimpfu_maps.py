
# Just OLD CODE from v2

'''
lkk temporary comment out
PF_INT8        = PDB_INT8
PF_INT16       = PDB_INT16
PF_INT32       = PDB_INT32
PF_INT         = PF_INT32
PF_FLOAT       = PDB_FLOAT
PF_STRING      = PDB_STRING
PF_VALUE       = PF_STRING
#PF_INT8ARRAY   = PDB_INT8ARRAY
#PF_INT16ARRAY  = PDB_INT16ARRAY
#PF_INT32ARRAY  = PDB_INT32ARRAY
#PF_INTARRAY    = PF_INT32ARRAY
#PF_FLOATARRAY  = PDB_FLOATARRAY
#PF_STRINGARRAY = PDB_STRINGARRAY
PF_COLOR       = PDB_COLOR
PF_COLOUR      = PF_COLOR
PF_ITEM        = PDB_ITEM
PF_DISPLAY     = PDB_DISPLAY

PF_IMAGE       = pdb.PDB_IMAGE

PF_LAYER       = PDB_LAYER
PF_CHANNEL     = PDB_CHANNEL
PF_DRAWABLE    = PDB_DRAWABLE
PF_VECTORS     = PDB_VECTORS
#PF_SELECTION   = PDB_SELECTION
#PF_BOUNDARY    = PDB_BOUNDARY
#PF_PATH        = PDB_PATH
#PF_STATUS      = PDB_STATUS

PF_TOGGLE      = 1000
PF_BOOL        = PF_TOGGLE
PF_SLIDER      = 1001
PF_SPINNER     = 1002
PF_ADJUSTMENT  = PF_SPINNER

PF_FONT        = 1003
PF_FILE        = 1004
PF_BRUSH       = 1005
PF_PATTERN     = 1006
PF_GRADIENT    = 1007
PF_RADIO       = 1008
PF_TEXT        = 1009
PF_PALETTE     = 1010
PF_FILENAME    = 1011
PF_DIRNAME     = 1012
PF_OPTION      = 1013

_type_mapping = {
    PF_INT8        : PDB_INT8,
    PF_INT16       : PDB_INT16,
    PF_INT32       : PDB_INT32,
    PF_FLOAT       : PDB_FLOAT,
    PF_STRING      : PDB_STRING,
    #PF_INT8ARRAY   : PDB_INT8ARRAY,
    #PF_INT16ARRAY  : PDB_INT16ARRAY,
    #PF_INT32ARRAY  : PDB_INT32ARRAY,
    #PF_FLOATARRAY  : PDB_FLOATARRAY,
    #PF_STRINGARRAY : PDB_STRINGARRAY,
    PF_COLOR       : PDB_COLOR,
    PF_ITEM        : PDB_ITEM,
    PF_DISPLAY     : PDB_DISPLAY,
    PF_IMAGE       : PDB_IMAGE,
    PF_LAYER       : PDB_LAYER,
    PF_CHANNEL     : PDB_CHANNEL,
    PF_DRAWABLE    : PDB_DRAWABLE,
    PF_VECTORS     : PDB_VECTORS,

    PF_TOGGLE      : PDB_INT32,
    PF_SLIDER      : PDB_FLOAT,
    PF_SPINNER     : PDB_INT32,

    PF_FONT        : PDB_STRING,
    PF_FILE        : PDB_STRING,
    PF_BRUSH       : PDB_STRING,
    PF_PATTERN     : PDB_STRING,
    PF_GRADIENT    : PDB_STRING,
    PF_RADIO       : PDB_STRING,
    PF_TEXT        : PDB_STRING,
    PF_PALETTE     : PDB_STRING,
    PF_FILENAME    : PDB_STRING,
    PF_DIRNAME     : PDB_STRING,
    PF_OPTION      : PDB_INT32,
}

_obj_mapping = {
    PF_INT8        : int,
    PF_INT16       : int,
    PF_INT32       : int,
    PF_FLOAT       : float,
    PF_STRING      : str,
    #PF_INT8ARRAY   : list,
    #PF_INT16ARRAY  : list,
    #PF_INT32ARRAY  : list,
    #PF_FLOATARRAY  : list,
    #PF_STRINGARRAY : list,
    PF_COLOR       : gimpcolor.RGB,
    PF_ITEM        : int,
    PF_DISPLAY     : gimp.Display,
    PF_IMAGE       : gimp.Image,
    PF_LAYER       : gimp.Layer,
    PF_CHANNEL     : gimp.Channel,
    PF_DRAWABLE    : gimp.Drawable,
    PF_VECTORS     : gimp.Vectors,

    PF_TOGGLE      : bool,
    PF_SLIDER      : float,
    PF_SPINNER     : float,

    PF_FONT        : str,
    PF_FILE        : str,
    PF_BRUSH       : str,
    PF_PATTERN     : str,
    PF_GRADIENT    : str,
    PF_RADIO       : str,
    PF_TEXT        : str,
    PF_PALETTE     : str,
    PF_FILENAME    : str,
    PF_DIRNAME     : str,
    PF_OPTION      : int,
}
end lkk comment out
'''


'''
Map PF_TYPE to WidgetFactoryMethod
'''

"""
_edit_mapping = {
        PF_INT8        : IntEntry,
        PF_INT16       : IntEntry,
        PF_INT32       : IntEntry,
        PF_FLOAT       : FloatEntry,

        PF_INT         : IntEntry,
        PF_STRING      : StringEntry,

        #PF_INT8ARRAY   : ArrayEntry,
        #PF_INT16ARRAY  : ArrayEntry,
        #PF_INT32ARRAY  : ArrayEntry,
        #PF_FLOATARRAY  : ArrayEntry,
        #PF_STRINGARRAY : ArrayEntry,
        PF_COLOR       : gimpui.ColorSelector,
        PF_ITEM        : IntEntry,  # should handle differently ...
        PF_IMAGE       : gimpui.ImageSelector,
        PF_LAYER       : gimpui.LayerSelector,
        PF_CHANNEL     : gimpui.ChannelSelector,
        PF_DRAWABLE    : gimpui.DrawableSelector,
        PF_VECTORS     : gimpui.VectorsSelector,

        PF_TOGGLE      : ToggleEntry,
        PF_SLIDER      : SliderEntry,
        PF_SPINNER     : SpinnerEntry,
        PF_RADIO       : RadioEntry,
        PF_OPTION      : ComboEntry,

        PF_FONT        : gimpui.FontSelector,
        PF_FILE        : FileSelector,
        PF_FILENAME    : FilenameSelector,
        PF_DIRNAME     : DirnameSelector,
        PF_BRUSH       : gimpui.BrushSelector,
        PF_PATTERN     : gimpui.PatternSelector,
        PF_GRADIENT    : gimpui.GradientSelector,
        PF_PALETTE     : gimpui.PaletteSelector,
        PF_TEXT        : TextEntry
}
"""
