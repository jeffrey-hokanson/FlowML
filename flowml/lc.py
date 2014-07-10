# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
import numpy as np

class LabeledColumns:
    """LabeledColumns: a minimalist clone of Pandas's features for data with labeled columns.
    The data model use here is that each row is interchangable with access via named columns.
    """
    def __init__(self, data = None, columns = None):
        # TODO: Add checking for size of column list
        # TODO: split data into 1D arrays
        self.data = data
        self.columns = columns

    def __getitem__(self, index):
        # First check if we have to select a subset
        if index.__class__ is np.ndarray or isinstance(index, int) or isinstance(index, slice):
            new = LabeledColumns()
            new.data = self.data[index,:]
            new.columns = self.columns
            return new

        # If we provide a single column name
        if index in self.columns:
            i = self.columns.index(index)
            return self.data[:,i]
        # If we provide a list of column names
        i = []
        for ind in index:
            try:
                i.append(self.columns.index(ind))
            except ValueError:
                raise ValueError("'{}' is not a valid column".format(ind))
        return self.data[:,i]

    def __str__(self):
        val = "{}".format(self.columns)
        val += '\n' + self.data.__str__()
        return val



