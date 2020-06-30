

class TestStats:

    stats = {}  # dictionary of counters


    @classmethod
    def _sample(cls, name):
        """ Increment count of samples of name. """

        if name in cls.stats:
            cls.stats[name] = cls.stats[name] + 1
        else:
            cls.stats[name] = 1

    @classmethod
    def sample(cls, name, subcategory=None):
        """ Increment count of samples of name. """

        # sample the main stat
        cls._sample(name)

        # sample the subcategory, with condensing
        if subcategory is not None:
            # condense
            if subcategory.find("out of range") > 0:
                cls._sample(name + ": out of range")
            elif subcategory.find("not a text layer") > 0:
                cls._sample(name + ": not a text layer")
            else:
                # not condense
                cls._sample(name + ": " + subcategory)


    @classmethod
    def summarize(cls):

        print("megaTestGimp Test Statistics")
        print("============================")
        for key in cls.stats:
            print (f" {key} : {cls.stats[key]}" )
        print("============================")
