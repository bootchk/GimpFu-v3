

#    psd2html - Converts a .psd file (or other layered image) to an .html template.
#    Copyright © 2010 Seán Hayes

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from gimpfu import *
import os
import re
import string
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)

gettext_domain = "gimp30-python"
gettext.install(gettext_domain, gimp.locale_directory)

justifications = ('left', 'right', 'center', 'justify')

opacity_template = """
    opacity: %.1f;
    filter: alpha(opacity=%i);"""

#TODO: add relative positioning option
css_image_template = """#%(id)s
{
    background-image: url("%(url)s");
    position: absolute;
    top: %(top)dpx;
    left: %(left)dpx;
    width: %(width)dpx;
    height: %(height)dpx;
    z-index: %(z-index)d;%(opacity_s)s
}

"""

css_text_template = """#%(id)s
{
    position: absolute;
    top: %(top)dpx;
    left: %(left)dpx;
    width: %(width)dpx;
    height: %(height)dpx;
    font-size: %(font-size)s;
    font-family: %(font-family)s;
    color: %(color)s;
    text-align: %(text-align)s;
    text-indent: %(text-indent)s;
    line-height: %(line-height)s;
    letter-spacing: %(letter-spacing)s;
    z-index: %(z-index)d;%(opacity_s)s
}

"""

html_div_open_template = """
%(indent)s<div id=\"%(id)s\">%(text)s"""

html_div_close_template = """
%(indent)s</div>"""

html_body_open_template = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <meta name="generator" content="psd2html GIMP Plug-in" />
    <link href="%s" rel="stylesheet" type="text/css" />
