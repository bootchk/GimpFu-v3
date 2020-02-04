'''
A test Gimp plugin
that:
- accesses a missing attribute of Drawable, as a property
'''

from gimpfu import *

def plugin_func(image, drawable):
  print("plugin_func called")

  # expect "AttributeError: since it doesn't exist anywhere"
  # TODO GimpFu catches AttributeError earlier, we can't catch it
  """
  try:
      foo = drawable.bar
  except AttributeError:

      print ("Pass AttributeError on drawable.bar")
  """

  '''
  Access an attribute of adaptee as property (improperly)
  (when has_alpha had not been adapted yet)
  Expect:  gi.FunctionInfo(has_alpha)
  '''
  foo = drawable.has_alpha
  # TODO this is not working: assert isinstance(foo, gi.FunctionInfo)
  print(foo)
  print("Type of adaptee attribute:", type(foo))

  '''
  Access an attribute of adaptee as callable.
  I.E. properly
  (before has_alpha has been wrapped)
  # TODO find an attribute that should not be wrapped.
  Expect: True or False (depends o)
  '''
  foo = drawable.has_alpha()
  assert isinstance(foo, bool)
  print(foo)

  '''
  Access an attribute that has been wrapped as a property.
  Use syntax for a property (no parens)
  '''
  foo = drawable.height
  print(foo)
  assert isinstance(foo, int)

  '''
  Access an attribute that has been wrapped as a property.
  Use syntax for a callable (use parens)
  Expect: TypeError: 'int' object is not callable
  '''
  foo = drawable.height()
  print(foo)







register(
      "test-missing-drawable-attribute",
      "blurb",
      "help message",
      "author",
      "copyright",
      "year",
      "Test missing drawable attribute...",
      "*",
      [
          (PF_IMAGE, "image", "Input image", None),
          (PF_DRAWABLE, "drawable", "Input drawable", None),
      ],
      [],
      plugin_func,
      menu="<Image>/Test")
main()
