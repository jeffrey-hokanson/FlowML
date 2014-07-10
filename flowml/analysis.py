# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import numpy as np
import matplotlib
import matplotlib.pyplot as plt

from kde import kde

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
    
    data = []
    titles = []
    # Attempt to load data
    for ds in datasets:
        try:
            data.append(ds[[axis1,axis2]].values)
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
        xmin = min([np.min(d[:,0]) for d in data])
    if xmax is None and range is None:
        xmax = max([np.max(d[:,0]) for d in data])
    if ymin is None and range is None:
        ymin = min([np.min(d[:,1]) for d in data])
    if ymax is None and range is None:
        ymax = max([np.max(d[:,1]) for d in data])


    fig, ax = plt.subplots()
    xgrid = np.linspace(xmin, xmax, npoints[0])
    ygrid = np.linspace(xmin, xmax, npoints[1])
    for (d, t) in zip(data, titles):
        den = kde.hat_linear2(d, bandwidth, npoints, xmin, xmax, ymin, ymax)
        #ax.pcolor(xgrid, ygrid, den)
        ax.imshow(den, norm = matplotlib.colors.SymLogNorm(1))
    print np.max(den)
    ax.set_xlabel(axis1)
    ax.set_ylabel(axis2) 
    return fig

def hist1(axis, datasets, bins = None, xmin = None, xmax = None, range = None):
    
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
     
    
    fig, ax = plt.subplots()
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
        patch = matplotlib.patches.PathPatch(barpath, facecolor = base_line.get_color(), edgecolor = base_line.get_color(),  alpha = 0.2)
        ax.add_patch(patch)
        max_value = max(max_value, top.max())
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(1, max_value )
    ax.set_yscale('log')

    
    ax.set_xlabel(axis)    

    return fig

def hist2(axis1, axis2, datasets, bins = None, xmin = None, xmax = None, ymin = None, ymax = None, range = None):
    
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

    
    fig, ax = plt.subplots()
    # We do not use the Matplotlib API for histograms because we want to have transparent plots
    # Following example: http://matplotlib.org/examples/api/histogram_path_demo.html
    max_value = float('-inf')
    for (dx, dy, t) in zip(datax, datay, titles ):
        ax.hist2d(dx, dy, bins = bins, norm = matplotlib.colors.LogNorm()) 
    
    ax.set_xlabel(axis1)
    ax.set_ylabel(axis2)    

    return fig

