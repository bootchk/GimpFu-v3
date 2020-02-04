
'''
Define __all__ so that "from gimpfu import *" imports only gimpfu modules

TODO should be submodules gimpfu, and gimp (having image, layer, etc.)
'''

__all__ = ["gimpfu",        # defines register(), and establishes Gimp.Plugin
           "gimpfu_pdb",    # defines symbol "pdb"
           "gimpfu_gimp",   # defines symbol "gimp"
           "gimpfu_enums",  # defines convenience symbols for Gimp enums
           "adapters.image",  # defines convenience classes (could be imported separately)
           "adapters.layer",
           "gimpfu_types",  # The rest support the above
           "gimpfu_widgets",
           "gimpfu_maps",
           "gimpfu_compatibility",
           "gimpfu_marshal",
           "adapter",
           "item",
           ]
