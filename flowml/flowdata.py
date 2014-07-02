# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
#
# A package containing a data structure for a single flow cytometry experiment

import os
import pandas as pd
import fcs
import numpy as np

class FlowData(pd.DataFrame):
    def __init__(self, filename):
        (data, metadata, analysis, meta_analysis) = fcs.read(filename)
        
        # List of column names
        columns = map(lambda j: metadata['$P{}N'.format(j)], range(1,data.shape[0]+1))
        
        # There is an endian-ness bug that requires changing the type of data to satisfy
        # pandas
        super(FlowData,self).__init__(np.transpose(data).astype('f8'),  columns = columns)