</head>
<body>"""

html_body_close_template = """
</body>
</html>
"""

html_file_path_template = '%s%shtml'
css_file_path_template = 'style%scss'
media_dir_template = '%s_files'
image_filename_template = '%s%spng'

step_size = 1
progress = 0

def add_progress(steps):
    global progress
    progress += steps * step_size
    gimp.progress_update(progress)

def set_step_size(s):
    global step_size
    step_size = s

def get_sort_keys_func(layers_meta):
    def sort_keys(key):
        return layers_meta[key]['z-index']
    return sort_keys

def nest_layers(d, layers, layers_meta):
    logger.debug('nest_layers()')
    logger.debug('dict: %s' % str(d))
    # lkk Python 3 dict_keys has no sort
    #sort_keys_func = get_sort_keys_func(layers_meta)
    #d_keys = d.keys()
    #d_keys.sort(key=sort_keys_func)
    d_keys = sorted(d)
    logger.debug(d_keys)
    for key in reversed(d_keys):
        #verify this key still exists since the dict can be chaged within this loop
        # lkk Python3
        #if not d.has_key(key):
        if not key in d:
            continue
        val = d[key]
        #logger.debug('key: %s, val: %s' % (key, str(val)))
        for key2 in d_keys:
            if key == key2:
                continue
            if not d.has_key(key2):
                continue

            lk = layers[key]
            lk2 = layers[key2]

            #if they're the same size, they can't be parents or children of each other
            if lk.width == lk2.width and lk.height == lk2.height:
                continue
            #if key2 is smaller, it might be a child
            elif (lk.width >= lk2.width) and (lk.height >= lk2.height):
                lmk = layers_meta[key]
                lmk2 = layers_meta[key2]
                #if key2 is within the bounds of key
                if (lmk['x'] <= lmk2['x'] and lmk['x2'] >= lmk2['x2']) and (lmk['y'] <= lmk2['y'] and lmk['y2'] >= lmk2['y2']):
                    #logger.debug('layer: %s, x: %d, y: %d, x2: %d, y2: %d' % (key, lmk['x'], lmk['y'], lmk['x2'], lmk['y2']))
                    #logger.debug('layer2: %s, x: %d, y: %d, x2: %d, y2: %d' % (key2, lmk2['x'], lmk2['y'], lmk2['x2'], lmk2['y2']))
                    d[key][key2] = d.pop(key2)
            #otherwise, key2 is a parent of key, in which case it'll be sorted in another iteration

    for key in d:
        d[key] = nest_layers(d[key], layers, layers_meta) if d[key] else {}
    return d

def layers_to_dict(layers, layers_meta):
    logger.debug('layers_to_dict()')
    d = {}
    l = {}
    for layer in layers:
        logger.debug(layer.name)
        d[layer.name] = {}
        l[layer.name] = layer
    d = nest_layers(d, l, layers_meta)
    return (d, l)

def get_html(parent_key, d, layers, layers_meta, layer_order, css_opacity, depth=0):
    px = 0
    py = 0
    if parent_key is not None:
        px = layers_meta[parent_key]['x']
        py = layers_meta[parent_key]['y']

    style = []
    html = []
    for key in [layer for layer in layer_order if layer in d]:
        val = d[key]
        gimp.progress_init('psd2html: Inspecting %s' % layers[key].name)
        opacity_string = ''
        if css_opacity and layers[key].opacity is not 1:
            opacity_string = opacity_template % (layers[key].opacity/100.0, layers[key].opacity)

        sub_s, sub_html = get_html(key, val, layers, layers_meta, layer_order, css_opacity, depth=depth+1)

        vals = {
            'id': layers_meta[key]['id'],
            'top': layers_meta[key]['y']-py,
            'left': layers_meta[key]['x']-px,
            'width': layers[key].width,
            'height': layers[key].height,
            'opacity_s': opacity_string,
            'indent': '\t'*depth,
            'text': '',
            'z-index': layers_meta[key]['z-index'],
        }

        if pdb.gimp_drawable_is_text_layer(layers[key]):
            vals['text'] = pdb.gimp_text_layer_get_text(layers[key])
            size, units = pdb.gimp_text_layer_get_font_size(layers[key])
            vals['font-size'] = '%s%s' % (size, pdb.gimp_unit_get_abbreviation(units))
            vals['font-family'] = pdb.gimp_text_layer_get_font(layers[key])
            color = list(pdb.gimp_text_layer_get_color(layers[key]))
            for i, c in enumerate(color):
                color[i] = hex(color[i])[2:]
            vals['color'] = '#%s%s%s' % tuple(color[0:3])
            vals['text-align'] = justifications[pdb.gimp_text_layer_get_justification(layers[key])]
            vals['text-indent'] = '%dpx' % pdb.gimp_text_layer_get_indent(layers[key])
            #FIXME: line height doesn't translate well into CSS
            vals['line-height'] = '%dpx' % pdb.gimp_text_layer_get_line_spacing(layers[key])
            vals['letter-spacing'] = '%dpx' % pdb.gimp_text_layer_get_letter_spacing(layers[key])
            s = css_text_template
        else:
            vals['url'] = layers_meta[key]['image_rel_path']
            s = css_image_template

        #CSS for this layer
        style.append(s % vals)
        #CSS for sub elements
        style.extend(sub_s)
        #HTML for this layer
        html.append(html_div_open_template % vals)
        #HTML for sub elements
        html.extend(sub_html)
        html.append(html_div_close_template % vals)

    return (style, html)

#FIXME: remove CSS opacity, since it's inherited by child elements in HTML+CSS
def plugin_func(image, drawable, css_opacity, extract_text_images, export_images=True):
    """
    This is the function that does most of the work. See register() below for more info.

    For a given image with the folloing path:
    /home/user/dev/template.psd

    the following file structure will result:
    /home/user/dev/template.psd
    /home/user/dev/template.html
    /home/user/dev/template_files/
    /home/user/dev/template_files/style.css
    /home/user/dev/template_files/<layer_name_0>.(gif|jpg|png)
    /home/user/dev/template_files/<layer_name_1>.(gif|jpg|png)
    /home/user/dev/template_files/<layer_name_n...>.(gif|jpg|png)

    When testing in the console, call this function with:
plugin_func(gimp.image_list()[0], gimp.image_list()[0], True, False)
    OR
