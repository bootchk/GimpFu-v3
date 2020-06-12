
from message.framestack import Framestack

import logging


'''
GimpFu is an interpreter of a language.

The language includes statements (or phrases) from:
- Python language
- Gimp language
-   GI Gimp
-   PDB
- GimpFu (i.e. symbols and methods defined by GimpFu)

This module handles certain errors in interpretation
returned mostly at points of contact with Gimp.
Referred to as proceeds.
GimpFu can continue past proceeds,
so that more errors can be detected in one interpretation run.
proceeds are often the author's mistaken use of GimpFu API or Gimp API.

Bugs in GimpFu source can also be erroneously declared as proceeds.

These are NOT proceeds:
   - errors in Python syntax in the author's code
   - severe GimpFu API errors (not calling register(), main())
These raise Python Exceptions that terminate the plugin.

The GimpFu code, when it discovers a proceed() at a statement,
attempts to continue i.e. to proceed,
returning for example None for results of the erroneous author's statement.
Any following author's statements may generate spurious proceeds.

The results of a plugin (on the Gimp state, e.g. open image)
after a proceed can be very garbled.
Usually Gimp announces this fact.
Any effects on existing images should still be undoable.

This behaviour is helpful when you are first developing a plugin.
Or porting a v2 plugin.

FUTURE this behaviour is configurable to raise an exception instead of proceeding.
'''

# cumulative error messages, possibly many lines per error
proceedLog = []

module_logger = logging.getLogger('GimpFu.proceed')

'''
When proceed is called,
framestack is usually a sequence of frameinfo's like this:
(this for the case where plugin source and gimpfu source all in /plug-ins/ directory)
filename                                  code_context               what the code is
---------------------------------------------------------------------------------
.../plug-ins/gimpfu/message.proceed_error.py   framestack.inspect(stack)  the current line from this source file
.../plug-ins/gimpfu/message.proceed_error.py   source_text=...            the calling line
...
.../plug-ins/gimpfu/gimpfu.py             <something>                lines from gimpfu source
...
.../plug-ins/sphere/sphere.py             "pdb.foo()"                the errant line of author's run_func
...
... (more lines in gimpfu source files)
...
.../plug-ins/sphere/sphere.py            "pdb.foo()"                the author's call to GimpFu main()
'''



def proceed(message):
    """ Proceed past an error (logging the fact.) """

    # Log to logger
    # level=>error, not critical, since we can proceed to find other possible Author errors
    module_logger.error(f"Proceed past error: {message}")

    # Log to cummulative private log
    proceedLog.append("Error: " + message)
    source_text = Framestack.get_errant_source_code_line()
    proceedLog.append("Plugin author's source:" + source_text)

    # For debugging inexplicable calls to proceed(), uncomment this line
    # It will print the stack trace at the exception
    # Framestack.print_trace()



def summarize_proceed_errors():
    '''
    Print the proceedLog of errors that we continued past.

    Returns whether exist errors.

    In general, GimpFu calls this if the plugin finishes,
    but GimpFu does NOT call this if the plugin ends
    with an exception (that is NOT turned into a proceed.)
    Such an exception may be:
      - in ordinary (not GimpFu-related) Python code written by the author
      - in GimpFu code, written by .
    '''

    if not proceedLog:
        result = False
    else:
        print("===========================")
        print("GimpFu's summary of errors continued past.")
        print("The first error may engender subsequent errors that are spurious,")
        print("e.g., a Python exception on source lines after the first error.")
        print("Such Python exceptions should appear above this.")
        print("")
        print("Gimpfu warnings may also appear prior to this in the console.")
        print("===========================")
        for line in proceedLog:
            print(line)
        print("")
        result = True
    return result
