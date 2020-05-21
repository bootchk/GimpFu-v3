

suggestLog = []


"""
GimpFu suggested improvements to Author code.
Not deprecations.
"""

class Suggest:

    @staticmethod
    def say(message):

        # Not log to logger

        suggestLog.append(message)

        # TODO need a context


    @staticmethod
    def summarize():
        if not suggestLog:
            result = False
        else:
            print("===========================")
            print("GimpFu's suggestions.")
            print("Your code might be clearer if you use explicit conversions or literals that denote the type.")
            print("===========================")
            for line in suggestLog:
                print(line)
            print("")
            result = True
        return result
