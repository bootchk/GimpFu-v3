
Work in progress.  Just deep proof of concept, no breadth.

Port of GimpFu (the simplified Gimp plugin API for Python) to Gimp 3 and Python3

A few, hacked files from gimp/plug-ins/pygimp.
For example gimpfu.py
The current Gimp build does not even install them.
You can test them in your own Gimp 2.99 build
simply by installing (copying) them
to say /usr/local/lib/gimp/2.99/python/gimpfu.py

Repository also includes a Vagga script to create a development container for Gimp 3.


Dev environment
===============

I use Vagga tool for development containers.

The vagga.yaml script builds a userspace container,
and has commands to execute in the container.

In other words, the vagga.yaml script completely builds a dev system,
installing the base OS, all dependencies, and building babl, gegl, and Gimp.


Vagga:
    - knows when it needs to rebuild.
    - doesn't require root privileges.
    - Easily deletable (rm -Rf .vagga).

Getting started
===============

    install Vagga from its website
    >sudo apt-get install uidmap
    clone this repository
    cd to the clone
    clone gimp repository into this repository (see below)
    >vagga --use-env DISPLAY gimpRunGUI

The last command will take a long time (the first time you run it.)
Ultimately, it will run Gimp from within the container.
And a test.py GimpFu plugin is installed in the container (Gimp menu Somewhere/test.)

Then you can hack at the .py files in your clone and rerun the last commmand.
It will take a minute or so to restart (not ideal, probably there is a better way.)
Advantages:
   - your machine is completely isolated.
   - if you hack at the Gimp clone, the command will rebuild Gimp automatically.
   - you can pull nightly changes to Gimp and the command will rebuild Gimp automatically.




Before you begin creating a dev environment,
clone the Gimp reposistory into /gimp in the project directory.
Since the build scripts copy from there into the container.
So that the container builds Gimp from a local possibly hacked copy.
I have one minor hack in my Gimp clone to support Gimpfu.

The vagga.yaml script copies hacked .py files
from this repository
into the right install place e.g. /usr/local/lib/gimp/2.99/python/gimpfu.py
at the last possible moment (after compile Gimp, before running Gimp.)

Hack to Gimp itself
===================

gimp/libgimp/gimp_procedure.c is hacked to allow
several procedure.add_arg_from_property() calls with the same named property.
Comment out the preemptive return after the error "duplicate argument name"
See discussion Gimp issue TODO
