

class TestStats:

    stats = {}  # dictionary of counters

    @classmethod
    def sample(cls, name):
        """ Increment count of samples of name. """
        if name in cls.stats:
            cls.stats[name] = cls.stats[name] + 1
        else:
            cls.stats[name] = 1

    @classmethod
    def summarize(cls):

        print("megaTestGimp Test Statistics")
        print("============================")
        for key in cls.stats:
            print (f" {key} : {cls.stats[key]}" )
        print("============================")
