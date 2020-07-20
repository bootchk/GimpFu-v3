

GimpFu (the simplified Gimp plugin API for Python)  for Gimp 3 and Python3.

Note: *The planned Gimp 3 still supports Python plugins, but using GObject Introspection.  Gimp 3 does not plan to support GimpFu plugins without this unofficial repository.  If you need the certainty that a new plugin will work in Gimp 3, you should use the official machinery.*

# Status

## Completeness

Work in progress.  It proves the idea is possible.

GimpFu v3 is not complete: some features of GimpFu v2 are not yet supported.
GimpFu v3  works for many existing plugins in the wild (requiring only a few minor edits to said plugins.)

As users and developers test wild plugins and GimpFu v3 is improved,
fewer holes are found in GimpFu v3.

## Support

For now, GimpFu v3 is *not* supported by Gimp.org.
It is a third-party plugin.

GimpFu v3 might be supported by Gimp.org if:
* there is enough demand
* someone steps forward to maintain and fix issues in GimpFu v3

## Stability

Gimp 2.99 is constantly changing, and GimpFu v3 frequently changes,
both to accomodate changes to Gimp 2.99
and to improve GimpFu v3.
Pull and rebuild often.

# Installation

In the command line in a terminal:
```
>cd *wherever you cloned this repository*
>cp -r gimpfu ~/.config/GIMP/2.99/plug-ins/gimpfu
```
Note that we copy the 'gimpfu' directory to another directory named 'gimpfu' in the plugins directory.

Run:
```
>export PYTHONPATH=~/.config/GIMP/2.99/plug-ins/gimpfu:${PYTHONPATH}
>/usr/local/bin/gimp-2.99 --verbose
```
If you also have or installed some GimpFu v3 plugins,
expect to see them in the Gimp menus.
(A typical Gimp 2.99 build will have no GimpFu plugins.)  GimpFu itself does not appear in the Gimp menus.

## Notes on Installation

GimpFu v3 does not require building or compiling; it is all Python scripts.

GimpFu v3 does depend on Gimp 2.99 and Python 3.  You probably need to build Gimp 2.99 yourself.

Thus you can test GimpFu v3 after you build Gimp 2.99
simply by copying the gimpfu directory this repository to either:

