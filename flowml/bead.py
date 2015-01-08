# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import numpy as np
import util

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

