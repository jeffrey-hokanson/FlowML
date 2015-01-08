from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import six
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.path as mpath
import matplotlib.patches as mpatches

from IPython.html import widgets
from IPython.display import display
from IPython.utils.traitlets import Unicode, Integer

import mpld3
from mpld3._display import NumpyEncoder
from mpld3.urls import MPLD3_URL, D3_URL
from mpld3.utils import get_id
from mpld3.mplexporter import Exporter
from mpld3.mpld3renderer import MPLD3Renderer

import json
import random


JAVASCRIPT = r"""require(["widgets/js/widget"], function(WidgetManager){
    
    var fig;
    var FigureView = IPython.DOMWidgetView.extend({
        render: function(){
            IPython.figure_view = this;
            IPython.test_model = this.model;  // debugging
            this.$figure = $('<div />')
                .attr('id', this.model.get('figid'))
                .appendTo(this.$el);

            var that = this;
            
            // This must be called after the DOM is updated
            // to include the <div> for this view.
            var draw_plot =  function() {
                // Fill div with mpld3 figure.
                var figid = that.model.get('figid');
                var figure_json = JSON.parse(that.model.get('figure_json'));
                var extra_js = that.model.get('extra_js');
            
                if(typeof(window.mpld3) !== "undefined" && window.mpld3._mpld3IsLoaded){
                    !function (mpld3){
                            eval(extra_js);
                            that.fig = mpld3.draw_figure(figid, figure_json);
                    }(mpld3);
                } else {
                    var d3_url = that.model.get('d3_url');
                    var mpld3_url = that.model.get('mpld3_url');
                    require.config({paths: {d3: d3_url }});
                    require(["d3"], function(d3){
                        window.d3 = d3;
                        $.getScript(mpld3_url, function(){
                            eval(extra_js);
                            that.fig = mpld3.draw_figure(figid, figure_json);
                        });
                    });
                }
            };
            
            var handle_coord_change = function(coord_name) {
                that.move_point(coord_name);
            };

            this.model.on("change:x0", handle_coord_change('x0'));
            this.model.on("change:initialized", draw_plot);
            
        },
        
        move_point: function(coord_name) {
            
            var that = this;
            
            if(typeof(window.mpld3) !== "undefined" && window.mpld3._mpld3IsLoaded){
                console.log("HEY");
                !function (mpld3){
                    var pts = mpld3.get_element(that.model.get('idpts'));
                    console.log(pts);
                    if (pts != null) {
                        pts.elements().transition().attr('x', 2);
                        console.log('moved');
                    }
                }(mpld3);
            } else {
                var d3_url = this.model.get('d3_url');
                var mpld3_url = this.model.get('mpld3_url');
                require.config({paths: {d3: d3_url }});
                require(["d3"], function(d3){
                    window.d3 = d3;
                    console.log("HEY");
                    $.getScript(mpld3_url, function(){
                        var pts = mpld3.get_element(that.model.get('idpts'));
                        console.log(pts);
                        if (pts != null) {
                            pts.elements().transition().attr('x', 2);
                            console.log('moved');
                        }
                    });
                });
            }
        },
        
        update: function() {
            
            return;
        
        },
        
    });
    WidgetManager.register_widget_view('FigureView', FigureView);
});"""


def crop(image):
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
    
    fig, ax = plt.subplots()

    Path = mpath.Path
    path_data = [
	(Path.MOVETO, (0, 0)),
	(Path.LINETO, (0, image.shape[0])),
	(Path.LINETO, (image.shape[1], image.shape[0])),
	(Path.LINETO, (image.shape[1], 0)),
	(Path.CLOSEPOLY, (image.shape[1], 0)),
	]
    codes, verts = zip(*path_data)
    path = mpath.Path(verts, codes)
    patch = mpatches.PathPatch(path, facecolor='r', alpha=0.5)
    ax.add_patch(patch)

    # plot control points and connecting lines
    x, y = zip(*path.vertices[:-1])
    points = ax.plot(x, y, 'go', ms=10)
    line = ax.plot(x, y, '-k')

    ax.grid(True, color='gray', alpha=0.5)
    ax.imshow(image)
    ax.axis('equal')
    ax.set_title("Drag Points to Change Path", fontsize=18)

    mpld3.plugins.connect(fig, LinkedDragPlugin(points[0], line[0], patch))

    renderer = MPLD3Renderer()
    Exporter(renderer, close_mpl=False).run(fig)
    fig, figure_json, extra_css, extra_js = renderer.finished_figures[0]


    my_widget = FigureWidget()
    my_widget.figure_json = json.dumps(figure_json, cls=NumpyEncoder)
    my_widget.extra_js = extra_js
    my_widget.extra_css = extra_css
    my_widget.figid = 'fig_' + get_id(fig) + str(int(random.random() * 1E10))
    my_widget.idpts = mpld3.utils.get_id(points[0], 'pts')
    my_widget.y1 = image.shape[0]
    my_widget.x2 = image.shape[1]
    my_widget.x2 = image.shape[0]
    my_widget.x3 = image.shape[1]

    display(Javascript(JAVASCRIPT))
    fig.clf()

    return my_widget


