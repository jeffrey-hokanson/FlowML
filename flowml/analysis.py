# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from kde import kde

from mpld3 import plugins
import tsne as lib_tsne

CYTOF_LENGTH_NAMES = ['Event_length', 'Cell_length']


def kde1(axis, datasets, bandwidth = 0.5, npoints = 1001, xmin = None, xmax = None, range = None ):
    """
    """
    data = []
    titles = []
    # Attempt to load data
    for ds in datasets:
        try:
            data.append(ds[axis].values)
            titles.append(ds.title)
        except KeyError:
            print('Warning, no such column name found')
    try: 
        xmin = range[0]
        xmax = range[1]
    except:
        pass

    # Determine the range, if we were not provided one
    if xmin is None and range is None:
        xmin = min([np.min(d) for d in data])
    if xmax is None and range is None:
        xmax = max([np.max(d) for d in data])
        
    fig, ax = plt.subplots()
    fig._flowml_axis = (axis, )
    xgrid = np.linspace(xmin, xmax, npoints)
    for (d, t) in zip(data, titles):
        den = kde.hat_linear(d, bandwidth, xmin, xmax, npoints)
        ax.plot(xgrid, den, label = t)
    ax.set_yscale('log')
    ax.set_xlabel(axis)
    return fig


def kde2(axis1, axis2, datasets, bandwidth = 1.0, npoints = (100,100),
        xmin = None, xmax = None, ymin = None, ymax = None, 
        range = None):
    
    datax = []
    datay = []
    titles = []
    # Attempt to load data
    for ds in datasets:
        try:
            datax.append(ds[axis1].values)
            datay.append(ds[axis2].values)
            titles.append(ds.title)
        except KeyError:
            print('Warning, no such column name found')
    
    try: 
        xmin = range[0][0]
        xmax = range[0][1]
        ymin = range[1][0]
        ymax = range[1][1]
    except:
        pass
   
    # Set ranges automatically if not provided 
    if xmin is None and range is None:
        xmin = min([np.min(d) for d in datax])
    if xmax is None and range is None:
        xmax = max([np.max(d) for d in datax])
    if ymin is None and range is None:
        ymin = min([np.min(d) for d in datay])
    if ymax is None and range is None:
        ymax = max([np.max(d) for d in datay])

    fig, ax = plt.subplots()
    fig._flowml_axis = (axis1, axis2)
    xgrid = np.linspace(xmin, xmax, npoints[0])
    ygrid = np.linspace(xmin, xmax, npoints[1])
    
    den_ = [kde.hat_linear2(dx, dy, bandwidth, npoints, xmin, xmax, ymin, ymax) 
                for dx, dy in zip(datax, datay)]
    _2d_backend(ax, den_, xgrid, ygrid, titles, axis1, axis2)
    return fig

def hist1(axis, datasets, bins = None, xmin = None, xmax = None, range = None, axes = None):
    
    data = []
    titles = []
    # Attempt to load data
    for ds in datasets:
        try:
            data.append(ds[axis].values)
            titles.append(ds.title)
        except KeyError:
            print('Warning, no such column name found')
    
    try: 
        xmin = range[0]
        xmax = range[1]
    except:
        pass
    
    if xmin is None and range is None:
        xmin = min([np.min(d) for d in data])
    if xmax is None and range is None:
        xmax = max([np.max(d) for d in data])
    
    if axis in CYTOF_LENGTH_NAMES and bins is None:
        bins = xmax - xmin
   
    if bins is None:
        bins = 100
     
    if axes is None: 
        fig, ax = plt.subplots()
    else:
        ax = axes
        fig = ax.figure

    fig._flowml_axis = (axis, )
    # We do not use the Matplotlib API for histograms because we want to have transparent plots
    # Following example: http://matplotlib.org/examples/api/histogram_path_demo.html
    max_value = float('-inf')
    for (d, t) in zip(data, titles ):
        (hist, bin_edges) = np.histogram(d, bins = bins, range = (xmin, xmax))
        left = np.array(bin_edges[:-1])
        right = np.array(bin_edges[1:])
        bottom = 1e-6*np.ones(len(left))
        top = bottom + hist
        XY = np.array([[left,left,right,right], [bottom, top, top, bottom]]).T
        barpath = matplotlib.path.Path.make_compound_path_from_polys(XY)
        base_line, = ax.plot(hist, alpha = 0)
        patch = matplotlib.patches.PathPatch(barpath, facecolor = base_line.get_color(), edgecolor = base_line.get_color(),  alpha = 0.1)
        # Clear the unneeded line 
        base_line.remove()
        patch.set_label(t)
        ax.add_patch(patch)
        max_value = max(max_value, top.max())
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(1, max_value )
    ax.set_yscale('log')
    ax.legend()
    
    ax.set_xlabel(axis)    

    return fig

