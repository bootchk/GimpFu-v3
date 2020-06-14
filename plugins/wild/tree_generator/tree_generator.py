#!/usr/bin/env python
import math
import time

PHI = (1 + math.sqrt(5)) / 2
deg_to_rad=lambda deg: (deg*math.pi)/180
rad_to_deg=lambda rad: (rad/math.pi)*180

class Tree(object):
    def __init__(self, length, slope, root_point, gen_order):
        self.length = length
        self.slope = slope
        self.root_point = root_point
        self.end_point = self._get_end_point()
        self.right_branch = None
        self.left_branch = None
        self.gen_order = gen_order
        self._generate_next_generation()


    def __str__(self):
        return "Root point {0}, End point {1}, Length {2}".format(
             self.root_point, self.end_point, self.length)


    def _get_end_point(self):
        # This is mostly black magic taken from the math stack exchange..
        # no I don't have shame nor will I show my work.
        s_x, s_y = self.root_point
        e_x = - (self.length * (1 / math.sqrt(1 + (self.slope * self.slope)))) + s_x
        e_y = - (self.length * (self.slope / math.sqrt(1 + (self.slope * self.slope)))) + s_y
        return (e_x, e_y)


    def _gen_right_branch(self):
        r_len = self.length
        r_slope = self.slope + math.tan(120)
        r_root_point = self.end_point
        r_gen_order = self.gen_order - 1
        self.right_branch = Tree(r_len, r_slope, r_root_point, r_gen_order)


    def _gen_left_branch(self):
        l_len = self.length / PHI
        l_slope = self.slope - math.tan(36)
        l_root_point = self.end_point
        l_gen_order = self.gen_order - 1
        self.left_branch = Tree(l_len, l_slope, l_root_point, l_gen_order)


    def _generate_next_generation(self):
        if self.gen_order != 0:
            self._gen_left_branch()
            self._gen_right_branch()


    def walk(self):
        if self.right_branch != None:
            for branch in self.right_branch.walk():
                yield branch
        if self.left_branch != None:
            for branch in self.left_branch.walk():
                yield branch
        yield self


def gimp_run(*args):
    gen_order, length = args
    #TODO: These are stub values, they really should be taken from either a user
    # dialogue or from the active layer if ther is one
    height = 1000
    width = 1000
    root_point = (int(math.floor(height/3)), int(math.floor(width/2)))
    tree = Tree(length, 0, root_point, gen_order)
    img = gimp.Image(height, width, RGB)
    layer = gimp.Layer(img, 'Layer 1', height, width, RGB_IMAGE, 100, NORMAL_MODE)
    img.add_layer(layer, 0)
    pdb.gimp_edit_fill(layer, BACKGROUND_FILL)
    gimp.Display(img)
    gimp.displays_flush()
    # lkk make color a tuple
    # lkk call pdb instead of deprecated gimp method
    # gimp.set_foreground(0, 0, 0)
    pdb.gimp_context_set_foreground((0, 0, 0))
    drw = pdb.gimp_image_active_drawable(img)
    for b in tree.walk():
        s_x, s_y = b.root_point
        e_x, e_y = b.end_point
        ctrl_points = [s_x, s_y, e_x, e_y]
        pdb.gimp_paintbrush_default(drw, len(ctrl_points), ctrl_points)
        gimp.displays_flush()
        # lkk no sleep
        # time.sleep(1)


################################################################################
# Entry points: either it is a plugin for the gimp or we are debuggin the class
# on the terminal
################################################################################
try:
    from gimpfu import *
    register(
        "Tree_gen", "", "", "", "", "",
        "<Toolbox>/Xtns/Languages/Python-Fu/_Golden Tree Generator", "",
        [
            (PF_INT,    "arg0", "The number of generations deep the tree will be", 4),
            (PF_INT,    "arg1", "Length of the root branch", 30),
        ],
        [],
        gimp_run
        )
    main()
except ImportError:
    if __name__ == '__main__':
        # We must be on the terminal debugging....
        gen_order = 4
        length = 30
        root_point = (333, 500)
        slope = 0
        tree = Tree(length, slope, root_point, gen_order)
        for branch in tree.walk():
            print(branch)