* /usr/local/lib/gimp/2.99/python/gimpfu.py (Gimp's official installation place, varies by distribution)
* ~/.config/GIMP/2.99/plug-ins (the local, custom installation place)

Then, because Gimp does not alter PYTHONPATH when it starts a Python interpreter,
you must set PYTHONPATH so Python will find the 'gimpfu' module when a Gimp Python plugin does "from gimpfu import *."

Then you can start your own Gimp 2.99 (typically installed to /usr/local/bin)

The current Gimp development branch (mainline, 2.99) repository
has abandoned maintenance of GimpFu v2.
The files in the Gimp repository (in the /gimp/plug-ins/python/pygimp directory) are relics.
A 2.99 build does not build or install those files.

# Hacking

To change GimpFu v3, you can just edit the files in the directory where you installed them, then restart Gimp. (There is no C source to be compiled for GimpFu v3.)

## Test Plugins

The repository includes a set of test plugins (GimpFu v3 compatible), in /plugins.  See /plugins/readme.txt

You can copy a test plugin (that uses GimpFu) from the repository
to your user local location for plugins (say ~/.config/GIMP/2.99/plug-ins).

In Gimp 3:
* each plugin must be inside its own directory
* each plugin (the top .py file) must have execute permission

Thus copy an entire test plugin's directory, for example:

```
>cd *wherever you cloned this repository*
>cp -r plugins/wild/foggify   ~/.config/GIMP/2.99/plug-ins
>chmod +x ~/.config/GIMP/2.99/plug-ins/foggify/foggify.py
```
*A typical plugin found on the net is for Gimp 2 and might require minor edits to work with GimpFu v3.*

# Differences between v2 and v3 of GimpFu

GimpFu v3 maintains the outward capabilities and API or "language" of GimpFu v2.

## Design/Programming documents

The documents that tell you how to write a plugin:

v2 [Gimp Python Documentation](https://www.gimp.org/docs/python/index.html)  
This document will not be supported by Gimp.org starting with Gimp 3.

v3 The above document guides what the GimpFu v3 must do, for backward compatibility.

Some of the document will change:
* description of the implementation methods (C language) and installation
* import modules: the 'gimpfu' module is all that most authors will use
* anything for which the model has changed in Gimp itself (example?)
* Tile and Pixel Region objects are obsoleted

The document will also say more about how GimpFu reports errors.
Because of the dynamic binding, the nature of error messages is changed.
GimpFu v3 may attempt to keep going (so that more errors are found) where GimpFu v2 might have stopped.


## Implementation

GimpFu v3 is not a port:  GimpFu v3 is almost a total rewrite.

* v2 uses static binding: C language files to bind Python to Gimp
* v3 uses dynamic binding: uses Python language files and GI (GObject Introspection.)

GimpFu v3, since it is all Python, might have fewer lines of code.
It is more readable.  GimpFu v2 static binding was an art understood by few people.

### More about GI.  

Gimp 3 is being enhanced with GObject annotations that allow GI of its API.
The PyGObject module (import gi) lets Python code do GI.
The PyGObject module is partially implemented in the C language,
but GimpFu no longer uses any C language.

PyGObject automatically marshals many Python objects (e.g. lists)
into GObjects that Gimp can use.

Now, to port a Gimp Python plugin using only GI:

* the author must understand many details of GI.
  For example, how to create a GValueArray.
* each ported Gimp Python plugin uses much boilerplate.
  The boilerplate is different (authors must re learn) from v2 GimpFu boilerplate

With GimpFu, most existing GimpFu plugins will work with minor changes.

The advantages of using GimpFu over Python with GI:

* many details of GI are hidden
* boilerplate is reduced
* boilerplate is backward compatible with PyGimp/GimpFu v2

## Source directory

* v2 gimp/plug-ins/pygimp
* v3 this_repository/gimpfu

## Plugin source code

* v2 The gimp repository has a parallel directory named gimp/plug-ins/python.
  Some of those plugins use v2 GimpFu while others are use the full PyGimp API.
* v3 (branch mainline, i.e. 2.99) gimp/plug-ins/python: Python language plugins
  but *none* of the plugins use GimpFu; they all have been ported to use only
  Gimp and GI.
* this repository:  /plug-ins : test plugins, that mostly use GimpFu.
  Some (/wild) are copied from the net, often at GitHub.
  Some (/test) are written specificially to test features of GimpFu v3

## Plugin source directory structure

* v2 /gimp/plug-ins/pygimp is unstructured.
  It contained many modules, some implemented in C.
  One module was gimpfu.py, which imported many of the other modules.
  But an author could import the other modules without importing the gimpfu module.

* v3 /gimpfu is a Python package.
  It is structured into sub-packages for ease of maintenance.
  The gimpfu package still imports many submodules.
  But I anticipate that few Gimp Python plugins will import submodules
  without importing the entire gimpfu package.
  (You could do that: "from gimpfu.gimpenums import *")


## Disambiguation

* v2: PyGimp was larger than GimpFu.  PyGimp included the 'gimpfu' module
  as well as some modules that were useful without GimpFu.
* v3: PyGimp is no longer a useful moniker.  The pygimp directory no longer exists.
  Much existing documentation refers to 'PyGimp.'
  Usually you can just substitute 'GimpFu' for 'PyGimp'.

GimpFu **is** the package that provides a mostly backward compatible API for writing Gimp Python plugins.
An author can still write a Gimp 3 Python plugin, using only GI, without any modules from the GimpFu package.

## Porting Gimp Python plugins from v2 to v3

See the document in this repository: gimpfu/docs/pluginPortingGuide.txt

# Python GI API documents

It is better to read documents for the Python API than to read documents for the C API.
Although with some mental energy you can read the C API and figure out the Python API.

## GObject, Gio, GLib, but *not* Gimp 2.99 GI API docs

The best documentation about the GObject introspected Python API's of various projects
is found at [PyGObject API Reference](https://lazka.github.io/pgi-docs/)
Many other docs on the web (such as at the Gnome project?) are outdated, or for the C API.

## Gimp 2.99 GI API docs

You should generate docs yourself for the GObject introspected Python API for GIMP.
Since Gimp2.99 is a development branch, you should pull it often, and the API might change.
When you build Gimp, the gir goes to say, /usr/local/share/gir-1.0/Gimp-3.0.gir

To create a document:

```
> g-ir-doc-tool --language=Python -o ~/gimp-doc /usr/local/share/gir-1.0/Gimp-3.0.gir
```
To browse the document:

```
> yelp ~/gimp-doc
```

You might need to install package 'yelp'.
The command g-ir-doc-tool might be in package 'libgirepository1.0-dev'.



# TODO list

This is a high-level list of features that GimpFu provides,
that need to be ported/rewritten
along with the status in parenthesis

1. Automatic plugin GUI generation (needs breadth, and may go away when Gimp itself will do it, as planned.)
2. pdb and gimp convenience objects  (needs breadth)
3. Other convenience Python objects e.g. "image" (needs breadth)
4. Gimp enums to Python names (needs breadth)
5. PF_ enums, the ones that GimpFu/PythonFu defines ( needs breadth)
6. Use new plugin "defaults" machinery in Gimp 3, really "plugin settings", called "gimp_procedure_config" (done)
7. Write a "GimpFu plugin Porting Guide" (drafted)
8. Adapt to new plugin installation requirements (proved)
9. Marshalling of old Gimp types GimpFloatArray, GimpStringArray, etc.
10. Marshalling of new gimp types GimpObjectArray, GFile
11. pixel regions or a substitute


# Development strategy

Start coding, see what is broken, fix, and repeat.

Lacking a "Developers Guide to Architecture of PyGimp" you must reverse engineer.
From the PyGimp/GimpFu code and the GimpFu (Author's Guide) document.

Start with a primitive gimpfu.py module.
Test with a null GimpFu plugin (that does nothing really.)
Proceed to test with other existing GimpFu plugins, say clothify.py

The most basic statement of what the port involves is:
convert a static binding of Python to Gimp and to a dynamic GI binding.
That has already been done for many Python plugins that don't use GimpFu.
The problem is to convert GimpFu to a dynamic binding.
And what GimpFu does is automate (or provide simplified API) for authors.
So you take pieces from already ported/authored non-GimpFu Python3/Gimp3 plugins,
and put those pieces into the GimpFu framework.

# vagga

Repository also includes a Vagga script (vagga.yaml) to create a development container for Gimp 3.
That lets you build and test Gimp on many different Linux distributions without disturbing your machine.
Its not necessary for GimpFu v3, since GimpFu v3 is all scripts.
You might be interested in vagga as yet another way to build Gimp.
More info in the file vagga.md
