'''
A test Gimp plugin
that:
- tests pdb procedures that load files named file_foo_load()
'''

from gimpfu import *


def create_test_filename_for_format(format):
    return "/work/test/test." + format

def plugin_func(image, drawable, file_format):

      if file_format == 0 :
          file = create_test_filename_for_format("pdf")
          image =  pdb.file_pdf_load(file, file)
      elif file_format == 1 :
          file = create_test_filename_for_format("jpg")
          image =  pdb.file_jpeg_load(file, file)
      elif file_format == 2 :
           file = "/work/test/test.gif"
           image =  pdb.file_gif_load(file, file)
      else:
          raise Exception("Unhandled format case")

      image_display = pdb.gimp_display_new (image)
      gimp.displays_flush()

register(
      "python-fu-test-file-load",
      "blurb",
      "help message",
      "author",
      "copyright",
      "year",
      "File load...",
      "",
      [
          (PF_IMAGE, "image", "Input image", None),
          (PF_DRAWABLE, "drawable", "Input drawable", None),
          (PF_OPTION, "format", "Format", 0, ("pdf", "jpeg", "gif" )),
      ],
      [],
      plugin_func,
      menu="<Image>/Test")
main()
