# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
#
# A package containing a data structure for a single flow cytometry experiment

from __future__ import print_function
from __future__ import division


import os
import pandas as pd
import fcs
import numpy as np
import re

from IPython.html.widgets import interact
from functools32 import lru_cache

import analysis
from analysis import kde1, kde2, hist1, hist2
import gate
import copy

import matplotlib
import matplotlib.pyplot as plt

# List of Isotopes used by the CyTOF
ISOTOPE_LIST = [ 'Xe131', 'Cs133', 'La139', 'Ce140', 'Pr141', 'Nd144', 'Nd148',
                 'Eu151', 'Eu153', 'Gd156', 'Tb159', 'Dy162', 'Dy164', 'Ho165',
                 'Er166', 'Er168', 'Tm169', 'Yb172', 'Yb176', 'Ir191', 'Ir193',
                 'Pt195']

class FlowCore(object):
    """FlowCore: Provides data analysis facilities for classes that can access
    labeld columns via __getitem__ 
    """




    def matrix(self, *args):
        """Provides a numpy matrix where rows correspond to cells.

        If no arguments are provided, this returns all physical tags.
        """
        if len(args) == 0:
            args = self.physical_tags
        return np.vstack([ self[ch] for ch in args ]).T

    def kde(self, axis1, axis2 = None, **kwargs):
        """Plot a kernel density estimate of the given axis (a single item or tuple)
        """

        if axis2 is None:
            return kde1([self], axis1, **kwargs)
        else:
            return kde2([self], axis1, axis2, **kwargs)

    def hist(self, axis1, axis2 = None, **kwargs):
        if axis2 is None:
            return hist1([self], axis1, **kwargs)
        else:
            return hist2([self], axis1, axis2,  **kwargs)

    @property
    def tags(self):
        raise NotImplementedError

    @property
    def isotopes(self):
        """Provide list of isotope names used
        """
        pattern = re.compile(r"^[A-Za-z]{1,2}[1-2]\d{2}$")
        isotopes = []
        for tag in self.tags:
            if pattern.match(tag):
                isotopes.append(tag)

        return isotopes    

    @property
    def physical_tags(self):
        """List of actual tags (e.g., isotope names and fluorescent compounds)

        This does not include derived properties or additional data like time.
        """
        # TODO: Also check for fluorescent tags
        return self.isotopes


    def tsne(self, *args, **kwargs):
        """tsne wrapper
        """
        return analysis.tsne(self, *args, **kwargs)
    
    def marker_table(self):
    # TODO: Make this return an HTML table when called in IPython
        class ListTable(list):
            """Overidden to provide a pretty print table
             """
            # following http://calebmadrigal.com/display-list-as-table-in-ipython-notebook/
            def _repr_html_(self):
                html = ["<table>"]
                html.append("<tr><td>Isotope</td><td>Marker</td></tr>")
                for row in self:
                    html.append("<tr>")
                    for col in row:
                        html.append("<td>{0}</td>".format(col))
                    html.append("</tr>")
                html.append("</table>")
                return ''.join(html)

        rows = ListTable()
        for t, n in zip(self.tags, self.names):
            rows.append([t,n])
        return rows


    def tsne_plot(self, label, color_label = None, color = 'k', ax = None):
        """Show the results of t-SNE/viSNE

        """ 
        
        try:
            x = self[label + '1']
            y = self[label + '2']
        except:
            raise ValueError("The matching t-SNE/viSNE data is not in this object with name {}.  Run tsne.".format(label))

        x = x[x != float('NaN')]
        y = y[y != float('NaN')]

        if ax is None:
            fig, ax = plt.subplots()

        if color_label is None:
            ax.plot(x,y,'.',color = color)
        else:
            c = self[color_label]
            ax.scatter(x, y, c = c, s = 15, norm = matplotlib.colors.SymLogNorm(1), edgecolors = 'none') 
        
        return fig 
            

    def project(self, line, name= None):
        """Project measurements onto the line defined by line
        If name is specified, add the a new column with the specified name
        """
        
        X = []
        a = []
        for key in line:
            if key in self:
                a.append(line[key])
                X.append(self[key])
        X = np.vstack(X)
        a = np.array(a)
        Px = np.dot(a,X)/np.sqrt(np.dot(a,a))

        if name is None:
            return Px
        else:
            self[name] = Px


