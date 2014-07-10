# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
#
# A package containing a data structure for a single flow cytometry experiment

from __future__ import print_function

import os
import pandas as pd
import fcs
import numpy as np

from IPython.html.widgets import interact
from functools32 import lru_cache

from analysis import kde1, kde2, hist1, hist2


class FlowCore(object):
    """FlowCore: Provides data analysis facilities for classes that can access
    labeld columns via __getitem__ 
    """
    def kde(self, axis1, axis2 = None, **kwargs):
        """Plot a kernel density estimate of the given axis (a single item or tuple)
        """

        if axis2 is None:
            return kde1(axis1, [self], **kwargs)
        else:
            return kde2(axis1, axis2, [self], **kwargs)

    def hist(self, axis1, axis2 = None, **kwargs):
        if axis2 is None:
            return hist1(axis1, [self], **kwargs)
        else:
            return hist2(axis1, axis2, [self], **kwargs)

class FlowData(FlowCore):
    def __init__(self, filename):
        (data, metadata, analysis, meta_analysis) = fcs.read(filename)
        
        self._metadata = metadata
        self._analysis = analysis
        self._meta_analysis = meta_analysis
        self._data = data
        
        # List of column names
        columns = self.names
        
        # There is an endian-ness bug that requires changing the type of data to satisfy
        # pandas
        self.panda = pd.DataFrame(np.transpose(data).astype('f8'),  columns = columns)
       
        # This variable encodes the original length of the data set as imported for use
        # normalizing kernel density estimates 
        self._original_length = int(metadata['$TOT'])
        # Name that will appear in the legend of plots
        self.title = ''
        try:
            self.title = metadata['$FIL']
        except:
            pass



    @property
    def nparameters(self):
        """ Number of measuremen0t/property channels"""
        return self._metadata['$PAR']

    @property
    def short_names(self):
        """List of column names in the $PnN section of the FCS file
        Sometimes this corresponds to each marker; e.g., CD45.
        """
        return [self._metadata.get('$P{}N'.format(j),'{}'.format(j)) for j in range(1,self.nparameters+1)]
    @property
    def names(self):
        return [self._metadata.get('$P{}S'.format(j), self.short_names[j-1]) for j in range(1,self.nparameters+1)]
    
    def rename(self, columns):
        """Rename selected columns
        provide a dictionary mapping old names to new names
        """ 
        # Rename the columns in the metadata field
        for key in columns:
            if key in self.short_names:
                i = self.short_names.index(key)
                # NOTE: This changes the 'short name' field $PnN 
                self._metadata['$P{}N'.format(i+1)] = columns[key]
 
        self.panda.rename(columns = columns, inplace = True)


#    def gate(self, 


    # Direct calls to Pandas
    def __getitem__(self, index):
        return self.panda.__getitem__(index)
    def __str__(self):
        return self.panda.__str__()
    def __repr__(self):
        return self.panda.__repr__()
    def _repr_html_(self):
        return self.panda._repr_html_()
    def _repr_fits_vertical_(self):
        return self.panda._repr_fits_vertical_()
    def _repr_fits_horizontal_(self):
        return self.panda._repr_fits_horizontal() 
    @property
    def columns(self):
        return self.panda.columns
