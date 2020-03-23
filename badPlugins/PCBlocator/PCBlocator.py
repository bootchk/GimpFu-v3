#!/usr/bin/env python

# lkk Everywhere gimp.pdb => pdb

# lkk I abandoned testing this because I can't understand what the text parameter should be
# and the default appears not to be meaningful, the plugin just says "no match"


from gimpfu import *
import re

# create an output function that redirects to gimp's Error Console
def gprint( text ):
   pdb.gimp_message(text)
   return

#set board layer location relative to main layer
def set_locationrel(boardlayer,mainlayer,cox,coy):
    relposx , relposy = get_locationrel(boardlayer,mainlayer)

    images = gimp.image_list()

    g = pdb
    g.gimp_layer_translate(boardlayer,relposx-cox,relposy-coy)

def get_locationrel(mainlayer,boardlayer):
    images = gimp.image_list()

    mainlayercox = mainlayer.offsets[0]
    mainlayercoy = mainlayer.offsets[1]

    boardlayercox = boardlayer.offsets[0]
    boardlayercoy = boardlayer.offsets[1]

    relposx = boardlayercox - mainlayercox
    relposy = boardlayercoy - mainlayercoy

    return relposx,relposy

# our script
def set_btaction(image, drawable, text) :
   g = pdb
   images = gimp.image_list()

   gprint(text)
   m = re.compile('\(([^)]*)\)').search(text)

   if m:
      print('Match found:' + str(m.group()) )
      startsub = m.start()
      endsub = m.end()

      # Get bottom name layers #
      bottomboardlayerName = text[startsub+1 : endsub-1].split(',')
      bottommainlayerName = text[:startsub]

      # Get bottom  layer objects from name
      bottommainlayer = get_layer_from_name(bottommainlayerName)
      bottomboardlayer = []
      for n in bottomboardlayerName:
          # lkk add parens
         print ("**debug: "+str(get_layer_from_name(n)) )
         bottomboardlayer.append(get_layer_from_name(n))

      # Get names of top layers
      topmainlayerName = get_the_top_name(bottommainlayerName)
      topboardlayerName=[]
      for n in bottomboardlayerName:
         topboardlayerName.append(get_the_top_name(n))

      # Get top layer objects from name.
      topmainlayer = get_layer_from_name(topmainlayerName)
      topboardlayer = []
      for n in topboardlayerName:
         topboardlayer.append(get_layer_from_name(n))

      # sizes of top main layers.
      wtopmainlayer = g.gimp_drawable_width(topmainlayer)
      htopmainlayer = g.gimp_drawable_height(topmainlayer)

      print("The layer variable names")
      print(topmainlayer)
      print(topboardlayer)
      print(bottommainlayer)
      print(bottomboardlayer)

      for idx,n in enumerate(topboardlayer):
         cox,coy = get_locationrel(bottomboardlayer[idx],bottommainlayer)
         set_locationrel(n,topmainlayer, -(wtopmainlayer-(abs(cox)+g.gimp_drawable_width(topboardlayer[idx]) )) ,coy )
         g.gimp_flip(topboardlayer[idx],0)
         gprint("**"+str(cox)+"**"+str(coy))

   else:
      print('No match')


   return



def get_the_top_name(boardname):
    return  re.sub('bottom','top', boardname)


def get_layer_from_name(name):
   images = gimp.image_list()

   flagname=0
   for idx,nlayer in enumerate(images[0].layers):
      if(nlayer.name == name):
         flagname = idx
   return(images[0].layers[flagname])


# This is the plugin registration function
register(
    "locate_pcba",
    "Locate pcba",
    "Locates(and mirrors) the top side for double sided boards, in function of the position of the bottom ones",
    "Miguel Jimenez",
    "GPL licensed",
    "August 2011",
    "<Image>/PCB/PCBLocator",
    "*",
    [
      (PF_STRING, 'some_text', 'Layers operator[mainbottom(subbottom,...)]', '...'),
      #(PF_INT, 'some_integer', 'Some number input for our plugin', 2010)
    ],
    [],
    set_btaction,
    )

main()
