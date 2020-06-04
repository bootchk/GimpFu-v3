

class name_generator:
    """ Generate a unique name """

    def __init__():
        self.counter = 1

    def get_unique_name(self):
        """ Generate unique property name, unique over life of factory """
        result = "DummyProp" + str(self.counter)
        self.counter += 1
        return result
