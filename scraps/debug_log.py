
from message.framestack import Framestack



"""
Logging to console of debug prints

Controllable similar to NDEBUG
"""


isDebugging = True



class DebugLog:

    def log(message, severity=False):
        if  isDebugging:
            if severity:
                print(message, ". Stack trace follows...")
                Framestack.print_trace()
            else:
                print(message)
