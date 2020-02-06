#!/usr/bin/env python
from gimpfu import *
def resizerescaleandcenterlayers(img,drw):
    img=gimp.image_list()[0]
    layers = img.layers
    layerDMax=""
    a=0
    for i in layers:
    	if i.width>a:
    		layerDMax=i
    		a=i.width
    img.resize(layerDMax.width,layerDMax.height,0,0)
    for n in range(len(layers)):
    	layers[n].scale(layerDMax.width,layerDMax.height,1)
    	x= (img.width-layers[n].width)/2
    	y = (img.height - layers[n].height)/2
    	layers[n].set_offsets(x,y)


register(
        "ResizeRescaleCenterLayers",
        "Rescale differents layers and center them in a resize image",
        "Allows to rescale differents layers and center them in a resize image",
        "Giacomo Marchioro",
        "GPL License",
        "2013",
        "<Image>/ComparazioneImmagini/ResizeRescaleCenterLayers",
        "*",
        [],
        [],
        resizerescaleandcenterlayers)
main()
