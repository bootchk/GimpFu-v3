
import inspect


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
Referred to as proceedErrors.
GimpFu can continue past proceedErrors,
so that more errors can be detected in one interpretation run.
ProceedErrors are in the nature of GimpFu API or Gimp API errors.

These are NOT ProceedErrors:
   - errors in Python syntax in the GimpFu author's code
   - severe GimpFu API errors (not calling register(), main())
These raise Python Exceptions that terminate the plugin.

The GimpFu code, when it discovers a proceedError() at a statement,
attempts to continue i.e. to proceed,
returning for example None for results of the erroneous statement.
Any following statements may generate spurious proceedErrors.

The results of a plugin (on the Gimp state, e.g. open image)
after a proceedError can be very garbled.
Usually Gimp announces this fact.
Any effects on existing images should still be undoable.

This behaviour is helpful when you are first developing a plugin.
Or porting a v2 plugin.

FUTURE this behaviour is configurable to raise an exception instead of proceeding.
'''

# list of lines of error message
log = []

def do_proceed_error(message):

    # print it on console
    # interspersed with any other debug output
    # TODO print any exception strings?
    print(">>>>GimpFu continues past error:", message)
    log.append("Error: " + message)

    '''
    log the text line of Gimp author's source code file.
    E.G. from file "/work/.home/.config/GIMP/2.99/plug-ins/sphere/sphere.py", line 54, in sphere.
    The Gimp author's call is deep on the call stack.
    Search for said call by filename in the frame stack.
    '''
    framestack = inspect.stack()

    # FrameInfo(frame, filename, lineno, function, code_context, index)
    source_text = ""
    for frameinfo in framestack:
        # TODO this works but is fragile ???
        if frameinfo.filename.find("/plug-ins/") > 0 :
            # code_context is a list of source code lines from filename
            source_text = frameinfo.code_context[frameinfo.index]
            break

    log.append(source_text)


def summarize_proceed_errors():
    ''' Return True when there were errors. '''

    print("GimpFu's summary of errors.")
    print("The first error may engender subsequent errors that are spurious.")
    print("Gimpfu warnings may also appear earlier in the console.")
    for line in log:
        print(line)
    if log :
        return True
    else :
        return False
