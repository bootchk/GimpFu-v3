
Work in progress.

Port of GimpFu (the simplified Gimp plugin API for Python) to Gimp 3 and Python3

Repository also includes a Vagga script to create a development container for Gimp 3.

The current status: proved the concept, now working on breadth.
It works for many existing plugins in the wild (requiring only a few minor edits to said plugins.)
As I test new, wild plugins, the rate at which I find holes in the GimpFu implementation is decreasing.


# Differences between v2 and v3 of Gimpfu

## Implementation (this is the crux of GimpFu)

* v2 uses static binding: C language files to bind Python to Gimp
* v3 uses dynamic binding: uses Python language files and GI (GObject Introspection.)

More about GI.  Gimp is being enhanced with GObject annotations that allow GI of its API.
The PyGObject module (import gi) lets Python code do GI.
The PyGObject module is partially implemented in the C language,
but GimpFu no longer uses any C language.

PyGObject automatically marshals many Python objects (e.g. lists)
into GObjects that Gimp can use.

Now, to port a Gimp Python plugin:

* the author must understand many details of GI.
  For example, how to create a GValueArray.
* each ported Gimp Python plugin uses much boilerplate.
  The boilerplate is different (authors must re learn) from v2 GimpFu boilerplate

With GimpFu:

* many details of GI are hidden
* boilerplate is reduced
* boilerplate is backward compatible with PyGimp/GimpFu v2

## Source directory

* v2 gimp/plug-ins/pygimp
* v3 this_repository/gimpfu

## Plugin source code

* v2 The gimp repository has a parallel directory named gimp/plug-ins/python.
  Some of those plugins use v2 GimpFu.
* v3 (branch mainline, i.e. 2.99) gimp/plug-ins/python: Python language plugins
  but **none** of the plugins use GimpFu; they all have been ported to use only
  Gimp and GI.
* this repository:  /plug-ins : test plugins, that mostly use GimpFu.
  Most are copied from wild plugins found on the net, often at GitHub.

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


## Installation

The current Gimp development branch (mainline, 2.99) build does not even install the pygimp directory.

You can test this repository in your own Gimp 2.99 build
simply by installing (copying) the gimpfu directory to either:

* /usr/local/lib/gimp/2.99/python/gimpfu.py (the official installation place)
* ~/.config/GIMP/2.99/plug-ins (the local, custom installation place)

## Disambiguation

* v2: PyGimp was larger than GimpFu.  PyGimp included the 'gimpfu' module
  as well as some modules that were useful without Gimpfu.
* v3: PyGimp is no longer a useful moniker.  The pygimp directory no longer exists.
  Much existing documentation refers to 'PyGimp.'
  Usually you can just substitute 'GimpFu' for 'PyGimp'.

GimpFu **is** the package that provides a mostly backward compatible API for writing Gimp Python plugins.
An author can still write a Gimp Python plugin, using only GI, without any modules from the GimpFu package.

## Porting Gimp Python plugins from v2 to v3

See the document: pluginPortingGuide


TODO list
=========

This is a high-level list of features that GimpFu provides,
that need to be ported/rewritten
along with the status in parenthesis

1. Automatic plugin GUI generation (proved concept, needs breadth)
2. pdb convenience object (in progress)
3. Gimp enums to Python names (no progress)
4. PF_ enums, the ones that GimpFu/PythonFu defines (strategy devised, needs depth and breadth)
5. Use new plugin "defaults" machinery in Gimp 3, really "plugin settings", called "gimp_procedure_config" (strategy devised, no progress)
6. Other convenience Python objects e.g. "image" (not started, possibly obsolete them?)
7. Write a "GimpFu plugin Porting Guide" (drafted, this TODO list is its outline)
8. Adapt to new plugin installation requirements (proved)

Dev strategy
============

True hacking.  Start coding, see what is broken, fix, and repeat.