def hist2(axis1, axis2, datasets, bins = None, 
        xmin = None, xmax = None, ymin = None, ymax = None, range = None,
        axes = None, transform = None):
    
    datax = []
    datay = []
    titles = []
    # Attempt to load data
    for ds in datasets:
        try:
            datax.append(ds[axis1].values)
            datay.append(ds[axis2].values)
            titles.append(ds.title)
        except KeyError:
            print('Warning, no such column name found')
    
    try: 
        xmin = range[0][0]
        xmax = range[0][1]
        ymin = range[1][0]
        ymax = range[1][1]
    except:
        pass
    
    if transform is None:
        identity = lambda x: x
        transform = (identity, identity)

    if not isinstance(transform, (list, tuple)):
        transform = [transform, transform]
    
    for index, t in enumerate(transform):
        if t == 'log':
            transform[index] = lambda x: np.log(x)
        if t == 'arcsinh':
            transform[index] = lambda x: np.arcsinh(x)

 
    for index, d in enumerate(datax):
        datax[index] = transform[0](d)
    for index, d in enumerate(datay):
        datay[index] = transform[1](d) 

    if xmin is None and range is None:
        xmin = min([np.min(d) for d in datax])
    if xmax is None and range is None:
        xmax = max([np.max(d) for d in datax])
    if ymin is None and range is None:
        ymin = min([np.min(d) for d in datay])
    if ymax is None and range is None:
        ymax = max([np.max(d) for d in datay])


    default_bins = [100,100]
    if axis1 in CYTOF_LENGTH_NAMES:
        default_bins[0] = xmax - xmin + 1
    if axis2 in CYTOF_LENGTH_NAMES:
        default_bins[1] = ymax - ymin + 1
    
    if bins is None:
        bins = default_bins



    if axes is None: 
        fig, ax = plt.subplots()
    else:
        ax = axes
        fig = ax.figure
    fig._flowml_axis = (axis1, axis2)
    # We do not use the Matplotlib API for histograms because we want to have transparent plots
    # Following example: http://matplotlib.org/examples/api/histogram_path_demo.html

    den_ = []
    for (dx, dy) in zip(datax, datay):
        den, xedge, yedge = np.histogram2d(dx, dy, bins = bins, range = ((xmin, xmax), (ymin, ymax))) 
        den_.append(den)
    _2d_backend(ax, den_, xedge[0:-1], yedge[0:-1], titles, axis1, axis2, transform)
    

    return fig



def make_cmap(target, background = None):
    if background is None:
        background = 'white'
    cc = matplotlib.colors.ColorConverter()
    target = cc.to_rgb(target)
    background = cc.to_rgb(background)
    # Start halfway to filled
    start = [(bg+tg)/2 for bg, tg in zip(background, target)]
    
    cdict = {'red': [], 'green': [], 'blue': []}
    for (v, c) in zip(start, ['red', 'green', 'blue']):
        cdict[c].append( (0, v, v))
    for (v, c) in zip(target, ['red', 'green', 'blue']):
        cdict[c].append( (1, v, v))
    
    cmap = matplotlib.colors.LinearSegmentedColormap('my_colormap', cdict, 256)
    # makes under-range values transparent
    cmap.set_under(alpha = 0)


    return cmap
    
    
def _2d_backend(ax, den_, xgrid, ygrid, titles, axis1, axis2, transform = None):
    alpha = 0.4
    proxy = []
    line_collections = []
    levels = 10**np.arange(0,7)
    for den in den_: 
        line, = ax.plot(0,0)
        #ln = ax.contourf(xgrid, ygrid, den.T,
        #            norm = matplotlib.colors.LogNorm(vmin=1.), 
        #            cmap = make_cmap(line.get_color()), alpha = alpha,
        #            levels = levels) 
        ln = ax.imshow(den.T, cmap = make_cmap(line.get_color()), origin = 'lower',
                        norm = matplotlib.colors.LogNorm(),
                        extent = [np.min(xgrid), np.max(xgrid), np.min(ygrid), np.max(ygrid)],
                        interpolation = 'none',
                        aspect = 'auto')
        line_collections.append(ln)
        proxy.append( plt.Rectangle((0,0),1,1,fc = line.get_color(),alpha = alpha))
        line.remove()

    ax.legend(proxy, titles)
    ax.set_xlabel(axis1)
    ax.set_ylabel(axis2) 

    if transform is not None:
        # set ticks
        xticks = transform[0](np.concatenate([0*np.ones(1), 10**np.arange(0,6)]))
        yticks = transform[1](np.concatenate([0*np.ones(1), 10**np.arange(0,6)]))
        xticklabels = ["0"]
        for j in range(0,6):
            xticklabels.append("1e{}".format(j))
        yticklabels = ["0"]
        for j in range(0,6):
            yticklabels.append("1e{}".format(j))
        
        print xticks
        print xticklabels
        print len(xticks)
        print len(xticklabels)
        ax.set_xticks(xticks)
        ax.set_xticklabels(xticklabels)
        ax.set_yticks(yticks)
        ax.set_yticklabels(yticklabels)    




    # This feature does not yet work with this kind of density plot
    #plugins.connect(ax.figure, plugins.InteractiveLegendPlugin(line_collections, titles)) 