class LinkedDragPlugin(mpld3.plugins.PluginBase):
    JAVASCRIPT = r"""
    mpld3.register_plugin("drag", DragPlugin);
    DragPlugin.prototype = Object.create(mpld3.Plugin.prototype);
    DragPlugin.prototype.constructor = DragPlugin;
    DragPlugin.prototype.requiredProps = ["idpts", "idline", "idpatch"];
    DragPlugin.prototype.defaultProps = {}
    function DragPlugin(fig, props){
        mpld3.Plugin.call(this, fig, props);
    };

    DragPlugin.prototype.draw = function(){
        var patchobj = mpld3.get_element(this.props.idpatch, this.fig);
        var ptsobj = mpld3.get_element(this.props.idpts, this.fig);
        var lineobj = mpld3.get_element(this.props.idline, this.fig);

        var drag = d3.behavior.drag()
            .origin(function(d) { return {x:ptsobj.ax.x(d[0]),
                                          y:ptsobj.ax.y(d[1])}; })
            .on("dragstart", dragstarted)
            .on("drag", dragged)
            .on("dragend", dragended);

        lineobj.path.attr("d", lineobj.datafunc(ptsobj.offsets));
        patchobj.path.attr("d", patchobj.datafunc(ptsobj.offsets,
                                                  patchobj.pathcodes));
        lineobj.data = ptsobj.offsets;
        patchobj.data = ptsobj.offsets;

        ptsobj.elements()
           .data(ptsobj.offsets)
           .style("cursor", "default")
           .call(drag);

        function dragstarted(d) {
          d3.event.sourceEvent.stopPropagation();
          d3.select(this).classed("dragging", true);
        }

        function dragged(d, i) {
          d[0] = ptsobj.ax.x.invert(d3.event.x);
          d[1] = ptsobj.ax.y.invert(d3.event.y);
          d3.select(this)
            .attr("transform", "translate(" + [d3.event.x,d3.event.y] + ")");
          lineobj.path.attr("d", lineobj.datafunc(ptsobj.offsets));
          patchobj.path.attr("d", patchobj.datafunc(ptsobj.offsets,
                                                    patchobj.pathcodes));
        }

        function dragended(d, i) {
          d3.select(this).classed("dragging", false);
          IPython.test_model.set('x' + i.toString(), Math.round(d[0]));
          IPython.test_model.set('y' + i.toString(), Math.round(d[1]));
          IPython.figure_view.touch();
        }
    }

    mpld3.register_plugin("drag", DragPlugin);
    """

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
    _view_name = Unicode('FigureView', sync=True)
    
    mpld3_url = Unicode(MPLD3_URL, sync=True)  # TODO: Allow local mpld3 and d3.
    d3_url = Unicode(D3_URL[:-3], sync=True)
    
    figure_json = Unicode('', sync=True)  # to be filled in after instantiation
    extra_js = Unicode('', sync=True)  # for plugin support
    extra_css = Unicode('', sync=True)
    
    figid = Unicode('', sync=True)
    initialized = Unicode('', sync=True)  # used to trigger first drawing after DOM is updated
    
    x0 = Integer(0, sync=True)  # will connect to a slider widget
    y0 = Integer(0, sync=True)  # will connect to a slider widget
    x1 = Integer(0, sync=True)  # will connect to a slider widget
    y1 = Integer(0, sync=True)  # will connect to a slider widget
    x2 = Integer(0, sync=True)  # will connect to a slider widget
    y2 = Integer(0, sync=True)  # will connect to a slider widget
    x3 = Integer(0, sync=True)  # will connect to a slider widget
    y3 = Integer(0, sync=True)  # will connect to a slider widget
    idpts = Unicode('', sync=True)
    
    @property
    def slice(self):
        return [slice(min(self.y0, self.y1, self.y2, self.y3),
                      max(self.y0, self.y1, self.y2, self.y3)),
                slice(min(self.x0, self.x1, self.x2, self.x3),
                      max(self.x0, self.x1, self.x2, self.x3))]

    def display(self):
        display(self)
        self.initialized = ' '
