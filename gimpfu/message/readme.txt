Logging:

GimpFu uses Python standard logging module.
Uses a hierarchy of loggers.

Many log messages are for debugging GimpFu.

In addition, a layer on top, errors in Author's source that GimpFu discovered:

- ProceedErrors: probable errors in author's source, continued past
- Deprecations: author's source that is deprecated but that GimpFu fixed up

The above are logged at level ERROR.  GimpFu logging should be configured for at least level ERROR,
so that Authors may see their errors.

Also utilities for printing stack trace.

DebugLog: OBSOLETE, now using Python logging module
