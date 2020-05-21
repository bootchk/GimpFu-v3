
import inspect

"""
Thin wrapper around the Python "inspect" module.
"""

class Framestack:

    @classmethod
    def get_errant_source_code_line(cls):
        '''
        return the text line of author's source code file.
        E.G. from file "/work/.home/.config/GIMP/2.99/plug-ins/sphere/sphere.py", line 54, in sphere.
        The author's call is deep on the call stack.
        Search for said call by filename in the frame stack.

        If plugin being executed does an eval(), this returns "unknown" ??
        '''
        framestack = inspect.stack(context=2)   # 2 means, save 2 lines of source code

        # FrameInfo(frame, filename, lineno, function, code_context, index)
        source_text = "empty framestack"
        '''
        Find the first line from the top whose filename is not a gimpfu source file.
        This works but is fragile with respect to naming and directory structures
        for source of plugins and gimpfu
        '''
        for frameinfo in framestack:
            if frameinfo.filename.find("gimpfu") > 0 :
                # skip frames from gimpfu source
                pass
            else:
                """
                Found first line that is not a gimpfu source filename
                code_context is a list of source code lines from filename.

                Context is None if eval() is being executed?
                And then frameinfo.filename is "<string>"
                """
                context = frameinfo.code_context
                if context:
                    source_text = frameinfo.code_context[frameinfo.index]
                else:
                    source_text = " unknown context"
                break

        return source_text


    @classmethod
    def print_trace(cls):
        framestack = inspect.stack(context=2)   # 2 means, save 2 lines of source code
        for frameinfo in framestack:
            print(frameinfo.filename, frameinfo.lineno)
