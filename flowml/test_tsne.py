import numpy as np
from tsne import tsne


X = np.random.rand(1000,30)

Y = tsne(X, verbose = True)
