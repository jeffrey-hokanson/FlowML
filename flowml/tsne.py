# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
from bhtsne.bhtsne import bh_tsne, DEFAULT_PERPLEXITY, DEFAULT_THETA
import numpy as np

"""This holds the code actually implementing the t-SNE embedding.
"""

# TODO: Write python based bh-tsne


def tsne(points, perplexity = DEFAULT_PERPLEXITY, theta = DEFAULT_THETA, verbose = False):
    """Calls the best avalible implementation of t-SNE
    
    Currently only returns a two dimensional embedding.

    points - numpy matrix of coordinates, reading points across rows
    """


    # TODO: Currently, this calls Pontus Stenetorp's wrapper of Laurens van der
    # Maaten's Barnes-Hut t-SNE code, which is limited to non-commerical use.
    # We should implement a fresh, non-encumbered version

    npoints = points.shape[0]
    
    # this returns a generator, which returns a two entry array
    while True:
        try:
            gen = bh_tsne(points, perplexity, theta, verbose)
            break
        except:
            pass

    output = np.zeros((npoints, 2))
    for j, val in enumerate(gen):
        output[j][0] = val[0]
        output[j][1] = val[1]
    return output