plugin_func(gimp.image_list()[0], gimp.image_list()[0], True, False, export_images=False)
    to avoid writing images.
    """
    #step used for progress bar. 1 for html file, 1 for css file, 3 for each layer
    set_step_size(1 / (2 + 3 * len(image.layers)))

    gimp.progress_init('psd2html: Running')
    add_progress(0)
    #get name of file
    filename = os.path.splitext(image.filename)[0]
    directory = os.path.dirname(image.filename)
    #TODO: clean up existing files and folders in case this plugin has already been run (accept overwrite parameter from user, or fail)
    #create filename.html and filename_files/ folder
    html_file_path = os.path.join(directory, html_file_path_template % (filename, os.path.extsep))
    html_file = os.open(html_file_path, os.O_WRONLY|os.O_CREAT|os.O_TRUNC)
    media_dir = media_dir_template % filename
    if not os.path.exists(media_dir):
        os.mkdir(media_dir)
    css_file_path = os.path.join(directory, media_dir, css_file_path_template % os.path.extsep)
    css_file = os.open(css_file_path, os.O_WRONLY|os.O_CREAT|os.O_TRUNC)

    disallowed_chars = re.compile(r'[^\w-]+')
    leading_nonletters = re.compile(r'^([^a-z]+)(.*)')
    layers_meta = {}
    layer_order = []
    for layer in reversed(image.layers):
        layer_order.append(layer.name)
        #maybe parasites could be used instead, but I can't find any documentation on what the flags are
        layers_meta[layer.name] = {}
        layers_meta[layer.name]['x'], layers_meta[layer.name]['y'] = layer.offsets
        layers_meta[layer.name]['x2'] = layers_meta[layer.name]['x'] + layer.width
        layers_meta[layer.name]['y2'] = layers_meta[layer.name]['y'] + layer.height
        #TODO: only export visible layers
        #TODO: test for empty and duplicate ids
        #replace disallowed characters with an underscore
        layers_meta[layer.name]['id'] = disallowed_chars.sub('_', layer.name.lower())
        #remove leading non-letters
        layers_meta[layer.name]['id'] = leading_nonletters.sub(r'\2_\1', layers_meta[layer.name]['id'])
        #remove leading and trailing underscores
        layers_meta[layer.name]['id'] = layers_meta[layer.name]['id'].strip('_')
        layers_meta[layer.name]['z-index'] = layer.ID

        if layers_meta[layer.name]['id'] is '':
            layers_meta[layer.name]['id'] = str(layer.ID)

        #logger.debug(layers_meta[layer.name]['id'])

        if not pdb.gimp_drawable_is_text_layer(layer) or extract_text_images:
            logger.debug('extracting: %s' % layer.name)
            image_path = os.path.join(directory, media_dir, image_filename_template % (layers_meta[layer.name]['id'], os.path.extsep))
            logger.debug('path: %s' % image_path)
            #the path relative from the css file
            layers_meta[layer.name]['image_rel_path'] = os.path.relpath(image_path, os.path.dirname(css_file_path))
            #if layer is an image extract it to filename_files/
            add_progress(1)
            gimp.progress_init('psd2html: Saving %s' % image_path)
            if export_images:
                # lkk change order
                #pdb.gimp_file_save(image, layer, image_path, image_path, run_mode=1)
                pdb.gimp_file_save(1, image, layer, image_path, image_path)
            add_progress(2)
        else:
            add_progress(3)

    d, layers = layers_to_dict(reversed(image.layers), layers_meta)
    css, html = get_html(None, d, layers, layers_meta, layer_order, css_opacity)

    html.insert(0, html_body_open_template % os.path.relpath(css_file_path, os.path.dirname(html_file_path)))
    html.append(html_body_close_template)

    css = string.join(css)
    html = string.join(html)

    gimp.progress_init('psd2html: Saving %s' % html_file_path)
    os.write(html_file, html)
    os.close(html_file)
    add_progress(1)
    gimp.progress_init('psd2html: Saving %s' % css_file_path)
    os.write(css_file, css)
    os.close(css_file)
    add_progress(1)

    gimp.progress_init('psd2html: Finished')
    gimp.progress_update(1)
    #to do later: detect if multiple layers have the same size and position and treat them like buttons. Option to extract as css sprites.
    #to do later: use an XML library to construct .html file. Use an XHTML 1.0 Strict doctype and validate the markup.
    #to do later: add the following optional tests:
    #                Validate XHTML, CSS, JS
    #                Convert generated XHTML to image, compare it to flattened PSD

register(
    "psd2html",
    N_("Converts a .psd file (or other layered image) to an .html template."),
    N_("This is a Python plug-in for the GIMP that will extract images and text out of a .psd file (or other layered image) and create an .html template from it. I don't think this plugin will ever fully replace a human coder, but it should be able to do 50-90% of the work."),
    "Seán Hayes",
    "Seán Hayes",
    "2010",
    N_("_Convert to HTML..."),
    "*",
    [
        (PF_IMAGE, "image", _("Input image"), None),
        (PF_DRAWABLE, "drawable", _("Input drawable"), None),
        (PF_TOGGLE, "css-opacity", _("Whether to use CSS to specify opacity (1, True) or save it in the image file (0, False)."), True),
        (PF_TOGGLE, "extract-text-images", _("Extract images for text layers. Off by default, but you may want to turn this on if you have text in a special font that users aren't likely to have."), False),
        #TODO: add option for interactive file saving
        #to do later: add options for manually choosing CSS and JS to use, could be useful for compatibility with CSS and JS frameworks
    ],
    [],
    plugin_func,
    menu="<Image>/Filters/Web",
    domain=(gettext_domain, gimp.locale_directory),
)

main()
