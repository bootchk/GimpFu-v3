#!/usr/bin/env python

#   Random Shapes plugin for The Gimp 2.3.x
#   Written by Werner Hartnagel 2006/10/23
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.


from gimpfu import *
import random

class randomSVG:
	def __init__(self, svg_filename, width, height, interation, shape_position, palette_colors):
		self.filename = svg_filename
		self.interation = interation
		self.shape_position = shape_position
		self.palette_colors = palette_colors
		self.data = "<?xml version=\"1.0\" standalone=\"no\"?>\n"
		self.data+= "<!DOCTYPE svg PUBLIC \"-//W3C//DTD SVG 1.1//EN\" \"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd\">\n\n"
		self.data+= "<svg width=\"%s\" height=\"%s\" version=\"1.1\" xmlns=\"http://www.w3.org/2000/svg\">\n\n" % (width, height)

	def get_random_command(self):
		comm = ["L", "T"]
		commid = random.randint(0,1)
		return str(comm[commid])

	def get_random_color(self):
		colors = ["blue","yellow","lime","red","black","green"]
		colorid = random.randint(0,5)
		return "style=\"fill:%s\"" % colors[colorid]

	def get_random_palette_color(self):
		cur_palette = pdb.gimp_context_get_palette()
		max_colors = pdb.gimp_palette_get_info(cur_palette)
		random_number = random.randint(0,max_colors-1)
		random_color = pdb.gimp_palette_entry_get_color(cur_palette, random_number)
		return "style=\"fill: rgb(%.0f,%.0f,%.0f)\"" % (random_color.r*255, random_color.g*255, random_color.b*255)

	def addShape(self):
		path_data="M %i %i" % (random.randint(0,self.shape_position), random.randint(0,self.shape_position))
		pdatacount=random.randint(5,20)
		if self.palette_colors:
			style = self.get_random_palette_color()
		else:
			style = self.get_random_color()

		for i in xrange(0,pdatacount):
			path_data+=" %s %i %i" % (self.get_random_command(), random.randint(0,self.shape_position), random.randint(0,self.shape_position))

		self.data+= "<path d=\"%s\" %s/>\n" % (path_data, style)

	def __del__(self):
		self.data+="\n</svg>\n"
		f = open(self.filename, "w")
		f.write(self.data)
		f.close()

def py_random_shapes(svg_filename, width, height, interation, shape_position, palette_colors):
	mySVG = randomSVG(svg_filename, width, height, interation, shape_position, palette_colors)
	for i in xrange(0,int(interation)):
		mySVG.addShape()

	del mySVG
	svgdata = pdb.gimp_file_load(svg_filename, svg_filename)
#	svgdata = pdb.file_svg_load(svg_filename, svg_filename, 72, 400, 400, 0)
#	svgdata = pdb.gimp_vectors_import_from_string
	disp1 = gimp.Display(svgdata)

# Register with The Gimp
register(
	"python_fu_random_shapes",
	"random Shapes",
	"Render a stand-alone Image with random Shapes",
	"Werner Hartnagel",
	"(c) 2006, Werner Hartnagel",
	"2006",
	"<Toolbox>/Xtns/Python-Fu/Patterns/Random Shapes",
	"",
	[
		(PF_STRING, "svg_filename", "Filename to export", "/tmp/randomshapes.svg"),
		(PF_INT32, "width", "Width ", 400),
		(PF_INT32, "height", "Height ", 400),
		(PF_SPINNER, "interation", "How many Shapes? ", 80, (1, 1000, 1)),
		(PF_SPINNER, "shape_position", "max. Shape Position ", 400, (10, 4000, 1)),
		(PF_TOGGLE, "palette_colors", "Use Colors from current Palette ", 1),
	],
	[],
	py_random_shapes)

main()
