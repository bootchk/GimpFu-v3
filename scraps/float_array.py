# cruft follows



"""
TODO gimp_param_array
@staticmethod
def new_gimp_float_array(float_list):
    '''
    '''
    value_array = Gimp.FloatArray.new(len(float_list))
    index = 0
    for x in float_list:
        gvalue = FuValueArray.new_gvalue(GObject.TYPE_FLOAT, x)
        value_array.insert(index, gvalue)
        index += 1

    return value_array
"""

'''
!!! GArray is not mentioned in some older GObject documents, only GValueArray
'''
@staticmethod
def new_g_array_of_float(float_list):
    ''' '''
    length = len(float_list)
    # size of each element: enough to hold a g_double
    # Not GObject.GArray
    g_array = GLib.GArray.new( True, True, )  # optimize: sized_new()
    for x in float_list:
        #gvalue = FuValueArray.new_gvalue(GObject.TYPE_FLOAT, x)
        g_array.append_val(x)
    print("new_g_array_of_float returns:", g_array)
    return g_array


'''
Just cast, hope that GI converts it?

'''
@staticmethod
def new_gimp_float_array(float_list):
    ''' Returns instance of Gimp.FloatArray initialized from a Python list of float '''

    # return float_list, Gimp.FloatArray
    # error: expect Boxed

    #return float_list, Gimp.GimpFloatArray
    # Failed to create Gimp.FloatArray: 'gi.repository.Gimp' object has no attribute 'GimpFloatArray'.

    return float_list, Gimp.FloatArray.__gtype__
    # >>>>GimpFu continued past error: Creating GValue for type: <GType GimpFloatArray (19639968)>, value: [1536.0, 0.0, 1536.0, 1984.0], err: Expected Boxed


"""
@staticmethod
def new_gimp_float_array(float_list):
    ''' Returns instance of Gimp.FloatArray initialized from a Python list of float '''

    #This not work, there is no constructor for Gimp.FloatArray
    #value_array = Gimp.FloatArray(len(float_list))

    # This not work:
    # Just return the list and cast it, hope that PyGObject really treats lists as Arrays
    # return float_list

    g_array = FuValueArray.new_g_array_of_float(float_list)

    gimp_float_array = Gimp.FloatArray.copy(g_array)
    print("new_gimp_float_array returns:", gimp_float_array)
    return gimp_float_array
"""