def mi_matrix(datasets, axes = None, label = None):
    """Computes the mean intensity matrix for given axes and label

    Args:
        dataset (list): List of FlowData objects
    
    Kwargs:
        axes (list): list of column names to evaluate (e.g., 'CD45')
        label (list or string): name(s) of boolean columns in datasets
    """
    fn = lambda fd, axis: fd[axis].mean()
    
    return fn_matrix(datasets, fn, axes, label)

def count_matrix(datasets, labels):
    """Counts the events in the given label.

    Args:
        dataset (list): List of FlowData objects
        label (list or string): name(s) of boolean columns in datasets
    """
    
    fn = lambda fd, axis: fd.shape[0]
    return fn_matrix(datasets, fd, axes = None, label = labels)

def percent_matrix(datasets, label):
    """Precentage of events with a given label.

    Args:
        dataset (list): List of FlowData objects
        label (list or string): name(s) of boolean columns in datasets
    """
    fn = lambda fd, axis: fd.shape[0]*100./fd._original_length
    return fn_matrix(datasets, fn, axes = None, label = label)


def fn_matrix(datasets, fn, axes = None, label = None):
    """Apply a function to a list of datasets and either a list of axes or labels.

    Applies a user provided function *fn* to produce a matrix with columns for
    each dataset and rows either given by axes or label.  Both axes and label
    cannot both be lists.   
    
    Args:
        dataset (list): List of FlowData objects
        fn (function): A function taking a FlowData object and a column name 
                      and returning a value.
    
    Kwargs:
        axes (list): list of column names to evaluate (e.g., 'CD45')
        label (list or string): name(s) of boolean columns in datasets
    """

    if isinstance(axes, list) and isinstance(label, list):
        raise NotImplementedError('Only one of label or axes can be a list')

    # By default, run over axes if no keywords given
    if axes is None and label is None:
        axes = datasets[0].columns
 
    if axes is None:
        if isinstance(label, str):
            label = [label]
        matrix = [ [fn(fd[fd[la]], axes) for fd in datasets] for la in label]
        index = label
    elif isinstance(axes, list):
        index = axes
        if label is not None:
            matrix = [ [ fn(fd[fd[label]], axis) for fd in datasets] for axis in axes]
        else:
            matrix = [ [ fn(fd, axis) for fd in datasets] for axis in axes]
    
    cols = [fd.title for fd in datasets]
    mfn = pd.DataFrame(matrix, index = index, columns = cols)
    return mfn


def tsne(fd, new_label,  channels = None, transform = 'arcsinh', sample = 6000, verbose = False):
    """Perform t-SNE/viSNE on the FlowData object
    
    """

    if channels is None:
        channels = fd.isotopes

    points = np.vstack([ fd[ch] for ch in channels ]).T
    npoints = points.shape[0]
    # randomly sample
    idx = np.random.choice(points.shape[0], sample, replace = False)
    points = points[idx,:]

    # transform
    if transform == 'arcsinh':
        np.arcsinh(5*points, points)
    # perform t-SNE
    Y = lib_tsne.tsne(points, verbose = verbose)

    # now expand data to reassign these points back into the dataset
    Z = np.zeros( (npoints,2))*float('NaN')
    Z[idx,:] = Y
    # add to data view
    fd[new_label+'1'] = Z[:,0]
    fd[new_label+'2'] = Z[:,1]



def heatmap(df, cmap ='RdBu' ):
    """Draw a heatmap table.

    
    """

    # TODO: mpld3 does not display axis labels properly

    # TODO: Replace with an interactive plot, see bokeh:
    # http://bokeh.pydata.org/docs/gallery/les_mis.html

    fig, ax = plt.subplots()
    data = df.as_matrix()
    if isinstance(cmap, str):
        cmap = plt.get_cmap(cmap)

    ax.pcolor(data, cmap = cmap)
    ax.set_xticks(np.arange(data.shape[1])+0.5, minor = False)
    ax.set_xticklabels(df.columns)
    
    ax.set_yticks(np.arange(data.shape[0])+0.5, minor = False)
    ax.set_yticklabels(df.index)
    ax.invert_yaxis()
    ax.xaxis.tick_top()

    return fig 
