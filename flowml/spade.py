#!/usr/bin/env python
# -*- coding: latin_1 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import numpy as np
from math import floor, ceil
from scipy.spatial import cKDTree as KDTree
from scipy.spatial.distance import cityblock, pdist, squareform
from scipy.cluster.hierarchy import fcluster
from scipy.sparse.csgraph import minimum_spanning_tree as mst
from scipy.sparse import coo_matrix

import pyximport; pyximport.install()
from sum_pairs import _sum_pairs

try:
    from fastcluster import linkage, linkage_vector
except:
    from scipy.cluster.hierarchy import linkage


def _matrix_sum_pairs(pairs, m):
    # For each pair, we increase the local density for each. The operation is:
    # local_density = np.zeros(data.shape[0])
    # for p in pairs:
    #    local_density[p[0]] += 1
    #    local_density[p[1]] += 1 
    # This is a python based loop and too slow.  We use a coo_matrix to do
    # this sum rapidly.
    pairs = np.array(list(pairs))
    n = pairs.shape[0]
    X1 = coo_matrix( (np.ones(n), (pairs[:,0], np.zeros(n))), shape = (m,1) )
    X2 = coo_matrix( (np.ones(n), (pairs[:,1], np.zeros(n))), shape = (m,1) )
    X1 = np.array(X1.tocsr().todense()).reshape(-1)
    X2 = np.array(X2.tocsr().todense()).reshape(-1)
    local_density = X1 + X2
    return local_density 

def _slow_sum_pairs(pairs, m):
    local_density = np.zeros(m)
    for p in pairs:
        local_density[p[0]] += 1
        local_density[p[1]] += 1 

    return local_density


def downsample(data, npoints = 2000, distance_metric = 1, 
        distance_threshold = None, alpha = 5, outlier_percentile = 1.,
        target_percentile = 3., outlier_density = None, 
        target_density = None):
    """Performs density dependent downsampling as defined in SPADE.
        
    See algorithm description in section S8 in the supplemental material of
    Peng Qiu's SPADE paper in Nature Biotechnology.

    Local density is computed as the number of points within distance_threshold
    of the current point in the ell-p norm specified by distance_metric.
    If distance_threshold is not given, we estimate it as alpha times the 
    median distance between points.

    Arguments
    ---------
    data - numpy matrix where each data point is a row: e.g., an n x p matrix
        describes n points in p dimensional space.
    npoints - number of points to downsample to.
    distance_metric - which ell-p norm to use when computing distances for 
        downsampling penalties
    distance_threshold - size of balls when computing local_density
    alpha - coefficient for estimating distance_threshold if not specified.
    target_percentile - percentile of local density that picks the target
        density
    outlier_percentile - percentile of local density that picks outlier 
        density
    """

    # Initialize the KDTree we use for computing pairwise distances
    kdtree = KDTree(data)

    # Step 1: estiamte the median distance between points to compute the
    # distance threshold
    if distance_threshold is None:
        # Subsample a few points to get a notion of distance
        n_subsample = 2000
        if n_subsample < data.shape[0]:
            index = np.random.choice(data.shape[0], n_subsample, replace = False)
            x = data[index,:]
        else:
            index = np.arange(data.shape[0])
            x = data

        # Compute the distance between the points in x and other points
        # in the dataset.  We pick k = 2, since the nearest point is
        # the point itself.
        (dist, i) = kdtree.query(x, k = 2, p = distance_metric) 
        dist = dist[:,1]

        median_dist = np.median(dist)
        distance_threshold = alpha*median_dist

    # Step 2: compute local density for each point
    # First we compute a list of pairs that are within radius distance_threshold
    
    # An old implementation used the query_pairs function, but this proved too
    # slow
    # pairs = kdtree.query_pairs(distance_threshold, distance_metric)
    # local_density = _sum_pairs(pairs, data.shape[0])    
    
    # Using query_ball_point gave made the resulting code 75% faster.
    dens = kdtree.query_ball_point(data, distance_threshold, distance_metric)
    local_density = np.array( [ len(den) - 1 for den in dens ])
    
    #local_density = _slow_sum_pairs(pairs, data.shape[0])
    #print np.allclose(ld2, local_density)
    #print local_density

    # Step 3: Downsample points on local density

    # If we have only been given percentiles to downsample on, determine
    # the corresponding density.
    if target_density is None or outlier_density is None:
        local_density_sort = np.sort(local_density)
    if target_density is None:
        idx = int(floor(local_density.shape[0]*target_percentile/100.))
        target_density = local_density_sort[idx]
    if outlier_density is None:
        idx = int(floor(local_density.shape[0]*outlier_percentile/100.))
        outlier_density = local_density_sort[idx]

    # Determine events that must remain in the dataset (those correspodning to local density
    # between outlier and target density
    prob = np.less_equal(outlier_density, local_density)*np.less(local_density,target_density)
    #print "There are {} cells that are outliers".format(np.sum(prob)) 
    downsampled = data[prob,:]
    
    # Now we assign probabilities to points in high density regions
    prob = np.less(target_density, local_density)*(target_density/(local_density + 1e-14))
    prob_sum = prob.sum()
    #print "There are {} cells that are in the target range".format(int(ceil(prob_sum)))
    # Only if cells fall in this range, actually downsample
    if prob_sum > 0:
        idx = np.random.choice(data.shape[0], int(ceil(prob_sum)), replace = False, p = prob/prob_sum)
        downsampled = np.vstack( (downsampled, data[idx,:]) )

    return downsampled


