Goal is to put backward compatible enums into global namespace.


Following is uncertain:

in V2, it seems like Gimp GTypes had data.
Data was keyed by "gimp-compat-enum".
Data value was a pointer(?) to another type.
PyGimp got all the values from both types
and put them into the namespace, using pygobject?

Same mechanism also used by ScriptFu.

Since V3, seems like data keyed by "gimp-compat-enum" is gone?

So to maintain compatibility, need to capture from Gimp 2.10?
