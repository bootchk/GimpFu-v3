"""
From GimpFu v2.
Obsolete in GimpFu v3

Useful to make TRUE and FALSE still deprecated, but not obsolete
# !!! But this also requires upcast to G_TYPE_BOOLEAN in Marshal and Types
And it doesn't provide type() for the class, so it causes other problems
in prop_holder_factory.
"""
# start verbatim from v2

# This is from pygtk/gtk/__init__.py
# Copyright (C) 1998-2003  James Henstridge

class _DeprecatedConstant:
    def __init__(self, value, name, suggestion):
        self._v = value
        self._name = name
        self._suggestion = suggestion

    def _deprecated(self, value):
        import warnings
        message = '%s is deprecated, use %s instead' % (self._name,
                                                        self._suggestion)
        warnings.warn(message, DeprecationWarning, 3)
        return value

    __nonzero__ = lambda self: self._deprecated(self._v == True)
    __int__     = lambda self: self._deprecated(int(self._v))
    __str__     = lambda self: self._deprecated(str(self._v))
    __repr__    = lambda self: self._deprecated(repr(self._v))
    __cmp__     = lambda self, other: self._deprecated(cmp(self._v, other))
