#!/usr/bin/env python
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import math
import numpy as np
from scipy.spatial import cKDTree as KDTree

# Number of points to downsample to
DEFAULT_DOWNSAMPLE = 2000   
DEFAULT_DISTANCE_METRIC = 1
DEFAULT_DISTANCE_THRESHOLD = None
# if distance_threshold is none, then distance_threshold = median_min_dist * alpha
DEFAULT_ALPHA = 5

class Spade:
    """ Class implementing Peng Qiu's SPADE algorithm, following S8 in the
    supplemental methods of his Nature Paper.
    """
    nsamples = 2000
    distance_metric = 1
    distance_threshold = None
    alpha = 5   # if distance_threshold is none, then distance_threshold = median_min_dist * alpha

    def __init__(self, data, use_KD_tree = True):
        # We assume that data comes in the format stored in Flowdata class
        self.data = data.transpose()
        self.use_KD_tree = use_KD_tree
        
        if self.use_KD_tree:
            self._init_KD_tree()

        if self.use_KD_tree is False:
            self.kd_tree = None
    

    def run(self):
        """ 
            Apply SPADE algorithm
        """
        # Step 1: apply density dependent downsampling
        self.estimate_median_dist()
        self.compute_local_density()
        self.downsample()

    def _init_KD_tree(self):
        self.kd_tree = KDTree(self.data)

    def estimate_median_dist(self):
        """Estimate the median distance between cells.
        This is used to compute 
        """
        # Randomly selected indices
        if self.nsamples >= self.data.shape[1]:
            index = np.random.choice(self.data.shape[0], self.nsamples, replace = False)
            x = self.data[index,:]
        else:
            index = np.range(0,self.data.shape[0])
            x = self.data
        
        # which ell_p norm is used

        if self.use_KD_tree:
            # We need to take the first two points (k=2), since distance of the point
            # to itself is zero.
            (dist, i) = self.kd_tree.query(x, k=2, p = self.distance_metric)
            dist = dist[:,1] 
        else:
            dist = np.zeros(self.nsamples)
            d = np.zeros(self.data.shape[0])
            for j in range(self.nsamples):
                err = (np.abs(x[j] - self.data))**distance_metric
                np.sum(err,axis=1,out=d) 
                # give infinite distance to the point with itself
                d[index[j]] = float('inf')
                dist[j] = d.min()
        
        self.median_dist = np.median(dist)
    
        if self.distance_threshold is None:
            self.distance_threshold =  self.alpha*self.median_dist   

        return self.median_dist
    

    def compute_local_density_using_pairs(self):
        local_density = np.zeros(self.data.shape[0])
       
        if self.use_KD_tree:
            pairs = self.kd_tree.query_pairs(self.distance_threshold, p = self.distance_metric)
            print "Found {} pairs".format(len(pairs))
            for p in pairs:
                local_density[p[0]] += 1
                local_density[p[1]] += 1

        print local_density.max()
        
        
    def compute_local_density(self): 
        print self.distance_threshold 
   
        # This approach seems slightly faster, likely due to decreased memory
        # requirements 
        if self.use_KD_tree:
            local_density = np.zeros(self.data.shape[0])
            for j in range(self.data.shape[0]):
                index = self.kd_tree.query_ball_point(self.data[j], 
                            self.distance_threshold,
                            p = self.distance_metric)
                local_density[j] = len(index) -1
        
        # A slightly slower approach, I am leaving here in case of later
        # version changes
        if self.use_KD_tree and False:
            index = self.kd_tree.query_ball_point(self.data,
                        self.distance_threshold, 
                        p = self.distance_metric)
            
            local_density = map(lambda i: len(i) - 1, index)

        print local_density
        self.local_density = local_density
        return local_density

    def downsample(self):
        target_density = 10
        outlier_density = 3
        local_density = self.local_density
        # compute the probability of keeping vector

        # events that are in the outlier range
        prob = np.less_equal(outlier_density, local_density)*np.less(local_density,target_density)
        
        downsampled_data = self.data[prob,:]

        # events that are in high density regions
        prob2 = np.less(target_density, local_density)*(target_density/(local_density + 1e-14))
         
        downsample_index = np.random.choice(self.data.shape[0], 
                                math.ceil(prob2.sum()), 
                                replace = False, 
                                p = prob2/prob2.sum())
        downsampled_data = np.append(downsampled_data, self.data[downsample_index,:])
        print downsampled_data.shape

        self.downsampled_data = downsampled_data




def main():

    import time
    import fcs

    (data, metadata, analysis, meta_analysis) = fcs.read('test.fcs')
    print data.shape
    print "Original data length {}".format(data.shape[1])
    data = data[2:20,0:5000]
    start = time.time()
    s = Spade(data, use_KD_tree = True)
    s.nsamples = 2000
    print s.estimate_median_dist()
    s.compute_local_density()
    s.downsample()
    stop = time.time()
    print "Elapsed time {}".format(stop - start)
    

if __name__ == "__main__":
    main()
