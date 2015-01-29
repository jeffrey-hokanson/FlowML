# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import numpy as np

def _sum_pairs(set pairs, int m):
    local_density = np.zeros(m, dtype = np.int)
    for p in pairs:
        local_density[p[0]] += 1
        local_density[p[1]] += 1

    return local_density
