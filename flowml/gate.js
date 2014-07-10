require(["widgets/js/widget"], function(WidgetManager){
    
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
});
