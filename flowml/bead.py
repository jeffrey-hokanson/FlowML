# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
from __future__ import division
import numpy as np
import util
from louvain import *
from scipy import sparse as sp
from ipython_progress import progress_bar

def project(fdarray, line = 'bead', column = None):
    """Project onto a subspace defined by line.
    Line is either a string, specifying a predefined line or a dictionary 
    with keys that are isotope labels and values that are ratios,
    e.g., if line = 'bead', sets
    
    line = {'Ce140': 88.45, 'Ce142':11.11, 'Eu151':47.8,
            'Eu153':52.1, 'Ho165':100., 'Lu175':97.4, 'Lu176': 2.6}
    
    The projection uses only those markers that are avalible in the datasets.

    If column is not None, then a new column is appended to each flow dataset. 

    If there is only one element in fdarray, then this returns the projection
    of each event.

    The predefined line values are:
        bead - 4 Isotope bead labels
        cell - Ir191/Ir193 stain
    """

    if line == 'bead':
        line = {'Ce140': 88.45, 'Ce142':11.11, 'Eu151':47.8,
                'Eu153':52.1, 'Ho165':100., 'Lu175':97.4, 'Lu176': 2.6}

    if line == 'cell':
        line = {'Ir191': 37.3, 'Ir193':62.7}

    
    fdarray = util.make_list(fdarray)

    for fd in fdarray:
        a = np.zeros(len(fd.isotopes))
        for j, isotope in enumerate(fd.isotopes):
            if isotope in line:
                a[j]=line[isotope]
        X = np.vstack([fd[ch] for ch in fd.isotopes])
        Px = np.dot(a,X)/np.sqrt(np.dot(a,a))
        
        if column is not None:
            fd[column] = Px

    if len(fdarray) == 1:
        return Px


def calibrate(fd, bead_indicator, bead_value, target_median):
    """ Calibrate the provided flow data objects on their physical tags values;
    all other derived tags should be recomputed.
    This modifies data in place

    bead_indicator - boolean channel indicating if event is bead or not
    bead_value - channel in fd of the "beadness" of an event; 
                usually from project.
    target_median - value for the median of the bead_value 
    """

    sample_median = np.median(fd[fd[bead_indicator]][bead_value])
    scale = target_median/sample_median
    for ch in fd.physical_tags:
        #fd[ch] = fd[ch].apply(lambda x: x*scale)
        fd[ch] = fd[ch].copy()*scale



def identify_beads(fd, bead_signature = None):
    

    # Process options for the bead signature
    if bead_signature is None:
        bead_signature = 'quadbead'
    if bead_signature == 'eubead':
        bead_signature = {'Eu151': 47.8, 'Eu153': 52.1} 
    if bead_signature == 'quadbead':
        bead_signature = {'Ce140': 88.45, 'Ce142':11.11, 'Eu151':47.8,
                'Eu153':52.1, 'Ho165':100., 'Lu175':97.4, 'Lu176': 2.6}

    ############################################################################ 
    # STAGE 1: Estimate bead intensity
    ############################################################################ 
    beadness = project(fd, bead_signature)


    

    # First assemble the sparse adjaceny matrix
    sigma = 50
    tol = 1e-7
    # Empty arrays for each point
    i = []
    j = []
    v = []
    # build array of the distances between points, measured by a gaussian with fixed width
    #X = np.exp(-np.add.outer(beadness, -beadness)**2/(2*sigma**2))*(1/(sigma*np.sqrt(2*np.pi)))
    # Make this matrix sparse by only keeping elements above tol
    #I = np.argwhere(X>tol)  
    #for II in I:
    #    i.append(II[0])
    #    j.append(II[1])
    #    v.append(X[II])

    # Dumb enumerative approach
    #for ii, x in enumerate(beadness):
    #    for jj, y in enumerate(beadness):
    #        vv = np.exp( (x-y)**2/(2*sigma**2))/(sigma*np.sqrt(2*np.pi))
    #        if vv > tol
    #            i.append(ii)
    #            j.append(jj)
    #            v.append(vv)


    for ii, x in progress_bar(enumerate(beadness), expected_size = beadness.shape[0]):
        row = np.exp(-(x -beadness)**2/(2*sigma**2))*(1/(sigma*np.sqrt(2*np.pi)))
        J = np.argwhere(row>tol)
        for jj in J:
            i.append(ii)
            j.append(jj)
            v.append(row[jj])



    # Weighted distance matrix
    A = sp.coo_matrix( (v, (i,j)))
    print A
