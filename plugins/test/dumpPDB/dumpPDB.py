#!/usr/bin/env python3
# lkk add hashbang

'''
A test Gimp plugin that:
- dumps the PDB to a file in JSON format
'''

from gimpfu import *

import gi
from gi.repository import Gio

# import os

import gio


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

    for name in generateProcNames():
        print(name)

    # Temp hack: test a PDB procedure taking a GStrv
    pdb.file_gih_save(image, 1, (drawable,), "/work/tmp", 10, "foo", 1, 1, 1, 1, 1, (1,), 1, ("bar", "zed"))


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
      "Dump PDB in JSON to /work/pdb.json",
      "*",
      [
          (PF_IMAGE, "image", "Input image", None),
          (PF_DRAWABLE, "drawable", "Input drawable", None),
      ],
      [],
      plugin_func,
      menu="<Image>/Test")
main()