class FlowData(FlowCore):
    def __init__(self, filename = None,):
        """Load an FCS file specified by the filename.
        """
        (data, metadata, analysis, meta_analysis) = fcs.read(filename)
        
        self._metadata = metadata
        self._analysis = analysis
        self._meta_analysis = meta_analysis
        self._data = data
        
        # A dictionary that converts column names to index numbers
        # currently we default to using the long name value $PnS
        self._columns = self.names
        # Mapping of alternate names to column names
        self._alt_names = {}
        for col, sname in zip(self._columns, self.short_names):
            self._alt_names[sname] = col

        for col, iso in zip(self._columns, self.isotopes):
            self._alt_names[iso] = col

        # There is an endian-ness bug that requires changing the type of data to satisfy
        # pandas
        self.panda = pd.DataFrame(np.transpose(data).astype('f8'),  columns = self._columns)
        

       
        # This variable encodes the original length of the data set as imported for use
        # normalizing kernel density estimates 
        self._original_length = int(metadata['$TOT'])
        # Name that will appear in the legend of plots
        self.title = ''
        try:
            self.title = metadata['$FIL']
        except:
            pass

    
        self.spade_mst = {}
        self.spade_means = {} 

    @property
    def nparameters(self):
        """ Number of measuremen0t/property channels"""
        return int(self._metadata['$PAR'])

    @property
    def short_names(self):
        """List of column names in the $PnN section of the FCS file
        Sometimes this corresponds to each marker; e.g., CD45.
        """
        # TODO: PnN is actually the short name parameter
        
        return [self._metadata.get('$P{:d}N'.format(j),'{:d}'.format(j)) for j in range(1,self.nparameters+1)]
    @property
    def names(self):
        return [self._metadata.get('$P{:d}S'.format(j), self.short_names[j-1]) for j in range(1,self.nparameters+1)]
    
    @property 
    def shape(self):
        return self.panda.shape

    
    def fcs_export(self, filename, dtype = None):
        """Export to an FCS file
        """
        # TODO: remove this quick hack 
        #fcs.write(filename, self._data, self._metadata)  
        #return
        
        data = self.panda.values.T
        #data = np.nan_to_num(data).T
        
        data = data.astype('<f')        


        metadata = self._metadata 
        
        assert len(self._columns) == data.shape[0], "Not enough columns"
        metadata['$PAR'] = str(len(self._columns))
        
        for j, name in enumerate(self._columns):
            metadata['$P{}S'.format(j+1)] = name
            # If we don't have a previously recorded short name, use the long name
            if '$P{}N'.format(j+1) not in metadata:
                pass
                #metadata['$P{}N'.format(j+1)] = "anal{}".format(j+1)
        
        metadata['$TOT'] = str(data.shape[0])
        fcs.write(filename, data, metadata)  
            

    #@lru_cache(maxsize = None)
    @property
    def tags(self):
        """Provides the tags (e.g., Ir191) used in the experiment
        """
        tags = []
        for (sn, n) in zip(self.short_names, self.names):
            new_tag = n
            for iso in ISOTOPE_LIST:
                if iso.upper() in sn.upper() or iso.upper() in n.upper():
                    new_tag = iso
            if 'Event_length'.upper() in sn or 'Event_length'.upper() in n.upper():
                new_tag = 'Cell_length'
            tags.append(new_tag)
        return tags
                

    def rename(self, columns):
        """Rename selected columns
        provide a dictionary mapping old names to new names
        """ 
        # Rename the columns in the metadata field
        for old_name, new_name in columns.iteritems():
            assert old_name in self._columns, "Error in _columns"
            idx = self._columns.index(old_name)
            self._columns[idx] = new_name
        self.panda.rename(columns = columns, inplace = True)


    def label(self, labeler, name):
        # A boolian array determining class membership
        data = None
        if isinstance(labeler, np.ndarray) or isinstance(labeler, pd.Series):
            data = labeler
        if isinstance(labeler, gate.FigureWidget):
            axis = labeler._flowml_axis
            path = labeler.path
            pts = np.column_stack( [ self[a] for a in axis] )
            data = path.contains_points(pts) 

        if data is None:
            raise ValueError('Input labeler could not be used')
        
        self.panda[name] = data

    # Direct calls to Pandas
    def __getitem__(self, index):

        # First scan item to see if they appear using a short name
        
        
        def fix_name(name):
            return self._alt_names.get(name, name)

        if isinstance(index, str):
            index = fix_name(index)
        if isinstance(index,list):
            index = [ fix_name(i) for i in index]
        new_panda = self.panda.__getitem__(index)
        # If we get back a pandas instance, we need to make a copy of FlowData
        # and return
        if isinstance(new_panda, pd.DataFrame): 
            new = copy.deepcopy(self)
            new.panda = new_panda
            return new

        # Otherwise, we assume we got back a numpy array, and return that
        else:
            return new_panda
           
    def __setitem__(self, index, value):
        index = self._alt_names.get(index, index)
        if index not in self._columns:
            self._columns.append(index)
        else:
            self.panda[index] = value
    
    def __contains__(self, index):
        if index in self._columns or index in self._alt_names:
            return True
        else:
            return False

 

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
