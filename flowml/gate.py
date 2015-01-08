# This is taken from https://gist.githubusercontent.com/danielballan/ab5e28420ba1b24c5ad4/raw
# as described in http://nbviewer.ipython.org/gist/anonymous/ca4a567d58c150ae5ee0
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4


from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import six
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.path as mpath
import matplotlib.patches as mpatches

from IPython.html import widgets
from IPython.display import display
from IPython.utils.traitlets import Unicode, Float

import mpld3
from mpld3._display import NumpyEncoder
from mpld3.urls import MPLD3_URL, D3_URL
from mpld3.utils import get_id
from mpld3.mplexporter import Exporter
from mpld3.mpld3renderer import MPLD3Renderer

import json
import random

# TODO: relative paths
f = open('/Users/jhokanson/SVN/Flowml/flowml/gate.js')
JAVASCRIPT = f.read()
f.close()


def crop(ax):
    try:
	from IPython.html import widgets
	from IPython.display import display, Javascript
	from IPython.utils.traitlets import Unicode, Integer
    except ImportError:
        raise ImportError("You need IPython 2.0+ to use this feature.")
    try:
	import mpld3
	from mpld3._display import NumpyEncoder
	from mpld3.urls import MPLD3_URL, D3_URL
	from mpld3.utils import get_id
	from mpld3.mplexporter import Exporter
	from mpld3.mpld3renderer import MPLD3Renderer
    except ImportError:
         raise ImportError("You need mpld3 v0.3 to use this feature.")

    fig = None
    if isinstance(ax, mpl.figure.Figure):
        fig = ax
        ax = fig.axes[0]
    

    xmin, xmax = ax.get_xlim()
    ymin, ymax = ax.get_ylim()
    Path = mpath.Path
    path_data = [
	(Path.MOVETO, (xmin + 0.25*(xmax - xmin), ymin + 0.25*(ymax - ymin))),
	(Path.LINETO, (xmin + 0.25*(xmax - xmin), ymin + 0.75*(ymax - ymin))),
	(Path.LINETO, (xmin + 0.75*(xmax - xmin), ymin + 0.75*(ymax - ymin))),
	(Path.LINETO, (xmin + 0.75*(xmax - xmin), ymin + 0.25*(ymax - ymin))),
	(Path.CLOSEPOLY, (xmin + 0.75*(xmax - xmin), ymin + 0.25*(ymax - ymin))),
	]
    codes, verts = zip(*path_data)
    path = mpath.Path(verts, codes)
    patch = mpatches.PathPatch(path, facecolor='r', alpha=0.5)
    ax.add_patch(patch)
    fig = ax.figure
    # plot control points and connecting lines
    x, y = zip(*path.vertices[:-1])
    points = ax.plot(x, y, 'go', ms=10)
    line = ax.plot(x, y, '-k')

    ax.set_title("Drag Points to Change Path", fontsize=18)

    mpld3.plugins.connect(ax.figure, LinkedDragPlugin(points[0], line[0], patch))

    renderer = MPLD3Renderer()
    Exporter(renderer, close_mpl=False).run(fig)
    fig, figure_json, extra_css, extra_js = renderer.finished_figures[0]


    my_widget = FigureWidget()
    my_widget.figure_json = json.dumps(figure_json, cls=NumpyEncoder)
    my_widget.extra_js = extra_js
    my_widget.extra_css = extra_css
    my_widget.figid = 'fig_' + get_id(fig) + str(int(random.random() * 1E10))
    my_widget.idpts = mpld3.utils.get_id(points[0], 'pts')
    my_widget.x1 = xmin + 0.25*(xmax - xmin) 
    my_widget.x2 = xmin + 0.25*(xmax - xmin) 
    my_widget.x3 = xmin + 0.75*(xmax - xmin) 
    my_widget.x4 = xmin + 0.75*(xmax - xmin) 
    my_widget.y1 = ymin + 0.25*(ymax - ymin)
    my_widget.y2 = ymin + 0.75*(ymax - ymin)
    my_widget.y3 = ymin + 0.75*(ymax - ymin)
    my_widget.y4 = ymin + 0.75*(ymax - ymin)

    # Copy over preservation of axis information if looking at a FlowML
    # generated figure.
    if hasattr(fig, '_flowml_axis'):
        my_widget._flowml_axis = fig._flowml_axis

    display(Javascript(JAVASCRIPT))
    fig.clf()

    return my_widget


class LinkedDragPlugin(mpld3.plugins.PluginBase):
    # TODO: relative paths
    f = open('/Users/jhokanson/SVN/Flowml/flowml/linked_drag.js')
    JAVASCRIPT = f.read()
    f.close()

    def __init__(self, points, line, patch):
        if isinstance(points, mpl.lines.Line2D):
            suffix = "pts"
        else:
            suffix = None

        self.dict_ = {"type": "drag",
                      "idpts": get_id(points, suffix),
                      "idline": get_id(line),
                      "idpatch": get_id(patch)}


class FigureWidget(widgets.DOMWidget):
    # TODO: store state between sessions
    # return arrays
    _view_name = Unicode('FigureView', sync=True)
    
    mpld3_url = Unicode(MPLD3_URL, sync=True)  # TODO: Allow local mpld3 and d3.
    d3_url = Unicode(D3_URL[:-3], sync=True)
    
    figure_json = Unicode('', sync=True)  # to be filled in after instantiation
    extra_js = Unicode('', sync=True)  # for plugin support
    extra_css = Unicode('', sync=True)
    
    figid = Unicode('', sync=True)
    initialized = Unicode('', sync=True)  # used to trigger first drawing after DOM is updated
    
    x0 = Float(0, sync=True)  # will connect to a slider widget
    y0 = Float(0, sync=True)  # will connect to a slider widget
    x1 = Float(0, sync=True)  # will connect to a slider widget
    y1 = Float(0, sync=True)  # will connect to a slider widget
    x2 = Float(0, sync=True)  # will connect to a slider widget
    y2 = Float(0, sync=True)  # will connect to a slider widget
    x3 = Float(0, sync=True)  # will connect to a slider widget
    y3 = Float(0, sync=True)  # will connect to a slider widget
    idpts = Unicode('', sync=True)
    
    def display(self):
        display(self)
        self.initialized = ' '

    @property
    def path(self):
        Path = mpath.Path 
        path_data = [
                (Path.MOVETO, (self.x0, self.y0)),
                (Path.LINETO, (self.x1, self.y1)),
                (Path.LINETO, (self.x2, self.y2)),
                (Path.LINETO, (self.x3, self.y3)),
                (Path.CLOSEPOLY, (self.x3, self.y3))
                ]
        codes, verts = zip(*path_data)
        path  = mpath.Path(verts, codes)
        return path
