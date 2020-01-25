
Work in progress.  Just deep proof of concept, no breadth.

Port of GimpFu (the simplified Gimp plugin API for Python) to Gimp 3 and Python3

A few, hacked files from gimp/plug-ins/pygimp.
For example gimpfu.py
The current Gimp build does not even install them.
You can test them in your own Gimp 2.99 build
simply by installing (copying) them
to say /usr/local/lib/gimp/2.99/python/gimpfu.py

Repository also includes a Vagga script to create a development container for Gimp 3.

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
===============

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


Getting started
===============

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

Vagga leaves versioned containers which will fill your disk drive.
Occasionally you will need to:
>vagga _clean --unused

To start from scratch (rebuilding your container from nothing):
>rm -Rf .vagga
Dragging it to the trash doesn't help free up space.


Before you begin creating a dev environment,
clone the Gimp reposistory into /gimp in the project directory.
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
