# My dev environment

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


# Getting started developing GimpFu

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



## More about developing in a vagga container


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


# Hacks to Gimp itself

gimp/libgimp/gimp_procedure.c is hacked to allow
several procedure.add_arg_from_property() calls with the same named property.
Comment out the preemptive return after the error "duplicate argument name"
See discussion Gimp issue TODO

gimp/libgimpbase/gimparamspecs.c and .h are hacked re GimpFloatArray
