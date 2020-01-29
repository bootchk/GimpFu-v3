
class AdaptedCallSequencer():
    '''
    Enforces that all sequences of accesses
    to attributes of adapted Gimp objects
    are in proper syntax (sorta BNF notation):

    OK: <name>(...)   <name>(...)
    WRONG: <name>   <name>(...)

    The latter is wrong because the first access has property semantics,
    and no Gimp object has properties.
    IOW, the returned value of the first adapted access will be a callable,
    and probably assigned to a variable,
    and that is probably not what a GimpFu plugin author intends.

    This also catches the case where GimpFu promised (in the docs)
    to adapt a Gimp method as a Python property but didn't implement.

    Adapters bracket their adapted calls with start(), end().

    This is only for calls to Gimp objects (adaptees) adapted by
    the kind of adaption using __getattr__ and _adaptor_func.
    Other kinds of adaption don't use this.
    IOW, accesses to attributes of GimpFu<Foo> objects don't use this.

    Stateful.
    Singleton.
    Global to all adaptors:
      - GimpfuPDB, GimpfuGimp (classes)
      - instances of subclass of Adaptor: GimpfuLayer, etc.
    A call started by any adaptor and not ended prevents
    any other adapter (class or instance) from starting another call.

    To test this, use some obscure Gimp method that has not been adapted by Gimpfu
    and use it without parens e.g. "img.get_tatto_state"
    '''

    started_call = ""     # singleton, i.e. global state for calls to adaptees


    @classmethod
    def start_call(cls, callable_name):
        if cls.started_call :
            # TODO proceed?
            raise RuntimeError(f"Can't access as property Gimp symbol: {cls.started_call}")
        else:
            cls.started_call = callable_name

    @classmethod
    def end_call(cls):
        cls.started_call = ""