Lacking a "Developers Guide to Architecture of PyGimp" you must reverse engineer.
From the PyGimp/GimpFu code and the GimpFu (Author's Guide) document.

Start with a primitive gimpfu.py module.
Test with a null GimpFu plugin (that does nothing really.)
Proceed to test with other existing GimpFu plugins, say clothify.py

The most basic statement of what the port involves is:
convert a static binding of Python to Gimp and to a dynamic GI binding.
That has already been done for many Python plugins that don't use GimpFu.
The problem is to convert GimpFu to a dynamic binding.
And what GimpFu does is automate (or provide simplified API) for plugin authors.
So you take pieces from already ported/authored non-GimpFu Python3/Gimp3 plugins,
and put those pieces into the GimpFu framework.


To use the source
=================
The current Gimp 2.99 repository doesn't even attempt to build GimpFu.
You don't need to hack it so it does (but eventually it should.)

You can just copy the files in the source directory
into the Python plugin install directory of your dev system.
(There is no C source to be compiled for GimpFu)
You can copy a test plugin (that uses GimpFu) from the test directory
to your user local location for plugins (say ~/.config/gimp/....)
or to the install location for Gimp packaged Python plugins.



My dev environment
==================

I use Vagga tool for development containers.
You don't need this if you already can build Gimp.

The vagga.yaml script builds a userspace container,
and has commands to execute in the container.

In other words, the vagga.yaml script completely builds a dev system,
installing the base OS, all dependencies, and building babl, gegl, and Gimp.

Vagga:
    - knows when it needs to rebuild.
    - doesn't require root privileges.
    - Easily deletable (rm -Rf .vagga).
    - your machine (its original dev environment) is completely isolated.
    - if you hack at the Gimp clone, the command will rebuild Gimp automatically.
    - you can pull nightly changes to Gimp and the command will rebuild Gimp automatically.


Getting started developing GimpFu
=================================

    install Vagga from its website
    >sudo apt-get install uidmap
    clone this repository
    cd to the clone
    clone gimp repository into this repository (see below)
    >vagga --use-env DISPLAY gimpTestGUI

The last command will take a long time (the first time you run it.)
Ultimately, it will run Gimp from within the container.
And test GimpFu plugins and the Gimpfu source are installed in the container's home
(project/.home/.config/GIMP/2.99/plug-ins)
and PYTHONPATH is set to find them.
(That way, the container starts easily, but Gimp finds the local plugins and gimpfu
before finding what is installed by the Gimp build.)

Then you can hack at the .py files in your clone and rerun the last commmand.
It will take seconds to restart.

(Alternatively, if you run gimpRunGUI,
it uses the plugins and gimpfu source
that the vagga.yaml script puts into the container itself,
in the locations that a Gimp build would install plugins and gimpfu.)

If you change the text of a test plugin,
you need to rm project/.home/.config/GIMP/2.99/plug-ins.rc
which is where GIMP caches plugin specifications.
When you do that, GIMP will reread from the standard paths for plugins,
and RE-register all the plugins it finds.
If you don't, you will see the plugin in the GIMP GUI
with the old specifications, i.e.
at the old menu, or with old parameters, or with the old run_func, etc.



More about developing in a vagga container
==========================================

Vagga leaves versioned containers which will fill your disk drive.
Occasionally you will need to:
>vagga _clean --unused

To start from scratch (rebuilding your container from nothing):
>rm -Rf .vagga
Dragging it to the trash doesn't help free up space.


Before you begin creating a dev environment,
clone the Gimp repository into /gimp in the project directory.
Since the build scripts copy from there into the container.
So that the container builds Gimp from a local possibly hacked copy.
I have one minor hack in my Gimp clone to support Gimpfu.

Typically:
   vaggaGimp (clone of this repository)
      gimp (you add this clone of gimp 2.99 repository)
      .vagga (ephemera, ignored, created by vagga, the containers)
      source (from this repository )
      vagga.yaml (from this repository)
      test, readme, etc. (from this repository)


The vagga.yaml script copies hacked .py files
from this repository
into the container at the correct install place e.g. /usr/local/lib/gimp/2.99/python/gimpfu.py
at the last possible moment (after compile Gimp, before running Gimp.)


Hack to Gimp itself
===================

gimp/libgimp/gimp_procedure.c is hacked to allow
several procedure.add_arg_from_property() calls with the same named property.
Comment out the preemptive return after the error "duplicate argument name"
See discussion Gimp issue TODO
