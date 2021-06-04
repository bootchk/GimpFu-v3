#!/usr/bin/env python3
'''
A test Gimp plugin that:
- dumps the PDB to a file in JSON format

Here we generate JSON that is all string valued (no numeric literals on right hand side.)

Suitable for documentation. You can use nawk to manipulate it, if the strings are not what you want.

See libgimp/gimpprocview.c, from which this is derived/lifted
'''

from gimpfu import *

import gi
from gi.repository import Gio
# import gio

import json

def create_file(filename):
    with open(filename, 'w+') as file:
        file.write(" ")
    # assert file exists but is closed
    print(f"Created file {filename}")


def get_gfile(filename):
    # create a GObject file descriptor
    gfile =  Gio.file_new_for_path(filename)
    if gfile is None:
        print(f">>>>Failed to create {filename}")
        return None
    else:
        return gfile


def get_gfile2(filename):
    '''
    Here we use the gio.File class of PyGObject
    '''
    f = Gio.File(path=filename)
    f = Gio.File(uri=filename)
    # Both fails with NotImplementedError: File can not be constructed
    # Maybe it is GLib.File ????
    return f


def print_filetype(file):
    # Fails: FILE_QUERY_INFO_NONE
    # info = f.query_info('standard::type,standard::size', flags=Gio.FILE_QUERY_INFO_NOFOLLOW_SYMLINKS, cancellable=None)
    # info = f.query_info('standard::type,standard::size', flags=None, cancellable=None)
    info = file.query_info('standard::type, standard::size', flags=Gio.FileQueryInfoFlags.NONE, cancellable=None)

    print(f"File type is: {info.get_file_type()}")


def generateProcNames():
    names = pdb.gimp_pdb_query(".*", ".*", ".*", ".*", ".*", ".*", ".*", )
    for name in names:
        yield name

'''
Flawed signatures of getters in the PDB:

gimp-pdb-get-proc-argument ( gchararray gint ) =>
gimp-pdb-get-proc-attribution ( gchararray ) => gchararray gchararray gchararray
gimp-pdb-get-proc-documentation ( gchararray ) => gchararray gchararray gchararray
gimp-pdb-get-proc-image-types ( gchararray ) => gchararray
gimp-pdb-get-proc-info ( gchararray ) => GimpPDBProcType gint gint
gimp-pdb-get-proc-menu-label ( gchararray ) => gchararray
gimp-pdb-get-proc-menu-paths ( gchararray ) => gint GimpStringArray
gimp-pdb-get-proc-return-value ( gchararray gint ) =>
'''

def procedureType(procName):
    """ Returns short name for procedure type. """
    type, countArgs, countReturnValues = pdb.gimp_pdb_get_proc_info(procName)

    # Assert type is-a Gimp.PDBProcType
    # Since it is a GObject.GEnum, has property value_name
    # Or you can use:  if type == Gimp.PDBProcType.INTERNAL:

    # Shorten the name
    return type.value_name.replace("GIMP_PDB_PROC_TYPE_", "")



def getDictForParam(param):
    """
    Return a dict for a GObject.ParamSpec (by inheritance)
    E.G. is-a GimpParamImage
    """
    print(f"Param: {param}")
    print(f"Param type: {type(param)}")

    dict = {}
    dict["name"]    = param.name
    dict["type"]    = param.value_type.name  # GType

    # TODO not working
    # param is an instance, but get_blurb is a method on the class?
    #dict["blurb"]   = param.get_blurb()
    #dict["blurb"]   = param.gtype_get_type().get_blurb()
    # TODO default must be dispatched on subclass of GParamSpec

    # dict["default"] = param.get_default_value()
    return dict



def getDictForReturnValue(procName, argIndex):
    param = pdb.gimp_pdb_get_proc_return_value(procName, argIndex)
    return getDictForParam(param)

def getDictForInArg(procName, argIndex):
    param = pdb.gimp_pdb_get_proc_argument(procName, argIndex)
    return getDictForParam(param)



def getListOfArgsForProc(procName):
    """ Return ordered list of in args. """
    _type, countArgs, _countReturnValues = pdb.gimp_pdb_get_proc_info(procName)
    list = []
    for i in range(countArgs):
        list.append( getDictForInArg(procName, i))
    return list


def getListOfReturnValuesForProc(procName):
    """ Return ordered list of in args. """
    _type, _countArgs, countReturnValues = pdb.gimp_pdb_get_proc_info(procName)
    list = []
    for i in range(countReturnValues):
        list.append( getDictForReturnValue(procName, i))
    return list


def addKeywordsForMenuPaths(dict, procName):
    list = []
    paths = pdb.gimp_pdb_get_proc_menu_paths(procName)
    for path in paths:
        list.append(path)
    dict["menu paths"]  = list


def addKeywordsForPlugin(dict, procName):
    dict["menu label"]  = pdb.gimp_pdb_get_proc_menu_label(procName)
    addKeywordsForMenuPaths(dict, procName)
    dict["image types"] = pdb.gimp_pdb_get_proc_image_types(procName)
    dict["help"] = pdb.gimp_pdb_get_proc_documentation(procName)[0]


def getDictForProc(procName):
    """ Generate Python dictionary for a PDB proc """

    type = procedureType(procName)

    # Every procedure has name and type
    dict = {
        "name"        : procName,
        "type"        : type,
        }

    # Dict varies by type
    # "INTERNAL", EXTENSION, TEMPORARY :
    if type == "PLUGIN":
        addKeywordsForPlugin(dict, procName)

    dict["args"]          = getListOfArgsForProc(procName)
    dict["return values"] = getListOfReturnValuesForProc(procName)

    return dict


def getJSONForProc(procName):
    """ Generate JSON text for a PDB proc """
    # create a Python data struct composed using structs that JSON supports.
    dict = getDictForProc(procName)
    # pretty print
    return json.dumps(dict, indent=4)   # sort_keys=True,


def plugin_func(image, drawable):

    # filename = '/tmp/pdb.txt'
    filename = '/work/pdb.txt'

    # ?create the file, since Gio.file_new_for_path will not create a file?

    f = get_gfile(filename)

    # ??? can't get_info if not exist???  Easy enough to "touch pdb.txt" before starting
    # print_filetype(f)

    '''
    !!! See the API at "PyGObject API Reference, which is the most up-to-date"
    There exist many dated examples on the net.
    '''
    i = 0
    for name in generateProcNames():
        jsonText = getJSONForProc(name)
        print(jsonText)

        i += 1
        if i > 10:
            break   # Only the first one

    # Temp hack: test a PDB procedure taking a GStrv
    # pdb.file_gih_save(image, 1, (drawable,), "/work/tmp", 10, "foo", 1, 1, 1, 1, 1, (1,), 1, ("bar", "zed"))


    result = "foo"  # TODO create JSON text, put it in file

    print(result)
    if result:
      print(f"Success: file name: {filename}")
    else:
      print(">>>>Failed to dump")






register(
      "plug-in-dump-pdb-json",
      "blurb",
      "help message",
      "author",
      "copyright",
      "year",
      "Dump PDB to a JSON file",
      "*",
      [
          (PF_IMAGE, "image", "Input image", None),
          (PF_DRAWABLE, "drawable", "Input drawable", None),
      ],
      [],
      plugin_func,
      menu="<Image>/Test")
main()
