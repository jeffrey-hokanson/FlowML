# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
""" Sensible default configuration scripts.

There are many conventions in flow cytometry regarding plotting.  This file
contains many functions that assist in setting these defaults.
"""

import numpy as np
import flowdata
from matplotlib import pylab as plt
CYTOF_LENGTH_NAMES = ['Event_length', 'Cell_length']
CYTOF_LENGTH_NAMES += [x.lower() for x in CYTOF_LENGTH_NAMES]
CYTOF_TIME_NAMES = ['time']

# List of Isotopes used by the CyTOF
ISOTOPE_LIST = [ 'I127', 'Rh103',
                 'Xe131', 'Cs133', 'La139', 'Ce140', 'Pr141', 'Nd142', 'Nd143',
                 'Nd144', 'Nd145', 'Nd146', 'Sm147', 'Nd148', 'Sm149', 'Nd150',
                 'Eu151', 'Sm152', 'Eu153', 'Sm154', 'Gd155', 'Gd156', 'Gd158',
                 'Tb159', 'Gd160', 'Dy161', 'Dy162', 'Dy163', 'Dy164', 'Ho165',
                 'Er166', 'Er167', 'Er168', 'Tm169', 'Er170', 'Yb171', 'Yb172',
                 'Yb173', 'Yb174', 'Lu175', 'Yb176', 'Ir191', 'Ir193', 'Pt195']


def alt_names(names, short_names):
    """Generate a dictionary of alternate names for name. 
    Used to allow easier access to columns when used interactively.
    """
    alt_names = {}
    for name, short_name in zip(names, short_names):    
        alt_names[short_name] = name
        for isotope in ISOTOPE_LIST:
            if isotope.lower() in short_name.lower() or isotope.lower() in name.lower():
                alt_names[isotope] = name
   
    return alt_names

# TODO
def is_cytof():
    """Function to determine if the machine is a CyTOF
    """
    raise NotImplementedError

################################################################################
# Plotting Utility Functions
################################################################################

def default_bandwidth(channel, npoints, xmin, xmax):
    bandwidth = 0.5
    if channel.lower() in CYTOF_TIME_NAMES:
        bandwidth = (xmax - xmin)/ npoints

    if channel.lower() in CYTOF_LENGTH_NAMES:
        bandwidth = 1.

    return bandwidth

def default_scaling(channel, scaling = None, transform = None):
    """ Return a tuple of the preferred axis scaling and transform.
    The preferred axis scaling is one of 'linear' or 'log'.
    This should refer to a valid matplotlib transform

    The transform is applied to the data before using a kernel density 
    estimator or histogram for binning.
    """
    
    if scaling is None and transform is None:
        scaling = 'arcsinh'
    if scaling is None and transform == 'linear':
        scaling = 'linear'


    if transform is None:
        transform = lambda x: np.arcsinh(5*x)
    else:
        if transform == 'arcsinh':
            transform = lambda x: np.arcsinh(5*x)
        elif transform == 'linear':
            transform = lambda x: x
        elif transform == 'log':
            transform = lambda x: np.log(x)
 
    if channel.lower() in [ x.lower() for x in CYTOF_LENGTH_NAMES]:
        scaling = 'linear'
        transform = lambda x: x
    if channel.lower() in [ x.lower() for x in CYTOF_TIME_NAMES]:
        scaling = 'linear'
        transform = lambda x: x

    return (scaling, transform)

def default_yscale(channel):
    scaling = 'log'
    if channel.lower() in ['time']:
        scaling = 'linear'
    return scaling

def bin_default(channel, xmin, xmax, bins = None):
    """Default spacing of bins given data.
    """
    if bins is None:
        bins = 200

    if channel in CYTOF_LENGTH_NAMES:
        bins = xmax - xmin

    return bins

def alpha(items):
    """Returns an alpha value corresponding to the number of items given.
    """
    if items == 1:
        alpha = 1
    else:
        alpha = 0.1
    return alpha

def make_list(datasets):
    """
    """

    if isinstance(datasets, flowdata.FlowCore):
        return [datasets]
    else:
        return datasets

def set_limits(data, xmin = None, xmax = None, xrange_ = None, axis = None):
    """Determine bounding range of multiple datasets
    """
    
    # First see if we have a valid xrange_ given
    try:
        xmin = xrange_[0]
        xmax = xrange_[1]
    except:
        pass

    # Otherwise, we try the keyword arguments
    if xmin is None:
        xmin = min([np.min(d) for d in data])
    if xmax is None:
        xmax = max([np.max(d) for d in data])
  
    try: 
        if axis.lower() in CYTOF_TIME_NAMES:
            xmin = 0
    except:
        pass
    return xmin, xmax


def extract_data(datasets, channels):
    datasets = make_list(datasets)
    data = []
    if isinstance(channels, str):
        channel = channels
        for ds in datasets:
            try:
                data.append(ds[channel].values)
            except KeyError:
                print('Warning, no such column name found')
        return data
    else:
        for channel in channels:
            tmp_data = []
            for ds in datasets:
                try:
                    print channel
                    tmp_data.append(ds[channel].values)
                except KeyError:
                    print('Warning, no such column name found')
            data.append(tmp_data)
        return data

def extract_title(datasets):
    datasets = make_list(datasets)
    try:
        titles = [ ds.title for ds in datasets]
        return titles
    except AttributeError:
        print("Does not have title attribute")

def fig_ax(axes):
    if axes is None: 
        fig, ax = plt.subplots()
    else:
        ax = axes
        fig = ax.figure
    return fig, ax



