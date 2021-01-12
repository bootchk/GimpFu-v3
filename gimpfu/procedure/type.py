
from enum import Enum, unique


@unique
class FuProcedureType(Enum):
    Image = 1
    Context = 2
    Load = 3
    Save = 4
    Other = 5

'''
Image

Args necessarily include (image, drawable)

Context

Installs to a context menu, receives current selected item from said menu.
where context menu for items:
- Gimp data not specific to an image e.g. Brush
- data created on a specific image, but not pixel data e.g. Vectors
- structures of a specific image e.g. Layer

'''
