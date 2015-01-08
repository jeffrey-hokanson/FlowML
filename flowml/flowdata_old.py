# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
#
# A package containing a data structure for a single flow cytometry experiment

from __future__ import print_function

import os
import pandas as pd
import fcs
import numpy as np
from kde import kde

import matplotlib.pyplot as plt
from IPython.html.widgets import interact
from functools32 import lru_cache


class FlowCore(object):
    """FlowCore: Provides data analysis facilities for classes that can access
    labeld columns via __getitem__ 
    """
    def kde(self, axis):
        """Plot a kernel density estimate of the given axis (a single item or tuple)
        """
        if axis in self:
            print(axis)

        data = self[axis]
        xmin = np.min(data)
        xmax = np.max(data)
        bandwidth = 0.5
        npoints = 1000
        den = kde.hat_linear(self[axis], bandwidth, xmin, xmax, npoints)
        den = den*len(data)/self._original_length + 1e-10
        xgrid = np.linspace(xmin, xmax, npoints)

        fig, ax = plt.subplots()
        ax.plot(xgrid, den)



class FlowPandas(pd.DataFrame, FlowCore):
    def __init__(self, filename):
        (data, metadata, analysis, meta_analysis) = fcs.read(filename)
        
        # List of column names
        columns = map(lambda j: metadata['$P{}N'.format(j)], range(1,data.shape[0]+1))
        
        # There is an endian-ness bug that requires changing the type of data to satisfy
        # pandas
        super(FlowData,self).__init__(np.transpose(data).astype('f8'),  columns = columns)
       

        # This variable encodes the original length of the data set as imported for use
        # normalizing kernel density estimates 
        self._original_length = int(metadata['$TOT'])
        # Name that will appear in the legend of plots
        self.title = ''
        try:
            self.title = metadata['$FIL']
        except:
            pass

        self._metadata = metadata
        self._analysis = analysis
        self._meta_analysis = meta_analysis
        self._data = data

from lc import LabeledColumns

class FlowData(FlowCore):
    def __init__(self, filename):
        (data, metadata, analysis, meta_analysis) = fcs.read(filename)
        
        # List of column names
        columns = map(lambda j: metadata['$P{}N'.format(j)], range(1,data.shape[0]+1))
        
        self._data = LabeledColumns(data, columns) 

        # Same for Analysis
        columns = map(lambda j: metadata['$P{}N'.format(j)], range(1,data.shape[0]+1))
        self._analysis = LabeledColumns(analysis, columns)
        
        # This variable encodes the original length of the data set as imported for use
        # normalizing kernel density estimates 
        self._original_length = int(metadata['$TOT'])
        # Name that will appear in the legend of plots
        self.title = ''
        try:
            self.title = metadata['$FIL']
        except:
            pass

        self._metadata = metadata
        self._meta_analysis = meta_analysis
