# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from kde import kde

from mpld3 import plugins
import tsne as lib_tsne

import util
from util import CYTOF_LENGTH_NAMES

# backgating in tsne
from scipy.spatial import cKDTree as KDTree

def kde1(datasets, axis, bandwidth = None, npoints = 1001, xmin = None, xmax = None, xrange_ = None, axes = None):
    """
    """
    # Extract data
    data = util.extract_data(datasets, axis) 
    titles = util.extract_title(datasets)
    xmin, xmax = util.set_limits(data, xmin, xmax, xrange_, axis)    
   
    if bandwidth is None:
        bandwidth = util.default_bandwidth(axis, npoints, xmin, xmax)

    fig, ax = util.fig_ax(axes)     
    fig._flowml_axis = (axis, )
 
    xgrid = np.linspace(xmin, xmax, npoints)
    for (d, t) in zip(data, titles):
        den = kde.hat_linear(d, bandwidth, xmin, xmax, npoints)
        ax.plot(xgrid, den, label = t)
    
    ax.set_yscale(util.default_yscale(axis))
    ax.set_xlabel(axis)
    ax.set_ylabel('Density Estimate')
    if len(data) > 1:
        ax.legend()
    else:
        ax.set_title(titles[0])
    return fig


def kde2(datasets, axis1, axis2, bandwidth = 1.0, npoints = (100,100),
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

def hist1(datasets, axis, bins = None, xmin = None, xmax = None, xrange_ = None, axes = None):
    """One dimensional histograms.
    """

    # Extract data
    data = util.extract_data(datasets, axis) 
    titles = util.extract_title(datasets)
    xmin, xmax = util.set_limits(data, xmin, xmax, xrange_, axis)    
    
    if bins is None:
        bins = util.bin_default(axis, xmin, xmax)

    fig, ax = util.fig_ax(axes)     
    fig._flowml_axis = (axis, )

    # Plotting preferences
    alpha = util.alpha(len(data)) 
    
    # We do not use the Matplotlib API for histograms because we want to have transparent plots
    # Following example: http://matplotlib.org/examples/api/histogram_path_demo.html
    max_value = float('-inf')

    for (d, t) in zip(data, titles ):
        (hist, bin_edges) = np.histogram(d, bins = bins, range = (xmin, xmax))
        left = np.array(bin_edges[:-1])
        right = np.array(bin_edges[1:])
        # FIXES a bug in MPLD3 0.3 regarding NaNs in coordinates
        bottom = 1e-6*np.ones(len(left))
        top = bottom + hist
        XY = np.array([[left,left,right,right], [bottom, top, top, bottom]]).T
        barpath = matplotlib.path.Path.make_compound_path_from_polys(XY)
        # serves to get the current color
        base_line, = ax.plot(hist, alpha = 0)
        patch = matplotlib.patches.PathPatch(barpath, facecolor = base_line.get_color(), 
                    edgecolor = base_line.get_color(),  alpha = alpha)
        # Clear the unneeded line 
        base_line.remove()
        patch.set_label(t)
        ax.add_patch(patch)
        max_value = max(max_value, top.max())
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(1, max_value )
   
    ax.set_xlabel(axis)
    ax.set_yscale(util.default_yscale(axis))
    if len(data) > 1:
        ax.legend()
    else:
        ax.set_title(titles[0])
    return fig

def hist2(datasets, axis1, axis2, bins = None, 
        xmin = None, xmax = None, ymin = None, ymax = None, range_ = None,
        axes = None, transform = None):
    
   
    datax = util.extract_data(datasets, axis1) 
    datay = util.extract_data(datasets, axis2) 
    titles = util.extract_title(datasets)

    try: 
        xrange_ = range_[0]
        yrange_ = range_[1]
    except:
        xrange_ = None
        yrange_ = None

    xmin, xmax = util.set_limits(datax, xmin, xmax, xrange_, axis1)
    ymin, ymax = util.set_limits(datay, ymin, ymax, yrange_, axis2)
  
    if not isinstance(transform, (list, tuple)):
        transform = [transform, transform]
    scaling = [None, None]

    scaling[0], transform[0] = util.default_scaling(axis1, scaling = scaling[0], transform = transform[0])
    scaling[1], transform[1] = util.default_scaling(axis2, scaling = scaling[1], transform = transform[1])
    
    for index, d in enumerate(datax):
        datax[index] = transform[0](d)
    for index, d in enumerate(datay):
        datay[index] = transform[1](d) 
    
    xmin_transformed, xmax_transformed = util.set_limits(datax)
    ymin_transformed, ymax_transformed = util.set_limits(datay)
    
    # Determine how many bins to use 
    if bins is None:
        bins = [None, None]
    if isinstance(bins, int):
        bins = [bins, bins]
    bins = list(bins)
    bins[0] = util.bin_default(axis1, xmin, xmax, bins = bins[0])
    bins[1] = util.bin_default(axis2, xmin, xmax, bins = bins[1])

    fig, ax = util.fig_ax(axes)     
    fig._flowml_axis = (axis1, axis2)
    # We do not use the Matplotlib API for histograms because we want to have transparent plots
    # Following example: http://matplotlib.org/examples/api/histogram_path_demo.html

    den_ = []
    range_ = ((xmin_transformed, xmax_transformed),(ymin_transformed, ymax_transformed)) 
    for (dx, dy) in zip(datax, datay):
        den, xedge, yedge = np.histogram2d(dx, dy, bins = bins, range = range_) 
        den_.append(den)
    
    alpha = util.alpha(len(den_))       

    proxy = []
    line_collections = []
    levels = 10**np.arange(0,7)
    for den in den_: 
        line, = ax.plot(0,0)
        ln = ax.imshow(den.T, cmap = make_cmap(line.get_color()), origin = 'lower',
                        norm = matplotlib.colors.LogNorm(),
                        extent = [xmin, xmax, ymin, ymax],
                        interpolation = 'none',
                        aspect = 'auto')
        line_collections.append(ln)
        proxy.append( plt.Rectangle((0,0),1,1,fc = line.get_color(),alpha = alpha))
        line.remove()
   
    if len(datax) == 1:
        ax.set_title(titles[0])
    elif len(datax) > 1:
        ax.legend(proxy, titles)
    ax.set_xlabel(axis1)
    ax.set_ylabel(axis2) 
    
    ax.set_xscale(scaling[0])
    ax.set_yscale(scaling[1]) 

    return fig

def make_cmap(target, background = None):
    if background is None:
        background = 'white'
    cc = matplotlib.colors.ColorConverter()
    target = cc.to_rgb(target)
    background = cc.to_rgb(background)
    # Start halfway to filled
    start = [(bg*0.9+0.1*tg) for bg, tg in zip(background, target)]
    
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

    alpha = util.alpha(len(den_))       
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
        
        #print xticks
        #print xticklabels
        #print len(xticks)
        #print len(xticklabels)
        ax.set_xticks(xticks)
        ax.set_xticklabels(xticklabels)
        ax.set_yticks(yticks)
        ax.set_yticklabels(yticklabels)    




    # This feature does not yet work with this kind of density plot
    #plugins.connect(ax.figure, plugins.InteractiveLegendPlugin(line_collections, titles)) 


def mean_matrix(datasets, axes = None, label = None):
    """Computes the mean intensity matrix for given axes and label

    Args:
        dataset (list): List of FlowData objects
    
    Kwargs:
        axes (list): list of column names to evaluate (e.g., 'CD45')
        label (list or string): name(s) of boolean columns in datasets
    """
    fn = lambda fd, axis: fd[axis].mean()
    
    return fn_matrix(datasets, fn, axes, label)

def median_matrix(datasets, axes = None, label = None):
    """Computes the median intensity matrix for given axes and label

    Args:
        dataset (list): List of FlowData objects
    
    Kwargs:
        axes (list): list of column names to evaluate (e.g., 'CD45')
        label (list or string): name(s) of boolean columns in datasets
    """
    fn = lambda fd, axis: fd[axis].median()
    
    return fn_matrix(datasets, fn, axes, label)

def count_matrix(datasets, labels):
    """Counts the events in the given label.

    Args:
        dataset (list): List of FlowData objects
        label (list or string): name(s) of boolean columns in datasets
    """
    
    fn = lambda fd, axis: fd.shape[0]
    return fn_matrix(datasets, fn, axes = None, label = labels)

def percent_matrix(datasets, label, relative_to = None):
    """Precentage of events with a given label.

    Args:
        dataset (list): List of FlowData objects
        label (list or string): name(s) of boolean columns in datasets
    """
    
    if relative_to is None: 
        fn = lambda fd, la: fd[fd[la]].shape[0]*100./fd._original_length
    else:
        fn = lambda fd, la: fd[fd[la]].shape[0]*100./fd[fd[relative_to]].shape[0]
    matrix = [ [ fn(fd,la) for fd in datasets] for la in label]
    cols = [fd.title for fd in datasets]
    mat = pd.DataFrame(matrix, index = label, columns = cols)

    # https://stackoverflow.com/questions/18876022/how-to-format-ipython-html-display-of-pandas-dataframe
    style = '<style>.dataframe td { text-align: right; }</style>'

    from IPython.display import HTML
    int_frmt = lambda x: '{:,}'.format( x )
    float_frmt = lambda x: '{:,.0f}'.format( x ) if x > 1e3 else '{:,.2f}'.format( x )
    frmt_map = { np.dtype( 'int64' ):int_frmt, np.dtype( 'float64' ):float_frmt }
    frmt = { col:frmt_map[ mat.dtypes[ col ] ] for col in mat.columns if mat.dtypes[ col ] in frmt_map.keys( ) }
    html = HTML(style + mat.to_html( formatters=frmt ) )
    return mat


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


def tsne(fdarray, new_label = 'tsne',  channels = None, transform = 'arcsinh', sample = 6000,
         verbose = False, backgate = True):
    """Perform t-SNE/viSNE on the FlowData object
    
    """

    fdarray = util.make_list(fdarray)

    # If the user has not provided a list of channels to use, 
    # use the intersection of all isotope channels
    if channels is None:
        channel_set = []
        for fd in fdarray:
            channel_set.append(set(fd.isotopes))
        channels = list(set.intersection(*channel_set))
    
    # Make a copy of the data in files that we want    
    points = []
    for fd in fdarray:
        points.append(np.vstack([ fd[ch] for ch in channels ]).T)

    # transform
    if transform == 'arcsinh':
        for pts in points:
            # Apply the transform inplace to the data
            np.arcsinh(5*pts, pts)
    
    # Randomly sample to reduce the number of points
    sample_masks = []
    for pts in points:
        if sample < pts.shape[0]:
            # If we have enough points to subsample
            sample_masks.append(np.random.choice(pts.shape[0], sample, replace = False))
        else:
            # Otherwise we add all the points
            sample_masks.append(np.array(range(pts.shape[0])))

    # Sample the points, and construct a large matrix
    sample_points = []
    for mask, pts in zip(sample_masks, points):
        sample_points.append(pts[mask,:])
    X = np.vstack(sample_points)

    # Perform t-SNE
    Y = lib_tsne.tsne(X, verbose = verbose)
    assert Y is not None, ('t-SNE failed to return') 

    # Split Y into a matrix for each dataset
    splits = np.cumsum( np.array([ mask.shape[0] for mask in sample_masks], dtype = int))
    Y_split = np.split(Y, splits, axis = 0)

    # now expand data to reassign these points back into the dataset
    tsne_coords = []
    for (pts, mask, Yspt) in zip(points, sample_masks, Y_split):
        npoints = pts.shape[0]
        Z = np.zeros((npoints, 2))*float('NaN')
        Z[mask,:] = Yspt
        tsne_coords.append(Z)

    # If a point didn't get sampled, place its t-SNE coordinates at its nearest 
    # neighbor.
    if backgate:
        kd = KDTree(X)
        # select points not assigned values with t-SNE
        for pts, mask, coords, j  in zip(points, sample_masks, tsne_coords, range(len(points))):
            nan_points = np.argwhere(np.isnan(coords[:,0]))            
            d,near = kd.query(pts[nan_points],1) 
            # convert back to coordinates on the whole dataset
            coords[nan_points, :] = Y[near,:]
            tsne_coords[j] = coords
    # add to data to FlowData structure
    for fd, coords in zip(fdarray, tsne_coords):
        fd[new_label+'1'] = coords[:,0]
        fd[new_label+'2'] = coords[:,1]



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


def spade_plot(datasets, label = 'SPADE_CLUSTER', channel = None):
    pass
 


    


 
