'''
A test Gimp plugin
that:
dump libgimp enum type names
'''

from gimpfu import *

import gi
from gi.repository import GLib
from gi.repository import GObject

"""
Code derived from scheme-wrapper.c
IOW, similar to what ScriptFu does.
"""

def putEnumInNamespace(enum_type):
    """ Put enumerated names of gtype into the global namespace.

    See ts_init_enum() of scriptfu/scheme-wrapper.c

    See Gimp 2.10/plugins/pygimp/gimpenumsmodule.c
    Which used the old pygobject and pyg_enum_add_constants()
    """

    # Make sure the class exists
    #enum_class = GLib.g_type_class_ref (enum_type);
    #for value in enum_class.values():

    #GObject.TypeClass?? ObjectClass ???
    print(f"Has value table: {enum_type.has_value_table()}")

    # Get qdata, is for compatibility???
    quark = GLib.quark_from_static_string ("gimp-compat-enum")
    otherTypeName = GObject.type_get_qdata (enum_type, quark)
    if (otherTypeName !=0):
        print(f"Other type: {otherTypeName}")

    """
    We don't need to use GObject: the names are already in Python.
    """
    # Look up values
    # Fail: need GObject.EnumClass, to gobject.GType
    # value = GObject.enum_get_value(enum_type, 0)



    # GObject.EnumClass is array of GObject.EnumValue.value_name



    '''
    {
      GEnumClass  *enum_class = g_type_class_ref (enum_type);
      GEnumValue  *value;

      for (value = enum_class->values; value->value_name; value++)
        {
          if (g_str_has_prefix (value->value_name, "GIMP_"))
            {
              gchar   *scheme_name;
              pointer  symbol;

              scheme_name = g_strdup (value->value_name + strlen ("GIMP_"));
              convert_string (scheme_name);

              symbol = sc->vptr->mk_symbol (sc, scheme_name);
              sc->vptr->scheme_define (sc, sc->global_env, symbol,
                                       sc->vptr->mk_integer (sc, value->value));
              sc->vptr->setimmutable (symbol);

              g_free (scheme_name);
            }
        }

      g_type_class_unref (enum_class);
    }
    '''
    return

def getGimpEnums():
    names, count_names = gimp.enums_get_type_names()
    # [[name1,...], count_names]

    for enum_type_name in names:
        print (enum_type_name)
        enum_gtype  = GObject.GType.from_name (enum_type_name)
        putEnumInNamespace(enum_gtype)


def plugin_func(image, drawable):
      print("plugin_func called args: ")
      getGimpEnums()



"""
      enum_type_names = gimp_enums_get_type_names (&n_enum_type_names);
    quark           = g_quark_from_static_string ("gimp-compat-enum");

    for (i = 0; i < n_enum_type_names; i++)
      {
        const gchar *enum_name  = enum_type_names[i];
        GType        enum_type  = g_type_from_name (enum_name);

        ts_init_enum (sc, enum_type);

        enum_type = (GType) g_type_get_qdata (enum_type, quark);

        if (enum_type)
          ts_init_enum (sc, enum_type);
      }
"""

register(
      "python-fu-dumpEnums",
      "blurb",
      "help message",
      "author",
      "copyright",
      "year",
      "Dump enums...",
      "*",
      [
          (PF_IMAGE, "image", "Input image", None),
          (PF_DRAWABLE, "drawable", "Input drawable", None),
      ],
      [],
      plugin_func,
      menu="<Image>/Test")
main()
