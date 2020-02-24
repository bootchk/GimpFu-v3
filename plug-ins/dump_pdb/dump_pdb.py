'''
A test Gimp plugin that:
- dumps the PDB to a file
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
        print(">>>>Failed to create /tmp/pdb.txt")
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
    return f

def plugin_func(image, drawable):

    # filename = '/tmp/pdb.txt'
    filename = '/work/pdb.txt'

    # ?create the file, since Gio.file_new_for_path will not create a file?

    f = get_gfile(filename)

    '''
    !!! See the API at "PyGObject API Reference, which is the most up-to-date"
    There exist many dated examples on the net.
    '''
    # Fails: FILE_QUERY_INFO_NONE
    # info = f.query_info('standard::type,standard::size', flags=Gio.FILE_QUERY_INFO_NOFOLLOW_SYMLINKS, cancellable=None)
    # info = f.query_info('standard::type,standard::size', flags=None, cancellable=None)
    info = f.query_info('standard::type,standard::size', flags=Gio.FileQueryInfoFlags.NONE, cancellable=None)

    print(f"File type is: {info.get_file_type()}")

    result = gimp.get_pdb().dump_to_file(f)
    if result:
      print(f"Success: file name: {filename}")
    else:
      print(">>>>Failed to dump")






register(
      "dump-pdb",
      "blurb",
      "help message",
      "author",
      "copyright",
      "year",
      "Dump PDB to /tmp/pdb.txt",
      "*",
      [
          (PF_IMAGE, "image", "Input image", None),
          (PF_DRAWABLE, "drawable", "Input drawable", None),
      ],
      [],
      plugin_func,
      menu="<Image>/Test")
main()
