# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
from __future__ import division
import numpy as np
import util
from louvain import *
from scipy import sparse as sp
from sklearn.cluster import KMeans

def project(fdarray, line = 'bead', column = None, orth = False):
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
        
        
        # Compute the orthogonal projector if asked.
        if not orth:
            Px = np.dot(a,X)/np.sqrt(np.dot(a,a))
        else:
            Px = np.sqrt(np.sum( (X - np.outer(a,np.dot(a,X))/np.dot(a,a) )**2, axis = 0))

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
    # STAGE 1: Estimate bead location using K-means.
    ############################################################################ 
    beadness = project(fd, bead_signature)
    # Form two clusters using K-Means on the beadness projection
    km = KMeans(2)
    n = beadness.shape[0]
    c = km.fit_predict(np.reshape(beadness, (n,1)))
    centers = km.cluster_centers_
    if centers[0] > centers[1]:
        bead = (c == 0)
    else:
        bead = (c == 1)
    ############################################################################ 
    # STAGE 2: Estimate bead intensity
    ############################################################################ 

    return bead
    