def agglom_cluster(down, nclusters):
    """Performs agglomerative clustering on downsampled data

    as per paper, this is single linkage, L1 distance metric 
    """ 

    # see http://www.jstatsoft.org/v53/i09/paper for details on fastcluster
    # by Daniel Müllnerout of Carlsson's group
    
    # NOTE: Ideally, we would call the linkage function as
    # `Z = linkage(down, method = 'single', metric = cityblock)`
    # which would prevent the explicit formation of a distance matrix
    # however, since this involves calling back to Python, the overhead
    # is too much.  So we form the distance matrix and pass it to the 
    # linkage function.
    try:
        Z = linkage_vector(down, method = 'single', metric = 'cityblock')
    except:
        dist = pdist(down, metric = 'minkowski', p = 1)
        Z = linkage(dist, method = 'single', preserve_input = False)
    return fcluster(Z, nclusters, criterion = 'maxclust') 
   

def minimum_spanning_tree(cluster_means):
    """
    L1 single linkage, minimum spanning tree
    """
    dist = pdist(cluster_means, metric = 'minkowski', p = 1)
    #dist = mst(squareform(dist), overwrite = False)
    dist = mst(squareform(dist), overwrite = False)
    return dist 

def drive(fdarray, channels = None, nclusters = 200,
        npoints = 2000, 
        transform = lambda x: np.arcsinh(5*x),
        label = 'SPADE_CLUSTER' ):
    """Driver for SPADE

    fdarray - Array of FlowData types
    channels - list of markers
    nclusters - number of clusters desired
    """

    # STEP 1: Density Dependent Downsampling
    data = []
    data_transformed = []
    for j, fd in enumerate(fdarray):
        # Grab matrix data and transform
        if channels is None:
            X = transform(fd.matrix())
        else:
            X = transform(fd.matrix(*channels))
        data_transformed.append(X)
        # Downsample
        down = downsample(X, npoints = npoints)
        # Attach label
        data.append(np.hstack( (down, j * np.ones( (down.shape[0],1)) )))
    
    # STEP 2: Pool downsampled data
    data = np.vstack(data)
    
    # STEP 3: Clustering
    clust = agglom_cluster(data[:,0:-1], nclusters)
    nclusters = np.max(clust)
    
    # STEP 4: Minimum spanning tree
    cluster_means = np.zeros( (nclusters, data.shape[1]-1))
    for j in range(nclusters):
        idx = (clust == j + 1)
        cluster_means[j,:] = np.mean( data[idx,0:-1], axis =0)
    
    mst = minimum_spanning_tree(cluster_means)   
    
    # STEP 5: Upsample
    kdtree = KDTree(data[:,0:-1])
    
    for j, X in enumerate(data_transformed):
        # Get nearest neigbors 
        d, nearest = kdtree.query(X, p = 1)
        cluster_upsample = clust[nearest]

        fd[label] = cluster_upsample
        fd.spade_mst[label] = mst
        fd.spade_means[label] = cluster_means
    return dist 

