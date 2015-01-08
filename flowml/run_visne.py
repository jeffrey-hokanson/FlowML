#! /opt/local/bin/python
from flowdata import FlowData

fd = FlowData('test.fcs')
fd.tsne('visne', sample = 100)
fd.write('test_write.fcs')

#fcs.write('test_write.fcs',data, metadata)

