

'''
This is a test case for the adaption techniques used
in the implementation of GimpFu.

IOW it is a much simplfied version of some of the guts of GimpFu
'''


# Adapter should import mock Marshal
# temporarily hack Adapter, define is_test = 1


# We are testing Adapter
from gimpfu.adapter import Adapter

# mocks
from gimpfu.mock.adapted_adaptee import AdaptedAdaptee


'''
generic test harness i.e. mocks:
Adaptee  in this file

in mock directory
    AdaptedAdaptee
    Marshal
'''





'''
This is the class of some amorphous object to be adapted.
For example, it could be a GObject Introspected object.
More specifically, it could be a Gimp.Image
'''
class Adaptee():
    ''' Class to mock a Gimp.Image or similar. '''

    '''
    These are properties in the sense that there are no args to getter calls.
    But they are set and get using call syntax.
    '''
    def __init__(self):
      self._othernameRW = "qux"
      self._instance_nameRW = "in_initial"

    '''
    Adaptee must implement copy()
    '''
    def copy(self):
        ''' Create copy of self. '''
        other = Adaptee()
        # Copy values of direct attributes of self to other. '''
        other._othernameRW = self._othernameRW
        other._instance_nameRW  = self._instance_nameRW
        return other


    def get_filename(self):
      return "foo"

    def get_othernameRO(self):
      # A constant, more or less
      return "zed"

    def get_othernameRW(self):
      return self._othernameRW
    def set_othernameRW(self, arg):
      self._othernameRW = arg

    def get_instance_nameRW(self):
        return self._instance_nameRW
    def set_instance_nameRW(self, arg):
        self._instance_nameRW = arg



    # method whose  [arg, result] both need marshalling
    def adapted_method(self, arg):
      return "bar"






# Test instances
# E.G. two wrapped instances of Gimp.Image
adaptee = Adaptee()
adapted = AdaptedAdaptee(adaptee)

adaptee2 = Adaptee()
adapted2 = AdaptedAdaptee(adaptee2)



# Run tests

print("\nTest normal results\n\n")

print("\nTest call adaptee method directly")
print("Usually author should use exposed property and not the  hidden getter")
print("Expect 'foo'")
print(adaptee.get_filename())


print("\nTest access static property of adapted adaptee")
print("Expect 'Adapted property accessed' ,  'foo' ")
print(adapted.filename)

print("\nTest access dynamic property of adapted adaptee")
print("Expect 'Adapted property RO accessed' ,  'zed' ")
print(adapted.othernameRO)


# Test [read, write, read] dynamic property of adapted adaptee
print("\nExpect 'Adapted property RW set' ,  'qux', 'changedQux' ")
print(adapted.othernameRW)
adapted.othernameRW = "changedQux"
print(adapted.othernameRW)

# OBSOLETE: all properties are now instance properties
# Test crosstalk between adapted class properties
# We wrote othernameRW on first adapted
# Ensure othernameRW on second adapted is also changed
#print("\nExpect 'Instance 2 adapted property RW get' ,  'changedQux' ")
#print(adapted2.othernameRW)


print("\nTest absence of crosstalk between adapted instance properties")
# We wrote othernameRW on first adapted
# Ensure othernameRW on second adapted is also changed
print("Expect 'Instance 2 adapted instance property RW get' ,  'in_initial', 'in_initial', 'in1', 'in2' ")
# Until set returns an initial value
print(adapted.instance_nameRW)
print(adapted2.instance_nameRW)
adapted.instance_nameRW = "in1"
adapted2.instance_nameRW = "in2"
print(adapted.instance_nameRW)
print(adapted2.instance_nameRW)


print("\nTest access adapted method, through adapter")
print("Expect: 'marshal args', 'unmarshal args', 'bar' ")
print(adapted.adapted_method("nothing"))






print("\nTest abnormal uses, expect error messages.\n")

print("\nTest attempt write to RO property")
print("Expect: AttributeError: ('Read only property:', 'othernameRO') ")
try:
    adapted.othernameRO = "nothing"
except AttributeError as err:
    print(err)
    pass

print("\nTest attempt to call a property on adaptee")
print("Expect: TypeError: 'str' object is not callable ")
try:
    foo = adapted.instance_nameRW()
except TypeError as err:
    print(err)
    pass


print("\nTest attempt to assign to adaptee callable ")
print("Expect: AttributeError:  Name get_filename on Adaptee is not assignable, only callable. ")
'''
!!! adaptee is not known to GimpfuPlugin author, only adapted.
But author could
But the callable is implemented by adaptee
'''
# TODO not implemented
try:
    adapted.get_filename = 0
except AttributeError as err:
    print(err)
    pass


print("\nTest attempt to assign to adapted callable ")
print("Expect: AttributeError: Attempt to assign to callable attribute of AdaptedAdaptee")
try:
    adapted.adapted_callable = 0
except AttributeError as err:
    print(err)
    pass








print("\nTest equality.\n")
print("Expect: True")
print( adapted == adapted )


print("\nTest non equality")
print("Expect: False")
print( adapted == adapted2 )



print("\nTest copy")
print("Expect: True")
adapted3 = adapted2.copy()
print( adapted3 == adapted2 )








print("\n Completed all tests")
